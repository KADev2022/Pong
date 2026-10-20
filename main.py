import pygame
import settings
import random
import math

from paddle import Paddle
from ball import Ball
from particle import Particle
from highscore import load_high_score, save_high_score
from music_manager import play_music, set_music_volume
from settings_manager import load_settings, save_settings

pygame.init()

pygame.mixer.init()

play_music(settings.MENU_MUSIC)

paddle_sound = pygame.mixer.Sound(settings.PADDLE_SOUND)
wall_sound = pygame.mixer.Sound(settings.WALL_SOUND)
score_sound = pygame.mixer.Sound(settings.SCORE_SOUND)

menu_move_sound = pygame.mixer.Sound(settings.MENU_MOVE_SOUND)
menu_select_sound = pygame.mixer.Sound(settings.MENU_SELECT_SOUND)
menu_back_sound = pygame.mixer.Sound(settings.MENU_BACK_SOUND)

menu_sounds = [menu_move_sound, menu_select_sound, menu_back_sound]

GAME_STATE = "MENU"

countdown = 3
countdown_timer = 0

font = pygame.font.Font(None, 50)
title_font = pygame.font.Font(None, 100)
countdown_font = pygame.font.Font(None, 120)

# Load saved preferences
saved_settings = load_settings()

music_volume = saved_settings["music_volume"]
sound_volume = saved_settings["sound_volume"]
difficulty = saved_settings["difficulty"]
fullscreen = saved_settings["fullscreen"]

# Apply saved music volume
settings.MUSIC_VOLUME = music_volume
set_music_volume(music_volume)

# Difficulty options and speeds
difficulty_options = ["Easy", "Medium", "Hard"]

ai_speeds = {
    "Easy": settings.AI_EASY_SPEED,
    "Medium": settings.AI_MEDIUM_SPEED,
    "Hard": settings.AI_HARD_SPEED
}

ai_speed = ai_speeds[difficulty]


settings_options = [
    "Music Volume",
    "Sound Effects Volume",
    "Difficulty",
    "Fullscreen"
]

selected_setting = 0

# Settings menu animations
display_music_volume = music_volume
display_sound_volume = sound_volume

settings_animation_time = 0.0

# Current vertical position of the selection arrow
settings_arrow_y = 230.0

# Vertical positions of all Settings options
settings_option_positions = [
    230,  # Music Volume
    360,  # Sound Effects Volume
    490,  # Difficulty
    570   # Fullscreen
]

# Start arrow at the currently selected option
settings_arrow_y = float(settings_option_positions[selected_setting])
settings_arrow_x = 0.0
settings_arrow_gap = 30

# Game's internal resolution
GAME_SIZE = (settings.WIDTH, settings.HEIGHT)

# Main menu animations
menu_animation_time = 0.0

# Title animation settings
title_float_amount = 8
title_float_speed = 1.5

# Main menu arrow animayion
menu_arrow_x = None
menu_arrow_y = None
menu_arrow_gap = 30
menu_arrow_speed = 12.0

# Create display using saved preference
if fullscreen:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode(GAME_SIZE)
    
pygame.display.set_caption("Pong")

clock = pygame.time.Clock()

game_surface = pygame.Surface((settings.WIDTH, settings.HEIGHT))
pause_overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)

pause_alpha = 0

pause_overlay.fill((0, 0, 0, pause_alpha))

player = Paddle(40, settings.HEIGHT // 2 - settings.PADDLE_HEIGHT // 2)
ai = Paddle(settings.WIDTH - 40 - settings.PADDLE_WIDTH, settings.HEIGHT // 2 - settings.PADDLE_HEIGHT // 2)

ball = Ball()

player_score = 0
ai_score = 0
high_score = load_high_score()
WIN_SCORE = 10
winner = ""

particles = []

screen_shake = 0
shake_amount = 5

selected_option = 0

def set_sound_volume(volume):
    paddle_sound.set_volume(volume)
    wall_sound.set_volume(volume)
    score_sound.set_volume(volume)

set_sound_volume(sound_volume)

def draw_centre_line(surface):
    for y in range(0, settings.HEIGHT, 40):
        pygame.draw.rect(surface, settings.WHITE, (settings.WIDTH // 2 - 2, y, 4, 20))

def create_particles(x, y, amount):
    for _ in range(amount):
        particles.append(Particle(x, y))

def draw_menu_button(surface, text, rect, selected, mouse_pos):
    hovered = rect.collidepoint(mouse_pos)
    
    if hovered or selected:
        colour = settings.GREEN
        size = 1.1
    else:
        colour = settings.WHITE
        size = 1.0
    
    button_font = pygame.font.Font(None, int(50 * size))
    
    text_surface = button_font.render(text, True, colour)
    surface.blit(text_surface, (rect.centerx - text_surface.get_width() // 2, rect.centery - text_surface.get_height() // 2))

def apply_display_mode():
    global screen
    
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(GAME_SIZE)

def draw_menu_arrow(surface, x, y, animation_time):
    # Gentle horizontal pulsing
    pulse = math.sin(animation_time * 4) * 5
    
    arrow_tip_x = int(x + pulse)
    arrow_tip_y = int(y)
    
    pygame.draw.polygon(surface, settings.GREEN, [
        (arrow_tip_x, arrow_tip_y - 10),
        (arrow_tip_x, arrow_tip_y + 10),
        (arrow_tip_x + 15, arrow_tip_y)
    ])

def update_menu_sound_volume():
    for sound in menu_sounds:
        sound.set_volume(sound_volume)

update_menu_sound_volume()

class MenuBackgroundParticle:
    def __init__(self):
        self.reset(initial=True)
    
    def reset(self, initial=False):
        # Random horizontal position
        self.x = random.uniform(0, settings.WIDTH)
        
        # Start particles through the screen
        if initial:
            self.y = random.uniform(0, settings.HEIGHT)
        else:
            self.y = settings.HEIGHT + 10
        
        # Random particle size
        self.radius = random.choice([1, 2, 3])
        
        # Slow upward movement
        self.speed_y = random.uniform(10, 30)
        
        # Gentle horizontal movement
        self.speed_x = random.uniform(-8, 8)
        
        # Animation offset
        self.phase = random.uniform(0, math.tau)
        
        # Particle colour
        self.colour = random.choice([
            (0, 110, 0),
            (0, 150, 0),
            (65, 65, 65),
            (90, 90, 90)
        ])
    
    def update(self, dt, animation_time):
        # Move upwards
        self.y -= self.speed_y * dt

        # Move slightly left and right
        self.x += (self.speed_x + math.sin(animation_time + self.phase) * 5) * dt

        # Reset when leaving the screen
        if self.y < -10:
            self.reset()

        # Wrap horizontally
        if self.x < 0:
            self.x = settings.WIDTH

        elif self.x > settings.WIDTH:
            self.x = 0
    
    def draw(self, surface, animation_time):
        # Gentle brightness variation
        brightness = (math.sin(animation_time * 2 + self.phase) + 1) / 2
        colour = tuple(min(255, int(channel * (0.6 + 0.4 * brightness))) for channel in self.colour)
        pygame.draw.circle(surface, colour, (int(self.x), int(self.y)), self.radius)

menu_background_particles = [MenuBackgroundParticle() for _ in range(35)]

running = True

while running:
    # Keep the game running at the chosen FPS
    dt = clock.tick(settings.FPS) / 1000.0
    
    # Main menu animations
    if GAME_STATE == "MENU":
        menu_animation_time += dt
        
        # Update background particles
        for particle in menu_background_particles:
            particle.update(dt, menu_animation_time)
    
    # Settings menu animations
    if GAME_STATE == "SETTINGS":
        # Advance animation timer
        settings_animation_time += dt
        
        # Smoothly animate the volume bars
        animation_speed = min(1.0, 10.0 * dt)
        
        display_music_volume += (music_volume - display_music_volume) * animation_speed
        display_sound_volume += (sound_volume - display_sound_volume) * animation_speed
        
        # Find the target position
        target_arrow_y = settings_option_positions[selected_setting]
        
        # Calculate arrow movement speed
        arrow_speed = min(1.0, 12.0 * dt)
        
        # Smoothly move towards selected option
        settings_arrow_y += (target_arrow_y - settings_arrow_y) * arrow_speed
        
        # Get the currently selected setting text
        if selected_setting == 0:
            selected_text = (f"Music Volume: {round(music_volume * 100)}%")
        elif selected_setting == 1:
            selected_text = (f"Sound Effects Volume: {round(sound_volume * 100)}%")
        elif selected_setting == 2:
            selected_text = f"Difficulty: {difficulty}"
        else:
            if fullscreen:
                fullscreen_status = "On"
            else:
                fullscreen_status = "Off"
            selected_text = f"Fullscreen: {fullscreen_status}"
        
        # Measure text width using the same font
        selected_text_width = font.size(selected_text)[0]

        # Calculate target horizontal position
        text_left = (settings.WIDTH // 2 - selected_text_width // 2)

        target_arrow_x = text_left - settings_arrow_gap

        # Smoothly move horizontally
        horizontal_speed = min(1.0, 12.0 * dt)

        settings_arrow_x += (target_arrow_x - settings_arrow_x) * horizontal_speed
        
        # Snap into place when extremely close
        if abs(target_arrow_y - settings_arrow_y) < 0.5:
            settings_arrow_y = float(target_arrow_y)
    
    mouse_pos = pygame.mouse.get_pos()
    
    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if GAME_STATE == "PLAYING":
                    GAME_STATE = "PAUSED"
                    pause_alpha = 0
                elif GAME_STATE == "PAUSED":
                    GAME_STATE = "PLAYING"
                    pause_alpha = 0
                elif GAME_STATE == "SETTINGS":
                    menu_back_sound.play()
                    GAME_STATE = "MENU"

            elif GAME_STATE == "MENU":
                if event.key == pygame.K_UP:
                    selected_option -= 1
                    
                    if selected_option < 0:
                        selected_option = len(menu_options)
                    
                    menu_move_sound.play()
                elif event.key == pygame.K_DOWN:
                    selected_option += 1
                    
                    if selected_option >= len(menu_options):
                        selected_option = 0
                    
                    menu_move_sound.play()
                elif event.key == pygame.K_RETURN:
                    menu_select_sound.play()
                    
                    if selected_option == 0:
                        GAME_STATE = "COUNTDOWN"
                        countdown = 3
                        countdown_timer = pygame.time.get_ticks()
                        play_music(settings.GAMEPLAY_MUSIC)
                    elif selected_option == 1:
                        GAME_STATE = "SETTINGS"
                    elif selected_option == 2:
                        running = False
                elif event.key == pygame.K_1:
                    difficulty = "Easy"
                    ai_speed = settings.AI_EASY_SPEED
                elif event.key == pygame.K_2:
                    difficulty = "Medium"
                    ai_speed = settings.AI_MEDIUM_SPEED
                elif event.key == pygame.K_3:
                    difficulty = "Hard"
                    ai_speed = settings.AI_HARD_SPEED
                elif event.key == pygame.K_SPACE:
                    GAME_STATE = "COUNTDOWN"
                    countdown = 3
                    countdown_timer = pygame.time.get_ticks()
                    play_music(settings.GAMEPLAY_MUSIC)
            
            elif GAME_STATE == "PAUSED":
                if event.key == pygame.K_SPACE:
                    GAME_STATE = "PLAYING"
                    pause_alpha = 0
                elif event.key == pygame.K_r:
                    player_score = 0
                    ai_score = 0
                                
                    ball.reset()
                                
                    particles.clear()
                                
                    GAME_STATE = "COUNTDOWN"
                                
                    countdown = 3
                    countdown_timer = pygame.time.get_ticks()
                elif event.key == pygame.K_q:
                    running = False
            
            elif GAME_STATE == "GAME_OVER":
                if event.key == pygame.K_r:
                    player_score = 0
                    ai_score = 0
                    
                    winner = ""
                    
                    ball.reset()
                    
                    GAME_STATE = "COUNTDOWN"
                    
                    countdown = 3
                    countdown_timer = pygame.time.get_ticks()
                    play_music(settings.GAMEPLAY_MUSIC)
            
            elif GAME_STATE == "SETTINGS":
                if event.key == pygame.K_LEFT:
                    setting_changed = False
                    
                    if selected_setting == 0:
                        old_volume = music_volume
                        music_volume = max(0.0, round(music_volume - 0.1, 1))
                        
                        if music_volume != old_volume:
                            settings.MUSIC_VOLUME = music_volume
                            set_music_volume(music_volume)
                            setting_changed = True
                    elif selected_setting == 1:
                        old_volume = sound_volume
                        sound_volume = max(0.0, round(sound_volume - 0.1, 1))
                        
                        if sound_volume != old_volume:
                            set_sound_volume(sound_volume)
                            update_menu_sound_volume()
                            setting_changed = True
                    elif selected_setting == 2:
                        difficulty_index = difficulty_options.index(difficulty)
                        difficulty_index = (difficulty_index - 1) % len(difficulty_options)
                        difficulty = difficulty_options[difficulty_index]
                        ai_speed = ai_speeds[difficulty]
                        
                        setting_changed = True
                    elif selected_setting == 3:
                        fullscreen = not fullscreen
                        apply_display_mode()
                        
                        setting_changed = True
                    
                    # Play sound and save only when changed
                    if setting_changed:
                        menu_move_sound.play()
                        save_settings(music_volume, sound_volume, difficulty, fullscreen)
                elif event.key == pygame.K_RIGHT:
                    setting_changed = False
                    
                    if selected_setting == 0:
                        old_volume = music_volume
                        music_volume = min(1.0, round(music_volume + 0.1, 1))
                        
                        if music_volume != old_volume:
                            settings.MUSIC_VOLUME = music_volume
                            set_music_volume(music_volume)
                            setting_changed = True
                    elif selected_setting == 1:
                        old_volume = sound_volume
                        sound_volume = min(1.0, round(sound_volume + 0.1, 1))
                        
                        if sound_volume != old_volume:
                            set_sound_volume(sound_volume)
                            update_menu_sound_volume()
                            setting_changed = True
                    elif selected_setting == 2:
                        difficulty_index = difficulty_options.index(difficulty)
                        difficulty_index = (difficulty_index + 1) % len(difficulty_options)
                        difficulty = difficulty_options[difficulty_index]
                        ai_speed = ai_speeds[difficulty]
                        
                        setting_changed = True
                    elif selected_setting == 3:
                        fullscreen = not fullscreen
                        apply_display_mode()
                        
                        setting_changed = True
                    
                    # Play sound and save only when changed
                    if setting_changed:
                        menu_move_sound.play()
                        save_settings(music_volume, sound_volume, difficulty, fullscreen)
                elif event.key == pygame.K_UP:
                    selected_setting = (selected_setting - 1) % len(settings_options)
                    menu_move_sound.play()
                elif event.key == pygame.K_DOWN:
                    selected_setting = (selected_setting + 1) % len(settings_options)
                    menu_move_sound.play()

    # Clear game surface
    game_surface.fill(settings.BLACK)
    
    if GAME_STATE == "MENU":
        # Draw background particles first
        for particle in menu_background_particles:
            particle.draw(game_surface, menu_animation_time)
        
        # Animated PONG title
        # Calculate smooth floating movement
        title_offset = math.sin(menu_animation_time * title_float_speed) * title_float_amount
        
        # Calculate subtle brightness pulse
        title_brightness = int(225 + 30 * (math.sin(menu_animation_time * 2) + 1) / 2)
        title_colour = (title_brightness, title_brightness, title_brightness)
        
        title = title_font.render("PONG", True, title_colour)
        
        # Calculate animated position
        title_y = int(120 + title_offset)
        title_rect = title.get_rect(center=(settings.WIDTH // 2, title_y))
        
        high_score_text = font.render(f"High Score: {high_score}", True, settings.WHITE)
        difficulty_text = font.render(f"Difficulty: {difficulty}", True, settings.WHITE)
        
        # Draw menu options
        menu_options = [
            "Start Game",
            "Settings",
            "Quit"
        ]
        
        start_y = 280
        menu_spacing = 60
        
        # Create text surfaces and positions
        option_surfaces = []
        option_positions = []
        
        for index, option in enumerate(menu_options):
            is_selected = (index == selected_option)
            
            if is_selected:
                # Smoothly pulse green brightness
                pulse = (math.sin(menu_animation_time * 3) + 1) / 2
                green_brightness = int(160 + 95 * pulse)
                colour = (0, green_brightness, 0)
            else:
                colour = settings.WHITE
             
            option_surface = font.render(option, True, colour)
            
            text_x = settings.WIDTH // 2 - option_surface.get_width() // 2
            text_y = start_y + index * menu_spacing
            
            option_surfaces.append(option_surface)
            option_positions.append((text_x, text_y))
        
        # Calculate arrow target position
        selected_surface = option_surfaces[selected_option]
        selected_text_x, selected_text_y = option_positions[selected_option]
        target_arrow_x = selected_text_x - menu_arrow_gap
        target_arrow_y = selected_text_y + selected_surface.get_height() // 2
        
        # Initialise arrow position
        if menu_arrow_x is None:
            menu_arrow_x = float(target_arrow_x)
        
        if menu_arrow_y is None:
            menu_arrow_y = float(target_arrow_y)
        
        # Smooth arrow movement
        arrow_factor = min(
            1.0,
            menu_arrow_speed * dt
        )

        menu_arrow_x += (
            target_arrow_x - menu_arrow_x
        ) * arrow_factor

        menu_arrow_y += (
            target_arrow_y - menu_arrow_y
        ) * arrow_factor

        # Snap into position when very close
        if abs(target_arrow_x - menu_arrow_x) < 0.5:
            menu_arrow_x = float(target_arrow_x)

        if abs(target_arrow_y - menu_arrow_y) < 0.5:
            menu_arrow_y = float(target_arrow_y)
        
        # Draw main menu options
        for index, option_surface in enumerate(option_surfaces):
            text_x, text_y = option_positions[index]
            
            game_surface.blit(option_surface, (text_x, text_y))
        
        # Draw animated selection arrow
        draw_menu_arrow(game_surface, menu_arrow_x, menu_arrow_y, menu_animation_time)
        
        # Controls footer
        controls_font = pygame.font.Font(None, 30)
        controls_text = controls_font.render("Move    ENTER Select", True, settings.WHITE)
        
        controls_y = settings.HEIGHT - 40
        arrow_center_y = controls_y + controls_text.get_height() // 2
        center_x = settings.WIDTH // 2
        
        # Up arrow
        pygame.draw.polygon(game_surface, settings.WHITE, [
            (center_x - 175, arrow_center_y - 10),
            (center_x - 185, arrow_center_y + 5),
            (center_x - 165, arrow_center_y + 5)
        ])
        
        # Down arrow
        pygame.draw.polygon(game_surface, settings.WHITE, [
            (center_x - 140, arrow_center_y + 10),
            (center_x - 150, arrow_center_y - 5),
            (center_x - 130, arrow_center_y - 5)
        ])
        
        game_surface.blit(title, title_rect)
        game_surface.blit(high_score_text, (settings.WIDTH // 2 - high_score_text.get_width() // 2, 170))
        game_surface.blit(difficulty_text, (settings.WIDTH // 2 - difficulty_text.get_width() // 2, 500))
        game_surface.blit(controls_text, (center_x - 100, controls_y))
    
    elif GAME_STATE == "COUNTDOWN":
        current_time = pygame.time.get_ticks()
        
        if current_time - countdown_timer >= 1000:
            countdown -= 1
            countdown_timer = current_time
        
        if countdown == 0:
            GAME_STATE = "PLAYING"
        
        countdown_text = countdown_font.render(str(countdown), True, settings.WHITE)
        game_surface.blit(countdown_text, (settings.WIDTH // 2 - countdown_text.get_width() // 2, 200))
    
    elif GAME_STATE == "PLAYING":
        player.move(pygame.K_w, pygame.K_s)
        ai.ai_move(ball, ai_speed)
        
        if ball.move():
            wall_sound.play()
            
            screen_shake = settings.WALL_SHAKE
            
            create_particles(ball.rect.centerx, ball.rect.centery, settings.WALL_PARTICLES)
        
        if ball.check_collision([player, ai]):
            paddle_sound.play()
            
            screen_shake = settings.PADDLE_SHAKE
            
            create_particles(ball.rect.centerx, ball.rect.centery, settings.PADDLE_PARTICLES)
        
        # Check scoring first
        if ball.rect.left <= 0:
            ai_score += 1
            score_sound.play()
            ball.reset()
        elif ball.rect.right >= settings.WIDTH:
            player_score += 1
            
            if player_score > high_score:
                high_score = player_score
                save_high_score(high_score)
            
            score_sound.play()
            ball.reset()
        # Only play wall sounds if no score happened
        else:
            if ball.rect.top <= 0 or ball.rect.bottom >= settings.HEIGHT:
                wall_sound.play()
        
        # Check winner
        if player_score >= WIN_SCORE:
            winner = "PLAYER WINS!"
            GAME_STATE = "GAME_OVER"
            play_music(settings.MENU_MUSIC)
        elif ai_score >= WIN_SCORE:
            winner = "AI WINS!"
            GAME_STATE = "GAME_OVER"
            play_music(settings.MENU_MUSIC)
        
        draw_centre_line(game_surface)
        
        # Update particles
        for particle in particles[:]:
            particle.update()
        
            if particle.life <= 0:
                particles.remove(particle)
        
        # Draw particles
        for particle in particles:
            particle.draw(game_surface)
        
        player.draw(game_surface)
        ai.draw(game_surface)
        ball.draw(game_surface)
        
        player_text = font.render(str(player_score), True, settings.WHITE)
        ai_text = font.render(str(ai_score), True, settings.WHITE)
        game_surface.blit(player_text, (settings.WIDTH // 4, 20))
        game_surface.blit(ai_text, (settings.WIDTH * 3 // 4, 20))
    
    elif GAME_STATE == "PAUSED":
        # Fade in pause overlay
        if pause_alpha < 150:
            pause_alpha += 5
        pause_overlay.fill((0, 0, 0, pause_alpha))
        
        # Darken the background
        game_surface.blit(pause_overlay, (0, 0))
        
        paused_text = title_font.render("PAUSED", True, settings.GREEN)
        resume_text = font.render("SPACE - Resume", True, settings.WHITE)
        restart_text = font.render("R - Restart", True, settings.WHITE)
        quit_text = font.render("Q - Quit", True, settings.WHITE)
        game_surface.blit(paused_text, (settings.WIDTH // 2 - paused_text.get_width() // 2, 150))
        game_surface.blit(resume_text, (settings.WIDTH // 2 - resume_text.get_width() // 2, 300))
        game_surface.blit(restart_text, (settings.WIDTH // 2 - restart_text.get_width() // 2, 350))
        game_surface.blit(quit_text, (settings.WIDTH // 2 - quit_text.get_width() // 2, 400))
    
    elif GAME_STATE == "GAME_OVER":
        winner_text = title_font.render(winner, True, settings.WHITE)
        restart_text = font.render("Press R to restart", True, settings.WHITE)
        game_surface.blit(winner_text, (settings.WIDTH // 2 - winner_text.get_width() // 2, 200))
        game_surface.blit(restart_text, (settings.WIDTH // 2 - restart_text.get_width() // 2, 350))
    
    elif GAME_STATE == "SETTINGS":
        def draw_settings_arrow(y, text_width):
            global settings_arrow_x
            
            # Calculate left edge of selected text
            text_left = (settings.WIDTH // 2 - text_width // 2)
            
            # Target horizontal position
            target_arrow_x = text_left - settings_arrow_gap
            
            if settings_arrow_x == 0.0:
                settings_arrow_x = float(target_arrow_x)
            
            # Calculate gentle horizontal movement
            pulse = math.sin(settings_animation_time * 4) * 5
            
            arrow_x = int(settings_arrow_x + pulse)
            arrow_y = int(settings_arrow_y)
            
            # Draw right-pointing green triangle
            pygame.draw.polygon(game_surface, settings.GREEN, [
                (arrow_x, arrow_y - 10),
                (arrow_x, arrow_y + 10),
                (arrow_x + 15, arrow_y)
            ])
        
        title = title_font.render("SETTINGS", True, settings.WHITE)
        
        # Volume
        volumes = [
            display_music_volume,
            display_sound_volume
        ]
        
        actual_volumes = [
            music_volume,
            sound_volume
        ]
        
        start_y = 230
        spacing = 130
        bar_width = 300
        bar_height = 20
        
        for index in range(2):
            option = settings_options[index]
            volume = volumes[index]
            actual_volume = actual_volumes[index]
            y = start_y + index * spacing
            
            # Check whether this option is selected
            is_selected = (index == selected_setting)
            
            # Calculate selected colour
            if is_selected:
                brightness = int(200 + 55 * (math.sin(settings_animation_time * 3) + 1) / 2)
                text_colour = (0, brightness, 0)
                bar_colour = text_colour
            else:
                text_colour = settings.WHITE
                bar_colour = settings.WHITE
            
            # Setting label
            label = font.render(f"{option}: {round(actual_volume * 100)}%", True, text_colour)
            
            game_surface.blit(label, label.get_rect(center=(settings.WIDTH // 2, y)))
            
            # Draw selection arrow
            if is_selected:
                draw_settings_arrow(y, label.get_width())
            
            # Volume bar position
            bar_x = settings.WIDTH // 2 - bar_width // 2
            bar_y = y + 35
            
            # Draw background bar
            pygame.draw.rect(game_surface, (70, 70, 70), (bar_x, bar_y, bar_width, bar_height), border_radius=8)
            
            # Draw animated fill bar
            fill_width = int(bar_width * volume)
            
            if fill_width > 0:
                pygame.draw.rect(game_surface, bar_colour, (bar_x, bar_y, fill_width, bar_height), border_radius=8)
        
        # Difficulty selection
        if selected_setting == 2:
            brightness = int(200 + 55 * (math.sin(settings_animation_time * 3) + 1) / 2)
            difficulty_colour = (0, brightness, 0)
        else:
            difficulty_colour = settings.WHITE
        
        difficulty_text = font.render(f"Difficulty: {difficulty}", True, difficulty_colour)
        
        # Fullscreen selection
        if selected_setting == 3:
            brightness = int(200 + 55 * (math.sin(settings_animation_time * 3) + 1) / 2)
            fullscreen_colour = (0, brightness, 0)
        else:
            fullscreen_colour = settings.WHITE
        
        if fullscreen:
            fullscreen_status = "On"
        else:
            fullscreen_status = "Off"
        
        fullscreen_text = font.render(f"Fullscreen: {fullscreen_status}", True, fullscreen_colour)
        
        # Instructions
        controls_font = pygame.font.Font(None, 28)

        controls_text = controls_font.render("UP / DOWN - Select    LEFT / RIGHT - Adjust", True, settings.WHITE)
        back_text = controls_font.render("ESC - Back", True, settings.WHITE)
        
        game_surface.blit(title, (settings.WIDTH // 2 - title.get_width() // 2, 100))
        game_surface.blit(controls_text, controls_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT - 85)))
        game_surface.blit(back_text, back_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT - 40)))
        
        game_surface.blit(difficulty_text, difficulty_text.get_rect(center=(settings.WIDTH // 2, 490)))
        if selected_setting == 2:
            draw_settings_arrow(490, difficulty_text.get_width())
        
        game_surface.blit(fullscreen_text, fullscreen_text.get_rect(center=(settings.WIDTH // 2, 570)))
        if selected_setting == 3:
            draw_settings_arrow(570, fullscreen_text.get_width())
    
    if screen_shake > 0:
        offset_x = random.randint(-shake_amount, shake_amount)
        offset_y = random.randint(-shake_amount, shake_amount)
        screen_shake -= 1
    else:
        offset_x = 0
        offset_y = 0
        
    # Get the current display dimensions
    display_width, display_height = screen.get_size()
    
    # Calculate scaling while maintaining aspect ratio
    scale = min(display_width / settings.WIDTH, display_height / settings.HEIGHT)
    
    scaled_width = max(1, int(settings.WIDTH * scale))
    scaled_height = max(1, int(settings.HEIGHT * scale))
    
    # Scale the game surface
    scaled_surface = pygame.transform.smoothscale(game_surface, (scaled_width, scaled_height))
    
    # Centre the game on the display
    center_x = (display_width - scaled_width) // 2
    center_y = (display_height - scaled_height) // 2
    
    # Clear the display
    screen.fill(settings.BLACK)
    
    # Draw the scaled game with screen shake
    screen.blit(scaled_surface, (center_x + int(offset_x * scale), center_y + int(offset_y * scale)))
    
    # Draw everything
    pygame.display.flip()

pygame.quit()