# This file encoded and decoder the lists of docId and frequency
# (The encoding method is described in the analysis.pdf)

# Checks how many bytes the number needs
# Assumption: num is positive integer
def number_bytes(num):
    arr_limit = [4294967295, 16777215, 65535, 255, 0]
    if num>arr_limit[0]:
        return -1;
    for i in range(1,len(arr_limit)):
        if num>arr_limit[i]:
            return 4-i+1
    return 1 # for num=0


# creater a string of binary number from integer number
def num_to_binary_str(num):
    bin_num = str(bin(num))
    bin_num = bin_num[2:]
    return bin_num

# get num bytes and converts to String
def order_group_data(num_bytes):
    num_bytes=num_bytes-1
    num_bytes_str = num_to_binary_str(num_bytes)
    num_bytes_str=num_bytes_str.zfill(2)
    return num_bytes_str


# input: list of 4 couple of doc_id and freq
# output: string of binary number (The encoding method is described in the analysis.pdf)
def build_group(four_docs):
    group_data = ""
    buffer_4_docs = ""

    for i in range(len(four_docs)):
        num = four_docs[i]
        if i%2==1:
            val = EncodeNumber(num)
            buffer_4_docs+=val
            continue
        num_bytes = number_bytes(num)
        if num_bytes == -1:
            print('Maximum exceeded')
        num_bits = num_bytes * 8
        bin_num = num_to_binary_str(num)

        padding_num = str(bin_num).zfill(num_bits)
        buffer_4_docs += padding_num
        group_data += order_group_data(num_bytes)
    if len(group_data)<8:
        group_data = group_data.ljust(8,'0')
    buffer_group=group_data+buffer_4_docs
    return buffer_group

# input: list of couple: doc_id and freq
# output: list of lists, each list has four couple of doc_id and freq
def div_four_in_group(list_docs):
    docs_in_group = 4
    docs_in_group *=2 #with couple docs and freq
    buffer_all_docs = ""

    while list_docs!=[]:
        list_to_build = list_docs[:docs_in_group]
        group_varint=build_group(list_to_build)
        list_docs = list_docs[docs_in_group:]
        buffer_all_docs+=group_varint
    num_of_bytes_to_this_list = int(len(buffer_all_docs)/8)
    return buffer_all_docs,num_of_bytes_to_this_list

# input: list of couple: doc_id and freq
# output: List of differences between file id (Frequency numbers do not change)
def build_differential_list(list_doc,encode):

    list_differential=[list_doc[0]]
    num_loop = len(list_doc)
    for i in range(1,num_loop):
        if i%2==0:
            if encode ==True:
                dif = list_doc[i] - list_doc[i - 2]
            else:
                dif = list_doc[i] + list_differential[- 2]
        else:
            dif = list_doc[i]
        list_differential.append(dif)

    return list_differential


# decode binary number to integer
def decode_bin_to_int(bin_num):
    if(not bin_num):
        print("error: bin num is empty")

    int_num = int(bin_num.decode(),2)
    return int_num


#init function for Recursive function
def EncodeNumber(n):
    return RecEncodeNumber(n, "","1")

# encoded number (The encoding method is described in the analysis.pdf)
def RecEncodeNumber(n,str_binery,seg_bit):
    rem =n% 128
    temp_bin = str(bin(rem)[2:])
    temp_bin = str(temp_bin).zfill(7)
    str_binery = seg_bit + temp_bin+str_binery
    if n < 128:
        return str_binery

    return RecEncodeNumber(int(n/128), str_binery,"0")


#  input: binary number
#  output: decode the number to integer
def decodeNumber(binary_num_with_sig,start):
    int_num=0
    while True:
        byte_num = binary_num_with_sig[start:start+8]
        binary_num=byte_num[1:]# 7 last bits in the byte
        int_num += decode_bin_to_int(binary_num)#int(binary_num.decode(),2)
        seg_bit=byte_num[:1]# the first bit in the byte
        if int(seg_bit)==1:
            return int_num,start+8
        int_num*=128
        start+=8


# decode sring of binury num, to list of 4 couple of: doc_id and freq
def decode_data_on_one_group(bin_data_group):
    data_group = []
    for i in range(0, 8, 2):
        data_one_doc = bin_data_group[i:i+2]
        data_group.append(decode_bin_to_int(data_one_doc))
    return data_group


# create a list of couple: docId and freq from the binary code
def decode_all(binary_data):

    last_read = 0
    docs_and_freq = []

    # loop run about groups of four (or less in the last group)
    while last_read+8 < len(binary_data):
        bin_data_group = binary_data[last_read:last_read + 8]# decode data of one group
        last_read+=8
        data_group = decode_data_on_one_group(bin_data_group)
        for index_group in range(4):#max enter this loop - 4 times
            if last_read+8 > len(binary_data):
                break
            doc_id=0

            # Runs on all Bytes that the document number needs - max enter this loop - 4 times
            for num_byte_of_doc in range(data_group[index_group]+1):
                doc_id*=256
                doc_id_bin = binary_data[last_read:last_read + 8]
                last_read += 8
                doc_id+=decode_bin_to_int(doc_id_bin)
            freq_for_doc,last_read=decodeNumber(binary_data,last_read)
            docs_and_freq.append(doc_id)
            docs_and_freq.append(freq_for_doc)

    docs_and_freq = build_differential_list(docs_and_freq,encode=False)
    return docs_and_freq