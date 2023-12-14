import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
RADIUS = 20
GAP = 15

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE_PINK = (255, 153, 153)
LIGHT_BROWN_ORANGE = (204, 153, 102)

# Adjusted coordinates to place the frame image and the hangman image inside it
FRAME_X = 80
FRAME_Y = 60
OFFSET_X = 45
OFFSET_Y = 45

# Fonts
LETTER_FONT = pygame.font.SysFont('comicsansms', 35)
WORD_FONT = pygame.font.SysFont('comicsansms', 45)
TEXT_FONT = pygame.font.SysFont('comicsansms', 35)
TITLE_FONT = pygame.font.SysFont('comicsansms', 70)
BUTTON_FONT = pygame.font.SysFont('comicsansms', 45)
HINT_FONT = pygame.font.SysFont('comicsansms', 25)

# Load images
IMAGES = [
    pygame.image.load("hangman0.png"),
    pygame.image.load("hangman1.png"),
    pygame.image.load("hangman2.png"),
    pygame.image.load("hangman3.png"),
    pygame.image.load("hangman4.png"),
    pygame.image.load("hangman5.png"),
    pygame.image.load("hangman6.png"),
    pygame.image.load("hangman7.png"),
]

