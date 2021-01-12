import random
import os

DICTIONARY_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "dictionary.txt")


class RandomWords:
    def __init__(self):
        with open(DICTIONARY_FILE, 'r') as dictionary:
            self.word_list = [line.strip() for line in dictionary.readlines()]

    def get_random_words(self, count):
        """Get 'count' random words"""
        return random.sample(self.word_list, count)
