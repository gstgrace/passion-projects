class Player:
    """
    This class represents a player in the game with attributes to track their progress and performance.
    Attributes:
        name (str): The name of the player.
        guessed_letters (set): A set of letters that the player has guessed so far.
        score (int): The current score of the player.
        hints_used (bool): A flag indicating whether the player has used a hint.
        hints_left (int): The number of hints left for the player.
    """
    def __init__(self, name):
        self.name = name
        self.guessed_letters = set()
        self.score = 0
        self.hints_used = False
        self.hints_left = 3  # Each player starts with 3 hints

    def make_guess(self, letter):
        """
        Adds a guessed letter to the set of guessed letters.
        Args:
            letter (str): The letter that the player guesses.
        """
        self.guessed_letters.add(letter)

    def reset(self):
        """Reset the player's guessed letters and score for a new game."""
        self.guessed_letters.clear()
        self.score = 0

    def update_score(self, points):
        """
        Updates the player's score by adding the specified points.
        Args:
            points (int): The number of points to add to the player's score.
        """
        self.score += points

    def provide_hint(self, words_clues, difficulty, current_word):
        """
        Provides a hint for the current word if hints are available.
        Args:
            words_clues (dict): A dictionary of words and their associated clues.
            difficulty (str): The difficulty level of the game.
            current_word (str): The current word that the player needs to guess.
        Returns:
            str: The hint for the current word or a message indicating no hints are left.
        """
        if self.hints_left > 0:
            self.hints_left -= 1  # Decrement hints_left when providing a hint
            self.hints_used = True
            hint = words_clues.get(difficulty, {}).get(current_word, "No clue available")
            return hint
        else:
            return "No hints left."

