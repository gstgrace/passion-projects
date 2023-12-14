import pygame
from player import Player
from utils import welcome_screen, player_selection, difficulty_theme_selection, show_game_rules, Button
import random
import math
import json
from constants import (
    IMAGES, WHITE, BLACK, LETTER_FONT, WORD_FONT, WIDTH, HEIGHT,
    RADIUS, GAP, TEXT_FONT, HINT_FONT, FRAME_X, FRAME_Y,
    OFFSET_X, OFFSET_Y, ORANGE_PINK, LIGHT_BROWN_ORANGE
)


def _init_letters():
    """ Initializes and returns a list of letters for the Hangman game."""
    letters = []
    startx = round((WIDTH - (RADIUS * 2 + GAP) * 13) / 2)
    starty = 520
    ascii_a = 97
    for i in range(26):
        x = startx + GAP * 2 + ((RADIUS * 2 + GAP) * (i % 13))
        y = starty + ((i // 13) * (GAP + RADIUS * 2))
        letters.append([x, y, chr(ascii_a + i), True])
    return letters


class HangmanGame:
    """
    This class represents a Hangman game.
    Attributes:
        window (pygame.Surface): The game window surface.
        background (pygame.Surface): The background image of the game.
        hangman_status (int): The current hangman status, indicating the number of incorrect guesses.
        current_word (str): The word to be guessed by the player.
        guessed_word (str): The word that the player successfully guessed.
        guessed (set): A set of letters that have been guessed.
        letters (list): A list of letters to be displayed for guessing.
        current_player_index (int): The index of the current player.
        players (list): A list of player objects.
        total_players (int): The total number of players in the game.
        current_round (int): The current round of the game.
        total_rounds (int): The total number of rounds in the game.
        frame_image (pygame.Surface): The hangman frame image.
        hint_active (bool): Indicates if the hint feature is active.
        hint_message (str): The hint message for the current word.
        difficulty (str): The difficulty level of the game.
        game_state (str): The current state of the game.
        exit_button (Button): The button to exit the game.
        continue_button (Button): The button to continue or start a new game.
        guess_correct_sound (pygame.mixer.Sound): Sound effect for a correct guess.
        guess_wrong_sound (pygame.mixer.Sound): Sound effect for a wrong guess.
        end_round_win_sound (pygame.mixer.Sound): Sound effect for winning a round.
        end_round_lose_sound (pygame.mixer.Sound): Sound effect for losing a round.
        end_game_sound (pygame.mixer.Sound): Sound effect for the end of the game.
    Methods:
        load_clues(self): Loads clues from a JSON file.
        start(self, difficulty): Starts a new game with the specified difficulty.
        reset_game_state(self): Resets the game state for a new round.
        run(self): The main game loop.
        wait_for_user_input(self): Waits for user input in end round/game states.
        update_scores(self): Update scores based on game conditions.
        handle_end_of_round(self): Increment rounds or change game state based on conditions.
        handle_button_click(self, m_x, m_y): Handles the button click events based on the current game state.
        handle_end_of_game(self): Handles the transition at the end of the game for two-player mode.
        display_status(self): Displays the current game status on the screen.
        _is_word_guessed(self): Checks if the current word has been completely guessed.
        provide_hint(self): Provides a hint for the current word.
        display_end_round_message(self, message, game_over=False, win=None): Displays a message at the end of a round.
        display_game_over_single_player(self): Displays a message when game over in single-player game.
        display_first_player_end(self): Displays a message when the game is over for the
        first player in a two-player game.
        display_game_over_two_players(self): Displays a message when the game is over
        for the second player in a two-player game.
        _display_end_first_player_button(self, message): Displays the exit and continue button at the
        end of the first player in a two-player game.
        _display_end_game_button(self, message): Displays the exit and continue button and message at the end of
        the second player in a two-player game.
        _draw_hint_button(self): Draws the hint button on the game window.
        _draw_rounded_rect(self, surface, rect, color, corner_radius): Draws a rounded rectangle on the given surface.
        get_theme_name(self, difficulty): Get the theme name based on the difficulty level.
        _draw(self): Draw the game elements on the game window.
    """
    def load_clues(self):
        """
        Loads clues from a JSON file.
        This method attempts to open and read a file named 'words_clues.json'.
        If successful, it loads the clues into the `words_clues` attribute.
        In case of an error (file not found or JSON decode error), it handles
        the exception and sets `words_clues` to an empty dictionary.
        """
        try:
            with open('words_clues.json', 'r') as file:
                self.words_clues = json.load(file)
        except FileNotFoundError:
            print("Error: 'words_clues.json' file not found. Loading clues failed.")
            self.words_clues = {}
        except json.JSONDecodeError:
            print("Error: JSON decoding failed. Check the format of 'words_clues.json'.")
            self.words_clues = {}

    def __init__(self, window, background, total_player, players, current_player_index):
        print("HangmanGame instance created")  # Keep this to monitor game progression.
        self.window = window
        self.background = background
        self.hangman_status = 0
        self.current_word = ""
        self.guessed_word = ""
        self.guessed = set()
        self.letters = _init_letters()
        self.current_player_index = current_player_index
        self.players = players
        self.total_players = total_player
        self.current_round = 1
        self.total_rounds = 3
        self.frame_image = pygame.image.load('frame.png')
        self.load_clues()
        self.hint_active = False
        self.hint_message = ""
        self.difficulty = None
        self.game_state = "playing"
        self.exit_button = Button(100, 550, 250, 50, 'Exit', (200, 0, 0))
        self.continue_button = Button(550, 550, 400, 50, 'Continue/New Game', (0, 200, 0))
        # Load sound effects with error handling
        try:
            self.guess_correct_sound = pygame.mixer.Sound('guess_correct.wav')
            self.guess_wrong_sound = pygame.mixer.Sound('guess_wrong.wav')
            self.end_round_win_sound = pygame.mixer.Sound('end_of_round_win.wav')
            self.end_round_lose_sound = pygame.mixer.Sound('end_of_round_lose.wav')
            self.end_game_sound = pygame.mixer.Sound('end_of_game.wav')
        except pygame.error as e:
            print(f"Failed to load a sound file: {e}")
            pygame.quit()  # Shut down Pygame modules
            quit()  # Exit the script

    def start(self, difficulty):
        """
        Starts a new game with the specified difficulty.
        Args:
            difficulty (str): The difficulty level for the new game round.
        """
        self.difficulty = difficulty
        self.hangman_status = 0
        self.guessed.clear()
        self.load_clues()
        words = list(self.words_clues[difficulty].keys())
        self.current_word = random.choice(words)
        self.letters = _init_letters()
        self.hint_active = False
        self.hint_message = ""

    def reset_game_state(self):
        """
        Resets the game state for a new round.
        This function clears the set of guessed letters, resets the hangman status,
        deactivates the hint flag, and selects a new word for guessing. It also
        re-initializes the letters and sets the game state to 'playing'
        """
        self.guessed.clear()
        self.hangman_status = 0
        self.hint_active = False
        self.hint_message = ""
        words = list(self.words_clues[self.difficulty].keys())
        self.current_word = random.choice(words)
        self.letters = _init_letters()
        self.game_state = "playing"
        current_player = self.players[self.current_player_index]
        current_player.hints_used = False

    def run(self):
        """
        The main game loop.
         This function runs the main loop of the game. It updates the game window,
         handles player input, checks game over conditions, and updates the game
         state accordingly.
         Returns:
                bool: False if the game is quit, True otherwise.
        """
        self.window.fill(WHITE)
        self.window.blit(self.background, (0, 0))

        if self.game_state == "playing":
            # Handle events during the game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self._handle_events(mouse_x, mouse_y)

            # Check game over conditions
            if self.guessed:
                if self.hangman_status >= len(IMAGES) - 1:
                    self.guessed_word = self.current_word
                    self.display_end_round_message("You were hanged!", game_over=True, win=False)
                    self.update_scores()
                    self.handle_end_of_round()

                elif self._is_word_guessed():
                    self.guessed_word = self.current_word
                    self._draw()
                    pygame.display.update()
                    pygame.time.delay(1000)
                    self.display_end_round_message("Congratulations, you won!", game_over=True, win=True)
                    self.update_scores()
                    self.handle_end_of_round()

        elif self.game_state in ["end_of_round", "end_of_game_single_player", "end_of_game_two_players_first",
                                 "end_of_game_two_players_second"]:
            # Wait for user input in end round/game states
            self.wait_for_user_input()

        self._draw()

        pygame.display.update()
        return True

    def wait_for_user_input(self):
        """
        Waits for user input in end round/game states.
        This function keeps the game in a loop, waiting for the player to click
        a button. It handles the click events for the exit and continue/new game
        buttons.
        """
        waiting_for_user_input = True
        while waiting_for_user_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.handle_button_click(mouse_x, mouse_y)
                    waiting_for_user_input = False  # Stop waiting after a click

            # Redraw the exit and continue buttons
            self.exit_button.draw(self.window)
            self.continue_button.draw(self.window)
            pygame.display.update()

    def _handle_events(self, m_x, m_y):
        """
        Handles mouse button click events.
        This function is responsible for handling mouse click events, specifically
        for letter selection and hint button activation.
        Args:
            m_x (int): The x-coordinate of the mouse click.
            m_y (int): The y-coordinate of the mouse click.
        Returns:
            bool: True if an event was handled, False otherwise.
        """
        # Handle letter clicks
        for letter in self.letters:
            x, y, ltr, visible = letter
            if visible and math.sqrt((x - m_x) ** 2 + (y - m_y) ** 2) < RADIUS:
                letter[3] = False  # Mark the letter as not visible
                guessed_letter = ltr.lower()
                if guessed_letter not in self.guessed:
                    self.guessed.add(guessed_letter)
                    if guessed_letter in self.current_word:
                        self.guess_correct_sound.play()  # Play correct guess sound
                    else:
                        self.guess_wrong_sound.play()  # Play wrong guess sound
                        if self.hangman_status < len(IMAGES) - 1:
                            self.hangman_status += 1
                return True

        # Handle hint button click
        hint_button_rect = self._draw_hint_button()
        if hint_button_rect.collidepoint((m_x, m_y)):
            self.hint_message = self.provide_hint()
            self.hint_active = True

        self._draw()
        return True

    def update_scores(self):
        """Update scores based on game conditions."""
        current_player = self.players[self.current_player_index]
        if self._is_word_guessed() and self.hangman_status < len(IMAGES) - 1:
            # Add basic points based on remaining lives
            points_to_add = 7 - self.hangman_status
            current_player.update_score(points_to_add)
            # Add bonus points if no hint was used
            if not current_player.hints_used:
                current_player.update_score(10)  # Bonus points for not using a hint

    def handle_end_of_round(self):
        """ Increment rounds or change game state based on the conditions"""
        if self.total_players == 1:
            if self.current_round < self.total_rounds:
                self.current_round += 1
                self.reset_game_state()
            else:
                self.game_state = "end_of_game_single_player"
                self.display_game_over_single_player()
        else:
            if self.current_player_index + 1 == self.total_players:
                if self.current_round < self.total_rounds:
                    self.current_round += 1
                    self.reset_game_state()
                else:
                    self.game_state = "end_of_game_two_players_second"
                    self.display_game_over_two_players()
            else:
                if self.current_round < self.total_rounds:
                    self.current_round += 1
                    self.reset_game_state()
                else:
                    self.game_state = "end_of_game_two_players_first"
                    self.display_first_player_end()

    def handle_button_click(self, m_x, m_y):
        """
        Handles the button click events based on the current game state.
        This function determines the actions to take when the exit or continue buttons
        are clicked. It handles the logic for transitioning between game states or
        exiting the game based on the current state and the location of the mouse click.
        Args:
            m_x (int): The x-coordinate of the mouse click.
            m_y (int): The y-coordinate of the mouse click.
        """
        if self.game_state in ["end_of_round"]:
            if self.exit_button.is_over((m_x, m_y)):
                print("Exit button clicked.")
                pygame.quit()
                quit()
            elif self.continue_button.is_over((m_x, m_y)):
                print("Continue button clicked.")
                self.reset_game_state()
        elif self.game_state in ["end_of_game_single_player", "end_of_game_two_players_second"]:
            if self.exit_button.is_over((m_x, m_y)):
                print("Exit button clicked.")
                pygame.quit()
                quit()
            elif self.continue_button.is_over((m_x, m_y)):
                print("Continue button clicked.")
                main()
        elif self.game_state == "end_of_game_two_players_first":
            if self.continue_button.is_over((m_x, m_y)):
                print("Continue button clicked.")
                # Logic to switch to the second player
                self.current_player_index = (self.current_player_index + 1) % self.total_players
                self.current_round = 1  # Reset round for the second player
                self.reset_game_state()
            elif self.exit_button.is_over((m_x, m_y)):
                print("Exit button clicked.")
                pygame.quit()
                quit()

    def handle_end_of_game(self):
        """
        Handles the transition at the end of the game for two-player mode.
        his function is used to switch the current player index to the next player
        after the first player completes their rounds in a two-player game.
        Returns:
            int: The index of the next player, or None if not applicable.
        """
        if self.game_state == "end_of_game_two_players_first":
            return (self.current_player_index + 1) % self.total_players

    def display_status(self):
        """ Displays the current game status on the screen."""
        # Define the starting position for the status text
        x = WIDTH - 150  # Adjust as needed
        y = 20

        current_player_hints = self.players[self.current_player_index].hints_left
        # Create and display each line of the status
        status_font = pygame.font.SysFont('comicsansms', 20)
        lines = [
            f"Player: {self.current_player_index + 1}/{self.total_players}",
            f"Round: {self.current_round}/{self.total_rounds}",
            f"Scores: {self.players[self.current_player_index].score}",
            f"Hints left: {current_player_hints}",
        ]

        for line in lines:
            text = status_font.render(line, 1, BLACK)
            self.window.blit(text, (x, y))
            y += 25  # Increment y to display the next line lower

    def _is_word_guessed(self):
        """
        Checks if the current word has been completely guessed.
        Returns:
            bool: True if all the alphabetic characters in the current word have been
            guessed, False otherwise.
        """
        if not self.current_word.strip():
            return False
        return all(letter in self.guessed for letter in self.current_word if letter.isalpha())

    def provide_hint(self):
        """
        Provides a hint for the current word.
        This function retrieves a hint from the current player's available hints,
            based on the game's difficulty and the current word.
        Returns:
            str: The hint for the current word, or a message if no hints are left.
        """
        current_player = self.players[self.current_player_index]
        return current_player.provide_hint(self.words_clues, self.difficulty, self.current_word)

    def display_end_round_message(self, message, game_over=False, win=None):
        """
        Displays a message at the end of a round. It also shows the final word and plays sounds based on win/lose.
        Args:
            message (str): The message to display.
            game_over (bool, optional): Indicates if the game is over. Defaults to False.
            win (bool, optional): Indicates if the player won the round. Defaults to None.
        """
        self.window.fill(WHITE)
        self.window.blit(self.background, (0, 0))
        text = TEXT_FONT.render(message, 1, BLACK)
        self.window.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - text.get_height() / 2))
        if game_over:
            if win:
                extra_message = f"The word was {self.guessed_word}. Your score has increased."
                self.end_round_win_sound.play()  # Play win sound
            else:
                extra_message = f"The word was {self.guessed_word}."
                self.end_round_lose_sound.play()  # Play lose sound
            extra_text = TEXT_FONT.render(extra_message, 1, BLACK)
            self.window.blit(extra_text, (WIDTH / 2 - extra_text.get_width() / 2, HEIGHT / 2 + 50))

            # Display remaining games
            games_left = self.total_rounds - self.current_round
            if games_left <= 0:
                games_left_message = "No more rounds left."
            else:
                games_left_message = f"You have {games_left} more round(s) left."
            games_left_text = WORD_FONT.render(games_left_message, 1, BLACK)
            self.window.blit(games_left_text, (WIDTH / 2 - games_left_text.get_width() / 2, HEIGHT / 2 + 150))

        pygame.display.update()
        pygame.time.delay(3000)

    def display_game_over_single_player(self):
        """ Displays a message when game over in single player game"""
        final_score = self.players[0].score
        self.end_game_sound.play()
        message = f"Game Over! Your final score: {final_score}."
        self.window.fill(WHITE)
        self.window.blit(self.background, (0, 0))
        self._display_end_game_button(message)
        # Wait for user input before proceeding
        self.wait_for_user_input()

    def display_first_player_end(self):
        """ Displays a message when game over for 1st player in two player game"""
        final_score = self.players[0].score
        self.end_game_sound.play()
        message = f"Player 1 has finished all rounds. Final score: {final_score}."
        self._display_end_first_player_button(message)
        self.wait_for_user_input()

    def display_game_over_two_players(self):
        """ Displays a message when game over for 2nd player in two player game"""
        player1_score = self.players[0].score
        player2_score = self.players[1].score
        self.end_game_sound.play()
        if player1_score > player2_score:
            winner = "Player 1 is the winner!"
        elif player2_score > player1_score:
            winner = "Player 2 is the winner!"
        else:
            winner = "It's a tie!"

        message = f"Game Over! Player 1: {player1_score}, Player 2: {player2_score}\n{winner}"
        self._display_end_game_button(message)
        self.wait_for_user_input()

    def _display_end_first_player_button(self, message):
        """ Displays the exit and continue button at the end of first player in a 2 player game"""
        self.window.fill(WHITE)
        self.window.blit(self.background, (0, 0))
        text = TEXT_FONT.render(message, 1, BLACK)
        self.window.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - text.get_height() / 2))

        self.exit_button.draw(self.window)
        self.continue_button.draw(self.window)
        pygame.display.update()

    def _display_end_game_button(self, message):
        """ Displays the exit and continue button and message at the end of second player in a 2 player game"""
        self.window.fill(WHITE)
        self.window.blit(self.background, (0, 0))

        # Split the message into lines
        lines = message.split('\n')
        y_offset = 0  # Starting y offset for the first line

        for line in lines:
            text_surface = WORD_FONT.render(line, 1, BLACK)
            text_x = WIDTH / 2 - text_surface.get_width() / 2
            text_y = HEIGHT / 2 - text_surface.get_height() / 2 + y_offset
            self.window.blit(text_surface, (text_x, text_y))
            y_offset += text_surface.get_height()  # Increase y_offset for the next line

        self.exit_button.draw(self.window)
        self.continue_button.draw(self.window)
        pygame.display.update()

    def _draw_hint_button(self):
        """ Draws the hint button on the game window."""
        hint_button_color = (255, 153, 102)  # Warm light orange color
        font = pygame.font.SysFont('comicsansms', 20)
        hint_text = font.render("Hint", True, WHITE)
        hint_button_rect = pygame.Rect(10, 10, hint_text.get_width() + 20, hint_text.get_height() + 20)
        pygame.draw.rect(self.window, hint_button_color, hint_button_rect)
        self.window.blit(hint_text, (hint_button_rect.x + 10, hint_button_rect.y + 10))
        return hint_button_rect

    def _draw_rounded_rect(self, surface, rect, color, corner_radius):
        """
        Draws a rounded rectangle on the given surface.
        Args:
            surface (pygame.Surface): The surface on which to draw the rectangle.
            rect (pygame.Rect): The rectangle to be drawn.
            color (tuple): The color of the rectangle.
            corner_radius (int): The radius of the corners of the rectangle.
        Raises:
            ValueError: If the width or height of the rect is less than twice the corner radius.
        """
        if rect.width < 2 * corner_radius or rect.height < 2 * corner_radius:
            raise ValueError("Both width and height must be > 2 * corner radius")

        # Draw the center of the rectangle
        pygame.draw.rect(surface, color, rect)

        # Draw the four rounded corners
        circle_kwargs = dict(color=color, radius=corner_radius)
        pygame.draw.circle(surface, **circle_kwargs, center=rect.topleft, width=0)
        pygame.draw.circle(surface, **circle_kwargs, center=rect.topright, width=0)
        pygame.draw.circle(surface, **circle_kwargs, center=rect.bottomleft, width=0)
        pygame.draw.circle(surface, **circle_kwargs, center=rect.bottomright, width=0)

        # Draw the four sides of the rectangle, without the corners
        pygame.draw.rect(surface, color, rect.inflate((0, -2 * corner_radius)))
        pygame.draw.rect(surface, color, rect.inflate((-2 * corner_radius, 0)))

    def get_theme_name(self, difficulty):
        """
        Get the theme name based on the difficulty level.
        Args:
            difficulty (str): The difficulty level, such as 'easy', 'medium', or 'hard'.
        Returns:
            str: The theme name corresponding to the difficulty level. Returns 'Unknown Theme' if the
            difficulty level is not recognized.
        """
        themes = {
            'easy': 'Food Theme',
            'medium': 'Movie Theme',
            'hard': 'CS Theme'
        }
        return themes.get(difficulty, 'Unknown Theme')

    def _draw(self):
        """
        Draw the game elements on the game window.
        This function draws various game elements on the game window, including the displayed word,
        theme information, letter buttons, hangman frame, player status, and hint button.
        """
        display_word = ""
        for letter in self.current_word:
            if letter in self.guessed:
                display_word += letter + " "
            else:
                display_word += "_ "
        text = WORD_FONT.render(display_word, 1, LIGHT_BROWN_ORANGE)
        self.window.blit(text, (480, 380))

        # Display the theme
        theme_text = self.get_theme_name(self.difficulty)
        theme_font = pygame.font.SysFont('comicsansms', 30)  # Choose an appropriate font size
        theme_surface = theme_font.render(theme_text, True, (0, 0, 0))  # Render the text

        # Calculate the position (upper mid-right of the screen)
        theme_x = WIDTH - theme_surface.get_width() - 320  # Adjust the position as needed
        theme_y = 90

        self.window.blit(theme_surface, (theme_x, theme_y))

        for letter in self.letters:
            x, y, ltr, visible = letter
            if visible:
                # Draw a square button with soft edges
                button_rect = pygame.Rect(x - RADIUS, y - RADIUS, 2 * RADIUS, 2 * RADIUS)
                pygame.draw.rect(self.window, ORANGE_PINK, button_rect, border_radius=RADIUS // 2)

                # Render the letter in white
                text = LETTER_FONT.render(ltr, True, WHITE)
                self.window.blit(text, (x - text.get_width() / 2, y - text.get_height() / 2))

        self.window.blit(self.frame_image, (FRAME_X, FRAME_Y))
        self.window.blit(IMAGES[self.hangman_status], (FRAME_X + OFFSET_X, FRAME_Y + OFFSET_Y))

        self.display_status()

        hint_button_rect = self._draw_hint_button()
        if self.hint_active:
            hint_text = HINT_FONT.render(self.hint_message, True, BLACK)
            self.window.blit(hint_text, (hint_button_rect.x + hint_button_rect.width + 10, hint_button_rect.y + 10))

        pygame.display.update()


def main():
    """
    Main function to run the Hangman game.
    This function initializes the game, handles sound loading, sets up the game window, and manages
    the game loop for both single-player and multiplayer modes.
    """
    pygame.init()
    pygame.mixer.init()  # Initialize the mixer module
    # exception handling for loading sound files
    try:
        pygame.mixer.music.load('background_music_2.mp3')
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)  # Loop the music indefinitely
        click_sound = pygame.mixer.Sound('click_sound.wav')
    except pygame.error as e:
        print(f"Failed to load sound files: {e}")
        pygame.quit()  # Shut down Pygame modules
        quit()  # Exit the script

    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Shuting's Hangman Game")

    # exception handling for loading background
    try:
        background = pygame.image.load("background.png")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except pygame.error as e:
        print(f"Failed to load background image: {e}")
        pygame.quit()  # Shut down Pygame modules
        quit()  # Exit the script

    welcome_screen(win, background, click_sound)
    action = show_game_rules(win, background, click_sound)
    if action == "exit":
        pygame.quit()
        return  # Exit the main function
    num_players = player_selection(win, background, click_sound)
    difficulty = difficulty_theme_selection(win, background, click_sound)  # Set a common difficulty for both players

    running = True
    current_player_index = 0  # Initialize the current player index
    total_rounds = 3  # Set the total number of rounds
    players = [Player(f"Player {i + 1}") for i in range(num_players)]

    while running:
        game = HangmanGame(win, background, num_players, players, current_player_index)
        game.start(difficulty)

        while True:
            if not game.run():
                game.current_round += 1
                if game.current_round > total_rounds:
                    # Check if the game for the current player is over
                    result = game.handle_end_of_game()
                    if result is not None:
                        current_player_index = result
                    break
                else:
                    game.start(difficulty)
                    game.reset_game_state()

        current_player_index = (current_player_index + 1) % num_players  # Switch to the next player

    pygame.quit()


if __name__ == "__main__":
    main()

