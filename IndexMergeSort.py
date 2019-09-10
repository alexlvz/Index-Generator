import os
import struct

BUFFER_SIZE = 8388608 

#reads buffer sized data from the unsorted file and generates a list from it
def create_list_of_nums(bin_file):

    list_of_nums = []
    buf = bin_file.read(BUFFER_SIZE)
    if not buf:
        return "done",list_of_nums

    fmt = '%si' % (len(buf) // 4)
    list_of_nums = list(struct.unpack(fmt, buf))
    return "not done", list_of_nums

#creates a tuples list form a regular list
def list_to_couples_of_tuples(l):
    list_of_couples = []
    for i in range(len(l)):
        if i%2==0:
            tmp_tuple=(l[i], l[i + 1])
            list_of_couples.append(tmp_tuple)
    return list_of_couples

#this will write buffer_sized data to small files in sorted way
def write_to_file_in_bin(dir,file_name,list,to_sort):
    tuples_list = list_to_couples_of_tuples(list)

    if to_sort:
        tuples_list.sort()
    tuples_list = [x for item in tuples_list for x in item]

    bin_file = open(dir+file_name + '.bin', 'ab')
    buf = struct.pack('%si' % len(tuples_list), *tuples_list)
    bin_file.write(buf)
    bin_file.close()

#gets list of tuples from file
def get_tupples_from_file(file):
    list_of_tupples =[]
    status, list_data = create_list_of_nums(file)
    if status == "done":
        print("error")
    else:
        list_of_tupples = list_to_couples_of_tuples(list_data)

    return list_of_tupples

#merge two sorted tuples lists into one sorted list of tuples
def merge(res_file,file_left,file_right,num_of_part):
    pos_left = 0
    pos_right = 0

    tupples_res=[]

    tupples_left = get_tupples_from_file(file_left)
    tupples_right= get_tupples_from_file(file_right)
    left_part_read = 1
    right_part_read = 1
    size_left = len(tupples_left)
    size_right = len(tupples_right)

    while left_part_read <= num_of_part and right_part_read <= num_of_part:

        if len(tupples_res) > BUFFER_SIZE*2: # write to res file only if buffer size is reached
            tupples_res = [x for item in tupples_res for x in item]
            buf = struct.pack('%si' % len(tupples_res), *tupples_res)
            res_file.write(buf)
            tupples_res = []

        if pos_left == size_left and pos_right == size_right and left_part_read == num_of_part and right_part_read == num_of_part:
            break

        if pos_left == size_left:
            if left_part_read == num_of_part:
                tupples_res.append(tupples_right[pos_right])
                pos_right += 1
            else:
                tupples_left = get_tupples_from_file(file_left)
                pos_left = 0
                left_part_read+=1
        elif pos_right == size_right:
            if right_part_read == num_of_part:
                tupples_res.append(tupples_left[pos_left])
                pos_left += 1
            else:
                tupples_right = get_tupples_from_file(file_right)
                pos_right = 0
                right_part_read+=1
        else:
            if tupples_left[pos_left] < tupples_right[pos_right]:
                tupples_res.append(tupples_left[pos_left])
                pos_left+=1
            else:
                tupples_res.append(tupples_right[pos_right])
                pos_right+=1
    return tupples_res

# breaks the unsorted tuples file into buffer sized sorted files
def create_buffer_sized_files(dir,bin_file):
    part_file_name = 0

    while True:

        status, num_list = create_list_of_nums(bin_file)
        if status == "done":
            break
        write_to_file_in_bin(dir,str(part_file_name), num_list,True)
        part_file_name += 1
    return part_file_name

#main function that generates the sorted tuples file
def generate_sorted_tuples(dir,num_of_files):
    num_of_parts = 1
    next_file_name = 0

    while num_of_files != 1:
        for i in range(num_of_files):

            if i % 2 == 0:
                left_file = open(dir+str(i) + ".bin", "rb")
                right_file = open(dir+str(i + 1) + ".bin", "rb")
                res_file = open(dir+"temp.bin", "ab")
                buf_res = merge(res_file,left_file, right_file, num_of_parts)
                left_file.close()
                right_file.close()
                os.remove(dir+str(i) + ".bin")
                os.remove(dir+str(i + 1) + ".bin")
                buf_res = [x for item in buf_res for x in item] # from tuples to list
                if len(buf_res) != 0:
                    buf = struct.pack('%si' % len(buf_res), *buf_res)
                    res_file.write(buf)
                res_file.close()
                os.rename(dir + "temp.bin", dir + str(next_file_name)+".bin")
                next_file_name += 1

        next_file_name = 0
        num_of_files = int(num_of_files / 2)
        num_of_parts *= 2

