import re
import itertools

ListofTransaction = []
sdc = 0.0


# Function to read input-data file as list of list
def Readinput():
    del ListofTransaction[:]

    input_file = open("input-data.txt", "r")
    # input_file = open("Test/data-1.txt", "r")
    lines = input_file.readlines()
    for line in lines:
        ListofTransaction.append(line[1:line.find('}')].replace(' ', '').split(','))
    input_file.close()


# Function to read input-parameter file as : MIS into dictionary, cannot_have_together and must_have into list, it also sorts MIS values
def paramfile():
    MIS = {}
    cannot_be_together = []
    must_have = []
    param = open("parameter-file.txt", "r")
    # param = open("Test/para1-1.txt", "r")
    data = [row for row in param]

    for index, d in enumerate(data):
        if d[0] == 'M':
            match = re.match(r'^.*\((.*)\).*= (\d*\.\d*)', d)
            MIS[match.group(1)] = float(match.group(2))
        elif d[0] == 'S':
            sdc = float(re.match(r'.*= (.*)', d).group(1))
        elif d[0] == 'm':
            must_have = [x.strip() for x in d.split(':')[1].split('or')]
        elif d[0] == 'c':
            elements = [x.strip() for x in d.split(':')[1].split('}, ')]
            for element in elements:
                cannot_be_together.append(element[1:].replace('{', '').replace(' ', '').replace('}', '').split(','))
    param.close()
    return MIS, cannot_be_together, must_have, sdc


# Initial pass
def init_pass(M, T):
    L = []
    for transaction in ListofTransaction:
        for item in transaction:
            if item in list(Support_count.keys()):
                Support_count[item] += 1
            else:
                Support_count.update({item: 1})

    for items in M:
        if (Support_count[items] / n >= MIS[items]):
            L.append(items)
            break

    for items in M:
        if items in Support_count.keys():
            if (Support_count[items] / n >= MIS[L[0]] and items != L[0]):
                L.append(items)
    # print(L)
    return L


# Function to  calculate Frequent 1- itemset
def Frequent1(L):
    F1 = []
    for items in L:
        if (Support_count[items] / n >= MIS[items]):
            F1.append(items)
    return F1


# Level 2 candidate generation
def level2_candidate_gen(L):
    c = []
    for i, l in enumerate(L):
        if (Support_count[l] / n >= MIS[l]):
            for h in range(i + 1, len(L)):
                if Support_count[L[h]] / n >= MIS[l] and (abs(Support_count[L[h]] / n - Support_count[l] / n) <= sdc):
                    twoItemsList = []
                    count = 0
                    if L[i] in cannot_be_together:
                        count = count + 1
                    if L[h] in cannot_be_together:
                        count = count + 1
                    if count != 2:
                        twoItemsList.append(L[i])
                        twoItemsList.append(L[h])
                        c.append({'c': twoItemsList, 'count': 0, 'tailcount': 0})
    return c


# Level 2 candidate generation
def MS_candidate_gen(F, k):
    c = []
    for i, f1 in enumerate(F):
        for j, f2 in enumerate(F[i + 1:]):
            if set(f1[:-1]) == set(f2[:-1]) and abs(Support_count[f2[k - 2]] / n - Support_count[f1[k - 2]] / n) <= sdc:
                x = list(f1)
                x.append(f2[k - 1])

                delete = False
                for s in list(itertools.combinations(x, k)):
                    if x[0] in s or MIS[x[0]] == MIS[x[1]]:
                        if list(s) not in F:
                            delete = True
                if not delete:
                    c.append({'c': x, 'count': 0, 'tailcount': 0})
    return c


# Ms-Apriori
Readinput()
MIS, cannot_be_together, must_have, sdc = paramfile()
n = len(ListofTransaction)
Support_count = {}
M = []
C = {}
F = []
Final_F = []
for item, mis in sorted(MIS.items(), key=lambda x: (x[1])):
    M.append(item)

L = init_pass(M, ListofTransaction)
F1 = Frequent1(L)
F.append(F1)

k = 1
while (len(F[k - 1]) != 0):

    if (k == 1):
        C[k] = level2_candidate_gen(L)

    else:
        C[k] = MS_candidate_gen(F[k - 1], k)
    for c in C[k]:
        for transaction in ListofTransaction:
            if set(c['c']).issubset(transaction):
                c['count'] += 1
            p = transaction
            if (set(c['c'][1:])).issubset(transaction):
                c['tailcount'] += 1
    Fk = []
    for c in C[k]:
        if c['count'] / n > MIS[c['c'][0]]:
            Fk.append(c['c'])
    F.append(Fk)
    k = k + 1

# print (F)

for k in range(1, len(F) - 1):
    for f in F[k]:
        delete = False
        if set(f).intersection(set(must_have)):
            for c in cannot_be_together:
                if set(c).issubset(set(f)):
                    delete = True
                    break
            if not delete:
                Final_F.append(f)
# print("       ",len(F),"   ",len(C))
f = open("Output_MS_Apr.txt", "w+")
f.write("Frequent 1-itemsets\n")
cnt1 = 0
for item in F[0]:
    if item in must_have:
        f.write("\t%s:" % Support_count[item])
        f.write("  {%s}\n" % item)
        cnt1 += 1
f.write("\n\tTotal number of frequent 1-itemsets = %s\n" % str(cnt1))

x = 1
while x != len(C):

    f.write("\nFrequent %s-itemsets\n\n" % str(x + 1))
    z = 0
    for c in C[x]:
        if c['count'] != 0 and c['c'] in F[x] and c['c'] in Final_F:
            z += 1
            f.write("\t%s : " % str(c['count']))
            f.write("%s \n" % str(set(c['c'])).replace('\'', ''))
            f.write("Tailcount = %s \n" % str(c['tailcount']).replace('\'', ''))
    if z != 0:
        f.write("\n\tTotal number of frequent %s-itemsets =" % str(x + 1))
        f.write(" %s \n" % str(z))
    x += 1
f.close()

if z == 0:
    f = open("Output_MS_Apr.txt", "r")
    line = f.readlines()
    x = len(line)
    x = x - 2
    open("Output_MS_Apr.txt", "w").writelines(line[:x])
    f.close()