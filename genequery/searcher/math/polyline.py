class Point:
    """
    Simple cartesian (x, y)
    """
    def __init__(self, x, y):
        """
        :type x: float
        :type y: float
        """
        self.x = x
        self.y = y

    def __repr__(self):
        return 'Point({},{})'.format(self.x, self.y)


class Line:
    """
    Line: y = kx + b
    """
    def __init__(self, p1, p2):
        """
        :type p1: Point
        :type p2: Point
        """
        self.k = (p2.y - p1.y) / (p2.x - p1.x)
        self.b = p1.y - self.k * p1.x

    def f(self, x):
        """
        :type x: float
        :rtype: float
        """
        return self.k * x + self.b

    def __repr__(self):
        return 'Line(k={},b={})'.format(self.k, self.b)


class PolyLine:
    """
    Polyline build from list of points.
    """
    def __init__(self, *points):
        """
        :type points: list[Point]
        """
        if len(points) < 2:
            raise Exception('Two or more points must be specified for polyline. {} was given.'.format(points))
        self.points = sorted(points, key=lambda p: p.x)

    def f(self, x, reg_line):
        """
        :type reg_line: Line
        :type x: float
        :rtype: float
        """
        if x < self.points[0].x or x > self.points[-1].x:
            return reg_line.f(x)
        for i in xrange(0, len(self.points) - 1):
            p1, p2 = self.points[i], self.points[i + 1]
            if p1.x <= x <= p2.x:
                return Line(p1, p2).f(x)