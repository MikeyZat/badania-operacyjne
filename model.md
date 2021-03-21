# Model matematyczny

### Struktury danych

$S = \{s_1, s_2, ..., s_n\}$ - zbiór przedmiotów
$mass: S \rarr \reals$ - funkcja zwracająca masę przedmiotu
$l_T\in\reals$ - ładowność ciężarówki
$l_C\in\reals$ - ładowność samochodu osobowego
$p_T\in\reals$ - cena przejazdu ciężarówki
$p_C\in\reals$ - cena przejazdu samochodu osobowego

### Reprezentacja rozwiązania

$m \in \mathbb{Z}$ - liczba wszystkich przejazdów
dla $\{1, 2, ... m\}$:
1, 4, 6, 2 - ciężarówka
3, 5 - osobówka
7, 8 - osobówka

TO DO: jak to zapisać matematycznie?

### Funkcja celu

Minimalizacja łącznego kosztu wszystkich przejazdów ciężarówek i samochodów osobowych.

$f(\pi) = \sum_{i=1}^m \pi_i \cdot l_C + (1 - \pi_i) \cdot l_T \to min$

$\pi_i =
\begin{cases}
0 &\text{ jeśli przejazd i jest samochodem ciężarowym} \\
1 &\text{ jeśli przejazd i jest samochodem osobowym}
\end{cases}$

TO DO: dostosować do matematycznej definicji w **reprezentacja rozwiązania**

#### Odległość

TODO

### Warunki ograniczające

Skończone ładowności $l_T$ oraz $l_C$.
Wszystkie przedmiotu z $S$ muszą zostać załadowane.
