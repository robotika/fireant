"""
  Simple read/write utility for remote control of servos on FireAnt
"""

import sys
import serial 
import datetime
import ctypes

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

class ReplyLog():
  "Read & verify log"
  def __init__( self, filename, assertWrite=True ):
    print "ReplyLog", filename
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


def main( filename=None ):
  if filename:
    com = ReplyLog( filename )
    verbose = True
  else:
    com = LogIt( serial.Serial( 'COM8',9600 ) )
    verbose = False
#  sendServoSeq( com, CMD_STOP, 10, "init...", verbose )
  sendServoSeq( com, CMD_CENTER, 100, "center ...", verbose )
  sendServoSeq( com, [70, -40, 60], 100, "moving ...", verbose )
  sendServoSeq( com, CMD_CENTER, 100, "center ...", verbose )
  sendServoSeq( com, CMD_STOP, 10, "stopping...", verbose )

if __name__ == "__main__":
  if len(sys.argv) > 1:
    main( sys.argv[1] )
  else:
    main()

