
# -*- coding: UTF-8 -*-
import os
import sys
import re
import time
model_file = open('model.mod', 'r')
model = model_file.read()
TRUNCATE = len(model.strip().strip('}'))
model_file.close()

def model_clear():
    solve_file.truncate(TRUNCATE)
    solve_file.seek(TRUNCATE)

def model_add(s):
    solve_file.write(s)
    solve_file.truncate()

def model_finish():
    solve_file.write('\n}\n')
    solve_file.truncate()

obj = ['MP', 'En']
obj_re = [re.compile('%s = \d+'%o) for o in obj]

solve_file = open('solve.mod', 'w')
model_add(model)
sol_file = open('log.txt', 'r')

def call_solve(TimeLimit = None):
    if TimeLimit:
        os.system("oplrun -v solve.mod ./data/%s.dat > log.txt" % (sys.argv[1]))
    else:
        os.system("oplrun -v solve.mod ./data/%s.dat > log.txt" % sys.argv[1])


def get_sol():
    sol_file.seek(0)
    sol = sol_file.read()
    if 'no solution' in sol:
        return None
    else:
        try:
            ret = []
            for r in obj_re:
                ret.append(eval(r.search(sol).group().split()[-1]))
            return tuple(ret)
        except:
            return None

        
pareto_sol = set()
def add_pareto(sol):
    global pareto_sol
    temp = pareto_sol.copy()
    for item in pareto_sol:
        if sum((sol[i] <= item[i]) for i in range(len(sol))) == len(sol):
            temp.remove(item)
    pareto_sol = temp
    pareto_sol.add(sol)

start = time.time()      
call_solve()
sol = get_sol()
print(sol)
TimeLimit = 3600

while sol and TimeLimit > 0:
    add_pareto(sol)
    print(pareto_sol)

    model_clear()
    pareto_constraint = ''
    for item in pareto_sol:
        pareto_constraint += '('
        for i in range(len(item)):
            if i > 0:
                pareto_constraint += '+'
            pareto_constraint += '(' + obj[i] + '<=' + str(item[i] - 1) + ')'
        pareto_constraint += '>= 1)'
        pareto_constraint += '+'
    pareto_constraint = pareto_constraint[:-1] + '== %d;'%len(pareto_sol)
    model_add(pareto_constraint)
    model_finish()
    start_ = time.time()
    call_solve(TimeLimit)
    end_ = time.time()
    TimeLimit -= end_ - start_
    sol = get_sol()
end = time.time()
for sol in pareto_sol:
    print('MP =', sol[0], '\tEn =', sol[1])

print('Total time:', end - start)

solve_file.close()
sol_file.close()


