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
from serial_servo import pos2angles

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
  
def writeRobotCmd( com, cmd, servoTime = 100 ):  
  buf = struct.pack( "HHHhhh", 0, 0xFFFF, servoTime, *cmd )
  com.write( PACKET_START )
  com.write( chr(len(buf)) )
  com.write( buf )
  com.write( chr( (-sum([ord(x) for x in buf])-len(buf)) % 256 ) )

#-----------------------------------------------------
# copy of piano playing stuff

def sendServoSeq( com, cmd, num, info=None ):
  if info:
    print info
  for i in xrange( num ):
    status = readRobotStatus( com )
    if verbose:
#      print status, cmd # debug
      print "FORCE\t" + "\t".join( [str(x) for x in status[2:]] )
    writeRobotCmd( com, cmd )

def pos2cmd( xyz ):
  "convert coordinates to servo angles (degrees*10)"
  c = (94, 38, 86-180)
  a = pos2angles( xyz, abc = (0.0525, 0.0802, 0.1283) )  # was (0.05, 0.08, 0.135)
  print "angles", a
  return [10*x for x in [c[0]+a[0], c[1]-a[1], c[2]+a[2]]]

def play( com, music ):
  numMove = 5
  numTone = 20
  xDist = 0.18
  zUp, zDown = -0.01, -0.063
  yStep = 0.026 # real measure = 0.0228
  m = dict( zip("AGFEDC", [i*yStep for i in xrange(-2,4)] ) )
  for t,l in zip(music[::2], music[1::2]):
    y = m[t] # tone to movement
    print "Play", t
    sendServoSeq( com, pos2cmd( (xDist, y, zUp) ), numMove, "move" )
    sendServoSeq( com, pos2cmd( (xDist, y, zDown) ), int(l)*numTone, "down" )
    sendServoSeq( com, pos2cmd( (xDist, y, zUp) ), numMove, "up" )
  
  sendServoSeq( com, [STOP_SERVO, STOP_SERVO, STOP_SERVO], 10, "stopping..." ) 


def ver0( com ):
  "test single servo"
  for i in xrange(30):
    readRobotStatus( com )
    writeRobotCmd( com, cmd=[STOP_SERVO, STOP_SERVO, 0] )
  readRobotStatus( com )
  writeRobotCmd( com, cmd=[STOP_SERVO, STOP_SERVO, STOP_SERVO] )


def main( filename=None ):
  global verbose

  if filename:
    com = ReplyLog( filename )
    verbose = True
  else:
    com = LogIt( serial.Serial( 'COM8',9600 ) )
    verbose = False
#  ver0( com )
  play( com, "E1E1E2" )

if __name__ == "__main__":
  if len(sys.argv) > 1:
    main( sys.argv[1] )
  else:
    main()

