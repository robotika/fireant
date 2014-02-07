"""
  FireAnt
"""
import sys
import os
import serial 
import datetime
import ctypes
import math
import struct

sys.path.append( ".."+os.sep+"serial_servo") 
from serial_servo import LogIt, ReplyLog

verbose = False

NUM_SERVOS = 23
SERIAL_BAUD = 38400

PACKET_START = chr(0xAB)
STOP_SERVO = -32768 # 0x8000


class FireAnt:
  def __init__( self, com ):
    self.com = com
    self.time = 0

  def readStatus( self ):
    while self.com.read(1) != PACKET_START:
      pass
    size = ord(self.com.read(1))
    chSum = size;
    buf = self.com.read( size + 1 ) # read data + checksum
    assert (size+sum([ord(x) for x in buf])) % 256 == 0, [hex(ord(x)) for x in buf]
    assert size-4 == 2*NUM_SERVOS, (size, NUM_SERVOS)
    raw = struct.unpack_from( "HH"+"h"*NUM_SERVOS, buf ) # big indian
    if verbose:
      print raw
      print "TIME\t%d" % raw[0]
    self.time = raw[0]
    return raw
  
  def writeCmd( self, cmd, servoTime = 100 ):
    self.time += servoTime
    if verbose:
      print "SEND", self.time
    buf = struct.pack( "HH"+"h"*NUM_SERVOS, self.time & 0xFFFF, servoTime, *cmd )
    self.com.write( PACKET_START )
    self.com.write( chr(len(buf)) )
    self.com.write( buf )
    self.com.write( chr( (-sum([ord(x) for x in buf])-len(buf)) % 256 ) )

  def update( self, cmd ):
    "wrapper for read-write pair"
    status = self.readStatus()
    self.writeCmd( cmd )
    return status


def main( filename=None ):
  global verbose

  if filename:
    com = ReplyLog( filename )
    verbose = True
  else:
    if sys.platform == 'linux2':
      com = LogIt( serial.Serial( '/dev/ttyUSB0', SERIAL_BAUD ) )
    else:
      com = LogIt( serial.Serial( 'COM8', SERIAL_BAUD ) )
    verbose = False

  robot = FireAnt( com )
  for i in xrange(10):
    robot.update( cmd=[STOP_SERVO]*NUM_SERVOS )

if __name__ == "__main__":
  if len(sys.argv) > 1:
    main( sys.argv[1] )
  else:
    main()


