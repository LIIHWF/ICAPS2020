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

Both MIP and CP optimization are implemented by getting a satisfiable solution first and add new constraints Iteratively until there is not feasible solution.

Let <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;P" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\inline&space;P" title="P" /></a> be a set of constraints of the problem. Let <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;M(P)" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\inline&space;M(P)" title="M(P)" /></a> be the satisfiable solution of <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;P" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\inline&space;P" title="P" /></a>. Maintain a solution set <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;S" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\inline&space;S" title="S" /></a> throughout the process. 

For each iteration:

- get a satisfiable solution <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;s=M(P)" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\inline&space;s=M(P)" title="s=M(P)" /></a>. If there is no feasible solution, break iteration.
- update <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;S" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\inline&space;S" title="S" /></a> (remove all elements <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;e" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\inline&space;e" title="e" /></a> in <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;S" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\inline&space;S" title="S" /></a> if <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;\forall&space;o\in&space;\text{objectives},{s[o]<e[o]}" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\inline&space;\forall&space;o\in&space;\text{objectives},{s[o]<e[o]}" title="\forall o\in \text{objectives},{s[o]<e[o]}" /></a>). 
- add a new constraint <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;\bigwedge_{e\in&space;S}({\bigvee_{o&space;\in&space;\text{objectives}}}o<e[o])" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\inline&space;\bigwedge_{e\in&space;S}({\bigvee_{o&space;\in&space;\text{objectives}}}o<e[o])" title="\bigwedge_{e\in S}({\bigvee_{o \in \text{objectives}}}o<e[o])" /></a> to <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;P" target="_blank"><img src="https://latex.codecogs.com/svg.latex?\inline&space;P" title="P" /></a>.

