# Algorytm genetyczny
### Idea matematyczna

## 1. Reprezentacja genetyczna
Pojedynczy podział zbioru wejściowego $S$, tj. $P=\{P_1, P_2, ..., P_m\} \sub 2^S$, można reprezentować jako jeden chromosom, w którym genami są poszczególne podzbiory razem z informacją, jaki transport jest wymagany do ich przewozu.

Taki podział wymaga metody uporządkowania, której definicja zbioru nie zapewnia. Ten problem będzie rozwiązany w dalszych sekcjach.

## 2. Funkcja sprawności
Inspirując się [1], definiujemy funcję sprawności zarówno dla całego rozwiązania, jak i pojedynczego genu. Sprawność rozwiązania będzie liczona jako zwykła przeciwność funkcji kosztu, natomiast sprawność genu jako:
$$
fitness(P_i, trans_i) = \begin{cases}
mass(P_i) \over l_C & trans_i = car \land mass(P_i) < l_C \\
mass(P_i) \over l_T & trans_i = truck \land mass(P_i) < l_T \\
0 & \text{w p.w.}
\end{cases}
$$


## N. Referencje
1. http://www.cs.uno.edu/people/faculty/bill/GAs-for-PartitioningSets-IJAIT-2001.pdf