#!/usr/bin/env python
# coding: utf-8

# In[1]:


from collections import defaultdict
import pandas as pd
from sklearn.metrics import cohen_kappa_score
import os
#Load all the cuis
#C0000000 is for anything labeled as 'other'
cuis = []
infile = open('./cuilist.txt')
for line in infile:
    cuis.append(line.strip())
#print (cuis)
#print (len(cuis))

#Now that we have the cuis loaded,
#we need to add negated or non-negated information.
#A simple way can be to append a '-0' or a '-1' tag indicating
#if a concept is negated or not.
cuis_with_neg_marker = []
for cui in cuis:
    cuis_with_neg_marker.append(cui+'-0')
    cuis_with_neg_marker.append(cui+'-1')

#print(cuis_with_neg_marker)

#Now we load the annotation files
def get_flagged_cuis_from_annotated_file (filepath):
    f1 = pd.read_excel(filepath)
    f1_flagged_cuis = defaultdict(list)
    for index,row in f1.iterrows():
        id_ = row['ID']
        cuis = row['Symptom CUIs'].split('$$$')
        neg_flags = row['Negation Flag'].split('$$$')
        for cui,flag in zip(cuis,neg_flags):
            if len(cui)>0 and len(flag)>0:
                f1_flagged_cuis[id_].append(cui+'-'+str(flag))
    return f1_flagged_cuis


# Define the folder path containing the .parquet files
folder_path = './annots/'

# List all files in the folder
files = os.listdir(folder_path)

default = {}
for file in files:
    file_path = os.path.join(folder_path, file)
    file_flagged_cuis = get_flagged_cuis_from_annotated_file(file_path)
    default[file] = file_flagged_cuis


file_names = list(default.keys())

cohen_kappa = {}
commonids_len = {}
for i in range(len(file_names)):
    for j in range(i + 1, len(file_names)):
        i_vec = []
        j_vec = []
        commonids = list(set(default[file_names[i]].keys()).intersection(set(default[file_names[j]].keys())))
        key = str(file_names[i]) + "_" + str(file_names[j])
        for k in commonids:
            for c in cuis_with_neg_marker:
                if c in default[file_names[i]][k]:
                    i_vec.append(1)
                else:
                    i_vec.append(0)
                if c in default[file_names[j]][k]:
                    j_vec.append(1)
                else:
                    j_vec.append(0)
        cohen_kappa[key] = cohen_kappa_score(i_vec, j_vec)
        commonids_len[key] = len(commonids)


# In[2]:


cohen_kappa


# In[3]:


commonids_len


# In[ ]:




