"""
Program to provide generic parsing for all files in a user-specified directory.
The program assumes the input files have been scrubbed,
  i.e., HTML, ASCII-encoded binary, and any other embedded document structures that are not
  intended to be analyzed have been deleted from the file.

Dependencies:
    Python:  MOD_Load_MasterDictionary_vxxxx.py
    Data:    LoughranMcDonald_MasterDictionary_XXXX.csv

The program outputs:
   1.  File name
   2.  File size (in bytes)
   3.  Number of words (based on LM_MasterDictionary
   4.  Proportion of positive words (use with care - see LM, JAR 2016)
   5.  Proportion of negative words
   6.  Proportion of uncertainty words
   7.  Proportion of litigious words
   8.  Proportion of modal-strong words
   9.  Proportion of modal-weak words
  10.  Proportion of constraining words (see Bodnaruk, Loughran and McDonald, JFQA 2015)
  11.  Number of alphanumeric characters (a-z, A-Z)
  12.  Number of digits (0-9)
  13.  Number of numbers (collections of digits)
  14.  Average number of syllables
  15.  Average word length
  16.  Vocabulary (see Loughran-McDonald, JF, 2015)

  ND-SRAF
  McDonald 201606 : updated 201803; 202107; 202201
"""
import os
import csv
import glob
import re
import string
import sys
import datetime as dt
import MOD_Load_MasterDictionary_v2022 as LM






os.chdir(r'E:\Personal projects\Website_parser_and_sentiment_analyser\data')
OUTPUT_FILE = r'E:\Personal projects\Website_parser_and_sentiment_analyser\sample_output_file.csv'

with open( OUTPUT_FILE, 'a', newline='') as csv_file:
        wr = csv.writer(csv_file)
        wr.writerow(['URL', 'file size', 'number of words', 'negative score', 'positive score',
                'Polarity score', 'subjectivity score', 'average word length', '% complex words','avg sentence length','Fog index',
                'Avg words/sentence','word count', 'average syllables / word', 'number of pronouns', '# of alphabetic', '# of digits', '# of numbers'])
                    
os.chdir(r'E:\Personal projects\Website_parser_and_sentiment_analyser/data')
for filename in os.listdir(os.getcwd()):
       with open(os.path.join(os.getcwd(), filename), 'a'):
        #    print(filename)
        #    print(os.path.join(os.getcwd(), filename))
        #    print(os.getcwd())
        # User defined directory for files to be parsed
            TARGET_FILES = filename
            # User defined file pointer to LM dictionary
            MASTER_DICTIONARY_FILE = r'Loughran-McDonald_MasterDictionary_1993-2021.csv'
            # User defined output file
            OUTPUT_FILE = r'E:\Personal projects\Website_parser_and_sentiment_analyser\sample_output_file.csv'
            # Setup output
            OUTPUT_FIELDS = ['URL', 'file size', 'number of words', 'negative score', 'positive score',
                            'Polarity score', 'subjectivity score', 'average word length', '% complex words','avg sentence length','Fog index',
                            'Avg words / sentence','word count', 'average syllables / word', 'number of pronouns', '# of alphabetic', '# of digits',
                            '# of numbers']

            lm_dictionary = LM.load_masterdictionary(MASTER_DICTIONARY_FILE, print_flag=True)


            def main():

                # f_out = open(OUTPUT_FILE, 'w')
                # wr = csv.writer(f_out,'a', newline='') as csv_file:
                #     wr.writerow(OUTPUT_FIELDS)
                with open( OUTPUT_FILE, 'a', newline='') as csv_file:
                    wr = csv.writer(csv_file)

                    file_list = glob.glob(TARGET_FILES)
                    n_files = 0
                    for file in file_list:
                        n_files += 1
                        print(f'{n_files:,} : {file}')
                        with open(file, 'r', encoding='UTF-8', errors='ignore', newline='') as f_in:
                            doc = f_in.read()
                        doc = doc.upper()      # for this parse caps aren't informative so shift

                        output_data = get_data(doc)
                        output_data[0] = 'https://www.huffpost.com/entry/' + file
                        output_data[1] = len(doc)
                        # wr.writerow(output_data)
                        if n_files == 3: break
                    wr.writerow(output_data)
                
            def get_data(doc):

                vdictionary = dict()
                _odata = [0] * len(OUTPUT_FIELDS)
                total_syllables = 0
                word_length = 0
                complex_words = 0
                sentences = len(re.split(r'[.!?]+', doc)) #splitting on sentence markers
                pronounRegex = re.compile(r'\b(I|we|my|ours|(?-i:us))\b',re.I) #regex for pronouns i, we, my, ours, uss
                pronouns = pronounRegex.findall(doc)
                
                tokens = re.findall('\w+', doc)  # Note that \w+ splits hyphenated words
                for token in tokens:
                    if not token.isdigit() and len(token) > 1 and token in lm_dictionary:
                        _odata[2] += 1  # word count
                        word_length += len(token)
                        if token not in vdictionary:
                            vdictionary[token] = 1
                        if lm_dictionary[token].negative: _odata[3] += 1
                        if lm_dictionary[token].positive: _odata[4] += 1
                        total_syllables += lm_dictionary[token].syllables
                        if total_syllables>2:
                            complex_words += 1

                _odata[5]  = ((_odata[4]-_odata[3])/(_odata[4] + _odata[3] + 0.000001)) # polarity score
                
                _odata[6] = ((_odata[4]+_odata[3])/_odata[2]+0.000001) # subjectivity score
                
                _odata[7] = word_length / _odata[2] # average word length
                
                _odata[8] = ((complex_words/_odata[2]) * (1/100)) # percentage of complex words
                
                _odata[9] = _odata[2] / sentences  # avg of sentences length 
                
                _odata[10] = 0.4*(_odata[9] + _odata[8]) # fog index
                
                _odata[11] = _odata[2] / _odata[9] # avg of words per sentence
                
                _odata[12] = _odata[2] # word count
                
                _odata[13] = total_syllables / _odata[2] # average syllables per word
                
                _odata[14] = len(pronouns) # number of pronouns
                
                _odata[15] = len(re.findall('[A-Z]', doc)) # no of alphabetic characters
                
                _odata[16] = len(re.findall('[0-9]', doc))  # no of digits
                
                
                
                
                # drop punctuation within numbers for number count
                doc = re.sub('(?!=[0-9])(\.|,)(?=[0-9])', '', doc)
                doc = doc.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))
                _odata[17] = len(re.findall(r'\b[-+\(]?[$€£]?[-+(]?\d+\)?\b', doc)) # number of numbers
                
                
                
                
                # Convert counts to %
                # for i in range(3, 9 + 1):
                    # _odata[i] = (_odata[i] / _odata[2]) * 100
                # Vocabulary
                    
                return _odata


            if __name__ == '__main__':
                start = dt.datetime.now()
                print(f'\n\n{start.strftime("%c")}\nPROGRAM NAME: {sys.argv[0]}\n')
                main()
                print(f'\n\nRuntime: {(dt.datetime.now()-start)}')
                print(f'\nNormal termination.\n{dt.datetime.now().strftime("%c")}\n')