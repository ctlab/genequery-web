from django.test import SimpleTestCase

from genequery.searcher.math.polyline import Point, Line, PolyLine


class TestMath(SimpleTestCase):

    def assertFloatEqual(self, a, b, digits=14):
        self.assertEqual(round(a, digits), round(b, digits))

    def test_line_1(self):
        p1 = Point(1, 6)
        p2 = Point(3, 2)
        line = Line(p1, p2)

        self.assertEqual(-2, line.k)
        self.assertEqual(8, line.b)
        self.assertEqual(p1.y, line.f(p1.x))
        self.assertEqual(4, line.f(2))

        p1 = Point(-3.65621, 0.6695)
        p2 = Point(-3.77191, 0.5850)
        line = Line(p1, p2)

        self.assertEqual(4.8004398876404535, line.f(2))

    def test_polyline(self):
        p1 = Point(-3.6562114761963302, 0.6695890667431851)
        p2 = Point(-3.7719114404393554, 0.5850644577846290)
        p3 = Point(-3.9210790890265040, 0.5511878067097776)
        p4 = Point(-4.0109642512299850, 0.6115200344396203)
        p5 = Point(-4.0833590906863390, 0.5558708552395484)
        p6 = Point(-4.1234932459765760, 0.5492958219756182)

        rline = Line(Point(0, 0), Point(1, 1))
        pline = PolyLine(p1, p3, p2, p5, p4, p6)

        self.assertEqual(rline.f(-2), pline.f(-2, rline))
        self.assertEqual(rline.f(-10), pline.f(-10, rline))

        x = (p1.x + p2.x) / 2
        line12 = Line(p1, p2)
        line23 = Line(p3, p2)
        self.assertFloatEqual(line12.f(x), pline.f(x, rline))
        self.assertFloatEqual(line12.f(p1.x), pline.f(p1.x, rline))
        self.assertFloatEqual(line12.f(p2.x), pline.f(p2.x, rline))
        self.assertFloatEqual(line23.f(p2.x), pline.f(p2.x, rline))

        self.assertFloatEqual(Line(p5, p6).f(p6.x), pline.f(p6.x, rline))