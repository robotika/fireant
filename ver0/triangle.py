"""
  Simple triangle math computations
"""
import math

class Unsolvable(Exception):
  pass

def robustACos( value ):
  "make sure that value is within defined limits"
  return math.acos( max(-1.0, min(1.0, value)) )
  

def triangleAngles( a, b, c ):
  # cosinus theorem ... a*a = b*b + c*c - 2*b*c*cos(alpha)
  # http://en.wikipedia.org/wiki/Law_of_cosines
  alpha = robustACos( (b*b + c*c - a*a)/(2.0*b*c) )
  beta = robustACos( (a*a + c*c - b*b)/(2.0*a*c) )
  gama = robustACos( (a*a + b*b - c*c)/(2.0*a*b) )
  return alpha, beta, gama

def pos2angles10thDeg( xyz, abc ):
  "convert position into angles for arm with lengths a, b, c"
  # a is closest to the body
  (x,y,z) = xyz
  (a,b,c) = abc
  # for simplicity ignore solutions under first segment
  d = math.hypot( x, y )
  if a > d:
    raise Unsolvable()
  # solve triangle in already turned leg plane (xy vs. z)
  ta,tb,tc = triangleAngles( b, c, math.hypot( d-a, z ) )
  a1 = math.atan2( y, x ) 
  a2 = math.atan2( z, d - a )
  return tuple([int(10*math.degrees(angle)) for angle in [a1, a2+tb, tc-math.pi]] )

