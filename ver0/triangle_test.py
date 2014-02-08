from triangle import *
import unittest

class TriangleTest( unittest.TestCase ):
  def testPos2angles10thDeg( self ):
    self.assertEqual( pos2angles10thDeg( xyz = (0.2, 0, 0), abc=(0.0525, 0.0802, 0.1283) ), (0, 602, -931) )
    self.assertEqual( pos2angles10thDeg( xyz = (0.2, 0, 0.03), abc=(0.0525, 0.0802, 0.1283) ), (0, 699, -906) )
    self.assertEqual( pos2angles10thDeg( xyz = (0.2, 0, -0.03), abc=(0.0525, 0.0802, 0.1283) ), (0, 469, -906) )

  def testTriangleAngles( self ):
    self.assertAlmostEqual( triangleAngles( 1, 1, 1 )[0], math.radians(60), 5 )
    self.assertAlmostEqual( triangleAngles( 3, 4, 5 )[2], math.radians(90), 5 )
    self.assertAlmostEqual( triangleAngles( 1, 1, 2 )[1], math.radians(0), 5 )
    self.assertAlmostEqual( triangleAngles( 1, 1, 2 )[2], math.radians(180), 5 )


if __name__ == "__main__":
  unittest.main() 

