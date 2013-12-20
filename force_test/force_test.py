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

def readRobotStatus( com, verbose ):
  while com.read(1) != PACKET_START:
    pass
  size = ord(com.read(1))
  chSum = size;
  buf = com.read( size )
  assert (size+sum([ord(x) for x in buf])) % 256 == 0, [hex(ord(x)) for x in buf]
  raw = struct.unpack_from( ">HHhhhhhh", buf ) # big indian
  if verbose:
    print raw
  


def main( filename=None ):
  if filename:
    com = ReplyLog( filename )
    verbose = True
  else:
    com = LogIt( serial.Serial( 'COM8',9600 ) )
    verbose = False

  for i in xrange(30):
    readRobotStatus( com, verbose )

if __name__ == "__main__":
  if len(sys.argv) > 1:
    main( sys.argv[1] )
  else:
    main()

