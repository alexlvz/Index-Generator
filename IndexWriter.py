import ReviewsParsing
import os
import data_encoder_decoder
import IndexMergeSort
import struct
import IndexObject
import shutil
import pickle

BUFFER_SIZE = 8388608


class IndexWriter():

    #generates the posting list file for all the words in the index. it uses the sorted tuples file
    def generateDocFreqs(dir, index_dictionary):
        sorted_tuples_file = open(dir + "0.bin", "rb")
        bin_doc_pos = 0
        doc_freq = []
        prev_doc_id = -1
        prev_word_id = -1
        total_byte_list = []
        flag_end = False
        while True:

            #we read BUFFER sized lists each time
            bin_num_list = sorted_tuples_file.read(BUFFER_SIZE)

            if not bin_num_list:
                flag_end = True
                word_id = -1
                doc_id = -1
            else:
                num_list = list(struct.unpack('%si' % (len(bin_num_list) // 4), bin_num_list)) # loads the list from the buffer

            for i in range(0, len(num_list) - 1,2):

                if bin_num_list:
                    word_id = num_list[i]
                    doc_id = num_list[i + 1]

                if doc_id == 0:
                    continue

                if prev_word_id == -1 and prev_doc_id == -1:
                    doc_freq.append(doc_id)
                    doc_freq.append(1)

                elif prev_word_id == word_id and prev_doc_id == doc_id:
                    doc_freq[-1] = doc_freq[-1] + 1

                elif prev_word_id == word_id:
                    doc_freq.append(doc_id)
                    doc_freq.append(1)

                else:
                    if len(doc_freq) % 2 == 0:
                        index_dictionary.word_freq.append(int(len(doc_freq) / 2))
                    else:
                        index_dictionary.word_freq.append(int((len(doc_freq) / 2) + 1))
                    # decoding the list to compressed binary data
                    doc_freq = data_encoder_decoder.build_differential_list(doc_freq, encode=True)
                    bin_doc_freq, num_bytes = data_encoder_decoder.div_four_in_group(doc_freq)
                    index_dictionary.bin_file_pos.append(bin_doc_pos)
                    bin_doc_pos += num_bytes
                    bit_strings = [bin_doc_freq[i:i + 8] for i in range(0, len(bin_doc_freq), 8)]
                    byte_list = [int(b, 2) for b in bit_strings]
                    total_byte_list += byte_list

                    if len(total_byte_list) > BUFFER_SIZE:
                        try:
                            with open(dir + 'doc_freq.bin', 'ab') as f:
                                f.write(bytearray(total_byte_list))
                        except:
                            print("Error in opening doc_freq.bin file")
                        del total_byte_list
                        total_byte_list = []

                    doc_freq = []

                    # add the current tupple
                    doc_freq.append(doc_id)
                    doc_freq.append(1)

                prev_word_id = word_id
                prev_doc_id = doc_id

                if flag_end:
                    break
            if flag_end:
                break

        if len(total_byte_list) > 0:
            try:
                with open(dir + 'doc_freq.bin', 'ab') as f:
                    f.write(bytearray(total_byte_list))
            except:
                print("Error in opening doc_freq.bin file")


    def write(self, inputFile, dir):

        if dir[-1] != '/':
            dir += '/'

        # creates a directory for the index files
        try:
            os.makedirs(dir)
        except FileExistsError:
            pass

        file = open(inputFile, 'r', errors='ignore')
        #first traverse of the raw data - we build the dictionary
        position_ptrs, index_str, num_of_reviews = ReviewsParsing.raw_review_parser(dir, file)
        index_dictionary = IndexObject.IndexObject()
        index_dictionary.dictionary_string += index_str
        index_dictionary.position_ptr = position_ptrs.copy()
        index_dictionary.num_of_reviews = num_of_reviews
        file.close()
        file = open(inputFile, 'r')
        #second traverse of the raw data. building the unsorted tuples list
        total_tokens = ReviewsParsing.build_tuples(dir, file, index_str, position_ptrs)
        index_dictionary.num_of_words = total_tokens
        file.close()
        bin_file = open(dir + "unsorted_tuples.bin", "rb")
        # sorting the unsorted tuples list
        num_of_files = IndexMergeSort.create_buffer_sized_files(dir, bin_file)
        bin_file.close()
        IndexMergeSort.generate_sorted_tuples(dir, num_of_files)
        #generating the posting lists compressed binary file
        IndexWriter.generateDocFreqs(dir, index_dictionary)
        #saving the dictionary to file
        try:
            with open(dir + "index_dictionary.pkl", "wb") as output:
                pickle.dump(index_dictionary, output, pickle.HIGHEST_PROTOCOL)
        except:
            print("Error in opening index_dictionary.pkl file")

        os.remove(dir + "0.bin")
        os.remove(dir + "unsorted_tuples.bin")
    #removes the index
    def removeIndex(self, dir):

        if dir[-1] != '/':
            dir += '/'

        shutil.rmtree(dir, ignore_errors=True)
