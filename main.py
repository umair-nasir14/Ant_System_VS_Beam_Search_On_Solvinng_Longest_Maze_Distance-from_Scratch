from random import seed

seed(0)

from models.utils import measure_time
from models.maze import Maze
from models.tree import Tree
from models.beam_search import BeamSearchSolver, find_beam_search_max_size
from models.ant_system import AntSystemSolver, find_ant_system_ants_count


if __name__ == "__main__":
    with measure_time("load maze"):
        # maze = Maze.load("/media/Data/Downloads/Mazes/Small1.bmp")
        # maze = Maze.load("/media/Data/Downloads/Mazes/Small-Medium1.bmp")  # For Small-Medium1: Best length is 7157 with max_size = 2597
        # maze = Maze.load("/media/Data/Downloads/Mazes/Medium1.bmp")
        maze = Maze.load("/media/Data/Downloads/Mazes/Large1.bmp")
        print(maze)

    with measure_time("build tree"):
        tree = Tree.build_from_maze(maze)
        print(len(tree))

    # with measure_time("beam search"):
    #     bss = BeamSearchSolver(max_size=822, max_count=500)
    #     path = bss.solve(tree, verbose=True)
    #     print(len(path))
    # maze.save(path, 'passed-mazes/BS-Small1.bmp')

    with measure_time("ant system"):
        ass = AntSystemSolver(ant_steps=10000000, ants_count=1000)
        path = ass.solve(tree, verbose=True)
        print(len(path))
    # maze.save(path, 'passed-mazes/AS-Small1.bmp')

    # find_beam_search_max_size(tree)
