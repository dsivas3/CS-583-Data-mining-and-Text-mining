#!/usr/bin/python3

#MS Apriori Algorithm to generate frequent itemsets with different MIS values

import collections
import itertools
import re
import sys

#default SDC=1.0
sdc = 1.0
must_have = []

def main(*args):
    global must_have
    if len(args) != 3:
        print("Incorrect arguments. Please pass the names of the transaction file, the parameter file and the output file")
        sys.exit()

    # transaction file - arg1 Parameter file- arg2 and output file - arg3

    transaction_file_name = args[0]
    parameter_file_name = args[1]
    output_file_name = args[2]

    T = []
    F = []
    MS = {}
    c_count = {}
    tail_count = {}
    cannot_be_together = []
    
    file_read(transaction_file_name, parameter_file_name, T, MS, cannot_be_together)
    F, c_count, tail_count = MSApriori(T, MS)
    if(cannot_be_together != []):
        apply_cannot_be_together_constraint(F, cannot_be_together)
    if(must_have != []):
        apply_must_have_constraint(F)
    write_output(output_file_name, F, c_count, tail_count)

#read transaction and parameter file

def file_read(transaction_file, parameter_file, transaction_list, mis_dict, cannot_be_together):
    global sdc, must_have

    with open(transaction_file) as t_file:
        for line in t_file:
            transaction = re.sub('[\{\}\s]', '', line).split(',')
            transaction_list.append(transaction)
    
    with open(parameter_file) as p_file:
        line = p_file.readline()
        while line is not '':
            if 'MIS' in line:
                temp = line.split('=')
                temp[0] = re.sub('MIS|\(|\)|\s', '', temp[0])
                mis_dict[temp[0]] = float(temp[1].strip())
            if 'SDC' in line:
                sdc = float(line.split('=')[1].strip())
            if 'cannot_be_together' in line:
                temp = line.split(':')
                temp[1] = temp[1].replace(' ', '').replace('},{', '-')
                f_items = re.sub('[\{\}]', '', temp[1]).strip().split('-')
                for i in range(len(f_items)):
                    cannot_be_together.append(list(f_items[i].split(',')))
            if 'must-have' in line:
                temp = line.split(':')
                temp[1] = temp[1].replace(' ', '')
                must_have = temp[1].strip().split('or')
            line = p_file.readline()

#Init pass to generate M and support count 

def init_pass(M, T, MS, sup_count, L, item_pos):
    default_sup_count = 0
    num_of_transactions = len(T)
    num_of_items = len(M)
    
    for item in M:
        for transaction in T:
            if item in transaction:
                sup_count[item] = sup_count.get(item, default_sup_count) + 1

    i = 0
    while i < num_of_items:
        if M[i] in sup_count.keys() and sup_count[M[i]] / num_of_transactions >= MS[M[i]]:
            L.append(M[i])
            break
        i = i + 1

    for j in range(i + 1, num_of_items):
        if M[j] in sup_count.keys() and sup_count[M[j]] / num_of_transactions >= MS[M[i]]:
            L.append(M[j])

    for i in range(len(L)):
        item_pos[L[i]] = i


#level 2 candidate generation takes L as input and generates C2 
#by checking 2 conditions (SDC and support)

def level2_candidate_gen(L, T, MS, sup_count):
    global sdc
    
    C2 = []
    
    for l in range(len(L) - 1):
        if sup_count[L[l]] / len(T) >= MS[L[l]]:
            for h in range(l + 1, len(L)):
                if sup_count[L[h]] / len(T) >= MS[L[l]] and abs((sup_count[L[h]] / len(T)) - (sup_count[L[l]] / len(T))) <= sdc:
                    c2 = []
                    c2.append(L[l])
                    c2.append(L[h])
                    C2.append(tuple(c2))
    
    return C2


#level 3 to 'k' candidate generation (C3 to Ck generation)

def MScandidate_gen(Fk_1, T, MS, sup_count, item_pos):
    global sdc
    
    Ck = []

    for l in range(len(Fk_1) - 1):
        for h in range(l + 1, len(Fk_1)):
            i = 0
            while Fk_1[l][i] == Fk_1[h][i] and i < len(Fk_1[l]) - 1:
                i = i + 1
            if i == len(Fk_1[l]) - 1 and item_pos[Fk_1[l][i]] < item_pos[Fk_1[h][i]] and abs((sup_count[Fk_1[l][i]] / len(T)) - (sup_count[Fk_1[h][i]] / len(T))) <= sdc:
                c = Fk_1[l] + tuple([Fk_1[h][-1]])
                subsets = set(itertools.combinations(c, len(c) - 1))
                flag = True
                for s in subsets:
                    if c[0] in s or MS[c[0]] == MS[c[1]]:
                        if tuple(s) not in Fk_1:
                            flag = False
                if flag == True:
                    Ck.append(c)

    return Ck
    


#MS Apriori takes T(set of all transactions) and MS(MIS values for each item) and returns frequent itemsets

def MSApriori(T, MS):
    global sdc
    
    c_count = {}
    tail_count ={}
    item_pos = {}
    L = []
    F = []
    FI = []

    M = sorted(MS.keys(), key = lambda i:(MS[i], i))
    init_pass(M, T, MS, c_count, L, item_pos)
    
    if len(L) != 0:
        for i in range(len(L)):
            if c_count[L[i]] / len(T) >= MS[L[i]]:
                F.append(L[i])
                FI.append(L[i])

    Fk_1 = F

    k = 2
    while len(F) != 0:
        F = []
#seperate frequent itemset generator for level 2 (k=2)
        if k == 2:
            Ck = level2_candidate_gen(L, T, MS, c_count)
        else:   
            Ck = MScandidate_gen(Fk_1, T, MS, c_count, item_pos)

        for t in T:
            for c in Ck:
                if set(c).issubset(set(t)):
                    c_count[tuple(c)] = c_count.get(tuple(c), 0) + 1
                if set(c[1:]).issubset(set(t)):
                    tail_count[tuple(c)] = tail_count.get(tuple(c), 0) + 1

        
        for c in Ck:
            if c in c_count.keys() and c_count[tuple(c)] / len(T) >= MS[c[0]]:
                F.append(c)
                FI.append(c)

        Fk_1 = F
        k = k + 1

    return FI, c_count, tail_count


#cannot-be-together constraint prunes sets which contain elements that cannot-be-together

def apply_cannot_be_together_constraint(F, cannot_be_together):
    for c in cannot_be_together:
        i = len(F) - 1
        while i >= 0:
            if (set(c).issubset(set(F[i]))):
                F.remove(F[i])
            i = i - 1

#must-have constraint prunes itemsets which does not contain these elements

def apply_must_have_constraint(F):
    global must_have
    
    i = len(F) - 1
    while i >= 0:
        flag = False
        for m in must_have:
            if type(F[i]) == type(''):
                if set(tuple([m])).issubset(set(tuple([F[i]]))):
                    flag = True
            else:
                if set(tuple([m])).issubset(set(F[i])):
                    flag = True

        if flag == False:
            F.remove(F[i])
        
        i = i - 1
    

#writes output to the file

def write_output(output_file_name, F, c_count, tail_count):
    if len(F) > 0:
        FI = {}
        for i in F:
            if type(i) == type(''):
                if 1 not in FI.keys():
                    t = []
                    t.append(i)
                    FI[1] = list(t)
                else:
                    FI[1].append(i)
            else: 
                if len(i) in FI.keys():
                    FI[len(i)].append(i)
                else:
                    t = []
                    t.append(i)
                    FI[len(i)] = list(t)
            
        with open(output_file_name, 'w') as o_file:
            for n in range(1, len(FI) + 1):
                print("Frequent {}-itemsets\n".format(n))
                o_file.write("Frequent {}-itemsets\n\n".format(n))
                for i in range(len(FI[n])):
                    print("\t{} : {{".format(c_count[FI[n][i]]), end = "")
                    o_file.write("\t{} : {{".format(c_count[FI[n][i]]))
                    if n == 1:
                        print(FI[n][i], end = "")
                        o_file.write(FI[n][i])
                        print("}")
                        o_file.write("}\n")
                    else:
                        for k in range(len(FI[n][i]) - 1):
                            print("{}, ".format(FI[n][i][k]), end = "")
                            o_file.write("{}, ".format(FI[n][i][k]))
                        print(FI[n][i][-1], end = "")
                        o_file.write(FI[n][i][-1])
                        print("}")
                        o_file.write("}\n")
                        print("Tailcount = {}".format(tail_count[FI[n][i]]))
                        o_file.write("Tailcount = {}\n".format(tail_count[FI[n][i]]))
                print("\n\tTotal number of frequent {}-itemsets = {}\n\n".format(n, len(FI[n])))
                o_file.write("\n\tTotal number of frequent {}-itemsets = {}\n\n".format(n, len(FI[n])))

    elif len(F) == 0:
        print("There are no frequent itemsets\n")
        with open(output_file_name, 'w') as o_file:
            o_file.write("There are no frequent itemsets\n")


if __name__ == "__main__": main(*sys.argv[1:])