import pygame
import random
import sys
import array
from arcade_machine_sdk import GameBase, GameMeta, BASE_WIDTH, BASE_HEIGHT, DEFAULT_FPS


# GENERADOR DE SONIDOS sintetizador 8-bit 

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


# CLASE PRINCIPAL: JUMPER

DIA_FONDO = (247, 247, 247)
DIA_TEXTO = (83, 83, 83)
NOCHE_FONDO = (32, 33, 36)
NOCHE_TEXTO = (241, 241, 241)
ALTURA_SUELO = BASE_HEIGHT - 100

class JumperGame(GameBase):
    def __init__(self):
        super().__init__()
        # El SDK inicializa el mixer, pero nos aseguramos de tener los sonidos listos
        self.snd_jump = SoundGenerator.create_tone(600, 0.1)
        self.snd_hit = SoundGenerator.create_tone(200, 0.5)
        self.snd_point = SoundGenerator.create_tone(1000, 0.1)
        
        self.font_large = pygame.font.SysFont("Courier", 80, bold=True)
        self.font_small = pygame.font.SysFont("Courier", 30)
        
        self.high_score = 0
        self.state = "MENU"
        self.reset_game()

    def reset_game(self):
        # Hitbox del Dino (44x47 es el estándar del original)
        self.player_rect = pygame.Rect(100, ALTURA_SUELO - 47, 44, 47)
        self.player_vel_y = 0
        self.is_jumping = False
        self.is_ducking = False
        self.step_index = 0
        
        self.obstacles = []
        self.clouds = [{"x": random.randint(0, BASE_WIDTH), "y": random.randint(50, 200)} for _ in range(5)]
        self.stars = [{"x": random.randint(0, BASE_WIDTH), "y": random.randint(20, 300)} for _ in range(15)]
        
        self.spawn_timer = 0
        self.game_speed = 10
        self.score = 0
        self.last_score_milestone = 0
        self.is_night = False
        self.state = "PLAYING"

    def update(self):
        if self.state == "PLAYING":
            # Lógica de Ciclo Noche (Cada 200 puntos)
            self.is_night = (int(self.score) // 200) % 2 != 0
            
            # Sonido de recompensa cada 100 puntos
            if int(self.score) > 0 and int(self.score) % 100 == 0 and int(self.score) != self.last_score_milestone:
                self.snd_point.play()
                self.last_score_milestone = int(self.score)

            # Animación de carrera
            self.step_index = (self.step_index + 1) % 14
            
            # Gestión de Input para Agacharse (Teclas nativas de Pygame)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN] and not self.is_jumping:
                self.is_ducking = True
                self.player_rect.height = 30
                self.player_rect.y = ALTURA_SUELO - 30
            else:
                self.is_ducking = False
                self.player_rect.height = 47
                if not self.is_jumping: 
                    self.player_rect.y = ALTURA_SUELO - 47

            # Gravedad
            if not self.is_ducking:
                self.player_vel_y += 0.8
                self.player_rect.y += self.player_vel_y
            
            if self.player_rect.bottom > ALTURA_SUELO:
                self.player_rect.bottom = ALTURA_SUELO
                self.player_vel_y = 0
                self.is_jumping = False

            # Movimiento y Dificultad
            self.game_speed += 0.0025
            self.score += 0.15
            self.spawn_timer += 1
            
            # Fondo (Nubes)
            for cloud in self.clouds:
                cloud["x"] -= 2
                if cloud["x"] < -100: cloud["x"] = BASE_WIDTH + 100

            # Generación Aleatoria de Cactus y Pájaros
            if self.spawn_timer > random.randint(40, 90):
                self.spawn_obstacle()
                self.spawn_timer = 0

            # Procesar Obstáculos
            for obs in self.obstacles[:]:
                obs['rect'].x -= self.game_speed
                if obs['rect'].right < 0:
                    self.obstacles.remove(obs)
                
                # Colisión Dinámica
                if self.player_rect.colliderect(obs['rect']):
                    self.snd_hit.play()
                    self.state = "GAMEOVER"
                    self.high_score = max(self.high_score, int(self.score))

    def spawn_obstacle(self):
        # Pájaros solo tras superar los 100 puntos
        if self.score > 100 and random.random() < 0.3:
            h_y = random.choice([ALTURA_SUELO - 85, ALTURA_SUELO - 55, ALTURA_SUELO - 25])
            self.obstacles.append({'rect': pygame.Rect(BASE_WIDTH, h_y, 46, 30), 'type': 'pajaro'})
        else:
            h = random.choice([40, 60, 75])
            self.obstacles.append({'rect': pygame.Rect(BASE_WIDTH, ALTURA_SUELO - h, 25, h), 'type': 'cactus'})

    def draw_dino(self, screen, color):
        # Dibujar Cuerpo
        pygame.draw.rect(screen, color, self.player_rect)
        # Dibujar Ojo (Color inverso al cuerpo)
        ojo_color = NOCHE_FONDO if self.is_night else DIA_FONDO
        pygame.draw.rect(screen, ojo_color, (self.player_rect.x + 30, self.player_rect.y + 8, 4, 4))
        
        # Animación de Patas (Intercambio de píxeles vacíos)
        if not self.is_jumping and self.state == "PLAYING":
            pata_offset = 5 if self.step_index < 7 else 25
            pygame.draw.rect(screen, ojo_color, (self.player_rect.x + pata_offset, self.player_rect.bottom - 10, 10, 10))

    def draw(self, screen):
        bg_color = NOCHE_FONDO if self.is_night else DIA_FONDO
        txt_color = NOCHE_TEXTO if self.is_night else DIA_TEXTO
        screen.fill(bg_color)
        
        # Elementos de Ambiente
        if self.is_night:
            for star in self.stars:
                pygame.draw.circle(screen, NOCHE_TEXTO, (star["x"], star["y"]), 2)
        
        for cloud in self.clouds:
            c_color = (210, 210, 210) if not self.is_night else (70, 70, 70)
            pygame.draw.ellipse(screen, c_color, (cloud["x"], cloud["y"], 60, 30))

        # Línea de Horizonte
        pygame.draw.line(screen, txt_color, (0, ALTURA_SUELO), (BASE_WIDTH, ALTURA_SUELO), 2)

        if self.state == "MENU":
            self.draw_text(screen, "JUMPER", self.font_large, txt_color, BASE_WIDTH//2, BASE_HEIGHT//3)
            self.draw_text(screen, "PRESIONA ESPACIO PARA INICIAR", self.font_small, txt_color, BASE_WIDTH//2, BASE_HEIGHT//2)
        else:
            self.draw_dino(screen, txt_color)
            for obs in self.obstacles:
                pygame.draw.rect(screen, txt_color, obs['rect'])
            
            # UI: Puntuación
            score_str = f"HI {str(self.high_score).zfill(5)}  {str(int(self.score)).zfill(5)}"
            self.draw_text(screen, score_str, self.font_small, txt_color, BASE_WIDTH - 200, 50)

            if self.state == "GAMEOVER":
                self.draw_text(screen, "G A M E  O V E R", self.font_large, txt_color, BASE_WIDTH//2, BASE_HEIGHT//3)
                self.draw_text(screen, "ESPACIO PARA REINTENTAR", self.font_small, txt_color, BASE_WIDTH//2, BASE_HEIGHT//2)

    def draw_text(self, screen, text, font, color, x, y):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(x, y))
        screen.blit(surf, rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.state != "PLAYING": 
                    self.reset_game()
                elif not self.is_jumping and not self.is_ducking:
                    self.snd_jump.play()
                    self.player_vel_y = -17
                    self.is_jumping = True

# METADATOS (Uso del Builder del SDK)

meta = (GameMeta()
        .with_title("JUMPER")
        .with_description("Clon dinámico del Dino de Google con ciclo noche/día, sonido 8-bit y animación.")
        .with_release_date("2024-05-24")
        .with_tags(["arcade", "retro", "runner", "night-mode"])
        .with_group_number(1)
        .with_authors(["IA-Assistant", "DevUser"]))

