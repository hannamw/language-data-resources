import argparse
import re
import random 
import pprint 
from collections import Counter

from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from gutenberg._domain_model.exceptions import UnknownDownloadUriException

def download_spanish_texts(max_words=1000000, output_file="spanish_corpus.txt", \
                           spanish_book_number_file="spanish_book_numbers.txt", shuffle=False):
    global total_words
    total_words = 0
    books_downloaded = 0
    word_counts = Counter()
    
    def format_count(word):
        global total_words 
        total_words += 1
        return re.sub(r'\W+', '', word.lower())
    
    # get the numbers corresponding to each of Gutenberg's spanish books
    with open(spanish_book_number_file, 'r') as f:
        spanish_book_numbers = list(set([int(line.strip()) for line in f.readlines()]))
        
    if shuffle:
        random.shuffle(spanish_book_numbers)
        
    completed = False
    
    print("initiating corpus download and compilation")
    
    # clear this file
    open(output_file, 'w').close()
    
    for index in spanish_book_numbers:
        if total_words >= max_words:
            completed = True
            break
            
        try:
            new_text = strip_headers(load_etext(index)).strip()
        except UnknownDownloadUriException:
            continue
        else:
            word_counts.update(format_count(word) for word in new_text.split())
            
            with open(output_file, 'a', encoding='utf-8') as g:
                g.write(new_text)
                g.write('\n')
                
            total_words -= word_counts[""]
            word_counts[""] = 0
            
            books_downloaded += 1
            
            print("Corpus collection: %.0f percent complete" % min(total_words * 100 / max_words, 100.0))
    
    if not completed:
        raise ValueError("You wanted to collect %d words, but there are only (around) %d total words in \
                          all of Project Gutenberg's Spanish books—sorry!" % (max_words, total_words))
                          
    print("Final corpus length: %d; num books: %d" % (total_words, books_downloaded))
    print("The 50 most common words (excluding punctuation and (upper/lower)case) are:")
    most_common = [word for word, _ in word_counts.most_common(50)]
    for i, word in enumerate(most_common):
        if i % 5 == 0:
            print()
        print(word, end='\t\t')
                          
                          
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--words', type=int, default=1000000, help='minimum corpus length')
    parser.add_argument('--output', type=str, default="spanish_corpus.txt", help='corpus output file')
    parser.add_argument('--indices', type=str, default="spanish_book_numbers.txt", help='file containing \
                                                                              indices / IDs of gutenberg books')
    parser.add_argument('--random', action='store_true', help='get text from random books (instead of taking\
                                                               from the same books every time')
    
    args = parser.parse_args()
    
    download_spanish_texts(args.words, args.output, args.indices, args.random)