"""
  Simple read/write utility for remote control of servos on FireAnt
"""

import sys
import serial 
import datetime

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



def main( filename=None ):
  if filename:
    com = ReplyLog( filename )
  else:
    com = LogIt( serial.Serial( 'COM8',9600 ) )
  for i in xrange(100):
    com.read(1)


if __name__ == "__main__":
  if len(sys.argv) > 1:
    main( sys.argv[1] )
  else:
    main()

