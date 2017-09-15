"""
Sabastian Mugazambi
assoc_rules.py
"""

import csv
import random
import numpy as np
import heapq
import math
import collections
import time
import copy
import scipy.stats
import sys
import itertools as it
from operator import itemgetter
T = 0


def freq_itemset_1(items_only, min_sup):
    fr_itemset = {}

    for i in range(items_only.shape[1]):
        #calculate the sup of each column and return itemsets
        # new_col = np.delete(items_only[:,i],0)
        new_col = items_only[:,i]
        int_col = new_col.astype(int)
        col_sup = sum(int_col)

        if (col_sup >= min_sup):
            fr_itemset[i] = col_sup
    #return dictionary of items sets
    return fr_itemset

def gen_cand(Lk_1,num):

    cand = []
    combinations = it.combinations(Lk_1,2)


    for comb in combinations:
        combined = comb[0].union(comb[1])

        if (len(combined) == (len(comb[0])+1)):
            bool_track = True

            #checking if all subset of k-1 is in
            eff_comb = it.combinations(combined,num-1)
            for i in eff_comb:
                if (set(i) not in Lk_1):
                    bool_track = False
                    # print "Test false statement"
                    break
                else:
                    bool_track = True

            if (bool_track == True):
                cand.append(set(combined))
    # print cand
    return cand

def apriori(items,L1,min_sup,mega_dict):

    k=2
    Lk_1 = L1
    dict_k = {}

    while (len(Lk_1) > 0):
        Ck =[]
        if(k==2):
            temp_Ck = []
            C = it.combinations(Lk_1,2)
            for set_it in C:
                temp_Ck.append(set(set_it))
        else:
            temp_Ck = gen_cand(Lk_1,k)


        if (len(temp_Ck) > 0):


            #now do counting
            trans = items[1:,:]
            all_t = []
            Counters = {}

            for t in trans:

                t = t.astype(int)
                set_t = np.where(t==1)[0]

                trans_k = []
                k_itemset_t = it.combinations(set_t,k)
                for sub_it in k_itemset_t:
                    trans_k.append(set(sub_it))

                #using set intersection as tree structure
                t_k = set(frozenset(i) for i in trans_k)
                c_k = set(frozenset(i) for i in temp_Ck)

                tree = t_k .intersection(c_k)
                #maybe make tree

                for i in tree:
                    all_t.append(i)

            Counters = collections.Counter(all_t)
            counts = Counters.values()
            candidat_list = Counters.keys()

            for i in range(len(candidat_list)):
                cand = candidat_list[i]
                cand_count = counts[i]
                if (cand_count >= min_sup):
                    mega_dict[cand] = cand_count
                    Ck.append(cand)

        # dict_lk = np.concatenate((dict_lk,Ck))
        dict_k[k] = Ck
        k += 1
        Lk_1 = Ck

    return (dict_k,mega_dict)

def confidence(I, J,p,mega_dict):
    return float(mega_dict[p])/(mega_dict[I])
def interest(conf,J,T,mega_dict):
    return conf - (float(mega_dict[J])/T)


def gen_rules(prio,min_conf, min_int,col_names,T,mega_dict):
    f=open('Out.txt', 'w+')
    l = []
    rules_conf = {}
    rules_inter = {}
    scores = {}
    trans = prio.keys()

    for t in trans:
        for j in prio[t]:
            permutes = list(it.permutations(j))
            for perm in permutes:

                for i in range(1,t):
                    I = perm[:i]
                    J = perm[i:]
                    #getting all permutations
                    confi = confidence(frozenset(I),frozenset(J),frozenset(perm),
                                        mega_dict)
                    intr = interest(confi,frozenset(J),T,mega_dict)

                    if (confi >= min_conf):
                        Iz = []
                        Vz = []
                        for i in I:
                            Iz.append(col_names[i])
                        for j in J:
                            Vz.append(col_names[j])

                        ruled =(','.join(map(str, Iz)) , ','.join(map(str, Vz)))
                        rules_conf[(' | '.join(map(str, ruled)))] = confi

                    if(intr >= min_int):
                        Iz = []
                        Vz = []
                        for i in I:
                            Iz.append(col_names[i])
                        for j in J:
                            Vz.append(col_names[j])

                        ruled =(','.join(map(str, Iz)) , ','.join(map(str, Vz)))
                        rules_inter[(' | '.join(map(str, ruled)))] = intr

    return (rules_conf,rules_inter)



def main():
    """ Main function and user interface of this program """
    start_time = time.time()
    if len(sys.argv) < 3:
    	print("Not enough args")
    	exit()
    else:
        #Grab the argv
        min_sup = int(sys.argv[1])
        min_conf = float(sys.argv[2])
        min_int = float(sys.argv[3])

        #loading the data as a matrix
        mega_data = np.loadtxt('BobRoss.txt',dtype=str,delimiter=",")

        #getting frequent itemsets of size 1
        items = mega_data[:,4:]
        col_names = items[0,:]
        items = items[1:,:]
        T = items.shape[0]

        #mapping for column names
        n = len(col_names)
        L1 = freq_itemset_1(items, min_sup)
        mega_dict = {}

        #Print All the Itemsets of size 1
        print "\nPrinting itemsets of size 1 ...\n"
        for key, value in L1.iteritems():
            print col_names[key], ":", value
            mega_dict[frozenset([key])] = value
        print "\n"

        print "Running Apriori ......"
        prio1 = apriori(items,L1.keys(),min_sup,mega_dict)
        prio = prio1[0]
        mega_dict = prio1[1]

        print "\nPrinting itemsets of size n ...\n"
        for key, value in prio.iteritems():
            print "Number of frequent sets of size",key, ":", len(value)
        print "\n"

        print "Generating Rules ......"
        f=open('./testfile', 'w+')
        rules = gen_rules(prio,min_conf, min_int,col_names,T,mega_dict)
        print "***Printing Rules by INTEREST Theshhold***\n"
        print "The number of rules found is: ", len(rules[1]),"\n"

        #printing top 10 by interest
        x = sorted(rules[1].items(), key=itemgetter(1))
        #getting the top 10
        top_ten = x[-9:]

        while len(top_ten) > 0:
            temp = top_ten.pop()
            temp2 = temp[0].split(" | ")
            print "Rule : If ", temp2[0] , " then ", temp2[1]
            print "Score for rule: ", temp[1],"\n"

        print "\n"
        print "***Printing Rules by CONFIDENCE Theshhold***\n"
        print "The number of rules found is: ", len(rules[1]),"\n"

        #printing top 10 by interest
        y = sorted(rules[0].items(), key=itemgetter(1))
        #getting the top 10
        top_ten = y[-9:]

        while len(top_ten) > 0:
            temp = top_ten.pop()
            temp2 = temp[0].split(" | ")
            print "Rule : If ", temp2[0] , " then ", temp2[1]
            print "Score for rule: ", temp[1],"\n"

        print("Run Time --- %s seconds ---" % (time.time() - start_time))



if __name__ == "__main__":
    main()
