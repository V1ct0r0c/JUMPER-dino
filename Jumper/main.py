from jumper import Jumper
from arcade_machine_sdk import GameMeta
import pygame

if not pygame.get_init():
    pygame.init()

metadata = (GameMeta()
        .with_title("Jumper")
        .with_description("Dino Arcade")
        .with_release_date("2024-05-26")
        .add_tag("Plataformas")
        .with_group_number(4)
        .with_authors(["Michel Larez", "Victor Coa"]))

game = Jumper(metadata)

if __name__ == "__main__":
    game.run_independently()