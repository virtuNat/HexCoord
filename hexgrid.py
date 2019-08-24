from enum import Enum, auto
from numbers import Real, Integral

import numpy as np

class CoordMode(Enum):
    ODD_ROW = auto()
    EVN_ROW = auto()
    ODD_COL = auto()
    EVN_COL = auto()
    DBL_ROW = auto()
    DBL_COL = auto()


class HexCoord(object):
    __slots__ = ('_x', '_y')

    def __init__(self, x, y, z=None):
        if z is not None and x + y + z != 0:
            raise ValueError('Invalid cubic hexagon coordinates provided')
        self._x = x
        self._y = y

    def __getattr__(self, name):
        if name == 'x':
            return self._x
        elif name == 'y':
            return self._y
        elif name == 'z':
            return -self._x - self._y

    def __str__(self):
        return f'({self._x}, {self._y}, {-self._x - self._y})'

    def __repr__(self):
        return f'{type(self).__name__}({self._x}, {self._y})'

    def __iter__(self):
        return (getattr(self, name) for name in 'xyz')

    def __bool__(self):
        return bool(self._x and self._y)

    @classmethod
    def from_offset(cls, mode, q, r):
        """Alternate constructor when the coordinates are given in offset format."""
        if mode == CoordMode.ODD_ROW:
            return cls(q + (r - (r&1))//2, r)
        elif mode == CoordMode.EVN_ROW:
            return cls(q + (r + (r&1))//2, r)
        elif mode == CoordMode.ODD_COL:
            return cls(q, r + (q - (q&1))//2)
        elif mode == CoordMode.EVN_COL:
            return cls(q, r + (q + (q&1))//2)
        raise ValueError('invalid offset coordinate mode provided')

    @classmethod
    def from_double(cls, mode, q, r):
        """Alternate constructor when the coordinates are given in double format."""
        if mode == CoordMode.DBL_ROW:
            return cls(q, (r - q)//2)
        elif mode == CoordMode.DBL_COL:
            return cls((q - r)//2, r)
        raise ValueError('invalid double coordinate mode provided')

    def as_cubic(self):
        """Converts the coordinate into a tuple in cubic format."""
        return (self._x, self._y, -self._x - self._y)

    def as_array(self):
        """Converts the coordinate into a numpy array vector in cubic format."""
        return np.array([self._x, self._y, -self._x - self._y])

    def as_offset(self, mode):
        """Converts the coordinate into a tuple in a valid offset format."""
        if mode == CoordMode.ODD_ROW:
            return (self._x - (self._y - (self._y%2))/2, self._y)
        elif mode == CoordMode.EVN_ROW:
            return (self._x - (self._y + (self._y%2))/2, self._y)
        elif mode == CoordMode.ODD_COL:
            return (self._x, self._y - (self._x - (self._x%2))/2)
        elif mode == CoordMode.EVN_COL:
            return (self._x, self._y - (self._x + (self._x%2))/2)
        raise ValueError('invalid offset coordinate mode provided')

    def as_double(self, mode):
        """Converts the coordinate into a tuple in a valid double format."""
        if mode == CoordMode.DBL_ROW:
            return (self._x, 2*self._y + self._x)
        elif mode == CoordMode.DBL_COL:
            return (2*self._x + self._y, self._y)
        raise ValueError('invalid double coordinate mode provided')

    def __hash__(self):
        return hash((type(self), self._x, self._y))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self._x == other._x and self._y == other._y
        return False

    def __add__(self, other):
        if isinstance(other, type(self)):
            return type(self)(self._x + other._x, self._y + other._y)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, type(self)):
            return type(self)(self._x - other._x, self._y - other._y)
        return NotImplemented

    def __mul__(self, scale):
        if not isinstance(scale, Real):
            return NotImplemented
        return type(self)(self._x * scale, self._y * scale)

    __rmul__ = __mul__

    def __round__(self, n=None):
        """Return the hexgrid tile coordinates this hex coordinate is located in."""
        x, y, z = round(self._x, n), round(self._y, n), round(-self._x - self._y, n)
        dx, dy, dz = abs(x - self._x), abs(y - self._y), abs(z + self._x + self._y)
        if dx > dy and dx > dz:
            return type(self)(-y - z, y)
        elif dy > dz:
            return type(self)(x, -x - z)
        return type(self)(x, y)

    def get_distance(self, ref=None):
        """Returns the taxicab distance of this hex coordinate from another reference hex
        coordiante, or the origin if None is passed or the argument is left empty.
        """
        if ref is None:
            ref = type(self)(0, 0)
        if not isinstance(ref, type(self)):
            raise TypeError('reference must be a HexCoord object')
        return max(map(abs, self - ref))

    def get_neighbors(self):
        """Returns a generator listing all the neighbors of the tile this coordinate is in
        by an arbitrary cyclical order. The actual direction and start of traversal depend
        on the coordinate system.
        """
        proxy = round(self)
        return (proxy + bdir for bdir in _basis_directions)

    def rotate_next(self):
        """Rotate a HexCoord vector 'forward' by 60 degrees. Whether this corresponds to
        left, right, clockwise, or counterclockwise depends on the coordinate system.
        """
        return type(self)(self._x + self._y, -self._x)

    def rotate_back(self):
        """Rotate a HexCoord vector 'backward' by 60 degrees. Whether this corresponds to
        left, right, clockwise, or counterclockwise depends on the coordinate system.
        """
        return type(self)(-self._y, self._x + self._y)

_basis_directions = (
    HexCoord(1, 0), HexCoord(1, -1), HexCoord(0, -1),
    HexCoord(-1, 0), HexCoord(-1, 1), HexCoord(0, 1),
    )


class HexGrid(object):
    pass
