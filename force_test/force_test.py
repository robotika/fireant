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

NUM_SERVOS = 23

SERIAL_BAUD = 38400

PACKET_START = chr(0xAB)
ECHO_CHAR = 'D'
STOP_SERVO = -32768 # 0x8000

verbose = False
g_time = 0

def readRobotStatus( com ):
  while com.read(1) != PACKET_START:
    pass
  size = ord(com.read(1))
  chSum = size;
  buf = com.read( size + 1 ) # read data + checksum
  assert (size+sum([ord(x) for x in buf])) % 256 == 0, [hex(ord(x)) for x in buf]
  assert size-4 == 4*NUM_SERVOS, (size, NUM_SERVOS)
  raw = struct.unpack_from( "HH"+"hh"*NUM_SERVOS, buf ) # big indian
  if verbose:
    print raw
    print "TIME\t%d" % raw[0]
  global g_time
  g_time = raw[0]
  return raw
  
def writeRobotCmd( com, cmd, servoTime = 100 ):
  global g_time
  g_time += servoTime
  if verbose:
    print "SEND", g_time
  buf = struct.pack( "HHH"+"h"*NUM_SERVOS, g_time, 0xFFFF, servoTime, *cmd )
  com.write( PACKET_START )
  com.write( chr(len(buf)) )
  com.write( buf )
  com.write( chr( (-sum([ord(x) for x in buf])-len(buf)) % 256 ) )

#-----------------------------------------------------
# copy of piano playing stuff

def sendServoSeq( com, cmd, num, info=None, trigger=None ):
  if info:
    print info
  for i in xrange( num ):
    status = readRobotStatus( com )
    if trigger and status[5] < trigger:
      # pure hacking of motion down
      cmd[1] -= 10
      if verbose:
        print "TRIGGER", cmd[1]
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
  scale = 4 # 4x faster communication (should be in time TODO)
  numMove = 2*scale
  numTone = 5*scale
  xDist = 0.18
  zUp, zDown = -0.01, -0.083 # added extra 2cm (was -0.063)
  yStep = 0.026 # real measure = 0.0228
  m = dict( zip("AGFEDC", [i*yStep for i in xrange(-2,4)] ) )
  for t,l in zip(music[::2], music[1::2]):
    y = m[t] # tone to movement
    print "Play", t
    sendServoSeq( com, pos2cmd( (xDist, y, zUp) ), numMove, "move" )
    sendServoSeq( com, pos2cmd( (xDist, y, zDown) ), int(l)*numTone, "down", trigger=-500 )
    sendServoSeq( com, pos2cmd( (xDist, y, zUp) ), numMove, "up" )
  
  sendServoSeq( com, [STOP_SERVO, STOP_SERVO, STOP_SERVO], 10, "stopping..." ) 

def testKey( com ):
  "press piano key and seach for y-coordinate limits"
  xDist = 0.18
  zUp, zDown = -0.01, -0.063
  yStep = 2*0.026 # real measure = 0.0228
  num = 10
  y = 0.0
  sendServoSeq( com, pos2cmd( (xDist, y, zUp) ), num, "move" )
  sendServoSeq( com, pos2cmd( (xDist, y, zDown) ), num, "down", trigger=-500 )
  sendServoSeq( com, pos2cmd( (xDist, y-yStep, zDown) ), num, "moveLeft", trigger=-500 )
  sendServoSeq( com, pos2cmd( (xDist, y+yStep, zDown) ), num, "moveRight", trigger=-500 )
  sendServoSeq( com, pos2cmd( (xDist, y, zDown) ), num, "center", trigger=-500 )
  sendServoSeq( com, pos2cmd( (xDist, y, zUp) ), num, "up" )


def ver0( com ):
  "test single servo"
  for i in xrange(30):
    readRobotStatus( com )
    writeRobotCmd( com, cmd=[STOP_SERVO, STOP_SERVO, 0] )
  readRobotStatus( com )
  writeRobotCmd( com, cmd=[STOP_SERVO, STOP_SERVO, STOP_SERVO] )

def record( com, filename, loopLen ):
  print "RECORDING", filename
  f = open( filename, "w" )
  for i in xrange( loopLen ):
    status = readRobotStatus( com )
    f.write( str(status) + '\n' )
    writeRobotCmd( com, cmd=[STOP_SERVO]*NUM_SERVOS )
  f.close()
  print "END"


def replay( com, filename ):
  print "REPLAY", filename
  for line in open( filename ):
    readRobotStatus( com )
    oldStatus = eval(line)
    cmd = oldStatus[2::2]
    print cmd
    writeRobotCmd( com, cmd=cmd )
  writeRobotCmd( com, cmd=[STOP_SERVO]*NUM_SERVOS )
  print "END"


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
#  ver0( com )
#  play( com, "E1E1E2" )
#  play( com, "E1E1E2E1E1E2E1G1C2D1E2F1F1F1F1F1E1E2E1D1D1E1D2" ) # Jingle Bells
#  testKey( com )
  cmdFile = "record.txt"
#  record( com, cmdFile, 100 )
  replay( com, cmdFile )

if __name__ == "__main__":
  if len(sys.argv) > 1:
    main( sys.argv[1] )
  else:
    main()

