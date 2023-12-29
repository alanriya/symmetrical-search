import xml 
import logging
import mwxml
import glob 
import re
from itertools import chain
import nltk
import pdb
from nltk.stem import WordNetLemmatizer, PorterStemmer
import json

class WikiXmlProcessor:
    '''
    class for processing text data in xml
    '''
    def __init__(self):
        self.stopwords = self.getStopWords()
    
    @staticmethod
    def basicParse():
        pass
    
    def getStopWords(self):
        stop_words_list = []
        with open('stopwords.txt', 'r') as f:
            lines = f.readlines()
            stop_words_list = [line for line in lines]
        return stop_words_list

def get_stop_words():
    stop_words_list = []
    with open('stopwords.txt', 'r') as f:
        lines = f.readlines()
        stop_words_list = [line.replace('\n', '').strip() for line in lines]
    return stop_words_list
    
STOP_WORDS_LIST = get_stop_words()

categoryPattern = r'\[\[category:(.*?)\]\]'
infoboxPattern ="{{Infobox((.|\n)*?)}}"
pattern = re.compile("[^a-zA-Z0-9]")
externalLinksPattern = r'==External links==\n[\s\S]*?\n\n'
referencesPattern = r'== ?references ?==(.*?)\n\n' #r'==References==\n[\s\S]*?\n\n'
removeLinksPattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',re.DOTALL)
removeSymbolsPattern = r"[~`!@#$%-^*+{\[}\]\|\\<>/?]"

def remove_unneccessary_text(text):
    removeLinksPattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',re.DOTALL)
    # to lowercase 
    text = text.lower()
    text = re.sub(removeLinksPattern, ' ', text)
    text = re.sub(r'{\|(.*?)\|}', ' ', text, flags = re.DOTALL)
    text = re.sub(r'{{v?cite(.*?)}}', ' ', text, flags = re.DOTALL)
    text = re.sub(r'<(.*?)>', ' ', text, flags = re.DOTALL)
    text = re.sub(r"'", '', text)
    text = re.sub(r"reflist", '', text)
    text = text.replace("|", " ").replace("/", " ").replace("(", "").replace(")", "")
    return text

def process_category_data(data):
    categories = re.findall(categoryPattern, data, flags=re.MULTILINE | re.IGNORECASE)
    categories = ' '.join(categories)
    categories = categories.replace("|", " ").replace("/", " ").replace("(", "").replace(")", "")
    return categories

def process_external_links_data(data):
    links = re.findall(externalLinksPattern, data, flags= re.IGNORECASE)
    links = " ".join(links)
    links = links[20:]
    links = re.sub('[|]', ' ', links)
    links = re.sub('[^a-zA-Z ]', ' ', links)
    links = re.sub('\n', '', links)
    links = links.replace("|", " ").replace("/", " ").replace("(", "").replace(")", "")
    return links

def process_info_box_data(data):
    infobox_data = []
    infobox = re.findall(r'{{infobox((.|\n)*?)}}', data, flags=re.IGNORECASE)
    if(len(infobox)<=15):
        infobox = list(chain(*infobox))
        #print(len(infobox), infobox)
        for line in infobox:
            tokens = re.findall(r'=(.*?)\|',line,re.DOTALL)
            #print(tokens)
            infobox_data.extend(tokens)
    infobox_data = ' '.join(infobox_data)
    infobox_data = re.sub(removeSymbolsPattern, ' ', infobox_data)
    infobox_data = re.sub('\n', '', infobox_data)
    infobox_data = infobox_data.replace("|", " ").replace("/", " ").replace("(", "").replace(")", "")
    return infobox_data

def process_references_data(text):
    references = re.findall(referencesPattern, text, flags=re.DOTALL | re.MULTILINE | re.IGNORECASE)
    references = ' '.join(references)
    references = re.sub(removeSymbolsPattern, ' ', references)
    references = re.sub('\n', '', references)
    references = references.replace("|", " ").replace("/", " ").replace("(", "").replace(")", "")
    return references

def process_body_data(data):
    body = re.findall(r'== ?[a-z]+ ?==\n(.*?)\n', data)
    data = " ".join(body)
    data = re.sub(removeSymbolsPattern, " ", data)
    data = re.sub('\n', '', data)
    data = re.sub('|', ' ', data)
    data = data.replace("|", " ").replace("/", " ").replace("(", "").replace(")", "")
    return data

def remove_stop_word(content):
    removed_stopword_content = []
    for word in content:
        if word not in STOP_WORDS_LIST:
            removed_stopword_content.append(word)
    return removed_stopword_content

def lemmatized_content(content): 
    stemmed_words = []
    try:
        lemmatizer = WordNetLemmatizer()
    except:
        logging.info("download wordnet")
        nltk.download('wordnet')
        lemmatizer = WordNetLemmatizer()
    finally:
        for word in content:
            stemmed_words.append(lemmatizer.lemmatize(word)) 
    return stemmed_words

def create_inverted_index(content_list, page_id):
    for word in content_list:
        if word == '':
            continue
        if word not in inverted_index:
            inverted_index[word] = {}
        if page_id not in inverted_index[word]:
            inverted_index[word][page_id] = 1
        else:
            inverted_index[word][page_id] += 1
    
def save_inverted_index(index):
    try:
        os.mkdir('indices')
    except:
        pass
    with open('indices/indices_latest.json', 'w') as out:
        json.dump(index, out)

def save_page_detail(page_index):
    try:
        os.mkdir('pages')
    except:
        pass
    with open('pages/pages_latest.json', 'w') as out:
        json.dump(page_index, out)

if __name__ == "__main__":
    inverted_index = {}
    page_index = {}
    import sys
    import os
    root_directory = "C:/Users/alanl/pinnacle/big_data_search_engine_knowledge"
    if len(sys.argv) < 2:
        logging.error("Did not specify the directory containing the data to start creating the index.")
        sys.exit(1)

    def process_dump(dump, path):
        for page in dump:
            for revision in page:
                yield page.id, page.title, revision.id, revision.timestamp, revision.text

    data_directory = fr"{root_directory}/{sys.argv[1]}"
    for directory, folder, files in os.walk(data_directory, topdown=False): 
        for file in files:
            print(f"processing {file}")
            paths = glob.glob(f"{data_directory}/{file}")
            for page_id, page_title, rev_id, rev_timestamp, rev_text in mwxml.map(process_dump, paths):
                page_index[page_id] = page_title
                rev_text = remove_unneccessary_text(rev_text)
                page_title =  remove_unneccessary_text(page_title)
                # get category
                categories = process_category_data(rev_text)
                # get references
                references = process_references_data(rev_text)
                # get info box
                info_box = process_info_box_data(rev_text)
                # get links
                links = process_external_links_data(rev_text)
                # get content
                content = process_body_data(rev_text)
                content_list = f"{page_title} {categories} {references} {info_box} {links} {content}".strip().split(' ')
                # lemmatized content
                lemmatize_content_list = lemmatized_content(content_list)
                # remove stop word
                cleaned_content_list = remove_stop_word(lemmatize_content_list)
                # process 
                create_inverted_index(cleaned_content_list, page_id)
                # print(f'completed {page_id}- {page_title}')
            print(f"processed {file}")
    # write dict to json
    save_inverted_index(inverted_index)
    save_page_detail(page_index)

    

    # 1) also store the page_id and also the clean content
    # 2) store term: [{page_id, frequency}, {}, ...]
    # 3) after indexing, implement lucene's practical scoring which is summation. 
    