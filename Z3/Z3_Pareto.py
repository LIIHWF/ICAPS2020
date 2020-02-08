#!/usr/bin/python

from z3local.z3 import *
import sys
import time
import csv
import re


#---------------------Functions---------------------
def abs(x):
    return If(x >= 0, x, -x)

#For add constraints
def boolToInt(x):
    return If(x, 1, 0)

#For print out
def boolToInt_P(x):
    if x:
        return 1
    else:
        return 0

#---------------------Data---------------------
shared =[[[[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ] ,
[[0, 1, 0, 1] ,
[0, 0, 0, 0] ,
[0, 1, 0, 0] ,
[0, 0, 0, 0] ] ,
[[0, 0, 1, 1] ,
[0, 0, 1, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ] ,
[[0, 1, 1, 2] ,
[0, 0, 0, 1] ,
[0, 0, 0, 1] ,
[0, 0, 0, 0] ] ],
[[[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ] ,
[[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ] ,
[[0, 0, 1, 0] ,
[0, 0, 1, 1] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ] ,
[[0, 0, 0, 1] ,
[0, 0, 1, 1] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ] ],
[[[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ] ,
[[0, 1, 0, 0] ,
[0, 0, 0, 0] ,
[0, 1, 0, 1] ,
[0, 0, 0, 0] ] ,
[[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ] ,
[[0, 0, 0, 1] ,
[0, 0, 0, 0] ,
[0, 1, 0, 1] ,
[0, 0, 0, 0] ] ],
[[[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ] ,
[[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ] ,
[[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ] ,
[[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ,
[0, 0, 0, 0] ] ]
]
NbProcs = 0
NbTasks = 0
Cycles = 0
xN = 0
yN = 0
Time = []
Freq = []
dPk = []
sPk = []
comm = []
Dep = []

xP = []
yP = []
#---------------------Other Data---------------------
link = 7
rout = 8
delay = 8
elink = 1
erout = 4

maxP = 3

if len(sys.argv) > 1:
    with open('./data/' + sys.argv[1] + '.dat', 'r') as f:
        data = f.read().replace(';', '').replace('//', '#').replace("/*", '''"""''').replace('*/', '''"""''')
        exec(data)

Procs = range(NbProcs)
Tasks = range(NbTasks)
Cycle = range(Cycles)
#---------------------Varaibles---------------------
c2t = [[Bool('c2t[%s][%s]' % (i, j)) for j in Procs] for i in Procs]
a2c = [[Bool('a2c[%s][%s]' % (i, j)) for j in Procs] for i in Tasks]

Map = [[Bool('Map[%s][%s]' % (i, j)) for j in Procs] for i in Tasks]

PLoad = [[Int('PLoad[%s][%s]' % (i, j)) for j in Procs] for i in Tasks]

o = [[Bool('o[%s][%s]' % (i, j)) for j in Tasks] for i in Tasks]

q = [[[Bool('q[%s][%s][%s]' % (i, j, k)) for k in Tasks] for j in Tasks] for i in Procs]

dis = [[Int('dis[%s][%s]' % (i, j)) for j in Tasks] for i in Tasks]

Load = [Int('Load[%s]' % i) for i in Procs]

tao = [[Int('tao[%s][%s]' % (i, j)) for j in Tasks] for i in Cycle]
fin = [[Int('fin[%s][%s]' % (i, j)) for j in Tasks] for i in Cycle]
se = [[[Int('se[%s][%s][%s]' % (i, j, k)) for k in Tasks] for j in Tasks] for i in Cycle]
fe = [[[Int('fe[%s][%s][%s]' % (i, j, k)) for k in Tasks] for j in Tasks] for i in Cycle]
conflict = [[[[Bool('conflict[%s][%s][%s][%s]' % (i, j, k, l)) for l in Tasks] for k in Tasks] for j in Tasks] for i in Tasks]

MP = Int('MP')
Mc = Int('Mc')
En = Int('En')
Ed = Int('Ed')
Es = [Int('Es[%s]' % i) for i in Procs]
Ec = [[Int('Ec[%s][%s]' % (i, j)) for j in Tasks] for i in Tasks]
#---------------------Constraints ---------------------
startAdd = time.time()
opt = Optimize()

#for objective optimization
for k in Procs:
    opt.add(Load[k] == sum(PLoad[i][k] for i in Tasks))

for i in Tasks:
    for k in Procs:
        opt.add(Implies(a2c[i][k], PLoad[i][k] == Time[k][i]))
        opt.add(Implies(Not(a2c[i][k]), PLoad[i][k] == 0))


opt.add(Ed == sum((dPk[k] * Load[k]) for k in Procs) * Cycles)

for k in Procs:
    opt.add(Implies(Not(Or([a2c[i][k] for i in Tasks])), (Es[k] == 0)))
    opt.add(Implies(Or([a2c[i][k] for i in Tasks]), (Es[k] == sPk[k] * (MP - Load[k] * Cycles))))

for i in Tasks:
    opt.add(Ec[i][i] == 0)
    for j in Tasks:
        if i!=j:
            opt.add(Implies(Not(o[i][j]), (Ec[i][j] == 0)))
            opt.add(Implies(o[i][j], (Ec[i][j] == comm[i][j] * (erout * (dis[i][j] + 1) + elink * dis[i][j]) * Cycles)))

opt.add(En == Ed + sum(Es[k] for k in Procs) + sum(Ec[i][j] for i in Tasks for j in Tasks))
opt.add(Mc == sum(Ec[i][j] for i in Tasks for j in Tasks))

#every task can only be mapped to one processor
for i in Tasks:
    opt.add(AtLeast_Generator([Map[i][k] for k in Procs], 1))
    opt.add(AtMost_Generator([Map[i][k] for k in Procs], 1))

#every processor has at most n task
for k in Procs:
    opt.add(AtMost_Generator([Map[i][k] for i in Tasks], maxP))

#whether two tasks have communication cost
for i in Tasks:
    for j in Tasks:
        if i!=j:
            if Dep[i][j] == 0:
               opt.add(o[i][j] == False)
            else:
               opt.add(o[i][j]==Not(Or([And(Map[i][k],Map[j][k]) for k in Procs])))

#relation between tile and core
for k in Procs:
    opt.add(AtMost_Generator([c2t[k][c] for c in Procs], 1))
    opt.add(AtLeast_Generator([c2t[k][c] for c in Procs], 1))

for c in Procs:
    opt.add(AtMost_Generator([c2t[k][c] for k in Procs], 1))
    opt.add(AtLeast_Generator([c2t[k][c] for k in Procs], 1))

#relation between task and core
for i in Tasks:
    for c in Procs:
        for k in Procs:
            opt.add(Or(Not(Map[i][k]), Not(c2t[k][c]), a2c[i][c]))
for i in Tasks:
    opt.add(AtMost_Generator([a2c[i][c] for c in Procs], 1))
    opt.add(AtLeast_Generator([a2c[i][c] for c in Procs], 1))
for c in Procs:
    opt.add(AtMost_Generator([a2c[i][c] for i in Tasks], maxP))

#the execution sequence on every processor
for i in Tasks:
    for j in Tasks:
        for k in Procs:
            for l in Procs:
                if k!=l:
                    opt.add(q[k][i][i] == False)
                    opt.add(And(q[k][i][j], q[l][i][j]) == False)

for i in Tasks:
    for j in Tasks:
        if i!=j:
            for k in Procs:
                opt.add(Or(q[k][i][j], q[k][j][i]) == And(Map[i][k], Map[j][k]))
                opt.add(And(q[k][i][j], q[k][j][i]) == False)
for i in Tasks:
    for j in Tasks:
        for l in Tasks:
            if i!=j and j!=l:
                for k in Procs:
                    opt.add(Implies(And(q[k][i][j],q[k][j][l]), q[k][i][l]))

#conflict calculation
shareds = []
for k1 in Procs:
    for k2 in Procs:
        for k3 in Procs:
            for k4 in Procs:
                if shared[k1][k2][k3][k4] > 0:
                    shareds.append([k1,k2,k3,k4])

for i in Tasks:
    opt.add(conflict[i][i][i][i] == False)
    for j in Tasks:
        opt.add(conflict[i][i][j][j] == False)
        for l in Tasks:
            for r in Tasks:
                if i!=j and l!=r:
                    if Dep[i][j] == 1 and Dep[l][r] == 1:
                        opt.add(Implies(conflict[i][j][l][r], o[i][j]))
                        opt.add(Implies(conflict[i][j][l][r], o[l][r]))
                        opt.add(And(o[i][j], o[l][r], Or([And(Map[i][k1], Map[j][k2], Map[l][k3], Map[r][k4]) for k1, k2, k3, k4 in shareds])) == conflict[i][j][l][r])
                    else:
                        opt.add(conflict[i][j][l][r] == False)

#the distance between i and j
for i in Tasks:
    for j in Tasks:
        if i!=j:
            for k1 in Procs:
                for k2 in Procs:
                    opt.add(Implies(And(Map[i][k1], Map[j][k2]), dis[i][j] == abs(xP[k1] - xP[k2]) + abs(yP[k1] - yP[k2])))
                    
#quanatitive relation for the actions
for i in Tasks:
    for j in Tasks:
        for u in Cycle:
            opt.add(tao[u][i] >= 0)
            opt.add(se[u][i][j] >= 0)
            opt.add(fe[u][i][j] >= 0)
            opt.add(dis[i][i] >= 0)

#the execution time
for i in Tasks:
    for u in Cycle:
        opt.add(fin[u][i] == tao[u][i] + sum(PLoad[i][c] for c in Procs))

for i in Tasks:
    for j in Tasks:
        if Dep[i][j] == 1:
            for u in Cycle:
                opt.add(fin[u][i] <= se[u][i][j])
                opt.add(fe[u][i][j] <= tao[u][j])

#the cost spent for tranmission
for i in Tasks:
    for j in Tasks:
        for u in Cycle:
            if comm[i][j] == 0:
                opt.add(se[u][i][j] == 0)
                opt.add(fe[u][i][j] == 0)
            else:
                opt.add(se[u][i][j] <= fe[u][i][j])
                opt.add(Implies(Not(o[i][j]), (se[u][i][j] == fe[u][i][j])))
                opt.add(Implies(o[i][j], (se[u][i][j] + comm[i][j] * dis[i][j] * link + (dis[i][j] + 1) * rout <= fe[u][i][j])))

#the total cost is larger than the last execution of the last task
for i in Tasks:
    opt.add(MP >= fin[Cycles-1][i])

#the execution sequence in the same processor
for i in Tasks:
    for j in Tasks:
        if i!=j:
            for u in Cycle:
                for k in Procs:
                    opt.add(Implies(q[k][i][j],fin[u][i] <= tao[u][j]))

#the same task on different cycles
for i in Tasks:
    for u in Cycle:
        for v in Cycle:
            if u < v:
                opt.add(fin[u][i] <= tao[v][i])

#the execution of a task in later cycles should be later than the last executed task in earlier cycles
for i in Tasks:
    for j in Tasks:
        for u in Cycle:
            for v in Cycle:
                if u < v:
                    for k in Procs:
                        opt.add(Implies(q[k][i][j],fin[u][j] <= tao[v][i]))

#two tasks on the same processor cannot overlap
for i in Tasks:
    for j in Tasks:
        for u in Cycle:
            for v in Cycle:
                if i!=j:
                    opt.add(And(Or([And(Map[i][k],Map[j][k]) for k in Procs]), (tao[u][j] < fin[v][i]), (tao[v][i] < fin[u][j])) == False)

#two transfer from the same source and occupying the same link should be sequentical
for i in Tasks:
    for j in Tasks:
        for l in Tasks:
            if j != l:
                if comm[i][j] > 0 and comm[i][l] > 0:
                    for u in Cycle:
                        opt.add(And(conflict[i][j][i][l], (se[u][i][j] - se[u][i][l] - delay < 0), (se[u][i][l] - se[u][i][j] - delay < 0)) == False)

#two data transfer on the same resource cannot overlap
for i in Tasks:
    for j in Tasks:
        for l in Tasks:
            for r in Tasks:
                if i != l or j != r:
                    if comm[i][j] > 0 and comm[l][r] > 0:
                        for u in Cycle:
                            for v in Cycle:
                                opt.add(And(conflict[i][j][l][r], (se[u][i][j] - se[u][i][l] < delay), (se[u][i][l] - se[u][i][j] < delay), (se[u][i][j] - fe[v][l][r] < 0) ,(se[v][l][r] - fe[u][i][j] < 0)) == False)

#Symmetry Breaking
#For chips
for j in Procs:
    for k in Procs:
        if j < k:
            opt.add(Implies(Freq[j] == Freq[k], Load[j] >= Load[k]))
#For tiles
for i in Tasks:
    for j in Tasks:
        opt.add(Implies(And(Not(Or([q[0][h][i] for h in Tasks])), Not(Or([q[1][h][j] for h in Tasks])), Map[i][0], Map[j][1]), i > j))
for i in Tasks:
    for j in Tasks:
        opt.add(Implies(And(Not(Or([q[0][h][i] for h in Tasks])), Not(Or([q[3][h][j] for h in Tasks])), Map[i][0], Map[j][3]), i > j))


if len(sys.argv) == 3:
    if sys.argv[2] =="smt2":
        smtlib_location = "./result/NoC_SMT_LIB_"+ sys.argv[1] +".txt"
        cf = open(smtlib_location, "w")
        print(opt.sexpr(), file = cf)
        exit()
#---------------------Excute ---------------------
result_location = "./result/Z3_NoC_Z3Pareto_Result_"+ sys.argv[1] +".txt"

startFind = time.time()

Obj = [MP, En]
for i in range(len(Obj)):
    opt.minimize(Obj[i])
opt.set("priority", "pareto")
while opt.check() == sat:
    m = opt.model()
    for i in range(len(Obj)):
        print(Obj[i], "=", m[Obj[i]], end = "\t")
    print("")

endCheck = time.time()

print("Time for adding constraints =", startFind - startAdd, "s")
print("Time for finding solutions =", endCheck - startFind, "s")
print("Total time =", endCheck - startAdd, "s")
