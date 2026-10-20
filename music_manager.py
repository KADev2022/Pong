import pygame
import settings

from paths import resource_path

current_music = None

def play_music(filename):
    global current_music
    
    if current_music == filename:
        return
    
    pygame.mixer.music.load(resource_path(filename))
    pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)
    pygame.mixer.music.play(-1)
    
    current_music = filename

def stop_music():
    global current_music
    
    pygame.mixer.music.stop()
    current_music = None

def set_music_volume(volume):
    pygame.mixer.music.set_volume(volume)