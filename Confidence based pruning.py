from __future__ import division
import numpy
import pandas as pd
from itertools import *
import time
start = time.clock()

def get_support(df_dict, combo):
    checklist = []
    for C in combo:
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

def prune(c, c_supp):
    data2 = pd.DataFrame({'col1': c})
    data2['col2'] = c_supp
    data2 = data2[data2.col2 >= minsup]
    f = data2['col1'].tolist()
    f_supp = data2['col2'].tolist()
    f2 = [set(l) for l in f]
    mainList1.append(f2)
    mainList2.append(f_supp)
    return f, f_supp

def get_f1_candidates(f1, f_old):
    a = []
    for i in f_old:
        for j in f1:
            dummy = []
            dummy.extend(i)
            if j not in dummy:
                dummy.append(j)
            else:
                break
            a.append(dummy)
    return a

def get_fk_candidates(f_old):
    a = []
    for list1 in f_old:
        index = f_old.index(list1)
        for j in range(index+1, len(f_old)):
            list2 = f_old[j]
            if list1[0:k-2] == list2[0:k-2]:
                b = []
                b = list1
                b = set(b + list2)
                if list(b) in a:
                    continue
                else:
                    if len(b) == k:
                        a.append(list(b))
    return a

def main(data):
    global k, mainList1, mainList2
    k += 1
    data = data.loc[(data != 0).any(axis=1)]
    data.loc[-1] = data.sum(axis=0)
    c1_dict = dict(zip(data.ix[:, 0:length], data.loc[-1]))
    f1 = {k: v for k, v in c1_dict.items() if v >= minsup}
    keyList = f1.keys()
    keyList2 = []

    for l in keyList:
        tup = (l,)
        keyList2.append(set(tup))
    data2 = pd.DataFrame({'col1': keyList2})
    data2['col2'] = f1.values()
    data2 = data2[data2.col2 >= minsup]
    mainList1.append(data2['col1'].tolist())
    mainList2.append(data2['col2'].tolist())

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
    c2_supp = get_support(df_dict, c2)

    if len(c2) > 0:
        f2, f_supp = prune(c2, c2_supp)
        #print("Using fk-1 X f-1 :: ")
        #fk_f1(f1, f2, f_supp, df_dict)
        #print("====================================================================================================================")
        ("Using fk-1 X fk-1 :: ")
        fk1_fk1(f2, f_supp, df_dict)
    return

def fk_f1(f1, f_old, supp_old, df_dict):
    global k
    global f_items
    k += 1
    combo = get_f1_candidates(f1, f_old)
    support = get_support(df_dict, combo)
    f_new, f_supp = prune(combo, support)
    if len(f_new) <= 0 or f_new == f_old or k == max_k:
        if len(f_new) <= 0:
            f_items = f_old
        else:
            f_items = f_new
        return
    else:
        fk_f1(f1, f_new, supp_old, df_dict)
    return

def fk1_fk1(f_old, supp_old, df_dict):
    global k
    global f_items
    k += 1
    combo = get_fk_candidates(f_old)
    support = get_support(df_dict, combo)
    f_new, f_supp = prune(combo, support)
    if len(f_new) <= 1 or f_new == f_old or k == max_k:
        if len(f_new) <= 0:
            f_items = f_old
        else:
            f_items = f_new
        return
    else:
        fk1_fk1(f_new, supp_old, df_dict)
    return

def generate_rules(f_items):
    global mainList1, mainList2
    l = len(f_items[0])
    rules_df = get_allRules(f_items)
    print("Number of rules found :: ", len(rules_df.index))
    final_df = pd.DataFrame
    confidenceList = []

    for index, row in rules_df.iterrows():
        rule = []
        rule2 = []
        rule.append(row['from'])
        rule2.append(row['from'])
        rule2 = sum(rule2, [])
        rule.append(row['to'])
        rule = sum(rule, [])
        s = set(rule)
        idx = mainList1.index(s)
        supp1 = mainList2[idx]
        s2 = set(rule2)
        idx = mainList1.index(s2)
        supp2 = mainList2[idx]
        confidence = supp1/supp2
        confidenceList.append(confidence)
    rules_df['confidence'] = confidenceList
    rules_df = rules_df[rules_df.confidence >= minConf]
    print("Number of rules found after pruning :: ", len(rules_df.values))
    #print(rules_df)
    return

def get_allRules(f_items):
    frequentList = numpy.asarray(f_items)
    fList = [list(l) for l in frequentList]
    data = pd.DataFrame(columns=('from', 'to'))
    fromList = []
    toList = []
    for l in fList:
        for pattern in product([True, False], repeat=len(l)):
            l1 = []
            l2 = []
            l1.append([x[1] for x in izip(pattern, l) if x[0]])
            l2.append([x[1] for x in izip(pattern, l) if not x[0]])
            if len(l1[0]) > 0 and len(l1[0]) < len(l):
                l1 = reduce(lambda x, y: x + y, l1)

                fromList.append(l1)
            if len(l2[0]) > 0 and len(l2[0]) < len(l):
                l2 = reduce(lambda x, y: x + y, l2)
                toList.append(l2)
    data['from'] = fromList
    data['to'] = toList
    return data

data = pd.read_csv('nursery.csv')
data = pd.get_dummies(data)
n = len(data.index)
m = len(data.columns)

minsup = raw_input("Enter the value of minimum support in % :: ")
minsup = int(minsup)
minsup = minsup*n/100
minConf = 0.5
k = 0
max_k = 3
#minConf = 1
mainList1 = []
mainList2 = []
length = len(data)
main(data)
mainList1 = sum(mainList1, [])
mainList2 = sum(mainList2, [])
generate_rules(mainList1)
print time.clock() - start