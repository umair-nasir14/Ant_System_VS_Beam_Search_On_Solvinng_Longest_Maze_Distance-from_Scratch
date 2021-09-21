from random import random, seed
from collections import defaultdict

from .utils import measure_time


class AntSystemSolver:
    def __init__(self, ant_steps, ants_count):
        self._ant_steps = ant_steps
        self._ants_count = ants_count

        self._r = 0.1
        self._a = 0.2
        self._c = 1.0
        self._q = 1.0
        self._f = lambda length: length**0.7

    def solve(self, tree, verbose=False):
        """
        Ant optimization algorithm on the tree.
        """
        pheromones_map = defaultdict(int)
        best_path = []
        best_path_length = 0

        for idx_count in range(self._ants_count):
            # Simulate ant
            path = [tree.begin]
            for idx_step in range(self._ant_steps):
                # Next coords
                coords_next = []
                for edge in tree[path[-1]]:
                    coord = edge[-1]
                    coords_next.append(coord)

                # Choose random coord
                coord = self._pheromones_choice(
                    path[-1], coords_next, pheromones_map
                )

                # Add coord or delete extra part in the path
                try:
                    idx = path.index(coord)
                except ValueError:
                    path.append(coord)
                else:
                    del path[idx + 1 :]

                # Leave the simulation if the end is reached
                if path[-1] == tree.end:
                    break

            if path[-1] == tree.end:
                # Get path_length
                path_length = tree.get_path_length(path)

                # Evolve pheromones
                self._pheromones_evolve(pheromones_map, path, path_length)

                # Update best_path
                if best_path_length < path_length:
                    best_path = path
                    best_path_length = path_length

            if verbose:
                print(f"Ant number: {idx_count + 1}, steps: {idx_step + 1}")
                print(f"Best path: {best_path_length}")
                print()

        # Raise error if a solution has not been found
        if not best_path:
            raise Exception("solution not found")

        return tree.build_full_path(best_path)

    def _pheromones_choice(self, coord_current, coords_next, pheromones_map):
        if len(coords_next) == 1:
            return coords_next[0]

        values = [
            pheromones_map[coord_current, coord]
            for coord in coords_next
        ]
        parts = [(self._c + value)**self._a for value in values]
        random_value = sum(parts) * random()
        agg = 0.0
        for idx, part in enumerate(parts):
            agg += part
            if agg >= random_value:
                return coords_next[idx]

    def _pheromones_evolve(self, pheromones_map, path, path_length=None, tree=None):
        # path_length is passed for optimization, if it is already know
        # there's no need to calculate it again
        if path_length is None:
            path_length = tree.get_path_length(path)

        # Tolerance for all pheromones everywhere
        for coord1, coord2 in pheromones_map.keys():
            pheromones_map[coord1, coord2] *= (1 - self._r)

        # Changes pheromones only in the places where ant passed
        for coord1, coord2 in zip(path[:-1], path[1:]):
            pheromones_map[coord1, coord2] += self._f(path_length)


def find_ant_system_ants_count(tree, ant_steps=1000000):
    """
    Iterates different ants_count for ant system solver to find
    the best value with the longest result path.
    """
    length_best = 0
    ants_count_best = 0

    for ants_count in (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000):
        seed(0)

        with measure_time("algorithm"):
            print(ants_count)
            try:
                ass = AntSystemSolver(ant_steps=ant_steps, ants_count=ants_count)
                path = ass.solve(tree)
                print("Result length:", len(path))

                if len(path) > length_best:
                    length_best = len(path)
                    ants_count_best = ants_count

            except Exception as exc:
                print(exc)

        print(f"Best length is {length_best} with ants_count = {ants_count_best}")

        print()
