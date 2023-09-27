#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.util import bigrams
from rapidfuzz import fuzz
from nltk.corpus import stopwords
import string
# Load Excel file
#df_posts = pd.read_excel('./GoldStandard.xlsx')
df_posts = pd.read_excel('./UnlabeledSet.xlsx')


# In[2]:


df_posts["TEXT"] = df_posts["TEXT"].astype(str)


# In[3]:


symptom_data = []

with open('./COVID-Twitter-Symptom-Lexicon.txt', 'r') as f:
    for line in f:
        standard_symptom, cui, expression = line.strip().split('\t')
        symptom_data.append((expression, standard_symptom, cui))


# In[4]:


negation_terms = ["no", "not", "haven't", "hasn't", "hadn't", "doesn't", "don't", "didn't", "never", "without"]


# In[5]:


#### This is the first system without fuzzy matching #####
def is_expression_matched(text, expression):
    # Exact match
    if expression in text:
        return expression
    
    # If there's no exact match, then proceed with regex matching
    pattern = r'\b' + r'\W*'.join(re.escape(word) for word in expression.split()) + r'\b'
    
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group()  # Return the matched word or phrase from the TEXT

    return None

# ##### This is the second system with fuzzy matching #####
# stop_words = set(stopwords.words('english'))


# def is_expression_matched(text, expression):
#     # Exact match
#     if expression in text:
#         return expression
    
#     pattern = r'\b' + r'\W*'.join(re.escape(word) for word in expression.split()) + r'\b'
    
#     match = re.search(pattern, text, re.IGNORECASE)
#     if match:
#         return match.group()  # Return the matched word or phrase from the TEXT
    
#     # Tokenization and removal of stop words and punctuation
#     tokens = word_tokenize(text)
#     filtered_tokens = [token for token in tokens if token.lower() not in stop_words and token not in string.punctuation]
    
#     # Generate both unigrams and bigrams
#     combined_list = filtered_tokens + [' '.join(bigram) for bigram in bigrams(filtered_tokens)]
    
#     for token_or_bigram in combined_list:
#         if fuzz.token_set_ratio(token_or_bigram, expression) > 85:  # Adjust the threshold as required
#             return token_or_bigram  # Return the matching token/bigram from the TEXT
#             break  # If the above condition is satisfied, exit the loop

#     return None


# In[6]:


# Iterate over rows in df_posts
for index, row in df_posts.iterrows():
    post_text = row["TEXT"].lower()

    if not isinstance(post_text, str):
        continue  

    matched_symptoms = set()  
    expressions_found = []
    standard_symptoms_found = []
    cuis_found = []
    negation_flags = []

    for expression, standard_symptom, cui in symptom_data:
        # Check if this symptom has already been matched
        if standard_symptom in matched_symptoms:
            continue
        
        matched_expression = is_expression_matched(post_text, expression)
        
        if matched_expression:
            matched_symptoms.add(standard_symptom) 
            
            # Check for negation terms
            negated = False
            for term in negation_terms:
                if post_text.split(matched_expression)[0].endswith(term + " "):
                    matched_expression = term + " " + matched_expression  # Append negation term to the expression
                    negated = True
                    break

            expressions_found.append(matched_expression)
            standard_symptoms_found.append(standard_symptom)
            cuis_found.append(cui)
            negation_flags.append("1" if negated else "0")

    if expressions_found:
        df_posts.at[index, "Symptom Expressions"] = "$$$" + "$$$".join(expressions_found) + "$$$"
        df_posts.at[index, "Standard Symptom"] = "$$$" + "$$$".join(standard_symptoms_found) + "$$$"
        df_posts.at[index, "Symptom CUIs"] = "$$$" + "$$$".join(cuis_found) + "$$$"
        df_posts.at[index, "Negation Flag"] = "$$$" + "$$$".join(negation_flags) + "$$$"


# In[7]:


#df_posts.to_excel('./GoldStandard_result_fuzzy.xlsx', index=False)
df_posts.to_excel('./UnlabeledSet_result_nofuzzy.xlsx', index=False)


# In[ ]:




