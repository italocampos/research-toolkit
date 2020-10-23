# Research toolkit

This repository contains two auxiliary methods that compound my master's
research application: a **Tabu Search** and a **Brute Force** algorithms, both
applied to the electric network reconfiguration problem.


## Dependencies

This repository depends on some other Python modules. Below I listed these
dependencies:

- [Pandapower](http://www.pandapower.org/);
- [Color lib](https://github.com/italocampos/color);
- [Graph](https://github.com/italocampos/graphs) (in the adjacency matrix
form);

To run the features of this repository, install the modules above in your
Python env.


## Tabu Search

The Tabu Search (TS) is modeled according the constraints and criterias defined
in my master's research. To know how they work, refer to my master's thesis
(Brazilian portuguese only).


### Running the Tabu Search

After installed the dependencies, run the TS on two ways:

1. Importing it in a Python shell:

``` python
import ts
tl.run(loops = 10)
```

2. Running the file directly trought the Linux shell:

``` shell
python ts.py
```

Running the TS throught the Linux shell, the method will run 10 times and it
will show the results at the end. If you want to run the TS for a less times,
import it in a Python shell and set the `loops` parameter in when calling the
`run(int)` method.

To set the parameters of the search, see the initial variables of the code in
the `ts.py` file. All the parameters of the search are respectively comemented.


## Brute Force algorithm

The Brute Force (BF) algorithm aims to list the optimal solutions of the
choosed scenario. To keenly know how it works, refer to my master's thesis
(Brazilian portuguese only).


### Running the Brute Force algorithm

After installed the dependencies, run the BF on two ways:

1. Importing it in a Python shell:

``` python
import bf
bf.run()
```

2. Running the file directly trought the Linux shell:

``` shell
python bf.py
```

To set the parameters of the search, see the initial variables of the code in
the `bf.py` file. All the parameters of the search are respectively comemented.