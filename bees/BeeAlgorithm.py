from bees import Scout, FlowerPatch
from ProblemParameters import ProblemParameters
from Item import Item
import random


class BeeAlgorithm:
    def __init__(self, ns, nb, ne, nre, nrb, rn, fpf: callable, sf: callable, pp: ProblemParameters):
        """
        Keyword arguments:
            ns - number of scouts
            nb - number of best sites nb < ns
            ne - number of the very best sites (elite sites) ne < nb
            nre - number of foragers recruited by the scouts that found ne elite sites
            nrb - number of foragers recruited by the scouts that found best sites that are not elite sites nrb < nre
            rn - number by how much the flower patch is suppose to be reduced after not founding a better solution
            fpf - function that determines size of the flower patch based on the scouts solution fitness
            sf - function that returns random solution
            pp - problem parameters (car/truck load, car/truck cost)
        """
        self.ns = ns
        self.nb = nb
        self.ne = ne
        self.nre = nre
        self.nrb = nrb
        self.rn = rn
        self.fpf = fpf
        self.sf = sf
        self.pp = pp
        self.scouts = []
        self.flower_patches = []

    def run(self, n):
        """
        Keyword arguments:
            n - number of times the algorithm is executed
        """
        for i in range(self.ns):
            self.scouts.append(Scout(self.sf(), i))
            self.flower_patches.append(FlowerPatch(self.scouts[i], self.fpf))

        for _ in range(n):
            print(max(self.scouts, key=lambda s : s.fitness).fitness)
            found_better = self.local_search()
            self.neighbourhood_shrinking(found_better)
            self.global_search()

    def local_search(self):
        found_better = [False] * self.ns
        ss = sorted(self.scouts, key=lambda s: s.fitness, reverse=True)
        for scout in ss[:self.ne]:
            mf = scout.fitness
            better_sol = None
            for _ in range(self.nre):
                sol = random.choice(self.flower_patches[scout.i].solutions)
                if sol.fitness > mf:
                    found_better[scout.i] = True
                    mf = sol.fitness
                    better_sol = sol
            if better_sol is not None:
                new_scout = Scout(better_sol, scout.i)
                self.flower_patches[scout.i] = FlowerPatch(new_scout, self.fpf)
                self.scouts[scout.i] = new_scout

        for scout in ss[self.ne:self.nb]:
            mf = scout.fitness
            better_sol = None
            for _ in range(self.nrb):
                sol = random.choice(self.flower_patches[scout.i].solutions)
                if sol.fitness > mf:
                    found_better[scout.i] = True
                    mf = sol.fitness
                    better_sol = sol
            if better_sol is not None:
                new_scout = Scout(better_sol, scout.i)
                self.flower_patches[scout.i] = FlowerPatch(new_scout, self.fpf)
                self.scouts[scout.i] = new_scout
        return found_better

    def neighbourhood_shrinking(self, found_better):
        for i, b in enumerate(found_better):
            if not b:
                if len(self.flower_patches[i].solutions) > self.rn:
                    self.flower_patches[i].solutions = self.flower_patches[i].solutions[:-self.rn]

    def global_search(self):
        ss = sorted(self.scouts, key=lambda s: s.fitness, reverse=True)
        for scout in ss[self.nb:]:
            self.scouts[scout.i] = Scout(self.sf(), scout.i)
