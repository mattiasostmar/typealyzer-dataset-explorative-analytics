#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Placeholder for code snippets related to uClassify text translation, pasted from the notebook
English_LIWC_on_uclassify_translated_texts.ipynb in project LIWC_to_swedish.
"""

import os
import requests
import json
import re
import pickle
import random
import pandas as pd
from collections import Counter

os.environ["UCLASSIFY_KEY"]

a_text = """
She's mine. I adore her. No matter what I will always love her - my special honey!
Idag har jag varit tio år på Twitter. 232987 tweets. 14715 följare. Vunnit Sveriges meste Twittrare 2009. Idag är min average 87 tweets per dag. Den var mycket högre förut. Twitter har gett mig en massa bra. En massa jobb, mängder av vänner (och en del fiender), stor kunskap.

Det bästa är att Twitter gav mig min bästa vän och min kompanjon Sarah aka @sanasilb. Hon betyder oerhört mycket. Tacksam för att hon började stalka mig våren 2010.

Livet hade helt klart sett annorlunda ut utan Twitter även om de senaste åren har inneburit mindre twittrande eftersom jag helt enkelt inte riktigt längre känner mig hemma där. Det är annorlunda. Det är mer broadcast. Och även om jag gillar algoritmerna på Instagram och Facebook så ogillar jag hur den implementerats på Twitter. Samtidigt som jag ogillar Tweetbot så jag kommer liksom inte undan den.

Tio år till? Om Twitter finns kvar. För Facebook, Twitter, Instagram är en del av min vardag. Snapchat lyckades inte ta den platsen. Linkedin inte fullt så.
"""

def translate_from_sv_to_en(list_of_texts):
    header = {"Content-Type": "application/json"}
    data = {"key":os.environ["UCLASSIFY_KEY"], 
            "source":"sv", 
            "target":"en", 
            "t":list_of_texts}
    result = requests.post("https://language.uclassify.com/translate/v1/",
                       json = data,
                       headers = header)

    return result.json()


def translate_from_sv_to_en(list_of_texts):
    header = {"Content-Type": "application/json"}
    data = {"key":os.environ["UCLASSIFY_KEY"], 
            "source":"sv", 
            "target":"en", 
            "t":list_of_texts}
    result = requests.post("https://language.uclassify.com/translate/v1/",
                       json = data,
                       headers = header)

    return result.json()


def load_liwc_dic_file_into_word_and_cats_dicts():
    cats = pickle.load(open("liwc_2007_cats_dict.pickle","rb"))
    words = pickle.load(open("liwc_2007_words_dict.pickle","rb"))
    
    category_names = []
    for key in cats.keys():
        category_names.append(cats[key])
    
    return cats, words, category_names


def detect_language(list_of_texts):
    """
    Sends a list of strings to uClassify's language-detector classifier and returns languages classifications.
    
    :param list_of_texts: list of strings to detect language of.
    :return: list of classification result dicts for each string in input list.
    """
    header = {"Content-Type":"application/json",
         "Authorization": "Token "+os.environ["UCLASSIFY_KEY"]}
    
    data = {"texts":list_of_texts}

    res = requests.post("https://api.uclassify.com/v1/uclassify/language-detector/classify", headers=header, json=data)

    return res.json()


def separate_punctuation_with_whitespace(original_string):
   return re.sub(r"([\w/'+$\s-]+|[^\w/'+$\s-]+)\s*", r"\1 ", original_string) # todo: not perfect - leaves "),"


def liwc_analysis_on_english_string(original_string, words):
    """
    Takes a string and returns word frequencies according to (most of) LIWC 2007.
    
    :param original_string: string representing the input text with no transformations.
    :param words: dictionary containing categories as keys with 0.0 as values plus "WC" = word count.
    :return: dictionary containg LIWC 2007 categories minus the psychological summary variables. 
    """ 
    liwc = dict.fromkeys(category_names, 0.0)
    punct_token_text = separate_punctuation_with_whitespace(paragraphs[para_cnt])
    liwc["WC"] = len(punct_token_text.split())

    for word in words:
        regex_word = re.sub(r"\*",r"\w+",word) # 'cousin*' in .dic file transformed into 'cousin\w+'
        word_patt = re.compile(regex_word)
        
        if word_patt.search(original_string):
            matches = word_patt.findall(original_string)
            print("word: {}".format(word))
            print("cat numbers: {}".format(words[word]))
            for cat_no in words[word]:
                if liwc.get(cats[cat_no]):
                    liwc[cats[cat_no]] += (len(matches) / liwc["WC"])   
                else:
                    liwc[cats[cat_no]] = (len(matches) / liwc["WC"])
    
    return liwc


    paragraphs = [paragraph for paragraph in a_text.split("\n") if not paragraph == ""]
print(paragraphs)
print()

cats, words, category_names = transform_liwc_dic_file_into_word_and_cats_dicts()
    
res_list = detect_language(paragraphs)

swedish_texts_indices_to_translate = []
    
para_cnt = 0
for index, res_dict in enumerate(res_list): # i.e. for each text we've sent to uClassify language-detector classifier
    para_cnt = index
    print("paragraphs index: {}".format(para_cnt))
    print("textCoverage: {}".format(res_dict["textCoverage"]))
    
    max_class = {"className":"dummy", "p":0.0}
    for class_res in res_dict["classification"]:
        if class_res["p"] > max_class["p"]:
            max_class = class_res
    print(max_class)

    if max_class["className"] == "English_eng":
        the_text = paragraphs[para_cnt]
        print(the_text)
        
        result = liwc_analysis_on_english_string(the_text, words)
        print(result)
        
    elif max_class["className"] == "Swedish_swe":
        swedish_texts_indices_to_translate.append(para_cnt)
        
    else:
        print("Skipping the following text, since it appears not be lang en or sv:\n{}".format(paragraphs[para_cnt]))
    print()
    
swedish_full_texts_to_translate = []
for ix, para in enumerate(paragraphs):
    if ix in swedish_texts_indices_to_translate:
        swedish_full_texts_to_translate.append(paragraphs[ix])
        
print("swedish_texts_indices_to_translate: {}".format(swedish_texts_indices_to_translate))
translation_results = translate_from_sv_to_en(swedish_full_texts_to_translate) 
for ix, text in enumerate(translation_results["translations"]):
    liwc_result = liwc_analysis_on_english_string(text, words)
    print("Text:\n{}\nLiwc:\n{}".format(text, liwc_result))
    print()


def create_pickled_cats_and_words_dics_from_liwc_dic_file(dicf="../data/external/LIWC2007_English131104.dic"):
	"""
	To be documented.
	"""
	dicf = open(dicf)
	dics = dicf.read()

	cats_test = """%
	1	funct
	2	pronoun
	3	ppron
	%
	also	1	2	3
	altar*	1
	although	1	3
	"""

	# Parse the categories and their corresponding number
	cats_patt = re.compile(r"%([\w\d\t\n]+)%")
	cats_res = cats_patt.search(dics)
	cats_string = cats_res.group(1)
	print(cats_string)
	cat_patt = re.compile(r"(?P<catnum>\d+)\t(?P<catname>\w+\*?)")
	cats = {}
	for item in cats_string.split("\n"):
    	if item != "":
        	cat_res = cat_patt.search(item)
        	cats[cat_res.group("catnum")] = cat_res.group("catname")
	pickle.dump(cats, open("liwc_2007_cats_dict.pickle","wb"))
	print(cats)

	# Parse words
	word_line_patt = re.compile(r"[^\W\d_]") # a "negative" way of getting alpha characters only
	words = {}
	for row in dics.split("\n"):
    	if word_line_patt.match(row):
        	items = row.split("\t")
        	words[items[0]] = items[1:]
	pickle.dump(words, open("liwc_2007_words_dict.pickle","wb"))
	words_only = list(words.keys())
	random.shuffle(words_only)
	print(words_only[:20])

