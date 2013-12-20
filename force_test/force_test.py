"""
  Simple read/write utility for remote control of servos on FireAnt
  (with 16bit position and force information)
"""

import sys
import serial 
import datetime
import ctypes
import math

import os
sys.path.append( ".."+os.sep+"serial_servo") 
from serial_servo import LogIt, ReplyLog

def readRobotStatus( com, verbose ):
  pass

def main( filename=None ):
  if filename:
    com = ReplyLog( filename )
    verbose = True
  else:
    com = LogIt( serial.Serial( 'COM8',9600 ) )
    verbose = False
  for i in xrange(1000):
    com.read(1)

if __name__ == "__main__":
  if len(sys.argv) > 1:
    main( sys.argv[1] )
  else:
    main()

