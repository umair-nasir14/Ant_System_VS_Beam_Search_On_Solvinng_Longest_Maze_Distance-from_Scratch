import numpy as np
from PIL import Image


class Maze:
    """
    Maze object contains 2D numpy array of 0 (wall) and 1 (pass) and
    coordinates of the begin and end.
    """

    def __init__(self, data):
        """
        Constructor to create a maze object from 2D numpy array.
        """
        self._data = data
        self._begin = self._find_begin()
        self._end = self._find_end()

    def __repr__(self):
        return repr(self._data)

    @property
    def shape(self):
        return self._data.shape

    @property
    def begin(self):
        return self._begin

    @property
    def end(self):
        return self._end

    def get_neighbours(self, coord):
        """
        Yields coordinates of neighbours in the maze for given coord.
        """
        for direction in self.available_directions(coord):
            yield self.next_coord(coord, direction)

    def available_directions(self, coord):
        """
        Gets a list available directions in the maze from given coord. Each
        direction is a tuple like (0, -1), which means the direction with negative
        Y and same X.
        """
        directions = []
        if coord[0] + 1 < self.shape[1] and self._data[coord[1], coord[0] + 1]:
            directions.append((1, 0))
        if coord[1] + 1 < self.shape[0] and self._data[coord[1] + 1, coord[0]]:
            directions.append((0, 1))
        if coord[0] - 1 >= 0 and self._data[coord[1], coord[0] - 1]:
            directions.append((-1, 0))
        if coord[1] - 1 >= 0 and self._data[coord[1] - 1, coord[0]]:
            directions.append((0, -1))
        return directions

    def save(self, path, filepath):
        """
        Saves the maze to a BMP file with given path (list of coordinates)
        colored with red.
        """
        # Preparing PNG data (as 3D array that is acceptable by Image.fromarray)
        data = np.where(
            self._data.reshape(self.shape[0], self.shape[1], 1),
            [[[255, 255, 255]]], [[[0, 0, 0]]]
        ).astype(np.uint8)

        # Drawing the path with red pixels
        for j, i in path:
            data[i, j] = [255, 0, 0]

        # Saving as image
        with Image.fromarray(data) as img:
            img.save(filepath)

    @classmethod
    def next_coord(cls, coord, direction):
        """
        Calculates next coord by given one and the direction.
        """
        return (coord[0] + direction[0], coord[1] + direction[1])

    @classmethod
    def load(cls, filepath):
        """
        Loads maze as a numpy array by filepath of a BMP file.
        """
        with Image.open(filepath) as img:
            data = np.array(img, dtype=np.int32)
        return cls(data)

    def _find_begin(self):
        """
        Gets coord of the begin.
        """
        return (np.where(self._data[0, :] == 1)[0][0], 0)


    def _find_end(self):
        """
        Gets coord of the end.
        """
        return (
            np.where(self._data[-1, :] == 1)[0][0],
            self._data.shape[1] - 1
        )
