Use 100.txt as small input file.
First read the instructions :)

This program parses a given reviews file and builds an index for it.
This index will be used later on to make queries on the data. 
Actually this is the fundementals for a search engine. 

Program files:

IndexWriter.py - Class that is implemented as requested in the project
IndexReader.py - Class that is implemented as requested in the project
indexObject.py - Class that holds the dictionary object that is part of the index and will load into the ram
ReviewsParsing.py - Class with text parsing functions that is used to parse the input file and return relevant parsed data to the writer class
data_encoder_decoder.py - binary encoder/decoder for the binary file which is part of the index
IndexMergeSort.py - Generates from unsorted file of tuples a sorted one

*** IF THE PROGRAM CRACHES ON MEMORY ERROR, CHANGE THE BUFFER SIZE TO 4194304 AT THE BELOW FILES:***
IndexWriter.py 
ReviewsParsing.py 
data_encoder_decoder.py 
THIS PROGRAM IS WRITTEN TO RUN ON HIGH END PC THAT IS FOUND AT THE COLLEGE LABORATORY
*** =============================================================================================***
How to compile and use the program:

1. Put all project files in one folder.
2. Create a main.py file, in this file, import SlowIndexWriter and indexReader.
3. Create an instance of InderWrtier with a dir where the index files will be located and with path to the input file. dir can't be a folder where the windows in installed. for example NOT C:\
4. Create an instance of indexReader with a dir where the index files will be located. dir can't be a folder where the windows in installed. for example NOT C:\
5. If you need to compile before running - compile with a standard mode
   we used PyCharm for development so that it did the compilation process automatically
5. After compilation, run diffrent functions of the inderReader, as described in its class.
   Make sure to print the output or print the variable that was recieved from the functions.
6. To delete the index files, run the corresponding function in the SlowInderWriter class

E n j o y !