from serial_servo import *
import unittest

class SerialServoTest( unittest.TestCase ):
  def testPos2angles( self ):
    self.assertEqual( pos2angles( xyz = (0.1, 0, 0), abc=(0.05, 0.1, 0.15) ), (0, 179, 0) )
    self.assertEqual( pos2angles( xyz = (0.1, 0.1, 0), abc=(0.05, 0.1, 0.15) ), (45, 103, 36) )
    self.assertEqual( pos2angles( xyz = (6, 0, 0), abc=(1, 3, 4) ), (0, 53, 90) )
    self.assertEqual( pos2angles( xyz = (0.265, 0, 0), abc=(0.05, 0.08, 0.135) ), (0, 0, 180) )
    self.assertEqual( pos2angles( xyz = (0.14, 0, 0), abc=(0.05, 0.08, 0.135) ), (0, 104, 40) )

  def testTriangleAngles( self ):
    self.assertAlmostEqual( triangleAngles( 1, 1, 1 )[0], math.radians(60), 5 )
    self.assertAlmostEqual( triangleAngles( 3, 4, 5 )[2], math.radians(90), 5 )

  def testPos2cmd( self ):
    self.assertEqual( pos2cmd( xyz = (0.265, 0, 0) ), [94, 38, 86] )
    self.assertEqual( pos2cmd( xyz = (0.14, 0, 0) ), [94, -49, -38] )


if __name__ == "__main__":
  unittest.main() 

