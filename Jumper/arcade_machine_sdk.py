import pygame
from abc import ABC, abstractmethod

BASE_WIDTH = 1024
BASE_HEIGHT = 768
DEFAULT_FPS = 60

class GameMeta:
    def __init__(self):
        self.title = "Sin título"
        self.description = ""
        self.release_date = ""
        self.authors = []

    def with_title(self, title):
        self.title = title
        return self

    def with_description(self, desc):
        self.description = desc
        return self

    def with_release_date(self, date):
        self.release_date = date
        return self

    def with_authors(self, authors):
        self.authors = authors
        return self

class GameBase(ABC):
    def __init__(self):
        self.surface = None 

    @abstractmethod
    def handle_events(self, events):
        pass

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def render(self):
        pass