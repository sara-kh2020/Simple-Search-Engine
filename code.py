from bs4 import BeautifulSoup
import requests
import bs4 as bs
import urllib.request
import re
import nltk
import itertools
import numpy as np
import webbrowser


fifty_urls_list=[]
fifty_filtered_words_list=[]                # word's list without part of speech
filtered_words_pos=[]                       # word's list with part of speech
words_dictionary={}                         # reversed_index dictionary
the_matrix=[]
count_the_matrix = []                       # count the rows of matrix to see how many 1 do we have
zero = []                                   # to see how many of our rows do not have 1
user_query_words = []                       # list of query words
results=[]                                  # list of lists that contain the page number of every word in user query
                                            # and the last one has all the common pages between other lists
word_index = []                             # word index of result[-1]
word_index_page_dictionary = {}

sorted_final = []
final_five_results_for_two_words = []
urls_result = []

def extract_urls(address):
    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(address).text

    # Parse the html content
    soup = BeautifulSoup(html_content, features="lxml")
    divTag = soup.find_all("div", {"class": "div-col columns column-width"})

    for tag in divTag:
        tdTags = tag.find_all("a")
        for link in tdTags:
            # Extract 50 urls
            if link.has_attr('href') and link.text!="edit" and link.text!= "Level 4" and link.text!= "Good articles" and link.text!= "Featured articles" and link.text!="Template:Icon/doc" and len(fifty_urls_list) < 50:
                url = "https://en.wikipedia.org"+ link['href']
                fifty_urls_list.append(url)
                
    return fifty_urls_list            


def preprocessing(our_urls_list):
    for url in our_urls_list:
        scraped_data = urllib.request.urlopen(url)
        article = scraped_data.read()
        parsed_article = bs.BeautifulSoup(article,'lxml')
        paragraphs = parsed_article.find_all('p')
        article_text = ""
        for p in paragraphs:
            article_text += p.text
        
        # Removing Square Brackets and Extra Spaces
        article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)
        article_text = re.sub(r'\s+', ' ', article_text)
        
        # Removing special characters and digits
        formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text )
        formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)  
    
        word = nltk.word_tokenize(formatted_article_text)
        stopwords = nltk.corpus.stopwords.words('english')
    
        # words without stopwords
        filtered_words=[] 
        not_repeated_words=[]
    
        for w in word: 
            if w.lower() not in stopwords: 
                filtered_words.append(w)
    
        for f in filtered_words:
            if f not in not_repeated_words:
                not_repeated_words.append(f)
    
        fifty_filtered_words_list.append(not_repeated_words)
        filtered_words_pos.append(nltk.pos_tag(not_repeated_words)) 
    
    return fifty_filtered_words_list, filtered_words_pos


def reversed_index(our_words_list):
    merged_words = list(itertools.chain.from_iterable(our_words_list))
    len("Length of your word's list is {} :".format(merged_words))
    
    for item in merged_words:
        for i in range(0,50):
            if item in fifty_filtered_words_list[i]:
                if item in words_dictionary.keys() and i not in words_dictionary[item]:
                    words_dictionary[item].append(i) 
                else:
                    words_dictionary[item] = [i]
                    
    return words_dictionary


def make_matrix(our_words_list, t):
    for i in our_words_list:
        common = []       
        for j in our_words_list:
            if i == j:
                common.append(0)
            else:
                k = list(set(i) & set(j))
                com = len(k)
                common.append(com)
                
        the_matrix.append(common)
     
    # Change the values of matrix to 1 or 0
    for m in range(0,50):
        for n in range(0,50):
            if the_matrix[m][n] > t:
                the_matrix[m][n] = 1
            else:
                the_matrix[m][n] = 0
       
    return the_matrix


def counting_matrix(matrix):
    for r in matrix:
        c = 0
        for i in r:
            if i == 1:
                c += 1
        count_the_matrix.append(c)
              
    for i in range(0,50):
        if count_the_matrix[i]<1:
            zero.append(i)
            
    print("Counting 1 for every row in matrix: {} ".format(count_the_matrix))
    print("These rows do not have any 1 : {}".format(zero))       

    return count_the_matrix, zero


def query():
    global user_query_words
    user_query = input("Enter what are you looking for: ")
    user_query_words = nltk.word_tokenize(user_query)
    
    for word in user_query_words:
        if word in words_dictionary.keys():
            results.append(words_dictionary[word])
        else:
            print("we could not found any result for {} ".format(word))
            
            
    if len(results) != 1:    
        elements_in_all = list(set.intersection(*map(set, results)))
        results.append(elements_in_all)
    
    return results

def ranking_list():
    global word_index_page_dictionary, word_index_page_dictionary1, word_index_page_dictionary2
    global sorted_final, sorted_final1, sorted_final2
    global final_five_results_for_two_words
    
    if len(user_query_words) == 1:
        for word in user_query_words:
            for r in results[-1]:
                word_index.append(fifty_filtered_words_list[r].index(word))
            
        word_index_page_dictionary = dict(zip(results[-1], word_index))
        sorted_word_index_page_dictionary = sorted(word_index_page_dictionary.items(), key = lambda kv:(kv[1], kv[0]))[0:5]
        
        score_sorted_word_index_page_dictionary = []
        
        i = 5
        for s in sorted_word_index_page_dictionary:
            score_sorted_word_index_page_dictionary.append(s + (i,))
            i = i-1
        
        final_score = score_sorted_word_index_page_dictionary

        final = {}
        for item in final_score:
            # score = alpha*score1 + (beta)*score2
            score = (0.4 * item[2]) + (0.6 * pr[item[0]])
            final[item[0]]=score   
            
        sorted_final = sorted(final.items(), key = lambda kv:(kv[1], kv[0]),reverse=True)
        
        return sorted_final
        
    
    
    if len(user_query_words) == 2:
        for word in user_query_words:
            arr=[]
            for r in results[-1]:
                arr.append(fifty_filtered_words_list[r].index(word))
                
            word_index.append(arr)
        
        word_index_page_dictionary1 = dict(zip(results[-1], word_index[0]))
        word_index_page_dictionary2 = dict(zip(results[-1], word_index[1]))
        
        sorted_word_index_page_dictionary1 = sorted(word_index_page_dictionary1.items(), key = lambda kv:(kv[1], kv[0]))[0:5]
        sorted_word_index_page_dictionary2 = sorted(word_index_page_dictionary2.items(), key = lambda kv:(kv[1], kv[0]))[0:5]
        
        score_sorted_word_index_page_dictionary1 = []        
        i = 5
        for s in sorted_word_index_page_dictionary1:
            score_sorted_word_index_page_dictionary1.append(s + (i,))
            i = i-1
        
        score_sorted_word_index_page_dictionary2 = [] 
        i = 5
        for s in sorted_word_index_page_dictionary2:
            score_sorted_word_index_page_dictionary2.append(s + (i,))
            i = i-1
        
        final_score1 = score_sorted_word_index_page_dictionary1        
        final1 = {}
        for item in final_score1:
            # score = alpha*score1 + (beta)*score2
            score = (0.4 * item[2]) + (0.6 * pr[item[0]])
            final1[item[0]]=score
            
        final_score2 = score_sorted_word_index_page_dictionary2
        final2 = {}
        for item in final_score2:
            # score = alpha*score1 + (beta)*score2
            score = (0.4 * item[2]) + (0.6 * pr[item[0]])
            final2[item[0]]=score
        
        sorted_final1 = sorted(final1.items(), key = lambda kv:(kv[1], kv[0]),reverse=True)
        sorted_final2 = sorted(final2.items(), key = lambda kv:(kv[1], kv[0]),reverse=True)
        
        five_results_for_two_words = []
        for s1 in sorted_final1:
            for s2 in sorted_final2:
                if s1[0]==s2[0]:
                    five_results_for_two_words.append((s1[0], s1[1]+s2[1]))
            
            f0_array = []
            for f in five_results_for_two_words:
                f0_array.append(f[0])
            
        if len(five_results_for_two_words) != 5:
            for s2 in sorted_final2:
                if s2[0] not in f0_array:
                    five_results_for_two_words.append(s2)
                    
        final_five_results_for_two_words = sorted(five_results_for_two_words, key=lambda x: x[1], reverse = True)
        
        return final_five_results_for_two_words

    else:
        print("Sorry! we can't respond to more than two words query!!!")

        
    
def open_in_browser(our_final_list):
    for item in our_final_list:
        urls_result.append(fifty_urls_list[item[0]])
    for u in urls_result:
        webbrowser.open(u,new=2)




extract_urls("https://en.wikipedia.org/wiki/Wikipedia:Vital_articles/Level/5/Biological_and_health_sciences/Animals")              
preprocessing(fifty_urls_list)     
reversed_index(fifty_filtered_words_list)          
make_matrix(fifty_filtered_words_list, 100)
counting_matrix(the_matrix)

###########################################################################################################

#PageRank
pr_the_matrix = np.array(the_matrix)

# initialization of all is 1
pr = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 , 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               1, 1, 1,1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]) 
d = 0.85
for iter in range(10):     
    pr = 0.15 + 0.85 * np.dot(pr_the_matrix, pr)
    
############################################################################################################
    
query()
open_in_browser(ranking_list())
