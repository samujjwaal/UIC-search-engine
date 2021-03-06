# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# load dependency libraries
import math
import os
import copy
import re
from nltk.corpus import stopwords
from collections import Counter
from nltk.stem import PorterStemmer
import pickle

# +
# number of webpages indexed
N = 6001

# extracting english stop words
stop_words = stopwords.words('english')

# Initializing Porter Stemmer object
st = PorterStemmer()

# folder to store pickel files
pickle_folder = "../PickleFiles/"
os.makedirs(pickle_folder, exist_ok=True)
# -

webpages_idf = {}
max_freq = {}
webpages_tf_idf = {}

# +
with open(pickle_folder + '6000_inverted_index.pickle', 'rb') as f:
    inverted_index = pickle.load(f)                   # rename

with open(pickle_folder + '6000_webpages_tokens.pickle', 'rb') as f:
    webpages_tokens = pickle.load(f)                   # rename

with open(pickle_folder + '6000_pages_crawled.pickle', 'rb') as f:
    urls = pickle.load(f)                   # rename


# +
# webpages_idf = {}

# function for computing idf of each token in the collection of webpages

def calc_idf(inverted_index):
    # df = {}
    idf = {}

    for key in inverted_index.keys():
        df = len(inverted_index[key].keys())
        idf[key] = math.log2(N/df)
    
    return idf
    
# webpages_idf = calc_idf(inverted_index) 


# +
# max_freq = {}

# for page in webpages_tokens:
#     most_freq_token = mode(webpages_tokens[page])
#     max_freq[page] = inverted_index[most_freq_token][page]

# +
# max_freq = {}

# for page in webpages_tokens:
#     max_freq[page] = Counter(webpages_tokens[page]).most_common(1)[0][1]

# +
# webpages_tf_idf = {}

# function to compute tf-idf of each token

def calc_tfidf(inverted_index):
    
    # making a temporary copy of the inverted index
    tf_idf = copy.deepcopy(inverted_index)
    
    for token in tf_idf:
        for page in tf_idf[token]:
            tf = tf_idf[token][page] / max_freq[page]
            tf_idf[token][page] = tf * webpages_idf[token]
    
    return tf_idf

# webpages_tf_idf = calc_tfidf(inverted_index)


# -

def calc_doc_len(doc, doc_tokens):
    doc_len = 0
    
    for token in set(doc_tokens):
        
        doc_len += webpages_tf_idf[token][doc] ** 2
    
    doc_len = math.sqrt(doc_len)
    
    return doc_len


# +
# calculate doc lengths for each fetched webpage

def doc_len_pages(list_of_tokens):
    
    doc_lens = {}
    
    for page in list_of_tokens:
        
#         print(page)
        doc_lens[page] = calc_doc_len(page, list_of_tokens[page])
        
    return doc_lens


# +
# doc_len_pages(webpages_tokens)
# webpages_lens = doc_len_pages(webpages_tokens)
# webpages_lens

# +
# count = 0
# t = []
# for token in inverted_index:
# #     print(inverted_index[token]['0'])
#     if c:= inverted_index[token].get('0'):
# #         count += 1
#         count += c 
#         t.append(token)

# # count
# # t

# +
# set(t) == set(webpages_tokens['0'])

# +
# Function to compute cosine similarity

def calc_cos_sim_scores(query, doc_lens):
    similarity_scores = {}
    query_len = 0
    query_weights = {}
    
    query_dict = Counter(query)
    
    
    for token in query_dict.keys():
        token_tf = query_dict[token] / query_dict.most_common(1)[0][1]
        query_weights[token] = token_tf * webpages_idf.get(token,0)
        query_len += query_weights[token] ** 2
    
    query_len = math.sqrt(query_len)
#     print(query_len,query_weights)

    
    for token in query:
        token_weight = query_weights.get(token)
#         print(token_weight)
        
        if token_weight:
#             print(token_weight)
            for page in webpages_tf_idf[token].keys():
                similarity_scores[page] = similarity_scores.get(page,0) + (webpages_tf_idf[token][page] * token_weight)
#                 print(tf_idf[token][page], token_weight)
    
#     print(similarity_scores)
    
    for page in similarity_scores:
        similarity_scores[page] = similarity_scores[page] / (doc_lens[page] * query_len)
        
#     print(similarity_scores)
    return similarity_scores


# +
# function to tokenize query text

def tokenize_query(query_text):
    text = query_text.lower()
    text = re.sub('[^a-z]+', ' ', text)
    tokens = text.split()
    clean_stem_tokens = [
            st.stem(token) for token in tokens 
            if (token not in stop_words and st.stem(token) not in stop_words) and len(st.stem(token))>2
        ]
    return clean_stem_tokens


# +
# query_text = query.lower()
# query_text = re.sub('[^a-z]+', ' ', query_text)
# query_tokens = query_text.split()
# clean_stem_query_tokens = [
#         st.stem(token) for token in query_tokens 
#         if (token not in stop_words and st.stem(token) not in stop_words) and len(st.stem(token))>2
#     ]
# clean_stem_query_tokens

# +
# query_tokens = tokenize_query(query)
# query_tokens

# +
# query_sim_pages = calc_cos_sim_scores(query_tokens, webpages_lens)
# most_relevant_pages = sorted(query_sim_pages.items(), key= lambda x: x[1], reverse=True)

# +
def show_relevant_pages(count,webpages):
    for i in range(count, count+10):
#         print(webpages[i])
        try:
            url_no = int(webpages[i][0])
            
        except Exception as e: 
            print("\nNo more results found !!")
            break
            
#         print(url_no)
        if urls.get(url_no, None):
            print(i+1,urls.get(url_no))
    
# show_relevant_pages(0,most_relevant_pages)    


# +
webpages_idf = calc_idf(inverted_index)

for page in webpages_tokens:
    max_freq[page] = Counter(webpages_tokens[page]).most_common(1)[0][1]
    
webpages_tf_idf = calc_tfidf(inverted_index)
webpages_lens = doc_len_pages(webpages_tokens)



# + run_control={"marked": false}

print('\n                     ---UIC Web Search Engine---\n')
query = str(input("Enter a search query: "))
print('\n')
query_tokens = tokenize_query(query)

query_sim_pages = calc_cos_sim_scores(query_tokens, webpages_lens)
most_relevant_pages = sorted(query_sim_pages.items(), key= lambda x: x[1], reverse=True)

yes = {'y','yes'}
first_pass = True
count = 0

while first_pass or choice.lower() in yes:
    first_pass = False
    show_relevant_pages(count, most_relevant_pages)
    choice = str(input("\nDo you want to more web page results? "))
    count += 10
