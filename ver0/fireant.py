"""
  FireAnt control via USB cable
  usage:
         ./fireant.py <Uno|Due> [<input logfile>]
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
from triangle import pos2angles10thDeg

verbose = False

NUM_SERVOS = 23
SERIAL_BAUD = 38400

PACKET_START = chr(0xAB)
STOP_SERVO = -32768 # 0x8000

calibration = {
    'Uno': [0]*NUM_SERVOS,
    'Due': (-121, 451, 420,  -68, 59, 497,  -77, 1, 526,  -139, -500, -602,  -76, -232, -950,  215, -662, -644, 
          -178, -134, -314, -258, 17),
    }

class FireAnt:
  def __init__( self, name, com ):
    self.servoOffset = calibration[name]
    self.com = com
    self.servoUpdateTime = 0.1
    self.time = 0.0
    self.tickTime = 0
    self.servoPosRaw = None
    self.power = None
    self.lastCmd = None
    self.init()

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
    self.tickTime = raw[0]
    self.time = self.tickTime/1000.0 # TODO 16bit overflow
    self.power = raw[1]/100.0
    self.servoPosRaw = raw[2:]
    return raw
  
  def writeCmd( self, cmd ):
    if verbose:
      print "SEND", self.time
    executeAt = (self.tickTime + int(self.servoUpdateTime*1000)) & 0xFFFF
    servoTime = int(self.servoUpdateTime*1000)
    buf = struct.pack( "HH"+"h"*NUM_SERVOS, executeAt, servoTime, *cmd )
    self.com.write( PACKET_START )
    self.com.write( chr(len(buf)) )
    self.com.write( buf )
    self.com.write( chr( (-sum([ord(x) for x in buf])-len(buf)) % 256 ) )
    self.lastCmd = cmd[:]

  def update( self, cmd ):
    "wrapper for read-write pair"
    status = self.readStatus()
    self.writeCmd( cmd )
    return status

  def init( self ):
    "skip invalid reading at the beginning"
    for i in xrange(5):
      self.update( cmd=[STOP_SERVO]*NUM_SERVOS )

  def stopServos( self ):
    "stop all servos"
    self.update( cmd=[STOP_SERVO]*NUM_SERVOS )


  def setLegsXYZ( self, legXYZ, num=2 ):
    "move legs to their relative XYZ coordinates"
    assert len(legXYZ) == 6, legXYZ
    servoDirs = (1,-1,1, 1,-1,1, 1,-1,1, -1,1,-1, -1,1,-1, -1,1,-1, 1,1,1,1,1 )
    angles = []
    for xyz in legXYZ:
      angles.extend( pos2angles10thDeg( xyz, abc=(0.0525, 0.0802, 0.1283) ) )
    angles += [0,0,0,0,0] # Head & Pincers
    cmd = [angle*servoDir+offset for angle, servoDir, offset in zip(angles, servoDirs, self.servoOffset)]
    if STOP_SERVO in self.lastCmd:
      prev = cmd[:]
    else:
      prev = self.lastCmd
    for i in xrange(num):
      self.update( [((i+1)*new+(num-1-i)*old)/num for old, new in zip(prev,cmd)] )

  def stable( self, coords, size=0.08 ):
    "add extra Y coordinate to front/back legs"
    assert len(coords) == 6, coords
    return [(x,y+s,z) for (x,y,z),s in zip( coords, [size,0,-size, size,0,-size] ) ] 

  def standUp( self ):
    "prepare robot to walking height"
    for z in [-0.01*i for i in xrange(12)]:
      self.setLegsXYZ( self.stable([(0.15, 0.0, z)]*6) )

  def sitDown( self ):
    for z in [-0.01*i for i in xrange(11,0,-1)]:
      self.setLegsXYZ( self.stable([(0.15, 0.0, z)]*6) )

  def wait( self, duration ):
    cmd = self.servoPosRaw[:]
    startTime = self.time
    while self.time < startTime+duration:
      self.update( cmd )

  def walk( self, dist ):
    up,down = -0.09, -0.11
    step = 0.05
    width = 0.12
    while dist > 0:
      self.setLegsXYZ( self.stable( [(width, 0, up), (width, step, down)]*3) )
      self.setLegsXYZ( self.stable([(width, step, up), (width, 0, down)]*3) )
      self.setLegsXYZ( self.stable([(width, step, down), (width, 0, up)]*3) )
      self.setLegsXYZ( self.stable([(width, 0, down), (width, step, up)]*3) )
      dist -= 2*step


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print __doc__
    sys.exit(-1)
  robotName = sys.argv[1]
  filename = None
  if len(sys.argv) > 2:
    filename = sys.argv[2]
  assert robotName in ['Uno', 'Due'], robotName

  if filename:
    com = ReplyLog( filename )
    verbose = False #True
  else:
    if sys.platform == 'linux2':
      com = LogIt( serial.Serial( '/dev/ttyUSB0', SERIAL_BAUD ) )
    else:
      com = LogIt( serial.Serial( {'Uno':"COM9", 'Due':"COM8"}[robotName], SERIAL_BAUD ) )
    verbose = False

  robot = FireAnt( robotName, com )
  print "Battery BEFORE", robot.power
  robot.standUp()
  robot.walk(1.0)
  robot.sitDown()
  robot.stopServos()
  print "Batter AFTER", robot.power
