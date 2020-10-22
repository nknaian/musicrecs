import random


class RandomWords:
    def __init__(self, dictionary_file):
        with open(dictionary_file, 'r') as dictionary:
            self.word_list = [line.strip() for line in dictionary.readlines()]

    def get_random_words(self, count):
        """Get 'count' random words"""
        return random.sample(self.word_list, count)
