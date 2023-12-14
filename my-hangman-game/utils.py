import pygame
from constants import WIDTH, HEIGHT


class Button:
    """
    A class for creating and managing buttons in a pygame window.
    Attributes:
        x (int): The x-coordinate of the button's top-left corner.
        y (int): The y-coordinate of the button's top-left corner.
        width (int): The width of the button.
        height (int): The height of the button.
        text (str): The text displayed on the button.
        color (tuple): The color of the button.
        border_radius (int): The radius of the button's corners.
    """
    def __init__(self, x, y, width, height, text, color, border_radius=0):
        """Initializes the Button with the specified attributes."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.border_radius = border_radius

    def draw(self, win, outline=None):
        """
        Draws the button onto a window.
        Args:
            win (pygame.Surface): The pygame window or surface to draw the button on.
            outline (tuple, optional): The color of the outline around the button.
        """
        if outline:
            # Pygame doesn't support border_radius in drawing outlines, so we have to draw an outline rect first
            pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4),
                             border_radius=self.border_radius)

        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), border_radius=self.border_radius)

        if self.text != '':
            font = pygame.font.SysFont('comicsansms', 40)
            text = font.render(self.text, True, (0, 0, 0))  # True to enable antialiasing
            win.blit(text, (
                self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def is_over(self, pos):
        """
        Checks if the given position is over the button.
        Args:
            pos (tuple): A tuple containing the x and y coordinates to check.
        Returns:
            bool: True if the position is over the button, False otherwise.
        """
        return self.x < pos[0] < self.x + self.width and self.y < pos[1] < self.y + self.height


def welcome_screen(win, background, click_sound):
    """
    Displays the welcome screen of the game.
    Args:
        win (pygame.Surface): The pygame window or surface to draw the welcome screen on.
        background (pygame.Surface): The background image for the welcome screen.
        click_sound (pygame.mixer.Sound): The sound to play when a button is clicked.
    """
    logo_image = pygame.image.load("logo.png")
    title_image = pygame.image.load("title.png")
    enter_game_image = pygame.image.load("enter.png")
    enter_game_rect = enter_game_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 180))  # Adjust position as needed

    # Position for the logo image
    logo_pos = ((WIDTH - logo_image.get_width()) // 2, HEIGHT // 4 - logo_image.get_height() // 2)

    # Position for the title image
    title_pos = ((WIDTH - title_image.get_width()) // 2, HEIGHT // 2 - title_image.get_height() // 2)

    run = True
    while run:
        # Blit background
        win.blit(background, (0, 0))

        # Blit logo image
        win.blit(logo_image, logo_pos)

        # Blit title image
        win.blit(title_image, title_pos)

        # Blit "Enter Game" text image
        win.blit(enter_game_image, enter_game_rect)

        # Update display
        pygame.display.update()

        # Mouse Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if enter_game_rect.collidepoint(pygame.mouse.get_pos()):
                    click_sound.play()
                    run = False  # Exit the welcome screen and proceed to the game


def show_game_rules(window, background, click_sound):
    """
    Displays the game rules screen.
    Args:
        window (pygame.Surface): The pygame window or surface to draw the rules screen on.
        background (pygame.Surface): The background image for the rules screen.
        click_sound (pygame.mixer.Sound): The sound to play when a button is clicked.
    """
    running = True
    # Create buttons
    start_button = Button(250, 600, 120, 50, 'Start', (0, 200, 0))  # Adjust position and size as needed
    exit_button = Button(550, 600, 120, 50, 'Exit', (200, 0, 0))

    while running:
        window.blit(background, (0, 0))
        font = pygame.font.SysFont('comicsansms', 20)
        rules = [
            "How to Play: ",
            " - Play Alone or With a Friend: Choose to play by yourself or with someone else.",
            " - Themes & Difficulty: Pick from 3 themes, each at a different level of difficulty.",
            " - Three Rounds to Play: Each game has THREE rounds.",
            " - In Each Round: You have 7 tries to guess the word.",
            " - Lose a Life for Wrong Guess: Each wrong guess costs you one try.",
            " - Right Guess: Correct guesses reveal letters.",
            " - Out of Tries? You are hanged.",
            " - Win Points: Correctly guess the word to win points based on remaining tries.",
            " - Bonus Points: You get ONE HINT per round, but you will get 10 BONUS POINTS ",
            " if you guess correctly without hint.",
            " - Highest Score Wins: The more points you score, the better!",
            "Have fun and good luck guessing the words!"
        ]

        y = 50  # Starting Y position of the first line
        for line in rules:
            text = font.render(line, True, (0, 0, 0))
            window.blit(text, (50, y))
            y += 40  # Increment Y position for next line

        # Draw buttons
        start_button.draw(window)
        exit_button.draw(window)

        # Mouse Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.is_over(pygame.mouse.get_pos()):
                    click_sound.play()
                    return "start"  # Proceed to start the game
                elif exit_button.is_over(pygame.mouse.get_pos()):
                    click_sound.play()
                    return "exit"  # Exit the game

        pygame.display.update()


def player_selection(win, background, click_sound):
    """
    Allows the player to select the number of players.
    Args:
        win (pygame.Surface): The pygame window or surface to draw the player selection screen on.
        background (pygame.Surface): The background image for the player selection screen.
        click_sound (pygame.mixer.Sound): The sound to play when a button is clicked.
    Returns:
        int: The number of players selected.
    """
    button_color = (204, 153, 102)  # Grey color for button
    title_font = pygame.font.SysFont('comicsansms', 50)
    title_text = title_font.render('Choose the number of players', True, (0, 0, 0))  # Black color for the title

    one_player_button = Button(WIDTH / 2 - 280, HEIGHT / 2 - 100, 500, 70, '1 Player', button_color)
    two_player_button = Button(WIDTH / 2 - 280, HEIGHT / 2, 500, 70, '2 Players', button_color)
    run = True
    while run:
        win.blit(background, (0, 0))
        win.blit(title_text, (WIDTH / 2 - title_text.get_width() / 2, HEIGHT / 2 - 200))
        one_player_button.draw(win)
        two_player_button.draw(win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                click_sound.play()
                if one_player_button.is_over(pos):
                    return 1
                elif two_player_button.is_over(pos):
                    return 2


def difficulty_theme_selection(win, background, click_sound):
    """
    Allows the player to select the game difficulty and theme.
    Args:
        win (pygame.Surface): The pygame window or surface to draw the difficulty/theme selection screen on.
        background (pygame.Surface): The background image for the selection screen.
        click_sound (pygame.mixer.Sound): The sound to play when a button is clicked.
    Returns:
        str: The selected difficulty level.
    """
    button_color = (204, 153, 102)  # Grey color for button
    title_font = pygame.font.SysFont('comicsansms', 50)
    title_text = title_font.render('Choose difficulty level', True, (0, 0, 0))

    easy_button = Button(WIDTH / 2 - 250, HEIGHT / 2 - 100, 500, 70, 'Easy - food theme', button_color)
    medium_button = Button(WIDTH / 2 - 250, HEIGHT / 2, 500, 70, 'Medium - movie theme', button_color)
    hard_button = Button(WIDTH / 2 - 250, HEIGHT / 2 + 100, 500, 70, 'Hard - CS theme', button_color)
    run = True
    while run:
        win.blit(background, (0, 0))
        win.blit(title_text, (WIDTH / 2 - title_text.get_width() / 2, HEIGHT / 2 - 200))
        easy_button.draw(win)
        medium_button.draw(win)
        hard_button.draw(win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                click_sound.play()
                if easy_button.is_over(pos):
                    return 'easy'
                elif medium_button.is_over(pos):
                    return 'medium'
                elif hard_button.is_over(pos):
                    return 'hard'
    return 'easy'

