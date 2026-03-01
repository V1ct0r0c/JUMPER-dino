import pygame
import random
import sys
import array
from arcade_machine_sdk import GameBase, GameMeta, BASE_WIDTH, BASE_HEIGHT, DEFAULT_FPS

class SoundGenerator:
    @staticmethod
    def create_tone(frequency, duration, volume=0.1):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * n_samples)
        for i in range(n_samples):
            t = i / sample_rate
            val = 32767 if (int(2 * frequency * t) % 2) == 0 else -32768
            buf[i] = int(val * volume)
        return pygame.mixer.Sound(buffer=buf)

DIA_FONDO = (247, 247, 247)
DIA_TEXTO = (83, 83, 83)
NOCHE_FONDO = (32, 33, 36)
NOCHE_TEXTO = (241, 241, 241)
ALTURA_SUELO = BASE_HEIGHT - 150 

class Jumper(GameBase): 
    def __init__(self):
        super().__init__()
        
        self.snd_jump = SoundGenerator.create_tone(600, 0.1)
        self.snd_hit = SoundGenerator.create_tone(200, 0.5)
        self.snd_point = SoundGenerator.create_tone(1000, 0.1)
        
        self.font_title = pygame.font.SysFont("Courier", 120, bold=True)
        self.font_main = pygame.font.SysFont("Courier", 40, bold=True)
        self.font_ui = pygame.font.SysFont("Courier", 25)
        
        self.high_score = 0
        self.flicker_timer = 0
        self.show_text = True
        
        self.clouds = [{"x": random.randint(0, BASE_WIDTH), "y": random.randint(50, 200)} for _ in range(5)]
        self.stars = [{"x": random.randint(0, BASE_WIDTH), "y": random.randint(20, 300)} for _ in range(15)]
        
        self.reset_game(to_menu=True)

    def reset_game(self, to_menu=False):
        self.dino_w, self.dino_h = 60, 65
        self.player_rect = pygame.Rect(100, ALTURA_SUELO - self.dino_h, self.dino_w, self.dino_h)
        
        self.player_vel_y = 0
        self.is_jumping = False
        self.is_ducking = False
        self.step_index = 0
        self.obstacles = []
        self.spawn_timer = 0
        self.game_speed = 12
        self.score = 0
        self.last_score_milestone = 0
        self.is_night = False
        self.state = "MENU" if to_menu else "PLAYING"

    def update(self, dt): 
        for cloud in self.clouds:
            cloud["x"] -= 1 if self.state == "MENU" else 2
            if cloud["x"] < -100: cloud["x"] = BASE_WIDTH + 100

        if self.state == "MENU":
            self.flicker_timer += 1
            if self.flicker_timer % 30 == 0:
                self.show_text = not self.show_text

        elif self.state == "PLAYING":
            self.is_night = (int(self.score) // 200) % 2 != 0
            
            if int(self.score) > 0 and int(self.score) % 100 == 0 and int(self.score) != self.last_score_milestone:
                self.snd_point.play()
                self.last_score_milestone = int(self.score)

            self.step_index = (self.step_index + 1) % 14
            
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and not self.is_jumping:
                self.is_ducking = True
                self.player_rect.height = 40
                self.player_rect.y = ALTURA_SUELO - 40
            else:
                self.is_ducking = False
                self.player_rect.height = self.dino_h
                if not self.is_jumping: self.player_rect.y = ALTURA_SUELO - self.dino_h

            if not self.is_ducking:
                self.player_vel_y += 1.1 
                self.player_rect.y += self.player_vel_y
            
            if self.player_rect.bottom > ALTURA_SUELO:
                self.player_rect.bottom = ALTURA_SUELO
                self.player_vel_y = 0
                self.is_jumping = False

            self.game_speed += 0.003
            self.score += 0.15
            self.spawn_timer += 1
            
            if self.spawn_timer > random.randint(40, 90):
                self.spawn_obstacle()
                self.spawn_timer = 0

            for obs in self.obstacles[:]:
                obs['rect'].x -= self.game_speed
                if obs['rect'].right < 0: self.obstacles.remove(obs)
                if self.player_rect.colliderect(obs['rect']):
                    self.snd_hit.play()
                    self.state = "GAMEOVER"
                    self.high_score = max(self.high_score, int(self.score))

    def spawn_obstacle(self):
        if self.score > 100 and random.random() < 0.35:
            h_y = random.choice([ALTURA_SUELO - 120, ALTURA_SUELO - 80, ALTURA_SUELO - 40])
            self.obstacles.append({'rect': pygame.Rect(BASE_WIDTH, h_y, 50, 35), 'type': 'pajaro'})
        else:
            h = random.choice([60, 90, 110])
            self.obstacles.append({'rect': pygame.Rect(BASE_WIDTH, ALTURA_SUELO - h, 30, h), 'type': 'cactus'})

    def render(self): 
        screen = self.surface
        bg_color = NOCHE_FONDO if self.is_night else DIA_FONDO
        txt_color = NOCHE_TEXTO if self.is_night else DIA_TEXTO
        screen.fill(bg_color)
        
        if self.is_night:
            for star in self.stars: pygame.draw.circle(screen, NOCHE_TEXTO, (star["x"], star["y"]), 2)
        for cloud in self.clouds:
            c_color = (220, 220, 220) if not self.is_night else (70, 70, 70)
            pygame.draw.ellipse(screen, c_color, (cloud["x"], cloud["y"], 100, 40))

        pygame.draw.line(screen, txt_color, (0, ALTURA_SUELO), (BASE_WIDTH, ALTURA_SUELO), 3)

        if self.state == "MENU":
            self.draw_text(screen, "JUMPER", self.font_title, DIA_TEXTO, BASE_WIDTH//2, BASE_HEIGHT//3)
            if self.show_text:
                self.draw_text(screen, "PRESIONA ESPACIO PARA JUGAR", self.font_main, DIA_TEXTO, BASE_WIDTH//2, BASE_HEIGHT//2 + 50)
            self.draw_text(screen, "CONTROLES: ESPACIO (SALTAR) | FLECHA ABAJO (AGACHARSE)", self.font_ui, DIA_TEXTO, BASE_WIDTH//2, BASE_HEIGHT - 50)
        else:
           
            pygame.draw.rect(screen, txt_color, self.player_rect)
            eye_x = self.player_rect.x + (50 if self.is_ducking else 35)
            pygame.draw.rect(screen, bg_color, (eye_x, self.player_rect.y + 12, 6, 6))
            
            if not self.is_jumping and self.state == "PLAYING":
                pata_offset = 10 if self.step_index < 7 else (self.player_rect.width - 20)
                pygame.draw.rect(screen, bg_color, (self.player_rect.x + pata_offset, self.player_rect.bottom - 12, 12, 12))

            for obs in self.obstacles:
                pygame.draw.rect(screen, txt_color, obs['rect'])
                if obs['type'] == 'pajaro':
                    wing_y = obs['rect'].y - 20 if self.step_index < 7 else obs['rect'].y + 30
                    pygame.draw.rect(screen, txt_color, (obs['rect'].x + 15, wing_y, 20, 10))

            score_str = f"HI {str(self.high_score).zfill(5)}  {str(int(self.score)).zfill(5)}"
            self.draw_text(screen, score_str, self.font_ui, txt_color, BASE_WIDTH - 200, 50)

            if self.state == "GAMEOVER":
                overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
                overlay.fill((bg_color[0], bg_color[1], bg_color[2], 180))
                screen.blit(overlay, (0,0))
                self.draw_text(screen, "G A M E  O V E R", self.font_main, txt_color, BASE_WIDTH//2, BASE_HEIGHT//2 - 50)
                self.draw_text(screen, "PRESIONA ESPACIO PARA REINTENTAR", self.font_ui, txt_color, BASE_WIDTH//2, BASE_HEIGHT//2 + 20)

    def draw_text(self, screen, text, font, color, x, y):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(x, y))
        screen.blit(surf, rect)

    def handle_events(self, events): 
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state != "PLAYING": 
                        self.reset_game(to_menu=False)
                        self.snd_jump.play()
                    elif not self.is_jumping and not self.is_ducking:
                        self.snd_jump.play()
                        self.player_vel_y = -22 
                        self.is_jumping = True


meta = (GameMeta()
        .with_title("JUMPER")
        .with_description("Dino Arcade")
        .with_release_date("2024-05-26")
        .with_authors(["Michel larez, Victor Coa"]))