import pygame
import random
import sys
import math

# Initialization
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BRICK_WIDTH = 60
BRICK_HEIGHT = 20
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 10
BALL_SIZE = 10
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Sound Handling
hit_sound = None
brick_sound = None
game_over_sound = None

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('AutoBreakout-AI')
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)

class AIController:
    def __init__(self, paddle):
        self.paddle = paddle
        self.smoothing_factor = 0.1
        self.target_x = paddle.x
        self.response_delay = 15

    def predict_position(self, ball, dx, dy):
        if dy <= 0:
            return None
            
        time_to_paddle = (self.paddle.top - ball.bottom) / dy
        predicted_x = ball.centerx + dx * time_to_paddle
        
        # Handle wall bounces
        predicted_x = abs(predicted_x) % (2 * SCREEN_WIDTH)
        if predicted_x > SCREEN_WIDTH:
            predicted_x = 2 * SCREEN_WIDTH - predicted_x
            
        return predicted_x
        
    def update(self, ball, dx, dy):
        prediction = self.predict_position(ball, dx, dy)
        if prediction:
            target = prediction - PADDLE_WIDTH//2
            step = (target - self.target_x) * self.smoothing_factor
            step = max(-12, min(12, step))

            self.target_x += step
            self.paddle.x = int(max(0, min(SCREEN_WIDTH - PADDLE_WIDTH, self.target_x)))

class GameState:
    def __init__(self):
        self.score = 0
        self.lives = 1
        self.ball_speed = 4
        self.ai_mode = False
        self.game_active = False
        self.reset_objects()
        
    def reset_objects(self):
        # Paddle
        self.paddle = pygame.Rect(
            SCREEN_WIDTH//2 - PADDLE_WIDTH//2,
            SCREEN_HEIGHT - 50,
            PADDLE_WIDTH,
            PADDLE_HEIGHT
        )
        
        # Ball
        self.ball = pygame.Rect(
            SCREEN_WIDTH//2 - BALL_SIZE//2,
            SCREEN_HEIGHT//2 - BALL_SIZE//2,
            BALL_SIZE,
            BALL_SIZE
        )
        self.ball_dx = self.ball_speed * random.choice((1, -1))
        self.ball_dy = -self.ball_speed
        
        # Bricks
        self.bricks = []
        colors = [BLUE, (0, 100, 200), (50, 150, 255)]
        brick_start_x = (SCREEN_WIDTH - (8*(BRICK_WIDTH+20)- 25)) // 2
        brick_start_y =  30

        for i in range(7):
            for j in range(8):
                brick = pygame.Rect(
                    brick_start_x + j*(BRICK_WIDTH+10) + 35,
                    brick_start_y + i*(BRICK_HEIGHT+5) + 50,
                    BRICK_WIDTH,
                    BRICK_HEIGHT
                )
                self.bricks.append((brick, colors[i%3]))
        
        # AI
        self.ai = AIController(self.paddle)

def show_menu():
    while True:
        screen.fill(BLACK)
        
        title = title_font.render('AutoBreakout-AI', True, GREEN)
        start = font.render('Press SPACE to Start', True, WHITE)
        inst = font.render('Press I for Instructions', True, WHITE)
        
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
        screen.blit(start, (SCREEN_WIDTH//2 - start.get_width()//2, 350))
        screen.blit(inst, (SCREEN_WIDTH//2 - inst.get_width()//2, 400))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_i:
                    show_instructions()

def show_instructions():
    while True:
        screen.fill(BLACK)
        
        lines = [
            "Instructions:",
            "- ←/→: Move paddle",
            "- M: Toggle AI/Human",
            "- SPACE: Start/Pause",
            "- Break all bricks to win",
            "- 3 lives, 10 points/brick",
            "- Ball speeds up every 5 bricks",
            "- Press SPACE to return"
        ]
        
        y = 100
        for line in lines:
            text = font.render(line, True, WHITE)
            screen.blit(text, (50, y))
            y += 40
            
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return

def game_loop():
    state = GameState()
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not state.game_active:
                    running = False

                if event.key == pygame.K_m:
                    state.ai_mode = not state.ai_mode

                if event.key == pygame.K_SPACE and not state.game_active:
                    if state.lives <= 0 or not state.bricks:
                            state = GameState()
                    state.game_active = True
        
        if state.game_active:
            # Human Control
            if not state.ai_mode:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    state.paddle.left = max(0, state.paddle.left - 10)
                if keys[pygame.K_RIGHT]:
                    state.paddle.right = min(SCREEN_WIDTH, state.paddle.right + 10)
            # AI Control
            else:
                state.ai.update(state.ball, state.ball_dx, state.ball_dy)

            # Ball Movement
            state.ball.x += state.ball_dx
            state.ball.y += state.ball_dy

            # Wall Collision
            if state.ball.left <= 0 or state.ball.right >= SCREEN_WIDTH:
                state.ball_dx *= -1
            if state.ball.top <= 0:
                state.ball_dy *= -1
                
            # Lose Life
            if state.ball.bottom >= SCREEN_HEIGHT:
                state.lives -= 1
                if state.lives > 0:
                    state.reset_objects()
                else:
                    state.game_active = False
                continue

            # Paddle Collision
            if state.ball.colliderect(state.paddle):
                state.ball_dy = -abs(state.ball_dy)
                # Speed increase on hit
                state.ball_dx *= 1.01
                state.ball_dy *= 1.01

            # Brick Collision
            for brick, color in state.bricks[:]:
                if state.ball.colliderect(brick):
                    state.bricks.remove((brick, color))
                    state.ball_dy *= -1
                    state.score += 10
                    
                    # Speed boost every 5 bricks
                    if state.score % 50 == 0:
                        state.ball_dx *= 1.1
                        state.ball_dy *= 1.1
                    break

            # Drawing
            screen.fill(BLACK)
            
            # Draw Bricks
            for brick, color in state.bricks:
                pygame.draw.rect(screen, color, brick)
            
            # Draw Game Objects
            pygame.draw.rect(screen, WHITE, state.paddle)
            pygame.draw.ellipse(screen, RED, state.ball)
            
            # UI Elements
            score_text = font.render(f"Score: {state.score}", True, WHITE)
            lives_text = font.render(f"Lives: {state.lives}", True, WHITE)
            mode_text = font.render(f"Mode: {'AI' if state.ai_mode else 'Human'}", True, GREEN)
            screen.blit(score_text, (20, 20))
            screen.blit(lives_text, (SCREEN_WIDTH - 150, 20))
            screen.blit(mode_text, (SCREEN_WIDTH//2 - 50, 20))
            
            # Win Condition
            if not state.bricks:
                win_text = font.render("YOU WIN! Press SPACE", True, YELLOW)
                screen.blit(win_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2))
                state.game_active = False
                
        else:
            # Game Over/Pause Screen
            screen.fill(BLACK)
            if state.lives <= 0:
                text = font.render("GAME OVER! Press SPACE or ESC", True, RED)
            else:
                text = font.render("PAUSED - Press SPACE for continue or ESC for menu", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text, text_rect)
            
            score_text = font.render(f"Final Score: {state.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            screen.blit(score_text, score_rect)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    show_menu()
    game_loop()
