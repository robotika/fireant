"""
  Simple read/write utility for remote control of servos on FireAnt
"""

import sys
import serial 
import datetime
import ctypes
import math

class LogEnd(Exception):
  "End of log notification"
  pass 


class LogIt():
  "Log communication via serial com"
  def __init__( self, com ):
    self._com = com
    self._logFile = None
    self.relog( 'logs/fa' )

  def relog( self, prefix ):
    dt = datetime.datetime.now()
    filename = prefix + dt.strftime("%y%m%d_%H%M%S.log") 
    self._logFile = open( filename, "wb" )
    print "LogIt:", filename
    return filename

  def read( self, numChars ):
    s = self._com.read( numChars )
    for ch in s:
      self._logFile.write( chr(0x01) )
      self._logFile.write( ch )
    self._logFile.flush()
    return s

  def write( self, chars ):
    for ch in chars:
      self._logFile.write( chr(0x00) )
      self._logFile.write( ch )
    self._logFile.flush()
    self._com.write( chars ) 

#-------------------------------------------------------------------

class ReplayLog():
  "Read & verify log"
  def __init__( self, filename, assertWrite=True ):
    print "ReplayLog", filename
    self._logFile = open( filename, "rb" )
    self.assertWrite = assertWrite

  def read( self, numChars ):
    s = []
    for i in range(numChars):
      marker = self._logFile.read(1)
      if not marker:
        raise LogEnd()
      assert( marker == chr(0x01) )
      s.append(self._logFile.read(1))
      if not s[-1]:
        raise LogEnd()
    return ''.join(s)

  def write( self, chars ):
    for ch in chars:
      marker = self._logFile.read(1)
      if not marker:
        raise LogEnd()
      assert( marker == chr(0x00) )
      verifyCh = self._logFile.read(1)
      if not verifyCh:
        raise LogEnd()
      if self.assertWrite:
        assert( verifyCh == ch ) 

#-------------------------------------------------------------------

class ReplyLogInputsOnly():
  "Read & verify log"
  def __init__( self, filename ):
    print "ReplyLogInputOnly", filename
    self._logFile = open( filename, "rb" )

  def read( self, numChars ):
    s = []
    for i in range(numChars):
      while( self._logFile.read(1) not in [chr(0x01), ''] ):
        c = self._logFile.read(1) # skip write output
        if not c:
          raise LogEnd()
        assert( i == 0 ) # the packets should be complete
      s.append(self._logFile.read(1))
      if not s[-1]:
        raise LogEnd()
    return ''.join(s)

  def write( self, chars ):
    pass 
  
#-------------------------------------------------------------------

START_BLOCK = chr(0x80)
END_BLOCK = chr(0x81)
STOP_SERVO = chr(0x82)
SERVO_OUT_OF_RANGE = chr(0x83)

def readServos( com ):
  ret = []
  b = com.read(1)
  while True:
    while b != START_BLOCK:
      b = com.read(1)
    b = com.read(1)
    while b != START_BLOCK and b != END_BLOCK:
      if b == SERVO_OUT_OF_RANGE:
        ret.append( None )
      else:
        ret.append( ctypes.c_byte(ord(b)).value )
      b = com.read(1)
    if b == END_BLOCK:
      return ret

def writeServos( com, servos ):
  com.write( START_BLOCK )
  for s in servos:
    if s == None:
      com.write( STOP_SERVO )
    else:
      com.write( chr( ctypes.c_ubyte(s).value ) )
  com.write( END_BLOCK )

def stepServos( servos ):
  if None not in servos:
    return [x+1 for x in servos]
  return servos


CMD_STOP = [None]*3
CMD_CENTER = [90, 18, -5] 

def sendServoSeq( com, cmd, num, info=None, verbose=False ):
  if info:
    print info
  for i in xrange( num ):
    servos = readServos( com )
    if verbose:
      print servos, cmd # debug
    writeServos( com, cmd )


class Unsolvable(Exception):
  pass

def robustACos( value ):
  "make sure that value is within defined limits"
  return math.acos( max(-1.0, min(1.0, value)) )

def triangleAngles( a, b, c ):
  # cosinus theorem ... a*a = b*b + c*c - 2*b*c*cos(alpha)
  alpha = robustACos( (b*b + c*c - a*a)/(2.0*b*c) )
  beta = robustACos( (a*a + c*c - b*b)/(2.0*a*c) )
  gama = robustACos( (a*a + b*b - c*c)/(2.0*a*b) )
  return alpha, beta, gama

def pos2angles( xyz, abc ):
  "convert position into angles for arm with lengths a, b, c"
  # a is closest to the body
  (x,y,z) = xyz
  (a,b,c) = abc
  a1 = math.atan2( y, x ) 
  d = math.hypot( x, y )
  if a > d:
    raise Unsolvable()
  ta,tb,tc = triangleAngles( b, c, d-a ) # TODO z-coordinate
  a2 = math.atan2( z, d - a )
  return tuple([int(math.degrees(angle)) for angle in [a1, a2+tb, tc]] )

def pos2cmd( xyz ):
  "convert angles and handle direction with offset"
  c = (94, 38, 86-180)
  a = pos2angles( xyz, abc = (0.0525, 0.0802, 0.1283) )  # was (0.05, 0.08, 0.135)
  print "angles", a
  return [c[0]+a[0], c[1]-a[1], c[2]+a[2]]

def play( com, music, verbose ):
  numMove = 5
  numTone = 20
  xDist = 0.18
  zUp, zDown = -0.01, -0.063
  yStep = 0.026 # real measure = 0.0228
  m = dict( zip("AGFEDC", [i*yStep for i in xrange(-2,4)] ) )
  for t,l in zip(music[::2], music[1::2]):
    y = m[t] # tone to movement
    print "Play", t
    sendServoSeq( com, pos2cmd( (xDist, y, zUp) ), numMove, "move", verbose )
    sendServoSeq( com, pos2cmd( (xDist, y, zDown) ), int(l)*numTone, "down", verbose )
    sendServoSeq( com, pos2cmd( (xDist, y, zUp) ), numMove, "up", verbose )
  
  sendServoSeq( com, CMD_STOP, 10, "stopping...", verbose )

def main( filename=None ):
  if filename:
    com = ReplayLog( filename )
    verbose = True
  else:
    com = LogIt( serial.Serial( 'COM8',9600 ) )
    verbose = False
#  play( com, "C2A2C2A2", verbose )
#  play( com, "C1D1E1F1G2G2A2A2G2F1F1F1F1E2E2D2D2C2", verbose ) # Kocka leze dirou
  play( com, "E1E1E2E1E1E2E1G1C2D1E2F1F1F1F1F1E1E2E1D1D1E1D2", verbose ) # Jingle Bells

if __name__ == "__main__":
  if len(sys.argv) > 1:
    main( sys.argv[1] )
  else:
    main()

