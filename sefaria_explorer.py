# -*- coding: utf-8 -*-
"""
Spyder Editor
​
This is a temporary script file.
"""
import requests
import re
import json
import csv
import sys
from collections import Counter 
import pandas as pd
import unicodedata
from wordcloud import WordCloud, STOPWORDS 
import matplotlib.pyplot as plt 
from bidi.algorithm import get_display

#imports Yoni's dataset of tanaim and amoraim as CSV
rav_df = pd.read_csv('RabbisNames_2.csv')

#fills out all NaN cells with empty string
rav_df = rav_df.fillna('')
#concatenates all name fields into single name field
rav_df['full name'] = (rav_df['Name1'] + " " + rav_df['Name2']                                              
+ " "+ rav_df['Name3'] + " " + rav_df['Name4']+ " " +  rav_df['Name5']+ " " + 
rav_df['Name6']+ " " +  rav_df['Name7']+ " " +  rav_df['Name8']+ " " + 
rav_df['Name9']+ " " + rav_df['Name10'])
#creates list of full names 
rav_list = rav_df['full name'].tolist() 

#reduces white space to nothing
rav_list = [x.strip() for x in rav_list]
 
#removes empty strings
rav_list = [i for i in rav_list if i]
#replaces R' with Rabi
rav_list = [i.replace("'", "בי") for i in rav_list]

rav_list = list(dict.fromkeys(rav_list))
#creates list of dafs for Masekhot Berakhot
daf_list = []
daf_list = [*range(2,65,1)]
daf_list = (daf_list * 2)
daf_list.sort() 
daf_list = [str(d) for d in daf_list]
daf_list = [x + ('a' if i%2 == 0 else '') for i, x in enumerate(daf_list)]
daf_list = [x + ('b' if i%2 != 0 else '') for i, x in enumerate(daf_list)]

#removes final element of list because Berakhot ends in 64a
daf_list.pop()
#creates a dict to capture the amud and talmud text for each amud
dict = {} 

#creates empty dictionary for holding all amud's & talmud texts in Berakhot
masekhet_dict = {}

#url for Sefaria's text API for Berakhot 
base_url = 'https://www.sefaria.org/api/texts/Berakhot.'

#uses API to populate dictionary keyed by daf where each value is the Hebrew
#text of the daf itself. 
for i in daf_list: 
    
    full_url = base_url+i
    print(full_url)
    r = requests.get(full_url)
    print(r)
    #stores response from URL as a JSON
    response = r.json()
    
#For Talmud references, Hebrew text is returned by Sefaria API as a list of strings
#The following line stores Hebrew text as list of strings "heb_text"
    heb_text = response["he"]
    print(heb_text)
    
    agg_heb_text = " ".join(heb_text)
    dict = {i: agg_heb_text}
    
    masekhet_dict.update(dict)

# Reduce hebrew vowel ניקוד marks for each string in maskhet_dict
flat_dict = {}
for k,v in masekhet_dict.items():
    flat_dict[k] = unicodedata.normalize('NFKD', v) 
    flat_dict[k]="".join([c for c in v if not unicodedata.combining(c)])

#concatenates each daf of berakhot into a single string
Berakhot = ''
for v in flat_dict.values():
    Berakhot += v

#converts list of ravs into dataframe 
rav_df = pd.DataFrame(rav_list, columns=['rav_names'] )

#Gets counts of rabbi's names in berakhot
for i in rav_df.index:
    rav_df.at[i, 'counts'] = Berakhot.count(rav_df.at[i, 'rav_names'])

#Sorts in descending order
rav_df = rav_df.sort_values(by='counts', ascending=False)

#Removes sages who have 0 references 
rav_df = rav_df[rav_df['counts'] != 0]

#resets index
rav_df = rav_df.reset_index()

#adds column for context_words
rav_df['context_words'] = ""

#function to get 10 words before and after rabbi's name 
def get_words(rav_name):
            if rav_name in Berakhot:
                words = Berakhot.split()
                ind = words.index(rav_name)
                return words[max(0, ind-10):min(ind+10, len(words))]

#function that returns a list of strings corresponding to the 10 words before and 10 words
#after each reference to a specific tana or amora
def context_words(n):
    text = Berakhot
    pattern = n
    r = re.search(pattern, text, re.IGNORECASE)
    output = []
    trim_words = ['אמר', 'דאמר', 'אמר ליה']
    if r:
        while text:
            before, match, text = text.partition(pattern)
            if match:
                if not output:
                    before = before.split()[-10:]
                else:    
                    before = ' '.join([pattern, before]).split()[-10:]
                after = text.split()[:10]
                output.append(before + after)
         
                output_flat = []
                for e in output:
                    output_flat += e
             
                final_output = [i for i in output_flat if i not in trim_words] 
    return(final_output)

for i,r in enumerate(rav_df['rav_names']):
    rav_df.at[i,'context_words'] = context_words(r)
    print(i)
    
def word_cloud(r):
    stopwords = set(STOPWORDS)

    t = rav_df.loc[rav_df['rav_names'] == r,'context_words']
    t = t.to_list()
    t = " ".join(str(v) for v in t)
    t = get_display(t)
    wordcloud = WordCloud(width = 800, height = 800, 
                background_color ='white', 
                stopwords = stopwords, 
                min_font_size = 10,
                font_path='FreeSansBold.ttf').generate(t) 
    
    # plot the WordCloud image                        
    plt.figure(figsize = (8, 8), facecolor = None) 
    plt.imshow(wordcloud) 
    plt.axis("off") 
    plt.tight_layout(pad = 0) 
    return plt.show()  

#produces world cloud for each tana/amora in Berakhot
for x in rav_df['rav_names']:
   word_cloud(x)
   print(x)
