from docplex.cp.model import CpoModel
from docplex.cp.expression import *
from docplex.cp.modeler import *
from docplex.cp.parameters import *


import sys

# =====================data============================


NbProcs = 4
NbTasks = 4
Cycles = 1
xN = 2
yN = 2


Time = [[19,14,17,19,15,19,17],[10,7,9,10,8,10,9],[19,14,17,19,15,19,17],[10,7,9,10,8,10,9]]

Freq = [1,2,1,2]

dPk = [10,20,10,20]
sPk = [3,6,3,6]
comm = [[0, 2, 0, 0, 2, 0, 0],
        [0, 0, 5, 0,  0, 0, 0],
        [0, 0, 0, 0, 11, 0, 0],
        [0, 0, 0, 0, 0, 8, 11],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0]]



Dep =  [[0, 1, 0, 0, 1, 0, 0],
[0, 0, 1, 0, 0, 0, 0],
[0, 0, 0, 0, 1, 0, 0],
[0, 0, 0, 0, 0, 1, 1],
[0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0]]

xP = [0,1,0,1]
yP = [0,0,1,1]


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

link = 7
rout = 8
delay = 8
elink = 1
erout = 4
maxP = 3
w1 = 1
w2 = 0



if len(sys.argv) > 1:
    with open('./data/' + sys.argv[1] + '.dat', 'r') as f:
        data = f.read().replace(';', '').replace('//', '#').replace("/*", '''"""''').replace('*/', '''"""''')
        exec(data)

Procs = range(NbProcs)
Tasks = range(NbTasks)
Cycle = range(Cycles)


# =====================data============================


# =====================variable========================


a2c2t = [[[[interval_var(length=Time[c][i], optional=True, name='a2c2t[%d][%d][%d][%d]'%(u, i,c,t)) for t in Procs] for c in Procs] for i in Tasks] for u in Cycle]
a2c = [[[interval_var(optional=True, name = 'a2c[%d][%d][%d]'%(u, i, c)) for c in Procs] for i in Tasks] for u in Cycle]
Run = [[interval_var(name='Run[%d][%d]'%(u, i)) for i in Tasks] for u in Cycle]

a2t = [integer_var(0, NbProcs - 1, name='a2t[%d]'%(i)) for i in Tasks]
c2t = [integer_var(0, NbProcs - 1, name='c2t[%d]'%(c)) for c in Procs]

Comm = [[[interval_var(optional=True, name='Comm[%d][%d][%d]'%(u, i, j)) for j in Tasks] for i in Tasks] for u in Cycle]


conflict = [[[[binary_var(name="conflict[%d][%d][%d][%d]"%(i,j,k,l)) for l in Tasks] for k in Tasks] for j in Tasks] for i in Tasks]

Load = [integer_var(0,name="Load[%d]"%i) for i in Procs]

o = [[binary_var(name="o[%d][%d]"%(i,j)) for j in Tasks] for i in Tasks]

dis = [[integer_var(0, name="dis[%d][%d]"%(i, j)) for j in Tasks] for i in Tasks]


MP = integer_var(0, name="MP")
En = integer_var(0, name="En")
Es = [integer_var(0, name="Es[%d]"%i) for i in Procs]
Ec = [[integer_var(0, name="Ec[%d][%d]"%(i,j)) for j in Tasks] for i in Tasks]
Ed = integer_var(0, name="Ed")


se = [[integer_var(0, name="se[%d][%d]"%(i,j)) for j in Tasks] for i in Tasks]
fe = [[integer_var(0, name="fe[%d][%d]"%(i,j)) for j in Tasks] for i in Tasks]

# =====================varibale========================



# =====================constraints=====================

start = time.time()

mdl = CpoModel()


for u in Cycle:
    for i in Tasks:
        for c in Procs:
            for t in Procs:
                a2c2t[u][i][c][t].set_start_min(0)

for u in Cycle:
    for i in Tasks:
        for j in Tasks:
            Comm[u][i][j].set_start_min(0)

for u in Cycle:
    for i in Tasks:
        for c in Procs:
            mdl.add(alternative(a2c[u][i][c], a2c2t[u][i][c]))

for u in Cycle:
    for i in Tasks:
        mdl.add(alternative(Run[u][i], a2c[u][i]))

for u in range(Cycles - 1):
    for i in Tasks:
        for c in Procs:
            for t in Procs:
                mdl.add(if_then(presence_of(a2c2t[u][i][c][t]), presence_of(a2c2t[u+1][i][c][t])))
    for i in Tasks:
        for j in Tasks:
            mdl.add(if_then(presence_of(Comm[u][i][j]), presence_of(Comm[u+1][i][j])))

for i in Tasks:
    for c in Procs:
        for t in Procs:
            mdl.add(if_then(presence_of(a2c2t[0][i][c][t]), a2t[i] == t))
            mdl.add(if_then(presence_of(a2c2t[0][i][c][t]), c2t[c] == t))

for c in Procs:
    mdl.add(sum([presence_of(a2c[0][i][c]) for i in Tasks]) <= maxP)

mdl.add(all_diff(c2t))


for i in Procs:
    for j in Procs:
        if i < j and Freq[i] == Freq[j]:
            mdl.add(c2t[i] < c2t[j])


for i in Tasks:
    for j in Tasks:
        if Dep[i][j]:
            mdl.add(presence_of(Comm[0][i][j]) == (mdl.sum((presence_of(a2c[0][i][k]) + presence_of(a2c[0][j][k]) == 2) for k in Procs) == 0))
        else:
            mdl.add(presence_of(Comm[0][i][j]) == 0)

for k in Procs:
    Load[k] = mdl.sum((presence_of(a2c[0][i][k])) * length_of(Run[0][i]) for i in Tasks)

for c in Procs:
    mdl.add(no_overlap([a2c[u][i][c] for i in Tasks for u in Cycle]))

for i in Tasks:
    mdl.add(dis[i][i] == 0)

for i in Tasks:
    for j in Tasks:
        if i != j:
            for t1 in Procs:
                for t2 in Procs:
                    mdl.add(if_then(logical_and(a2t[i] == t1, a2t[j] == t2), dis[i][j] == abs(xP[t1]-xP[t2]) + abs(yP[t1]-yP[t2])))

shareds = []
for k1 in Procs:
    for k2 in Procs:
        for k3 in Procs:
            for k4 in Procs:
                if shared[k1][k2][k3][k4] > 0:
                    shareds.append([k1,k2,k3,k4])

for i in Tasks:
    for j in Tasks:
        for l in Tasks:
            for r in Tasks:
                if Dep[i][j] == Dep[l][r] == 1:
                    mdl.add(conflict[i][j][l][r] == (presence_of(Comm[0][i][j]) + presence_of(Comm[0][l][r]) + (sum(((a2t[i] == c1) + (a2t[j] == c2) + (a2t[l] == c3) + (a2t[r] == c4) == 4) for c1, c2, c3, c4 in shareds) > 0) == 3))
                else:
                    mdl.add(conflict[i][j][l][r] == 0)

for u in Cycle:
    for i in Tasks:
        for j in Tasks:
            mdl.add(end_before_start(Run[u][i], Comm[u][i][j]))
            mdl.add(if_then(presence_of(Comm[u][i][j]), length_of(Comm[0][i][j]) == comm[i][j] * dis[i][j] * link + (dis[i][j] + 1) * rout))

for u in Cycle:
    for i in Tasks:
        for j in Tasks:
            if Dep[i][j]:
                mdl.add(end_before_start(Run[u][i], Run[u][j]))

for u in Cycle:
    for i in Tasks:
        for j in Tasks:
            for l in Tasks:
                if j != l and Dep[i][j] and Dep[i][l]:
                    mdl.add(if_then(conflict[i][j][i][l] == 1, (start_of(Comm[u][i][j]) >= start_of(Comm[u][i][l]) + delay) + (start_of(Comm[u][i][l]) >= start_of(Comm[u][i][j]) + delay) >= 1))

for i in Tasks:
    for j in Tasks:
        for l in Tasks:
            for r in Tasks:
                if Dep[i][j] and Dep[l][r] and i != l and j != r:
                    for u in Cycle:
                        for v in Cycle:
                            mdl.add(if_then(conflict[i][j][l][r] == 1, (start_of(Comm[u][i][j]) >= start_of(Comm[u][l][r]) + delay) + (start_of(Comm[u][l][r]) >= start_of(Comm[u][i][j]) + delay) + (start_of(Comm[u][i][j]) >= end_of(Comm[v][l][r])) + (start_of(Comm[v][l][r]) >= end_of(Comm[u][i][j])) >= 1))

for u in Cycle:
    for i in Tasks:
        for j in Tasks:
            if Dep[i][j] == 1:
                mdl.add(end_before_start(Comm[u][i][j], Run[u][j]))


mdl.add(MP == mdl.max(end_of(Run[u][i]) for i in Tasks for u in Cycle))

for i in Tasks:
    for j in Tasks:
        mdl.add(if_then(presence_of(Comm[0][i][j]), Ec[i][j] == comm[i][j] * (erout * (dis[i][j] + 1) + elink * dis[i][j] * Cycles)))
        mdl.add(if_then(presence_of(Comm[0][i][j]) == 0, Ec[i][j] == 0))

for k in Procs:
    mdl.add(if_then(Load[k] == 0, Es[k] == 0))
    mdl.add(if_then(Load[k] > 0, Es[k] == sPk[k] * (MP - Load[k] * Cycles)))

Ed = mdl.sum(dPk[k] * Load[k] for k in Procs) * Cycles
Em = mdl.sum(Ec[i][j] for i in Tasks for j in Tasks)
mdl.add(En == Ed + Em + mdl.sum(Es[k] for k in Procs))

# =====================constraints=====================

w1 = 1
w2 = 0

if len(sys.argv) >= 3:
    w1 = int(sys.argv[2])

if len(sys.argv) >=4:
    w2 = int(sys.argv[3])

params = CpoParameters()
params.set_LogVerbosity('Quiet')

mdl.set_parameters(params)

TIMELIMIT = 120

msol = mdl.solve(TimeLimit = TIMELIMIT)
pareto_sol = set()

def add_pareto(sol):
    global pareto_sol
    temp = pareto_sol.copy()
    for item in pareto_sol:
        if sum((sol[i] <= item[i]) for i in range(len(sol))) == len(sol):
            temp.remove(item)
    pareto_sol = temp
    pareto_sol.add(sol)
            
object_list = [MP, En]

object_tuple = None
while msol.is_solution() and TIMELIMIT > 0:
    object_tuple = tuple(msol[obj] for obj in object_list)
    add_pareto(object_tuple)
    print(pareto_sol)
    pareto_constraint = mdl.sum((mdl.sum((object_list[i] < item[i]) for i in range(len(item))) >= 1) for item in pareto_sol) == len(pareto_sol)
    repeat_constraint = mdl.sum(logical_and(MP == item[0], En == item[1]) for item in pareto_sol) == 0
    mdl.add(pareto_constraint)
    mdl.add(repeat_constraint)
    start_ = time.time()
    msol = mdl.solve(TimeLimit = TIMELIMIT)
    end_ = time.time()
    TIMELIMIT -= end_ - start_
    mdl.remove(pareto_constraint)
    mdl.remove(repeat_constraint)

end = time.time()

for item in pareto_sol:
    print('MP =', item[0], '\tEn =', item[1])

print("Total time:", end - start)

