import unittest
from genes import *


class GenesTest(unittest.TestCase):
    def setUp(self):
        self.items = [
            Item(name='chair1', weight=4),
            Item(name='chair2', weight=4),
            Item(name='chair3', weight=4),
            Item(name='chair4', weight=4),
            Item(name='table', weight=20),
        ]
        self.truck_load = 60
        self.truck_cost = 50
        self.car_load = 12
        self.car_cost = 15
        self.basic_args = (self.truck_load, self.car_load,
                           self.truck_cost, self.car_cost)

    def test_gene_constructor(self):
        self.assertRaises(AssertionError, lambda: Gene(self.items, 20, 20, 20, 20))
        gene1 = Gene(self.items, *self.basic_args)
        self.assertEqual(gene1.subset, set(self.items))
        self.assertTrue(gene1.is_by_truck)

    def test_chromosomes(self):
        chromosome1 = Chromosome([self.items[:3], self.items[3:]], *self.basic_args)
        chromosome2 = Chromosome([self.items[:1], self.items[1:]], *self.basic_args)
        chromosome2.cross(chromosome1)


if __name__ == '__main__':
    unittest.main()
