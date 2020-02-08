# NOC-solve

## Requirements

- Linux
- Python3
- Z3 python API ([link](https://github.com/LIIHWF/ICAPS2020/releases/download/z3local/z3local.zip))
- [DOcplex](http://ibmdecisionoptimization.github.io/docplex-doc/) (`pip install docplex`)
- CPLEX 12.9.0 (with `oplrun` and `cpoptimizer`)

**Z3 python API has been modified**, the new one can download [here](https://github.com/LIIHWF/ICAPS2020/releases/download/z3local/z3local.zip), `Z3_Pareto.py` should be placed in the same directory as `z3local` and `libz3.so`.

## Instructions for solving

### Z3

```
Z3$ python3 Z3_Pareto.py [data-name]
```

for example:

```
$ python3 Z3_Pareto.py 4_2x2_m
> MP = 103	En = 1192	
> MP = 85	En = 1615	
> MP = 93	En = 1418	
> Time for adding constraints = 0.22244930267333984 s
> Time for finding solutions = 0.16423273086547852 s
> Total time = 0.38668203353881836 s
```

### CPLEX MIP

```
MIP$ python3 cplex_mp.py [data-name]
```

for example:

```
$ python3 cplex_mp.py 4_2x2_m
> MP = 103 	En = 1192
> MP = 85 	En = 1615
> MP = 93 	En = 1418
> Total time: 7.67651891708374
```

### CPOptimizer

```
CPOptimizer$ python3 cp_pareto.py [data-name]
```

for example:

```
$ python3 cp_pareto.py 4_2x2_m
> MP = 103 	En = 1192
> MP = 85 	En = 1615
> MP = 93 	En = 1418
> Total time: 0.7674057483673096
```

## Implementation details

### Z3

Implementation with Z3's optimization of multiple objectives combined using Pareto fronts.

## MIP and CP

Both MIP and CP optimization are implemented by getting a satisfiable solution first and add new constraints Iteratively until there is not satisfiable solution.

Let $P$ be a set of constraints of the problem. Let $M(P)$ be the satisfiable solution of $P$. Maintain a solution set $S$ throughout the process. 

For each iteration:

- get a satisfiable solution $s=M(P)$. If there is not satisfiable solution, break iteration.
- update $S$ (remove all elements $e$ in $S$ if $\forall o\in \text{objectives},{s[o]<e[o]}$). 
- add a new constraint $\and_{e\in S}({\or_{o \in \text{objectives}}}o<e[o])$ to $P$.

