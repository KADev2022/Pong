import pygame
import random
import settings

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(
            settings.WIDTH // 2 - settings.BALL_SIZE // 2,
            settings.HEIGHT // 2 - settings.BALL_SIZE // 2,
            settings.BALL_SIZE,
            settings.BALL_SIZE
        )
        
        # Startng direction
        self.speed_x = settings.BALL_SPEED * random.choice([-1, 1])
        self.speed_y = settings.BALL_SPEED * random.choice([-1, 1])
        
        self.trail = []
    
    def move(self):
        wall_hit = False
        
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Store the new position
        self.trail.append(self.rect.center)
        
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        
        
        # Bounce off top and bottom walls
        if self.rect.top <= 0 or self.rect.bottom >= settings.HEIGHT:
            self.speed_y *= -1
            wall_hit = True
        
        return wall_hit
    
    def check_collision(self, paddles):
        hit = False
        
        for paddle in paddles:
            if self.rect.colliderect(paddle.rect):

                # Calculate where on the paddle the ball hit
                relative_y = self.rect.top - paddle.rect.top
                relative_y -= settings.PADDLE_HEIGHT / 2

                # Change the vertical direction based on hit position
                self.speed_y = relative_y * 0.45
                
                if abs(self.speed_y) > 10:
                    self.speed_y = 10 * (1 if self.speed_y > 0 else -1)

                # Reverse horizontal direction
                self.speed_x *= -1

                # Increase speed slightly
                self.speed_x *= 1.02

                # Move ball outside the paddle
                if self.speed_x > 0:
                    self.rect.left = paddle.rect.right
                else:
                    self.rect.right = paddle.rect.left
                
                hit = True
        
        return hit
    
    def reset(self):
        self.rect.center = (settings.WIDTH // 2, settings.HEIGHT // 2)
        self.speed_x = settings.BALL_SPEED * (1 if self.speed_x > 0 else -1)
        self.speed_y = 0
        self.trail.clear()
    
    def draw(self, screen):
        # Draw trail
        for position in self.trail:
            pygame.draw.circle(screen, settings.GREY, position, 4)
        
        # Draw the ball
        pygame.draw.circle(screen, settings.WHITE, self.rect.center, settings.BALL_SIZE // 2)