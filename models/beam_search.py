from operator import itemgetter

from .utils import measure_time


class BeamSearchSolver:
    def __init__(self, max_size, max_count):
        self._max_size = max_size
        self._max_count = max_count

    def solve(self, tree, verbose=False):
        """
        Beam search algorithm on the tree with limits.
        """
        paths = [[tree.begin]]
        lengths = [0]

        best_path = []
        best_length = 0

        for idx_count in range(self._max_count):
            paths_new = []
            lengths_new = []

            # Loop throught paths
            for path, length in zip(paths, lengths):
                for edge in tree[path[-1]]:
                    coord = edge[-1]

                    # Tabu condition
                    if coord not in path:
                        path_new = path + [coord]
                        length_new = length + len(edge) - 1

                        paths_new.append(path_new)
                        lengths_new.append(length_new)

                        # Update best if we reach the end
                        if coord == tree.end:
                            if best_length < length_new:
                                best_path = path_new
                                best_length = length_new

            # Filter the longest paths only in paths_new
            if len(paths_new) > self._max_size:
                enumerated_lengths = sorted(
                    enumerate(lengths_new), key=itemgetter(1), reverse=True
                )
                paths_new = [
                    paths_new[enumerated_lengths[i][0]]
                    for i in range(self._max_size)
                ]

            # Set paths
            paths = paths_new
            lengths = lengths_new

            if not paths:
                break

        if verbose:
            print(f"idx_count = {idx_count + 1}")

        # Raise error if a solution has not been found
        if not best_path:
            raise Exception("solution not found")

        # Extract coords of the best path
        return tree.build_full_path(best_path)


def find_beam_search_max_size(tree, max_size_from=1, max_size_to=200,
                              max_count=1000):
    """
    Iterates different max_size for beam search solver to find
    the best value with the longest result path.
    """
    length_best = 0
    max_size_best = 0

    for max_size in range(max_size_from, max_size_to + 1, 1):
        with measure_time("algorithm"):
            print(max_size)
            try:
                bss = BeamSearchSolver(max_size=max_size, max_count=max_count)
                path = bss.solve(tree, verbose=True)
                print("Result length:", len(path))

                if len(path) > length_best:
                    length_best = len(path)
                    max_size_best = max_size

            except Exception as exc:
                print(exc)

        print(f"Best length is {length_best} with max_size = {max_size_best}")

        print()
