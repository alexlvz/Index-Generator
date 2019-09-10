import os
from functools import reduce
import re
import math
import struct

BUFFER_SIZE = 8388608
# patterns are the different parts of review data that we would like to store in our index
patterns = ["product/productId: ", "review/helpfulness: ", "review/score: ", "review/text: "]


def Binary_Search(dictionary_string, position_ptrs, target):
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


# This function parses all words of the review/text field.
# It returns a list of words of a single  review, appends this words to the list that holds all review words,
# then removes duplicates and sorts it. Also returns the total number of words in all reviews
def review_words_to_list_generator(file,all_review_words):
    review_words=[]
    word="" #current word
    while True: #read file till the end of it
        char = file.read(1)

        if not char:  # end of file
            if word != "":
                review_words.append(word)
            break

        # can be end of tokens if so, break
        if char == "\n":
            pos = file.tell()
            char = file.read(19)
            if char == "\nproduct/productId:":
                file.seek(pos)
                if word != "":
                    review_words.append(word)
                break
            else: # found new line in a text, will remove it and continue as usual
                file.seek(pos)
                if word != "":
                    review_words.append(word)
                word = ""
                char = file.read(1)

        # regular char
        if char != " " and not char.isalpha() and not char.isdigit():
            if word != "":
                review_words.append(word)
            word = ""
            continue
        # normalize capital letters
        elif char.isalpha():
            char = char.lower()

        if char != " ":
            word = word + char

        else:
            if word != "":
                review_words.append(word)
            word = ""

    all_review_words += review_words
    num_of_tokens = len(review_words)
    del review_words
    return all_review_words, num_of_tokens

# sub function that searches for a pattern. returns found text if review text is found
# returns found not text and the rest of line for later parsing
def search_pattern(file,patterns):
    template=""
    while True:
        char = file.read(1)
        if not char:  # end of file
            return "", "", "eof"
        if char == "\n":
            break
        template = template + char # read while template is caught
        for pattern in patterns:
            if template == pattern:
                if not pattern == patterns[3]:# if patern is text dont read all the line
                    rest_of_the_line=file.readline()
                    if not rest_of_the_line:  # end of file
                        break

                    return pattern, rest_of_the_line,"found-not-text"
                return pattern,"","found-text"

    return "","","not_found"


# -----------------------------------------------------------------
# this is the main parsing function. it creates the parsed reviews file and returns number of words in all reviews
# and a list with all words, after removing duplicates and sorting
# also, during the parsing, it creates the parsed_reviews.txt file which will hold old meta-data about the reviews
# that we would like to extract
def raw_review_parser(dir,file):

    all_review_words = []
    pattern=""
    docID = 0
    string_to_file = ""

    if os.path.exists(dir+"parsed_reviews.txt"):
        os.remove(dir+"parsed_reviews.txt")

    try:
        f = open(dir+"parsed_reviews.txt", "w", encoding="utf-8")
    except:
        print("Error in opening parsed_reviews.txt file")
    # through this loop we will read and parse all the information in the given file
    # After each successfull parsing, the data is written to the parsed_reviews file.
    while True:
        productId = ""
        prv_pattern = pattern
        pattern,value,status = search_pattern(file, patterns)
        if status=="eof":
            break
        if status == "not_found":
            pattern = prv_pattern
            if pattern == patterns[0]:
                productId += value
        if status == "found-not-text":
            if pattern == patterns[0]:
                productId = value
                docID +=1
                string_to_file += str(docID) + "\n" + productId # write to file
            elif pattern == patterns[1]:
                numerator = ""
                denominator = ""
                flag = "numerator"
                for char in value:
                    if char == "/":
                        flag = "denominator"
                        continue
                    if flag == "numerator":
                        numerator += char
                    else:
                        denominator += char
                string_to_file += numerator + "\n" + denominator # write to file

            elif pattern == patterns[2]: #score
                string_to_file += str(value)

        if status == "found-text":
            all_review_words, num_of_tokens = review_words_to_list_generator(file,all_review_words)
            string_to_file += str(num_of_tokens) +"\n"
            if docID % 200000 == 0: #200000 docs is the max amount that our ram can handle with. this number can be changed
                all_review_words_copy = list(set(all_review_words))  # remove duplicates (for the index)
                del all_review_words
                all_review_words = all_review_words_copy.copy()
                del all_review_words_copy
    # free up the ram from the previous list
    all_review_words_copy = list(set(all_review_words))  # remove duplicates (for the index)
    del all_review_words
    all_review_words = all_review_words_copy.copy()
    del all_review_words_copy
    all_review_words.sort()

    position_ptrs = [] # list that holds positions of the words in the string
    word_index = 0
    #appending to the list of positions
    for word in all_review_words:
        position_ptrs.append(word_index)
        word_index += len(word)

    index_str = str(reduce(lambda x, y: x + y, all_review_words)) #list to string (we use dictionary as a string)
    f.write(string_to_file)
    f.close()
    #docID that is returned is the max doc id
    return position_ptrs, index_str, docID

#generates unsorted tuples of word id and doc id and saves them into file.
def build_tuples(dir,file,index_str, position_ptrs):
    doc_id = 0
    list_size = 0
    nums_list = []
    total_tokens = 0

    if os.path.exists(dir+"unsorted_tuples.bin" + '.bin'):
        os.remove(dir+"unsorted_tuples.bin" + '.bin')

    pairs_file = open(dir+"unsorted_tuples.bin", 'ab')

    while True:

        line = file.readline()
        type = line[:13]

        if not line:
            break

        if type == 'review/text: ':
            doc_id += 1
            line = str.rstrip(line)
            line = line[13:]
            line = line.lower()
            line = re.sub('[\W\_]', ' ', line) #remove special characters
            review_words = line.split() # build a list
            bad_chars = 0
            for word in review_words:
                word_index = Binary_Search(index_str,position_ptrs,word) #word id
                if word_index == -1:
                    bad_chars += 1
                else:
                    if len(nums_list) > BUFFER_SIZE: #write to file the buffersized list
                        buf = struct.pack('%si' % len(nums_list), *nums_list)
                        pairs_file.write(buf)
                        nums_list = []
                    nums_list.append(word_index)
                    nums_list.append(doc_id)
                    list_size += 2
                    total_tokens += 1

                # we used a temp parsed review file that stores the text of each review.
                # after we've built the index, we don't need the text anymore.
                # We will create a new text file, copy all data except replacing the text with number of words in the text.

    if len(nums_list) != 0:
        buf = struct.pack('%si' % len(nums_list), *nums_list)
        pairs_file.write(buf)

    pad_with_zeros(list_size,pairs_file)

    pairs_file.close()
    #returns the total words in the reviews
    return total_tokens

#pad the unsorted list with zeros until the list will be at the size of power of 2
def pad_with_zeros(list_size,file):
    zero = 0
    zeros_list = []
    pow_2 = int(math.log(list_size,2))
    is_pow_2 = list_size & (list_size - 1)

    if is_pow_2 == 0:
        return

    zero_to_add = math.pow(2,pow_2+1) #- size
    if list_size < BUFFER_SIZE:
        zero_to_add = BUFFER_SIZE

    count_zeros = 0

    while list_size < zero_to_add:

        if len(zeros_list) > BUFFER_SIZE:
            buf = struct.pack('%si' % len(zeros_list), *zeros_list)
            file.write(buf)
            zeros_list = []

        zeros_list.append(zero)
        count_zeros+=1
        list_size += 1

    if len(zeros_list) != 0:
        buf = struct.pack('%si' % len(zeros_list), *zeros_list)
        file.write(buf)


