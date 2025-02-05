import pygame
import random
import sys

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

# Sound Effects with fallback
# try:
#     hit_sound = pygame.mixer.Sound("hit.wav")
# except pygame.error:
#     hit_sound = None

# try:
#     brick_sound = pygame.mixer.Sound("brick.wav")
# except pygame.error:
#     brick_sound = None

# try:
#     game_over_sound = pygame.mixer.Sound("game_over.wav")
# except pygame.error:
#     game_over_sound = None

hit_sound = None
brick_sound = None
game_over_sound = None


# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Breakout Game++')

# Fonts
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)

class GameState:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.ball_speed = 3
        self.game_active = False
        self.show_instructions = False
        self.reset_objects()
    
    def reset_objects(self):
        # Paddle
        self.paddle = pygame.Rect(
            SCREEN_WIDTH//2 - PADDLE_WIDTH//2,
            SCREEN_HEIGHT - 30,
            PADDLE_WIDTH,
            PADDLE_HEIGHT
        )
        
        # Ball
        self.ball = pygame.Rect(
            SCREEN_WIDTH//2,
            SCREEN_HEIGHT//2,
            BALL_SIZE,
            BALL_SIZE
        )
        self.ball_dx = self.ball_speed * random.choice((1, -1))
        self.ball_dy = -self.ball_speed
        
        # Bricks
        self.bricks = []
        colors = [BLUE, (0, 100, 200), (50, 150, 255)]
        for i in range(6):
            for j in range(8):
                brick = pygame.Rect(
                    j*(BRICK_WIDTH+10) + 35,
                    i*(BRICK_HEIGHT+5) + 50,
                    BRICK_WIDTH,
                    BRICK_HEIGHT
                )
                self.bricks.append((brick, colors[i%3]))

def show_menu():
    while True:
        screen.fill(BLACK)
        
        title_text = title_font.render('BREAKOUT++', True, WHITE)
        start_text = font.render('Press SPACE to Start', True, WHITE)
        inst_text = font.render('Press I for Instructions', True, WHITE)
        
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 200))
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 350))
        screen.blit(inst_text, (SCREEN_WIDTH//2 - inst_text.get_width()//2, 400))
        
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
            "- Use LEFT/RIGHT arrows to move paddle",
            "- Break all bricks to win",
            "- You have 3 lives",
            "- Each brick gives 10 points",
            "- Ball speeds up every 5 bricks broken",
            "- Press SPACE to return to menu"
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return

def game_loop():
    state = GameState()
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        if state.game_active:
            # Move paddle
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and state.paddle.left > 0:
                state.paddle.left -= 5
            if keys[pygame.K_RIGHT] and state.paddle.right < SCREEN_WIDTH:
                state.paddle.right += 5

            # Move ball
            state.ball.x += state.ball_dx
            state.ball.y += state.ball_dy

            # Collision with walls
            if state.ball.left <= 0 or state.ball.right >= SCREEN_WIDTH:
                state.ball_dx = -state.ball_dx
                if hit_sound: hit_sound.play()
            if state.ball.top <= 0:
                state.ball_dy = -state.ball_dy
                if hit_sound: hit_sound.play()
                
            # Ball out of bottom
            if state.ball.bottom >= SCREEN_HEIGHT:
                state.lives -= 1
                if state.lives > 0:
                    state.reset_objects()
                else:
                    if game_over_sound: game_over_sound.play()
                    state.game_active = False
                continue

            # Collision with paddle
            if state.ball.colliderect(state.paddle):
                state.ball_dy = -state.ball_dy
                if hit_sound: hit_sound.play()
                state.ball_dx *= 1.02
                state.ball_dy *= 1.02

            # Collision with bricks
            for brick, color in state.bricks[:]:
                if state.ball.colliderect(brick):
                    state.bricks.remove((brick, color))
                    state.ball_dy = -state.ball_dy
                    state.score += 10
                    if brick_sound: brick_sound.play()
                    
                    if state.score % 50 == 0:
                        state.ball_dx *= 1.1
                        state.ball_dy *= 1.1
                    break

            # Drawing
            screen.fill(BLACK)
            
            for brick, color in state.bricks:
                pygame.draw.rect(screen, color, brick)
                
            pygame.draw.rect(screen, WHITE, state.paddle)
            pygame.draw.ellipse(screen, RED, state.ball)
            
            score_text = font.render(f"Score: {state.score}", True, WHITE)
            lives_text = font.render(f"Lives: {state.lives}", True, WHITE)
            screen.blit(score_text, (20, 20))
            screen.blit(lives_text, (SCREEN_WIDTH - 150, 20))
            
            if not state.bricks:
                win_text = font.render("YOU WIN! Press SPACE to continue", True, YELLOW)
                screen.blit(win_text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2))
                state.game_active = False
                
        else:
            screen.fill(BLACK)
            if state.lives <= 0:
                text = font.render("GAME OVER! Press SPACE to restart", True, RED)
            else:
                text = font.render("PAUSED - Press SPACE to continue", True, WHITE)
            
            screen.blit(text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2))
            score_text = font.render(f"Final Score: {state.score}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50))
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                if state.lives <= 0 or not state.bricks:
                    state = GameState()
                state.game_active = True

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    show_menu()
    game_loop()
