import pickle
import linecache
import data_encoder_decoder
NUM_OF_REVIEW_ATTRIBUTES = 6

class IndexReader():

    def __init__(self, dir):

        if dir[-1] != '/':
            dir += '/'

        self.__dir = dir
        try:
            with open(self.dir + "index_dictionary.pkl", "rb") as data:
                self.__index = pickle.load(data)  # index object
        except:
            print("Error in opening index_dictionary.pkl")

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, index):
        self.__index = index

    @property
    def dir(self):
        return self.__dir

    @dir.setter
    def dir(self, dir):
        self.__dir = dir

    def getProductId(self, reviewId):
        try:
            # get get line by index from the parsed_review file.
            line = linecache.getline(self.dir+"parsed_reviews.txt", (reviewId-1) * NUM_OF_REVIEW_ATTRIBUTES + 2)
        except:
            return None
        # remove \n
        line = line.rstrip()
        if line == "":
            return None
        else:
            return line

    def getReviewScore(self, reviewId):
        try:
            line = linecache.getline(self.dir+"parsed_reviews.txt", (reviewId - 1) * NUM_OF_REVIEW_ATTRIBUTES + 5)
        except:
            return -1
        line = line.rstrip()
        if line == "":
            return -1
        else:
            return float(line)

    def getReviewHelpfulnessNumerator(self, reviewId):
        try:
            line = linecache.getline(self.dir+"parsed_reviews.txt", (reviewId - 1) * NUM_OF_REVIEW_ATTRIBUTES + 3)
        except:
            return -1
        if line == "":
            return -1
        else:
            return int(line)

    def getReviewHelpfulnessDenominator(self, reviewId):
        try:
            line = linecache.getline(self.dir+"parsed_reviews.txt", (reviewId - 1) * NUM_OF_REVIEW_ATTRIBUTES + 4)
        except:
            return -1
        if line == "":
            return -1
        else:
            return int(line)

    def getReviewLength(self, reviewId):
        try:
            line = linecache.getline(self.dir+"parsed_reviews.txt", (reviewId - 1) * NUM_OF_REVIEW_ATTRIBUTES + 6)
        except:
            return -1
        if line == "":
            return -1
        else:
            return int(line)

    def getTokenFrequency(self, token):
        """Return the number of reviews containing a
        given token (i.e., word)
        Returns 0 if there are no reviews containing
        this token"""
        dictionary_string= self.index.dictionary_string
        position_ptr =self.index.position_ptr
        token_index = self.Binary_Search(dictionary_string, position_ptr, token)
        if token_index == -1:
            return 0
        if token_index or token_index == 0:
            return self.index.word_freq[token_index]
        return 0

    def getTokenCollectionFrequency(self, token):
        """Return the number of times that a given
        token (i.e., word) appears in
        the reviews indexed
        Returns 0 if there are no reviews containing
        this token"""

        word_doc_freq = self.getReviewsWithToken(token) # returns an array

        if word_doc_freq == []:
            return 0

        total_word_freq = 0
        # sum all frequencies
        for i in range (1,len(word_doc_freq),2):
            total_word_freq += word_doc_freq[i]

        return total_word_freq

    def getReviewsWithToken(self, token):
        """Returns a series of integers of the form id1, freq-1, id-2, freq-2, ... such
        that id-n is the n-th review containing the
        given token and freq-n is the
        number of times that the token appears in
        review id-n
        Note that the integers should be sorted by id
        Returns an empty Tuple if there are no reviews
        containing this token"""
        dictionary_string= self.index.dictionary_string
        position_ptr =self.index.position_ptr
        token_index = self.Binary_Search(dictionary_string, position_ptr, token)

        if (not token_index and not token_index == 0)or token_index == -1:
            return []
        try:
            with open(self.dir+"doc_freq.bin", "rb") as binary_file:
                #find the data for the token in the binary index file
                binary_file.seek(self.index.bin_file_pos[token_index])

                if token_index == len(self.index.bin_file_pos) - 1: # last token in index
                    bin_data = binary_file.read()
                    bytes_to_read =len(bin_data)
                else:
                    bytes_to_read= self.index.bin_file_pos[token_index + 1] - self.index.bin_file_pos[token_index]
                    bin_data = binary_file.read(bytes_to_read)

                # converting binary data (1010100..) to hex
                in_hex = bin_data.hex()
                # converting hex data to bin string data
                in_bin = str.encode(bin(int(in_hex, 16))[2:].zfill(8*bytes_to_read))

                list_frec_doc = data_encoder_decoder.decode_all(in_bin) # returns the binary data converted to array with numbers
                return list_frec_doc
        except:
             print("Error in opening doc_freq.bin")

    def getNumberOfReviews(self):
        return self.index.num_of_reviews

    def getTokenSizeOfReviews(self):
        return self.index.num_of_words

    def getProductReviews(self, productId):
        """Return the ids of the reviews for a given
        product identifier
        Note that the integers returned should be
        sorted by id
        Returns an empty Tuple if there are no reviews
        for this product"""
        productId_pos_in_file = 2 # position of each pid in the parsed_reviews file
        ids = []
        for i in range (productId_pos_in_file,self.index.num_of_reviews*6,NUM_OF_REVIEW_ATTRIBUTES):
            pid = linecache.getline(self.dir+"parsed_reviews.txt", i)
            pid = pid.rstrip() # remove \n
            if pid == productId: # id is found in the first line of each review data
                ids.append(int(linecache.getline(self.dir+"parsed_reviews.txt", i-1))) # we want the id

        return ids

    def Binary_Search(self, dictionary_string, position_ptrs, target):
        # Binary search is used on the index dictionary to find the location of the given token
        # The algorithm is standard, just we are adding token start and end positions so that we can move on the words
        # (Its a string without spaces)

        start = 0
        end = len(position_ptrs) - 1

        word_start = dictionary_string[position_ptrs[0]:position_ptrs[1]]
        word_end = dictionary_string[position_ptrs[-1]:]

        if word_start == target:
            return 0

        if word_end == target:
            return end

        if target < word_start or target > word_end:
            return

        while word_start <= word_end:
            middle_pos = (start + end) // 2
            mid_word = dictionary_string[position_ptrs[middle_pos]:position_ptrs[middle_pos + 1]]
            if mid_word > target:
                end = middle_pos  # - 1
            elif mid_word < target:
                start = middle_pos  # + 1
            else:
                return middle_pos
            word_start = dictionary_string[position_ptrs[start]:position_ptrs[start + 1]]
            word_end = dictionary_string[position_ptrs[end - 1]:position_ptrs[end]]

            if word_start == word_end and word_start != target:
                return -1


