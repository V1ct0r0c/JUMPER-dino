import pygame
import sys
from arcade_machine_sdk import BASE_WIDTH, BASE_HEIGHT, DEFAULT_FPS
from jumper import Jumper

def run_game():

    pygame.init()
    pygame.mixer.init() 
    
    screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT))
    pygame.display.set_caption("Arcade Machine Emulator - Jumper")
    
    try:
        game = Jumper()
        game.surface = screen
    except Exception as e:
        print(f"Error al instanciar el juego: {e}")
        return

    clock = pygame.time.Clock()
    running = True

    print("--- Emulador Iniciado ---")
    print("Controles: ESPACIO para saltar, FLECHA ABAJO para agacharse.")

    while running:
        dt = clock.tick(DEFAULT_FPS) / 1000.0
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        game.handle_events(events)
        
        game.update(dt)
        
        game.render()
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_game()