# Definicja problemu

## Ogólny opis problemu

Naszym celem jest rozwiązanie problemu przeprowadzki. Zakładamy, że mamy $n$ przedmiotów do przewiezienia z punktu A do punktu B. Każdy przedmiot ma określoną masę. Przewozić przedmioty możemy za pomocą naszego samochodu osobowego (ma on oczywiście skończoną ładowność $l_C$), lub też wynajętego samochodu ciężarowego (ładowność $l_T$). Każdy przejazd ma swoją cenę, w przypadku samochodu osobowego kosztuje nas paliwo ($p_C$), w przypadku ciężarowego koszt wynajmu + paliwo (łącznie $p_T$).
Naszym celem jest znalezienie takiego rozłożenia **wszystkich** przedmiotów pomiędzy przejazdy samochodem osobowym lub ciężarowym, aby łączny koszt naszej przeprowadzki był jak najmniejszy.

## Model matematyczny

### Struktury danych

$S = \{s_1, s_2, ..., s_n\}$ - zbiór przedmiotów
$mass: S \rarr \reals$ - funkcja zwracająca masę przedmiotu
$l_T\in\reals$ - ładowność ciężarówki
$l_C\in\reals$ - ładowność samochodu osobowego
$p_T\in\reals$ - cena przejazdu ciężarówki
$p_C\in\reals$ - cena przejazdu samochodu osobowego

### Reprezentacja rozwiązania

$P$ - partycja zbioru $S$ (podział przedmiotów na przejazdy odpowiednim samochodem)
$P = \{P_1, P_2, ..., P_m\} \sub 2^S$, gdzie:

- $\forall_{i, j \in \{1, 2, ..., m\}} i \ne j \implies P_i \cap P_j = \empty$
- $\displaystyle\bigcup_{i=1}^m P_i = S$
- $\displaystyle\forall_{P_i \in P} mass(P_i) = \sum_{s \in P_i}mass(s) \le l_T$

### Funkcja celu

Minimalizacja łącznego kosztu wszystkich przejazdów, tj.

$f(P) = \displaystyle\sum_{P_i \in P} cost(P_i) \to min$

, gdzie $cost(P_i)$ jest kosztem przejazdu $i$, tj.

$cost(P_i) =
\begin{cases}
0 & P_i = \empty \\
p_C & mass(P_i) \le l_C \\
p_T & mass(P_i) \gt l_C
\end{cases}$

#### Odległość

Specjalny przypadek odległości edycyjnej definiowany dla partycji zbioru:
https://www.sciencedirect.com/science/article/pii/S0166218X10003069

#### Sąsiedztwo

Pojedyncza zamiana elementu pomiędzy klasami (w tym stworzenie nowej klasy dla tego elementu).

### Warunki ograniczające

* Skończone ładowności $l_T$ oraz $l_C$.  
* Wszystkie przedmiotu z $S$ muszą zostać załadowane.  
* *Implicite* założenia o ładownościach i cenach:
    * $l_C \lt l_T$
    * $p_C \lt p_T$
