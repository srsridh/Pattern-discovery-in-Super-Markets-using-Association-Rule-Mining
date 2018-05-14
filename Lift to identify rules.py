from __future__ import division
import numpy as np
import pandas as pd
from itertools import *

#Main function block
def main(data):
    global k, frequent_items, frequent_support
    k += 1
    data = data.loc[(data != 0).any(axis=1)]
    data.loc[-1] = data.sum(axis=0)
    c1_dict = dict(zip(data.ix[:, 0:length], data.loc[-1]))
    f1 = {k: v for k, v in c1_dict.items() if v >= min_sup}
    keyList = f1.keys()
    keyList2 = []

    for l in keyList:
        tup = (l,)
        keyList2.append(set(tup))
    data2 = pd.DataFrame({'col1': keyList2})
    data2['col2'] = f1.values()
    data2 = data2[data2.col2 >= min_sup]
    frequent_items.append(data2['col1'].tolist())
    frequent_support.append(data2['col2'].tolist())

    data = data.drop(data.index[len(data) - 1])
    df_dict = {}
    for i in f1.keys():
        ele_list = []
        d = data.loc[data[i] == 1]
        ele_list = d.index.values
        if len(d.index) > 0:
            df_dict[i] = ele_list.tolist()
    k += 1
    c2 = list(combinations(f1.keys(), 2))
    c2_supp = find_support(df_dict, c2)

    if len(c2) > 0:
        f2, f_supp = prune(c2, c2_supp)
        # print("Using fk-1 X f-1 :: ")
        # fk_f1(f1, f2, f_supp, df_dict)
        print("Using fk-1 X fk-1 :: ")
        fk1_fk1(f2, f_supp, df_dict)
    return
#Function block to find F1 candidates
def find_f1_candidates(f1, freq_old):
    a = []
    for i in freq_old:
        for j in f1:
            lst = []
            lst.extend(i)
            if j not in lst:
                lst.append(j)
            else:
                break
            a.append(lst)
    return a
#Function block to find Fk candidates
def find_fk_candidates(freq_old):
    a = []
    for list1 in freq_old:
        index = freq_old.index(list1)
        for j in range(index + 1, len(freq_old)):
            list2 = freq_old[j]
            if list1[0:k - 2] == list2[0:k - 2]:
                b = []
                b = list1
                b = set(b + list2)
                if list(b) in a:
                    continue
                else:
                    if len(b) == k:
                        a.append(list(b))
    return a
#Support finding function
def find_support(df_dict, candidate_items):
    checklist = []
    for C in candidate_items:
        supp = []
        supp = df_dict[C[0]]
        for r in range(1, len(C)):
            b = df_dict[C[r]]
            supp = list(supp)
            supp = set(supp).intersection(set(b))
            supp = set(supp)
            if len(supp) < 1:
                break
        checklist.append(len(supp))
    return checklist

#Pruning function
def prune(c, c_supp):
    data2 = pd.DataFrame({'col1': c})
    data2['col2'] = c_supp
    data2 = data2[data2.col2 >= min_sup]
    f = data2['col1'].tolist()
    f_supp = data2['col2'].tolist()
    f2 = [set(l) for l in f]
    frequent_items.append(f2)
    frequent_support.append(f_supp)
    return f, f_supp

#Function block for fk-1 with f1
def fk_f1(f1, freq_old, supp_old, df_dict):
    global k
    global f_items
    k += 1
    candidate_items = find_f1_candidates(f1, freq_old)
    support = find_support(df_dict, candidate_items)
    freq_new, f_supp = prune(candidate_items, support)
    if len(freq_new) <= 0 or freq_new == freq_old or k <= k_max:
        if len(freq_new) <= 0:
            f_items = freq_old
        else:
            f_items = freq_new
        return
    else:
        fk_f1(f1, freq_new, supp_old, df_dict)
    return
#Function block for fk-1 with fk-1
def fk1_fk1(freq_old, supp_old, df_dict):
    global k
    global f_items
    k += 1
    candidate_items = find_fk_candidates(freq_old)
    support = find_support(df_dict, candidate_items)
    freq_new, f_supp = prune(candidate_items, support)
    if len(freq_new) <= 1 or freq_new == freq_old or k <= k_max:
        if len(freq_new) <= 0:
            f_items = freq_old
        else:
            f_items = freq_new
        return
    else:
        fk1_fk1(freq_new, supp_old, df_dict)
    return

def generate_rules(f_items):
    global frequent_items, frequent_support
    l = len(f_items[0])
    df_rules = get_rules(f_items)
    final_df = pd.DataFrame
    confidenceList = []
    liftList = []
    for index, row in df_rules.iterrows():
        rule = []
        rule2 = []
        rule3 = []
        rule.append(row['from'])
        rule2.append(row['from'])
        rule3.append(row['to'])
        rule2 = sum(rule2, [])
        rule.append(row['to'])
        rule = sum(rule, [])
        rule3 = sum(rule3, [])
        s = set(rule)
        ind = frequent_items.index(s)
        supp1 = frequent_support[ind]
        s2 = set(rule2)
        ind = frequent_items.index(s2)
        supp2 = frequent_support[ind]
        ind = frequent_items.index(set(rule3))
        supp3 = frequent_support[ind]
        confidence = supp1 / supp2
        confidenceList.append(confidence)
        lift = confidence / supp3
        liftList.append(lift)
    df_rules['confidence'] = confidenceList
    df_rules['lift'] = liftList
    df_rules = df_rules[df_rules.confidence >= min_conf]
    return df_rules

def get_rules(f_items):
    frequentList = np.asarray(f_items)
    fList = [list(l) for l in frequentList]
    data = pd.DataFrame(columns=('from', 'to'))
    fromList = []
    toList = []
    for l in fList:
        for p in product([True, False], repeat=len(l)):
            l1 = []
            l2 = []
            l1.append([x[1] for x in izip(p, l) if x[0]])
            l2.append([x[1] for x in izip(p, l) if not x[0]])
            if len(l1[0]) > 0 and len(l1[0]) < len(l):
                l1 = reduce(lambda x, y: x + y, l1)

                fromList.append(l1)
            if len(l2[0]) > 0 and len(l2[0]) < len(l):
                l2 = reduce(lambda x, y: x + y, l2)
                toList.append(l2)
    data['from'] = fromList
    data['to'] = toList
    return data

#Function to generate interesting  rules
def get_InterestingRules(df):
    df.sort_values('lift')
    if len(df.index) >= 5:
        d = df.head(5)
        print("Interesting rules found are: ")
        print(d)
    elif len(df) > 0:
        d = df.head(len(df.index))
        print("Interesting rules found are: ")
        print(d)
    else:
        print("No rules found!")
    return

#program begins here
data = pd.read_csv('mushroom.csv')
data = pd.get_dummies(data)
n = len(data.index)
m = len(data.columns)

#Getting minimum support from user
min_sup = raw_input("Enter minimum support in %: ")
min_sup = int(min_sup)
min_sup = min_sup * n / 100

#Getting minimum confidence from user
min_conf = raw_input("Enter minimum confidence in %: ")
min_conf = int(min_conf)
min_conf = min_conf / 100

k = 0
k_max = 3
frequent_items = []
frequent_support = []
length = len(data)
main(data)
frequent_items = sum(frequent_items, [])
frequent_support = sum(frequent_support, [])
df = generate_rules(frequent_items)
get_InterestingRules(df)