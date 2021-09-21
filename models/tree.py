from collections import defaultdict


class Tree:
    def __init__(self, edges, begin, end):
        self._edges = edges if edges is not None else {}
        self._begin = begin
        self._end = end

    @property
    def begin(self):
        return self._begin

    @property
    def end(self):
        return self._end

    def __repr__(self):
        """
        Strinfigies the structure.
        """
        lines = []
        for coord, paths in self._edges.items():
            lines.append(str(coord))
            for path in paths:
                lines.append(3 * " " + str(path))
            lines.append("")
        return "\n".join(lines)

    def __len__(self):
        """
        Returns number of nodes in the tree.
        """
        return len(self._edges)

    def __contains__(self, node):
        """
        Checks node in the tree.
        """
        return node in self._edges

    def __getitem__(self, node):
        """
        Gets edges of the node.
        """
        return self._edges[node]

    def build_full_path(self, path):
        """
        Builds full path as a list of all coordinates in the maze.
        """
        if not path:
            return []
        full_path = [path[0]]
        for i in range(len(path) - 1):
            for edge in self._edges[path[i]]:
                if edge[-1] == path[i + 1]:
                    full_path += edge[1:]
                    break
        return full_path

    def get_path_length(self, path):
        """
        Gets full length in the maze by given list of coords (path) with forks.
        """
        length = 0
        for i in range(len(path) - 1):
            for edge in self._edges[path[i]]:
                if edge[-1] == path[i + 1]:
                    length += len(edge) - 1
                    break
        return length

    @classmethod
    def build_from_maze(cls, maze):
        """
        Builds tree structure from the given maze.
        """
        tree = cls._build_plaint_tree(maze)
        tree._reduce()
        return tree

    @classmethod
    def _build_plaint_tree(cls, maze):
        # Collect tree as a dictionary with node as key and
        # list of paths to next forks as value
        edges = defaultdict(list)

        coords = [maze.begin]
        coords_seen = set()
        while coords:
            coords_next = []

            for coord in coords:
                if coord not in coords_seen:
                    for neighbour in maze.get_neighbours(coord):
                        edges[coord].append([coord, neighbour])
                        coords_next.append(neighbour)
                    coords_seen.add(coord)

            coords = coords_next

        return cls(edges, maze.begin, maze.end)

    def _reduce(self):
        while True:
            main_changed = False

            while True:
                is_changed = False

                is_changed |= self._reduce_transitional_nodes()
                is_changed |= self._reduce_dead_ends()
                is_changed |= self._reduce_single_loops()
                is_changed |= self._reduce_double_loops()

                if not is_changed:
                    break
                else:
                    main_changed = True

            main_changed |= self._reduce_jumper_loops()

            if not main_changed:
                break

    def _reduce_transitional_nodes(self):
        # Collect nodes to merge
        nodes_to_exclude = []
        for node, paths in self._edges.items():
            if len(paths) == 2:
                nodes_to_exclude.append(node)

        # Return False if no nodes to reduce
        if not nodes_to_exclude:
            return False

        else:
            # Merge edges loop
            while nodes_to_exclude:
                node = nodes_to_exclude.pop()
                self._reduce_transitional_one_node(node)

            # Returns True because some nodes were reduced
            return True

    def _reduce_transitional_one_node(self, node):
        # Create edge_new as the result of merge
        edge_new = (
            self._edges[node][0][:0:-1] + [node] + self._edges[node][1][1:]
        )

        # Delete edge for the node in the middle
        del self._edges[node]

        # Update left node edge
        idx = None
        for i, edge in enumerate(self._edges[edge_new[0]]):
            if edge[-1] == node:
                idx = i
                break
        self._edges[edge_new[0]][idx] = edge_new

        # Update right node edge
        idx = None
        for i, edge in enumerate(self._edges[edge_new[-1]]):
            if edge[-1] == node:
                idx = i
                break
        self._edges[edge_new[-1]][idx] = edge_new[::-1]

    def _reduce_dead_ends(self):
        # Collect dead ends (as nodes_to_remove)
        dead_ends = set()
        for node, paths in self._edges.items():
            if len(paths) == 1 and node not in (self._begin, self._end):
                dead_ends.add(node)

        # Returns False if no dead ends found
        if not dead_ends:
            return False

        else:
            # Remove dead ends themselves
            for node in dead_ends:
                del self._edges[node]
                is_removed = True

            # Remove edges led to the found dead ends
            for edges in self._edges.values():
                idx_to_remove = []
                for idx, edge in enumerate(edges):
                    if edge[-1] in dead_ends:
                        idx_to_remove.append(idx)
                for idx in reversed(idx_to_remove):
                    del edges[idx]

            return True

    def _reduce_single_loops(self):
        is_removed = False

        for edges in self._edges.values():
            idx_to_remove = []
            for idx, edge in enumerate(edges):
                if edge[-1] == edge[0]:
                    idx_to_remove.append(idx)

            for idx in reversed(idx_to_remove):
                del edges[idx]
                is_removed = True

        return is_removed

    def _reduce_double_loops(self):
        is_removed = False

        for edges in self._edges.values():
            finals_dct = defaultdict(list)
            for idx, edge in enumerate(edges):
                finals_dct[edge[-1]].append(idx)

            idx_to_remove = []

            for idx_list in finals_dct.values():
                if len(idx_list) >= 2:
                    idx_best = idx_list[0]
                    length_best = len(edges[idx_best])

                    for idx in idx_list[1:]:
                        length_new = len(edges[idx])
                        if length_new > length_best:
                            length_best = length_new
                            idx_best = idx

                    for idx in idx_list:
                        if idx != idx_best:
                            idx_to_remove.append(idx)

            for idx in sorted(idx_to_remove, reverse=True):
                del edges[idx]
                is_removed = True

        return is_removed

    def _reduce_jumper_loops(self):
        jumpers = list(self._get_jumpers())
        for node1, node2, node_a, node_b in jumpers:
            self._reduce_one_jumper(node1, node2, node_a, node_b)
        return bool(jumpers)

    def _get_jumpers(self):
        # Loop through pairs of nodes with exactly 3 neighbours
        for node1 in self._edges.keys():
            edges1 = self._edges[node1]

            if len(edges1) == 3:
                for edge1 in edges1:
                    node2 = edge1[-1]
                    if node1 < node2:
                        edges2 = self._edges[node2]
                        if len(edges2) == 3:
                            near = {
                                edges1[0][-1], edges1[1][-1], edges1[2][-1],
                                edges2[0][-1], edges2[1][-1], edges2[2][-1],
                            }
                            # Jumper is a structure of 4 nodes only
                            if len(near) == 4:
                                near.remove(node1)
                                near.remove(node2)
                                node_a, node_b = near
                                yield node1, node2, node_a, node_b

    def _reduce_one_jumper(self, node1, node2, node_a, node_b):
        if node1 in self and node2 in self and node_a in self and \
                node_b in self:
            # Find edges
            edge_12 = self._find_edge(node1, node2)
            edge_a1 = self._find_edge(node_a, node1)
            edge_a2 = self._find_edge(node_a, node2)
            edge_1b = self._find_edge(node1, node_b)
            edge_2b = self._find_edge(node2, node_b)

            # Paths to pass the jumper
            paths = [
                (edge_a1, edge_1b),  # a - 1 - b
                (edge_a2, edge_2b),  # a - 2 - b
                (edge_a1, edge_12, edge_2b),  # a - 1 - 2 - b
                (edge_a2, edge_12[::-1], edge_1b),  # a - 2 - 1 - b
            ]

            # Search for the best path
            path_best = None
            length_best = 0
            for path in paths:
                length = 0
                for edge in path:
                    length += len(edge) - 1
                if length > length_best:
                    length_best = length
                    path_best = path

            # Remove jumper structure
            self._remove_edge(node_a, node1)
            self._remove_edge(node_a, node2)
            self._remove_edge(node1, node_b)
            self._remove_edge(node2, node_b)
            del self._edges[node1]
            del self._edges[node2]

            # Calculate and set new edge
            edge_new = [node_a]
            for edge in path_best:
                edge_new.extend(edge[1:])
            self._edges[node_a].append(edge_new)
            self._edges[node_b].append(edge_new[::-1])

    def _find_edge(self, node1, node2):
        for edge in self._edges[node1]:
            if edge[-1] == node2:
                return edge
        raise ValueError("no edge")

    def _remove_edge(self, node1, node2):
        for idx, edge in enumerate(self._edges[node1]):
            if edge[-1] == node2:
                del self._edges[node1][idx]
                break
        for idx, edge in enumerate(self._edges[node2]):
            if edge[-1] == node1:
                del self._edges[node2][idx]
                break
