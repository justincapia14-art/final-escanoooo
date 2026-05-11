import pygame
import math
import random
from particle import Particle
from enemy import Enemy, Boss
from mechanics import *
from assets import *
from intermediate_level_blocks import intermediate_get_platforms, intermediate_draw_platforms
from camera import draw_zoomed_camera
from hindilalabas import apply_screen_bounds

def play_intermediate(screen, world_surface, width, height, clock, font, vignette_surface):
    running = True
    next_state = "menu"
    
    # Setup Variables (Intermediate)
    player_hp = 100
    max_hp = 100
    hit_cooldown = 0
    x = 480
    y = 440
    speed = 1.5
    gravity = 0.2 
    velocity_y = 0 
    jump_speed = -5
    player_width, player_height = 20, 20
    player_angle = 0
    
    player_bullets = []
    player_shoot_cooldown = 0 
    max_shoot_cooldown = 30 
    shoot_anim_timer = 0
    aim_direction = "right"
    
    direction = "face"
    particles = []
    active_heal_effects = []
    
    keys_collected = 0
    coin_count = 0
    exit_fade_start = None
    exit_fade_done = False
    screen_shake_frames = 0
    
    skills_list = ["Gun", "Ultimate"]
    current_skill_index = 0
    current_skill = skills_list[current_skill_index]
    skill_ui_timer = 0 
    
    escano_ult = EscanoUltimate()
    is_playing_charge_sound = False
    
    intermediate_keys = [(0, 460), (100, 80), (220, 320)]
    intermediate_coins = [(560, 200), (560, 180), (580, 200), (580, 180), (600, 200), (600, 180)]
    intermediate_lives = [(60, 400), (500, 400), (700, 200), (700, 40)]

    level_keys = [pygame.Rect(kx, ky, 20, 10) for kx, ky in intermediate_keys]
    keys_collected_status = [False] * len(level_keys)

    level_coins = [pygame.Rect(cx, cy, 20, 20) for cx, cy in intermediate_coins]
    coins_collected_status = [False] * len(level_coins)

    level_lives = [pygame.Rect(lx, ly, 20, 20) for lx, ly in intermediate_lives]
    lives_collected_status = [False] * len(level_lives)
    
    door_rect = pygame.Rect(80, 82, 5, 145)
    
    enemies = [
        Enemy(180, 180),
        Enemy(760, 180),
        Enemy(680, 60),
        Enemy(100, 440),
        Enemy(160, 440),
        Enemy(220, 440),
        Enemy(540, 380)
    ]

    bosses = [
        Boss(300, 300)
    ]

    breakable_bricks = [
        *[pygame.Rect(i, 460, 20, 20) for i in range(20, 100, 20)],
        *[pygame.Rect(i, 440, 20, 20) for i in range(20, 100, 20)],
        *[pygame.Rect(i, 400, 20, 20) for i in range(580, 680, 20)],
        *[pygame.Rect(i, 380, 20, 20) for i in range(580, 680, 20)],
        *[pygame.Rect(i, 80, 20, 20) for i in range(700, 800, 20)],
        *[pygame.Rect(i, 60, 20, 20) for i in range(700, 800, 20)]
    ]
    
    frame_index = 0
    animation_speed = 0.10
    time_float = 0

    while running:
        moving = False
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            if event.type == pygame.MOUSEWHEEL:
                current_skill_index = (current_skill_index + event.y) % len(skills_list)
                current_skill = skills_list[current_skill_index]
                skill_ui_timer = 120 
                click_sound.play()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button_game_rect.collidepoint(event.pos):
                    click_sound.play()
                    intermediate_music.stop()
                    main_menu_music.play()
                    return "levels"

        if back_button_game_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if hit_cooldown > 0:
            hit_cooldown -= 1

        keys = pygame.key.get_pressed()
        player_angle %= 360
        player_rect = pygame.Rect(x, y, player_width, player_height)

        escano_ult.update()
        mouse_buttons = pygame.mouse.get_pressed()
        left_click = mouse_buttons[0]
        right_click = mouse_buttons[2]

        if player_shoot_cooldown > 0:
            player_shoot_cooldown -= 1
            
        if shoot_anim_timer > 0:
            shoot_anim_timer -= 1

        if current_skill == "Ultimate":
            solid_platforms = intermediate_get_platforms() 
            if escano_ult.handle_input(left_click, right_click, x, y, player_width, player_height, solid_platforms):
                screen_shake_frames = 15 
                ultimate_sound.play()   
        else:
            escano_ult.is_charging = False
            escano_ult.charge_timer = 0
            if current_skill == "Gun":
                if left_click and player_shoot_cooldown <= 0:
                    player_bullets.append([x, y + (player_height // 2), -7]) 
                    player_shoot_cooldown = max_shoot_cooldown
                    shoot_anim_timer = 15
                    aim_direction = "left"
                    player_shoot_sound.play()
                    
                elif right_click and player_shoot_cooldown <= 0:
                    player_bullets.append([x + player_width, y + (player_height // 2), 7])
                    player_shoot_cooldown = max_shoot_cooldown
                    shoot_anim_timer = 15
                    aim_direction = "right"
                    player_shoot_sound.play()

        if escano_ult.is_charging:
            if not is_playing_charge_sound:
                charging.play(loops=-1) 
                is_playing_charge_sound = True
        else:
            if is_playing_charge_sound:
                charging.stop()
                is_playing_charge_sound = False

        if escano_ult.active_laser:
            laser = escano_ult.active_laser
            laser_rect = laser['rect']

            if laser['current_breaks'] < laser['max_breaks']:
                hit_bricks = [b for b in breakable_bricks if laser_rect.colliderect(b)]
                if laser['dir'] == "right":
                    hit_bricks.sort(key=lambda b: b.x)
                else:
                    hit_bricks.sort(key=lambda b: b.x, reverse=True) 
                
                for b in hit_bricks:
                    if laser['current_breaks'] < laser['max_breaks']:
                        if b in breakable_bricks:
                            breakable_bricks.remove(b)
                            laser['current_breaks'] += 1
                            for _ in range(40):
                                particles.append(Particle(b.x + 10, b.y + 10))
                    else:
                        break

            if 'hit_enemies' not in escano_ult.active_laser:
                escano_ult.active_laser['hit_enemies'] = []

            for e in enemies:
                e_rect = pygame.Rect(e.x, e.y, 40, 40)
                if e.hp > 0 and laser_rect.colliderect(e_rect):
                    if e not in escano_ult.active_laser['hit_enemies']:
                        e.hp -= escano_ult.active_laser['damage'] 
                        escano_ult.active_laser['hit_enemies'].append(e) 
                        if e.hp <= 0:
                            enemy_dead_sound.play() 
                            for _ in range(100):  
                                particles.append(Particle(e.x + 20, e.y + 20))

            if 'hit_bosses' not in escano_ult.active_laser:
                escano_ult.active_laser['hit_bosses'] = []

            for b in bosses:
                b_rect = pygame.Rect(b.x, b.y, b.width, b.height)
                if b.hp > 0 and laser_rect.colliderect(b_rect):
                    if b not in escano_ult.active_laser['hit_bosses']:
                        b.hp -= escano_ult.active_laser['damage'] 
                        escano_ult.active_laser['hit_bosses'].append(b)
                        if b.hp <= 0:
                            enemy_dead_sound.play()
                            for _ in range(100):  
                                particles.append(Particle(b.x + b.width//2, b.y + b.height//2))

        platforms = intermediate_get_platforms()
        for b in breakable_bricks:
            platforms.append(b)

        for bullet in player_bullets[:]:
            bullet[0] += bullet[2] 
            if bullet[0] < 0 or bullet[0] > width:
                if bullet in player_bullets:
                    player_bullets.remove(bullet)
                continue

            bullet_rect = pygame.Rect(bullet[0] - 4, bullet[1] - 4, 8, 8)
            
            for e in enemies:
                e_rect = pygame.Rect(e.x, e.y, 40, 40)
                if e.hp > 0 and bullet_rect.colliderect(e_rect):
                    e.hp -= 15 
                    if bullet in player_bullets:
                        player_bullets.remove(bullet)
                    if e.hp <= 0:
                        for _ in range(1000):  
                            particles.append(Particle(e.x + 20, e.y + 20))
                    break

            for b in bosses:
                b_rect = pygame.Rect(b.x, b.y, b.width, b.height)
                if b.hp > 0 and bullet_rect.colliderect(b_rect):
                    b.hp -= 15 
                    if bullet in player_bullets:
                        player_bullets.remove(bullet)
                    if b.hp <= 0:
                        enemy_dead_sound.play()
                        for _ in range(100):  
                            particles.append(Particle(b.x + b.width//2, b.y + b.height//2))
                    break
            
            bullet_hit_wall = False
            for plat in platforms:
                if bullet_rect.colliderect(plat):
                    if bullet in player_bullets:
                        player_bullets.remove(bullet)
                    bullet_hit_wall = True
                    for _ in range(5):
                        particles.append(Particle(bullet[0], bullet[1]))
                    break

            if bullet_hit_wall:
                continue

        if keys_collected == 3:
            intermediate_music.fadeout(1000)
            if keys[pygame.K_RETURN] and player_rect.colliderect(door_rect):
                screen.blit(black, (0, 0))
                victory_sound.play()
                return "victory"

        lives_collected_status, player_hp, just_healed = check_life_collection(player_rect, level_lives, lives_collected_status, player_hp, max_hp, 20, life_sound)
        if just_healed:
            active_heal_effects.append(HealEffect())

        player_rect = pygame.Rect(x, y, player_width, player_height)
        on_ground, baliktadrotate, y, velocity_y = check_pre_gravity_ground(player_rect, platforms, y, velocity_y)

        dx = 0
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and on_ground:
            velocity_y = jump_speed
            moving = True
            for _ in range(100):
                particles.append(Particle(x + player_width // 2, y + player_height))

        if keys[pygame.K_a]:
            dx = -speed
            moving = True
            if baliktadrotate == "no":
                direction = "left"
                player_angle += 8
            else:
                direction = "right"
                player_angle -= 8
        elif keys[pygame.K_d]:
            dx = speed
            moving = True
            if baliktadrotate == "no":
                direction = "right"
                player_angle -= 8
            else:
                direction = "left"
                player_angle += 8
        else:
            moving = False

        x += dx
        player_rect = pygame.Rect(x, y, player_width, player_height)
        x = handle_horizontal_collision(player_rect, platforms, x, dx, player_width)

        velocity_y += gravity
        y += velocity_y

        player_rect = pygame.Rect(x, y, player_width, player_height)
        y, velocity_y, on_ground, baliktadrotate = handle_vertical_collision(player_rect, platforms, y, velocity_y, player_height, baliktadrotate)
        x, y = apply_screen_bounds(x, y, player_width, player_height, width, height)

        if y >= height - player_height:
            velocity_y = 0
            on_ground = True
            baliktadrotate = "no"

        if moving:
            for _ in range(2):
                particles.append(Particle(x + player_width // 2, y + player_height))
            player_hp -= 0.01
            if player_hp < 0:
                player_hp = 0

        world_surface.blit(levels_background, (0, 0))

        if keys_collected == 3:
            world_surface.blit(open_door, (5, 145))
        else:
            world_surface.blit(close_door, (40, 140))

        time_float += 0.08
        offset = math.sin(time_float) * 5

        for i in range(len(level_lives)):
            if not lives_collected_status[i]:
                world_surface.blit(life, (level_lives[i].x, level_lives[i].y + offset))

        frame_index += animation_speed
        if frame_index >= len(coin_frames):
            frame_index = 0
        current_frame = coin_frames[int(frame_index)]

        # --- MANUAL DRAW AND CHECK ITEMS ---
        for i in range(len(level_keys)):
            if not keys_collected_status[i]:
                draw_x = level_keys[i].x
                draw_y = level_keys[i].y + offset
                float_rect = pygame.Rect(draw_x, draw_y, 20, 10)
                world_surface.blit(light, (draw_x - 10, draw_y - 15))
                world_surface.blit(key1, (draw_x, draw_y))
                if player_rect.colliderect(float_rect):
                    keys_collected_status[i] = True
                    keys_collected += 1
                    key_collect.play() 

        for i in range(len(level_coins)):
            if not coins_collected_status[i]:
                if player_rect.colliderect(level_coins[i]):
                    coins_collected_status[i] = True
                    coin_count += 1
                    coin_sound.play() 
                else:
                    world_surface.blit(current_frame, level_coins[i].topleft)

        intermediate_draw_platforms(world_surface, ground1, ground2, brick1, brick2)

        for b in breakable_bricks:
            world_surface.blit(brick2, (b.x, b.y))

        for e in enemies:
            e_rect = pygame.Rect(e.x, e.y, 40, 40)
            e.update(player_rect, enemy_shoot_sound, enemy_dead_sound)
            player_hp, hit_cooldown, x, y = e.update_bullets(player_rect, player_hp, hit_cooldown, x, y, natamaan_fire)

            if e.hp > 0:
                if player_rect.colliderect(e_rect):
                    if hit_cooldown <= 0:
                        natamaan_fire.play() 
                        player_hp -= 15 
                        hit_cooldown = 30 
                        if player_rect.centerx < e_rect.centerx:
                            x -= 40
                        else:
                            x += 40
                        y -= 20 
                        velocity_y = 0 
            
            e.draw(world_surface)
            e.draw_hp_bar(world_surface)
            for bullet in e.bullets:
                pygame.draw.circle(world_surface, (255, 0, 0), (int(bullet[0]), int(bullet[1])), 5)

        for b in bosses:
            b_rect = pygame.Rect(b.x, b.y, b.width, b.height)
            b.update(player_rect, particles, platforms, roll_sound, boss_shoot_sound)
            player_hp, hit_cooldown, x, y = b.update_bullets(player_rect, player_hp, hit_cooldown, x, y, natamaan_fire)

            if b.hp > 0 and player_rect.colliderect(b_rect):
                if hit_cooldown <= 0:
                    natamaan_fire.play()
                    player_hp -= 30 
                    hit_cooldown = 30
                    if player_rect.centerx < b_rect.centerx:
                        x -= 60
                    else:
                        x += 60
                    y -= 20
                    velocity_y = 0
            
            b.draw(world_surface)
            b.draw_hp_bar(world_surface)
            for bullet in b.bullets:
                pygame.draw.circle(world_surface, (255, 150, 0), (int(bullet[0]), int(bullet[1])), 6)

        for particle in particles[:]:
            particle.update()
            particle.draw(world_surface)
            if particle.lifetime <= 0:
                particles.remove(particle)

        for effect in active_heal_effects[:]:
            effect.update()
            effect.draw(world_surface, x + player_width // 2, y + player_height // 2)
            if effect.timer <= 0:
                active_heal_effects.remove(effect)

        shake_x, shake_y = escano_ult.get_player_shake()
        escano_ult.draw_glow(world_surface, x, y, player_width, player_height)

        if escano_ult.is_charging:
            if escano_ult.charge_direction == "left":
                world_surface.blit(break_block_left, (x + shake_x, y + shake_y))
            else:
                world_surface.blit(break_block_right, (x + shake_x, y + shake_y))
        elif shoot_anim_timer > 0:
            if aim_direction == "left":
                world_surface.blit(aim_left, (x + shake_x, y + shake_y))
            else:
                world_surface.blit(aim_right, (x + shake_x, y + shake_y))
        elif moving:
            rotated_player = pygame.transform.rotate(player_face, player_angle)
            new_rect = rotated_player.get_rect(center=(x + player_width // 2, y + player_height // 2))
            world_surface.blit(rotated_player, (new_rect.x + shake_x, new_rect.y + shake_y))
        else:
            world_surface.blit(player_face, (x + shake_x, y + shake_y))
        
        escano_ult.draw_ui(world_surface, x + shake_x, y + shake_y)

        if escano_ult.active_laser:
            laser = escano_ult.active_laser
            rect = laser['rect']
            for _ in range(100):
                px = random.randint(rect.left, rect.right)
                py = random.randint(rect.top, rect.bottom) 
                size = random.randint(1, 5) 
                color = random.choice([(255, 150, 0), (255, 200, 0), (255, 255, 150)]) 
                glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, 60), (size * 2, size * 2), size * 2)
                world_surface.blit(glow_surf, (px - size * 2, py - size * 2))
                pygame.draw.circle(world_surface, color, (px, py), size)

        for bullet in player_bullets:
            pygame.draw.circle(world_surface, (255, 255, 0), (int(bullet[0]), int(bullet[1])), 4)

        cam_shake_x, cam_shake_y = 0, 0
        if screen_shake_frames > 0:
            cam_shake_x = random.randint(-10, 10)
            cam_shake_y = random.randint(-10, 10)
            screen_shake_frames -= 1

        draw_zoomed_camera(screen, world_surface, x + cam_shake_x, y + cam_shake_y, player_width, player_height, width, height, zoom=2)

        if player_rect.colliderect(door_rect):
            screen.blit(enter, (0, 0 + offset))

        screen.blit(vignette_surface, (0, 0))

        text = font.render(f"{keys_collected}/3", True, (255, 255, 255))

        if keys_collected == 3 and not exit_fade_done:
            if exit_fade_start is None:
                exit_music.play(loops=-1, fade_ms=2000)
                exit_fade_start = pygame.time.get_ticks()
            elapsed = pygame.time.get_ticks() - exit_fade_start
            if elapsed <= 3000:
                if elapsed < 1000:
                    alpha = int((elapsed / 1000) * 255)
                elif elapsed < 2000:
                    alpha = 255
                else:
                    alpha = int(((3000 - elapsed) / 1000) * 255)
                exit_now.set_alpha(alpha)
                screen.blit(exit_now, (0, 0 + offset))
            else:
                exit_fade_done = True

        screen.blit(counter, (0, 0))
        screen.blit(text, (30, 25))

        hp_bar_width = 120
        hp_ratio = player_hp / max_hp
        hp_x, hp_y = 670, 50  

        if player_hp < 30:
            hp_color = (255, 0, 0)
        else:
            hp_color = (0, 255, 0)

        pygame.draw.rect(screen, (60, 60, 60), (hp_x, hp_y, hp_bar_width, 15)) 
        pygame.draw.rect(screen, hp_color, (hp_x, hp_y, hp_bar_width * hp_ratio, 15)) 
        pygame.draw.rect(screen, (255, 255, 255), (hp_x, hp_y, hp_bar_width, 15), 2) 

        coin_text = font.render(f"{coin_count}", True, (255, 255, 255))
        screen.blit(coin_text, (35,65))

        if skill_ui_timer > 0:
            skill_ui_timer -= 1
            if current_skill == "Gun":
                text_color = (100, 255, 100) 
            else:
                text_color = (255, 150, 0)   
            ui_text = font.render(f"EQUIPPED: {current_skill.upper()}", True, text_color)
            text_rect = ui_text.get_rect(center=(width // 2, height - 30))
            alpha = min(255, int((skill_ui_timer / 120) * 255 * 2))
            ui_surface = pygame.Surface((text_rect.width + 20, text_rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(ui_surface, (0, 0, 0, alpha // 2), ui_surface.get_rect(), border_radius=5)
            ui_text.set_alpha(alpha)
            screen.blit(ui_surface, (text_rect.x - 10, text_rect.y - 5))
            screen.blit(ui_text, text_rect)

        if hit_cooldown > 0:
            red_flash = pygame.Surface((width, height), pygame.SRCALPHA)
            alpha = int((hit_cooldown / 30) * 40) 
            red_flash.fill((255, 0, 0, alpha)) 
            screen.blit(red_flash, (0, 0))

        if keys[pygame.K_RETURN] and player_rect.colliderect(door_rect):
            screen.blit(black, (0, 0))

        if back_button_game_rect.collidepoint(mouse_pos):
            screen.blit(back_button_game_hover, back_button_game_rect)
        else:
            screen.blit(back_button_game, back_button_game_rect)

        if player_hp <= 0:
            defeat_sound.play()
            return "defeat"

        pygame.display.update()
        clock.tick(60)