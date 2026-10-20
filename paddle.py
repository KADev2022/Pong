import pygame
import settings

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, settings.PADDLE_WIDTH, settings.PADDLE_HEIGHT)
    
    def move(self, up_key, down_key):
        keys = pygame.key.get_pressed()
        
        if keys[up_key]:
            self.rect.y -= settings.PADDLE_SPEED
        
        if keys[down_key]:
            self.rect.y += settings.PADDLE_SPEED
        
        # Keep the paddle on the screen
        if self.rect.top < 0:
            self.rect.top = 0
        
        if self.rect.bottom > settings.HEIGHT:
            self.rect.bottom = settings.HEIGHT
    
    def ai_move(self, ball, speed):
        if ball.rect.centery < self.rect.centery:
            self.rect.y -= speed
        elif ball.rect.centery > self.rect.centery:
            self.rect.y += speed
        
        # Keep paddle on screen
        if self.rect.top < 0:
            self.rect.top = 0
        
        if self.rect.bottom > settings.HEIGHT:
            self.rect.bottom = settings.HEIGHT
    
    def draw(self, screen):
        pygame.draw.rect(screen, settings.WHITE, self.rect)