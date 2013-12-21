"""
  Simple read/write utility for remote control of servos on FireAnt
  (with 16bit position and force information)
"""

import sys
import serial 
import datetime
import ctypes
import math

import struct


import os
sys.path.append( ".."+os.sep+"serial_servo") 
from serial_servo import LogIt, ReplyLog

PACKET_START = chr(0xAB)
ECHO_CHAR = 'D'
STOP_SERVO = -32768 # 0x8000

verbose = False

def readRobotStatus( com ):
  while com.read(1) != PACKET_START:
    pass
  size = ord(com.read(1))
  chSum = size;
  buf = com.read( size + 1 ) # read data + checksum
  assert (size+sum([ord(x) for x in buf])) % 256 == 0, [hex(ord(x)) for x in buf]
  raw = struct.unpack_from( "HHhhhhhh", buf ) # big indian
  if verbose:
    print raw
  return raw
  
def writeRobotCmd( com ):
  servoTime = 100 # in ms
  buf = struct.pack( "HHHhhh", 0, 0xFFFF, servoTime, STOP_SERVO, STOP_SERVO, 0 )
  com.write( PACKET_START )
  com.write( chr(len(buf)) )
  com.write( buf )
  com.write( chr( (-sum([ord(x) for x in buf])-len(buf)) % 256 ) )


def main( filename=None ):
  global verbose

  if filename:
    com = ReplyLog( filename )
    verbose = True
  else:
    com = LogIt( serial.Serial( 'COM8',9600 ) )
    verbose = False

  for i in xrange(30):
    readRobotStatus( com )
    writeRobotCmd( com )

if __name__ == "__main__":
  if len(sys.argv) > 1:
    main( sys.argv[1] )
  else:
    main()

