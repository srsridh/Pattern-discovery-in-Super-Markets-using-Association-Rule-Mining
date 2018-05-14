import numpy
import pandas as pd
import itertools
from itertools import combinations
from numpy import array

#This function block does preprocessing on the sparse data matrix like removing all rows having 0's and generates
#Candidate itemset1, candidate itemset1 support, frequent itemset1, frequent itemset1 support
def main(data):
    global k, maximum_fcount1, closed_fcount1, maximum_fcount2, closed_fcount2
    data = data.loc[(data != 0).any(axis=1)]
    length = len(data)
    data.loc[-1] = data.sum(axis=0)
    #Candidate list one having all items and it's support
    candidate_ldict = dict(zip(data.ix[:, 0:length], data.loc[-1]))
    #Frequent itemset 1 having all items and it's support
    frequent_ldict = {key: val for key, val in candidate_ldict.items() if val > minsup}
    # extracting only the items from Frequent itemset 1
    frequent_l1 = frequent_ldict.keys()
    frequent_l1s = frequent_ldict.values()
    data = data.drop(data.index[len(data) - 1])
    #Find all possible combinations of items in F1 for candidate itemset 2
    candidate_l2 = list(combinations(frequent_l1, 2))
    # procedure to find the support count for candidate itemset 2
    #candidate_l2s has the support count for candidate itemset 2
    com_columns = data.columns.tolist()
    candidate_l2s = []
    for f in  candidate_l2:
        d = data.loc[data[f[0]] == 1]
        data3 = pd.DataFrame(d)
        for r in range(1,len(f)):
            d2 = data.loc[data[f[r]] == 1]
            data3 = pd.merge(data3, d, on=com_columns, how='inner')

        candidate_l2s.append(len(data3.index))
    data2 = pd.DataFrame({'col1':  candidate_l2})
    data2['col2'] = candidate_l2s
    # creating frequent itemset 2 by checking minsup
    data2 = data2[data2.col2 > minsup]
    #all items in frequent itemset2
    frequent_l2 = data2['col1'].tolist()
    frequent_l2s = data2['col2'].tolist()
    # Calling the fucntion to implement fk-1 with f1
    fk1(frequent_l1,frequent_l1s,frequent_l2,frequent_l2s)
    # Calling the function to implement fk1 with fk1
    f_k_1(frequent_l2,frequent_l2s,k)
    return
#Function block to implement fk-1 with f1
def fk1(frequent_l1,frequent_l1s,frequent_l2,frequent_l2s):
    global maximum_fcount1, closed_fcount1
    #print("entering function 1")
    #print("frequent_l2 is :", frequent_l2)
    #print("len of ")
    #Procedure to find Candidate itemset 3 only items
    candidate_l = []
    for i in frequent_l2:
        for j in frequent_l1:
            #j = list(j)
            dummy = []
            dummy.extend(i)
            if j not in dummy:
                dummy.append(j)
            else:
                break
            candidate_l.append(dummy)
    com_columns = data.columns.tolist()
    candidate_ls = []
    for f in candidate_l:
        d = data.loc[data[f[0]] == 1]
        data3 = pd.DataFrame(d)
        for r in range(1, len(f)):
            d2 = data.loc[data[f[r]] == 1]
            data3 = pd.merge(data3, d2, on=com_columns, how='inner')
        candidate_ls.append(len(data3.index))
    candidate_data = pd.DataFrame({'col1': candidate_l})
    candidate_data['col2'] = candidate_ls
    frequent_l,frequent_ls = prune(candidate_data)
    if len(frequent_l) <= 0  or frequent_l == frequent_l2:
        if len(frequent_l)>0:
            print("Maximum frequency count for fk1 with f1 is:", maximum_fcount1)
            print("Closed frequency count for fk1 with f1 is:", closed_fcount1)
        else:
            print("Maximum frequency count for fk1 with f1 is:", maximum_fcount1)
            print("Closed frequency count for fk1 with f1 is:", closed_fcount1)
        return
    else:
        maximum_fcount1 += maxfreitem1(frequent_l2,frequent_l)
        closed_fcount1 += closedfreitem1(frequent_l2, frequent_l2s,frequent_l, frequent_ls)
        fk1(frequent_l1,frequent_l1s,frequent_l,frequent_ls)
    return

#Function block to prune and generate frequent itemset
def prune(candidate_data):
    candidate_data = candidate_data[candidate_data.col2 > minsup]
    frequent_l = candidate_data['col1'].tolist()
    frequent_ls = candidate_data['col2'].tolist()
    return frequent_l, frequent_ls

#Function block to genereate maximum frequent itemset for fk-1 with fk1
def maxfreitem1(frequent_l2,frequent_l):
    maximum_fcount1 = 0
    for i in frequent_l2:
        Flag = True
        for j in frequent_l:
            if len(i)+1 == len(j) and set(i).issubset(set(j)):
                flag = False
                break
            #elif len(i)+2 == len(j):
            #    break
        if Flag:
            maximum_fcount1 += 1
    return maximum_fcount1

#Function block to genereate closed frequent itemset for fk-1 with fk1
def closedfreitem1(frequent_l2,frequent_l2s,frequent_l,frequent_ls):
    frequent_l2 = [tuple(l) for l in frequent_l2]
    maxdicti_l1 = dict(zip(frequent_l2, frequent_l2s))
    frequent_l = [tuple(l) for l in frequent_l]
    md = dict(zip(frequent_l,frequent_ls))
    #frequent_l = tuple(frequent_l)
    #frequent_ls = tuple(frequent_ls)
    #md = dict(zip(frequent_l, frequent_ls))
    closed_fcount1 = 0
    for i in frequent_l2:
        Flag = True
        for j in frequent_l:
            if len(i)+1 == len(j) and set(i).issubset(set(j)):
                if maxdicti_l1[i] == md[j]:
                    Flag = False
                    break
        if Flag:
            closed_fcount1 += 1
    return closed_fcount1

#Function block to implement fk-1 with fk-1
def f_k_1(frequent_l2,frequent_l2s,k):
    global maximum_fcount2, closed_fcount2
    l =[]
    for l1 in frequent_l2:
        ind = frequent_l2.index(l1)
        for j in range(ind +1, len(frequent_l2)):
            l2 = frequent_l2[j]
            if l1[0:k-2] == l2[0:k-2]:
                l3 = []
                l3 = l1
                l3 = set(l3 + l2)
                if list(l3) in l:
                    continue
                else:
                    if len(l3) == k:
                        l.append(list(l3))
    com_columns = data.columns.tolist()
    candidate_ls = []
    for f in l:
        d = data.loc[data[f[0]] == 1]
        # print("d in pandas")
        data3 = pd.DataFrame(d)
        for r in range(1, len(f)):
            d2 = data.loc[data[f[r]] == 1]
            data3 = pd.merge(data3, d2, on= com_columns, how='inner')
        candidate_ls.append(len(data3.index))
    candidate_data = pd.DataFrame({'col1': l})
    candidate_data['col2'] = candidate_ls
    frequent_l,frequent_ls = prune(candidate_data)
    if len(frequent_l) <= 0 or frequent_l == frequent_l2:
        if len(frequent_l)> 0:
            print("Maximum frequency count for fk-1 with fk-1 is:", maximum_fcount2)
            print("Closed frequency count for fk-1 with fk-1 is:", closed_fcount2)
        else:
            print("Maximum frequency count for fk-1 with fk-1 is:", maximum_fcount2)
            print("Closed frequency count for fk1 with f1 is:", closed_fcount2)
        return
    else:
        maximum_fcount2 += maxfreitem2(frequent_l2,frequent_l)
        closed_fcount2 += closedfreitem2(frequent_l2,frequent_l2s,frequent_l,frequent_ls)
        f_k_1(frequent_l,frequent_ls,k)
    return

#Function block to genereate maximum frequent itemset for fk-1 with fk-1
def maxfreitem2(frequent_l2,frequent_l):
    maximum_fcount2 = 0
    for i in frequent_l2:
        Flag = True
        for j in frequent_l:
            if len(i)+1 == len(j) and set(i).issubset(set(j)):
                Flag = False
                break
            #elif len(i)+2 == len(j):
            #    break
        if Flag:
            maximum_fcount2 += 1
    return maximum_fcount2

#Function block to genereate closed frequent itemset for fk-1 with fk-1
def closedfreitem2(frequent_l2,frequent_l2s,frequent_l,frequent_ls):
    frequent_l2 = [tuple(l) for l in frequent_l2]
    maxdicti_l2 = dict(zip(frequent_l2, frequent_l2s))
    frequent_l = [tuple(l) for l in frequent_l]
    md = dict(zip(frequent_l,frequent_ls))
    #frequent_l = tuple(frequent_l)
    #frequent_ls = tuple(frequent_ls)
    #mad = dict(zip(frequent_l, frequent_ls))
    closed_fcount2 = 0
    for i in frequent_l2:
        Flag = True
        for j in frequent_l:
            if len(i) + 1 == len(j) and set(i).issubset(set(j)):
                if maxdicti_l2[i] == md[j]:
                    Flag = False
                    break
        if Flag:
            closed_fcount2 += 1
    return closed_fcount2

maximum_fcount1 = 0
closed_fcount1 = 0
maximum_fcount2 = 0
closed_fcount2 = 0

data = pd.read_csv('mushroom.csv')
data = pd.get_dummies(data)
x = len(data.index)
minsup = input("Kindly enter the minimum support value:")
misnup = int(minsup)
minsup = minsup * x / 100

k = 3
#This is my data function
#x = 500
#y = 10
#data = pd.DataFrame(numpy.random.choice([0, 1], size=(x, y), p=[.8, .2]))
#minsup = 8
main(data)
#data = pd.read_csv('solarflare.csv')
#data = pd.get_dummies(data)
#x = len(data.index)
#minsup = input("Kindly enter the minimum support value:")
#misnup = int(minsup)
#minsup = minsup*x/100



