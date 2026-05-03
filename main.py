import pygame
import sys
import random
import math
import cv2

pygame.init()
pygame.mixer.init()

width = 800
height = 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Escano")

from enemy import Enemy, Boss, BigBoss
from particle import Particle
from hindilalabas import apply_screen_bounds
from camera import draw_zoomed_camera

from level_beginner import play_beginner
from level_intermediate import play_intermediate
from level_master import play_master

from mechanics import (
    check_key_collection, 
    check_coin_collection, 
    check_pre_gravity_ground, 
    handle_horizontal_collision, 
    handle_vertical_collision,
    check_life_collection,
    HealEffect,
    EscanoUltimate
)

# IMPORT NG ASSETS
from assets import *


clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20, bold=True)

world_surface = pygame.Surface((width, height))

fps = video_main.get(cv2.CAP_PROP_FPS)

game_state = "menu"
running = True
loading_progress = 0
target_level = ""     
target_music = ""

def generate_vignette(w, h):
    mini_w, mini_h = w // 10, h // 10
    vignette = pygame.Surface((mini_w, mini_h), pygame.SRCALPHA)
    center_x, center_y = mini_w / 2, mini_h / 2
    max_dist = math.hypot(center_x, center_y)
    
    for y in range(mini_h):
        for x in range(mini_w):
            dist = math.hypot(x - center_x, y - center_y)
            alpha = int(255 * (dist / max_dist) ** 1.2) 
            alpha = min(255, alpha) 
            vignette.set_at((x, y), (0, 0, 0, alpha))
            
    return pygame.transform.smoothscale(vignette, (w, h))

vignette_surface = generate_vignette(width, height)
is_menu_music_playing = False
frozen_game_frame = None

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "menu":
                if play_button_rect.collidepoint(event.pos):
                    game_state = "levels"
                    click_sound.play()
                elif how_to_play_button_rect.collidepoint(event.pos):
                    game_state = "how_to_play"
                    click_sound.play()
                elif exit_button_rect.collidepoint(event.pos):
                    game_state = "exit_confirm"
                    click_sound.play()

            elif game_state == "how_to_play":
                click_sound.play()
                game_state = "menu"

            elif game_state == "exit_confirm":
                if yes_rect.collidepoint(event.pos):
                    click_sound.play()
                    pygame.quit()
                    sys.exit()
                elif no_rect.collidepoint(event.pos):
                    click_sound.play()
                    game_state = "menu"

            elif game_state == "levels":
                if beginner_button_rect.collidepoint(event.pos):
                    click_sound.play()
                    loading_progress = 0
                    target_level = "level_beginner"         
                    target_music = "music/beginner_music.wav"   
                    game_state = "loading"
                elif intermediate_button_rect.collidepoint(event.pos):
                    click_sound.play()
                    loading_progress = 0
                    target_level = "level_intermediate"
                    game_state = "loading"
                elif master_button_rect.collidepoint(event.pos):
                    click_sound.play()
                    loading_progress = 0
                    target_level = "level_master"
                    game_state = "loading"
                elif back_button_rect.collidepoint(event.pos):
                    click_sound.play()
                    game_state = "menu"

            elif game_state in ["victory", "defeat"]:
                game_state = "menu"

    # ==========================================
    # GAME STATES & RENDERING
    # ==========================================
    if game_state == "menu":
        if not is_menu_music_playing:
            main_menu_music.play(loops=-1)
            is_menu_music_playing = True
        
        ret, frame = video_main.read()
        if not ret:
            video_main.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = video_main.read()
            
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            video_surface = pygame.image.frombuffer(frame_rgb.tobytes(), frame_rgb.shape[1::-1], "RGB")
            video_surface = pygame.transform.scale(video_surface, (width, height))
            screen.blit(video_surface, (0, 0))
        else:
            screen.blit(background_menu_scaled, (0, 0))

        if play_button_rect.collidepoint(mouse_pos) or settings_button_rect.collidepoint(mouse_pos) or exit_button_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if play_button_rect.collidepoint(mouse_pos):
            screen.blit(play_button_hover_scaled, play_button_rect)
        else:
            screen.blit(play_button_scaled, play_button_rect)
        
        if how_to_play_button_rect.collidepoint(mouse_pos):
            screen.blit(how_to_play_button_hover, how_to_play_button_rect)
        else:
            screen.blit(how_to_play_button, how_to_play_button_rect)

        if exit_button_rect.collidepoint(mouse_pos):
            screen.blit(exit_button_hover_scaled, exit_button_rect)
        else:
            screen.blit(exit_button_scaled, exit_button_rect)

    elif game_state == "levels":
        screen.blit(blur_back, (0, 0))
        screen.blit(level_selection_background, (0, 0))

        if (beginner_button_rect.collidepoint(mouse_pos) or intermediate_button_rect.collidepoint(mouse_pos) or master_button_rect.collidepoint(mouse_pos) or back_button_rect.collidepoint(mouse_pos)):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if beginner_button_rect.collidepoint(mouse_pos):
            screen.blit(beginner_button_hover, beginner_button_rect)
        else:
            screen.blit(beginner_button, beginner_button_rect)

        if intermediate_button_rect.collidepoint(mouse_pos):
            screen.blit(intermediate_button_hover, intermediate_button_rect)
        else:
            screen.blit(intermediate_button, intermediate_button_rect)

        if master_button_rect.collidepoint(mouse_pos):
            screen.blit(master_button_hover, master_button_rect)
        else:
            screen.blit(master_button, master_button_rect)

        if back_button_rect.collidepoint(mouse_pos):
            screen.blit(back_button_hover, back_button_rect)
        else:
            screen.blit(back_button, back_button_rect)

    elif game_state == "loading":
        ret, frame = video_main.read()

        if not ret:
            video_main.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = video_main.read()
            
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            video_surface = pygame.image.frombuffer(frame_rgb.tobytes(), frame_rgb.shape[1::-1], "RGB")
            video_surface = pygame.transform.scale(video_surface, (width, height))
            screen.blit(video_surface, (0, 0))
        else:
            screen.blit(background_menu_scaled, (0, 0))

        load_text = font.render("LOADING...", True, (255, 255, 255))
        screen.blit(load_text, (width // 2 - 50, 420))

        bar_width = 500
        bar_height = 10
        bar_x = (width // 2) - (bar_width // 2)
        bar_y = 460

        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        fill_width = int((loading_progress / 100) * bar_width)
        pygame.draw.rect(screen, (255, 215, 0), (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

        loading_progress += 0.5

        if loading_progress >= 100:
            if target_level == "level_beginner":
                game_state = "level_beginner"
                pygame.mixer.music.load(target_music)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
            elif target_level == "level_master":
                main_menu_music.stop()  
                game_state = "level_master"
                master_music.play(fade_ms=1000)
                master_music.set_volume(0.5)
                master_music.play(-1)
            elif target_level == "level_intermediate":
                main_menu_music.stop()    
                game_state = "level_intermediate"
                intermediate_music.play(fade_ms=1000)
                intermediate_music.set_volume(0.5)
                intermediate_music.play(-1)

    elif game_state == "how_to_play":
        screen.blit(blur_back, (0, 0))
        screen.blit(how_to_play, (0, 0))

    elif game_state == "exit_confirm":
        screen.blit(blur_back, (0, 0))
        screen.blit(exit_confirm_bg, (200, 140))

        if yes_rect.collidepoint(mouse_pos) or no_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if yes_rect.collidepoint(mouse_pos):
            screen.blit(yes_button_hover, yes_rect)
        else:
            screen.blit(yes_button, yes_rect)

        if no_rect.collidepoint(mouse_pos):
            screen.blit(no_button_hover, no_rect)
        else:
            screen.blit(no_button, no_rect)

    elif game_state == "victory":
        exit_music.fadeout(1000)
        screen.blit(victory_bg, (0, 0))

    elif game_state == "defeat":
        charging.stop()
        intermediate_music.fadeout(1000)
        master_music.fadeout(1000)
        exit_music.fadeout(1000)
        pygame.mixer.music.fadeout(1000)
        
        if frozen_game_frame:
            screen.blit(frozen_game_frame, (0, 0))
            
        tint = pygame.Surface((width, height), pygame.SRCALPHA)
        tint.fill((20, 0, 0, 150)) 
        screen.blit(tint, (0, 0))
        
        glitch_chance = random.randint(1, 100)
        
        if glitch_chance > 85:
            blink = pygame.Surface((width, height), pygame.SRCALPHA) 
            blink.fill((5, 5, 5, 220)) 
            screen.blit(blink, (0, 0))
            
        elif glitch_chance > 60:
            shift_x = random.randint(-15, 15)
            shift_y = random.randint(-10, 10)
            if frozen_game_frame:
                screen.blit(frozen_game_frame, (shift_x, shift_y))
            screen.blit(tint, (shift_x, shift_y))
            screen.blit(defeat, (shift_x, shift_y))
            
            for _ in range(random.randint(5, 15)):
                line_y = random.randint(0, height)
                line_thickness = random.randint(2, 8)
                pygame.draw.rect(screen, (20, 20, 20), (0, line_y, width, line_thickness))
        else:
            screen.blit(defeat, (0, 0))

    elif game_state == "level_beginner":
        main_menu_music.fadeout(1000)
        game_state = play_beginner(screen, world_surface, width, height, clock, font, vignette_surface)
        if game_state == "defeat":
            frozen_game_frame = screen.copy()

    elif game_state == "level_intermediate":
        main_menu_music.fadeout(1000)
        game_state = play_intermediate(screen, world_surface, width, height, clock, font, vignette_surface)
        if game_state == "defeat":
            frozen_game_frame = screen.copy()

    elif game_state == "level_master":
        main_menu_music.fadeout(1000)
        game_state = play_master(screen, world_surface, width, height, clock, font, vignette_surface)
        if game_state == "defeat":
            frozen_game_frame = screen.copy()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()