import pygame
import random
import settings

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed_x = random.uniform(-5, 5)
        self.speed_y = random.uniform(-5, 5)
        self.size = random.randint(3, 6)
        self.life = 40
        self.max_life = 40
        self.alpha = 255
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        
        # Fade out
        self.alpha = int(255 * (self.life / self.max_life))
        
        # Slowly shrink
        self.size *= 0.95
    
    def draw(self, screen):
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (255, 255, 255, self.alpha), (int(self.size), int(self.size)), int(self.size))
        screen.blit(particle_surface, (self.x - self.size, self.y - self.size))