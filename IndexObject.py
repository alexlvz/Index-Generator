
# This class represents a review object. This object is created during the parsing process of the reviews file.
# It will be used later on for index creation.
class IndexObject():

    def __init__(self):
        self.__position_ptr=[] # array for positions in the index text, with the size of all index words without duplicates
        self.__word_freq = []# array that holds for each word the number of reviews its founf in.
        self.__bin_file_pos = []  # holds the position of the data of a selected word in the dictionary
        self.__dictionary_string = "" # all dictionary words without spaces and duplicates

    @property
    def position_ptr(self):
        return self.__position_ptr

    @position_ptr.setter
    def position_ptr(self, position_ptr):
        self.__position_ptr= position_ptr

    @property
    def num_of_reviews(self):
        return self.__num_of_reviews

    @num_of_reviews.setter
    def num_of_reviews(self, num_of_reviews):
        self.__num_of_reviews = num_of_reviews

    @property
    def num_of_words(self):
        return self.__num_of_words #total words in the index ( with duplicates)

    @num_of_words.setter
    def num_of_words(self, num_of_words):
        self.__num_of_words = num_of_words


    @property
    def word_freq(self): # array
        return self.__word_freq

    @word_freq.setter
    def word_freq(self, word_freq):
        self.__word_freq= word_freq

    @property
    def bin_file_pos(self): #position of word meta data in binary index
        return self.__bin_file_pos

    @bin_file_pos.setter
    def bin_file_pos(self, bin_file_pos):
        self.__bin_file_pos = bin_file_pos

    @property
    def dictionary_string(self):
        return self.__dictionary_string

    @dictionary_string.setter
    def dictionary_string(self, dictionary_string):
        self.__dictionary_string= dictionary_string