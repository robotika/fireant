"""
  FireAnt control via USB cable
  usage:
         ./fireant.py <Uno|Due> [calibrate|walk] [<input logfile> [F]]
"""
import sys
import os
import serial 
import datetime
import ctypes
import math
import struct

sys.path.append( ".."+os.sep+"serial_servo") 
from serial_servo import LogIt, ReplayLog
from triangle import pos2angles10thDeg, angles10thDeg2pos

verbose = False

NUM_SERVOS = 23
SERIAL_BAUD = 38400

PACKET_START = chr(0xAB)
STOP_SERVO = -32768 # 0x8000

calibration = {
    'Uno': [0]*NUM_SERVOS,
    'Due': (-81, 447, 420, -35, 471, 487, -39, -32, 531, -119, -449, -580, -37, -228, -935, 247, -659, -654,
          -174, -130, -285, -266, 7),
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
    print "%d\t%d\t%d\t%d\t%d\t%d" % (status[2:5] + tuple(cmd[:3]))
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
    abc=(0.0525, 0.0802, 0.1283)
    servoDirs = (1,-1,1, 1,-1,1, 1,-1,1, -1,1,-1, -1,1,-1, -1,1,-1, 1,1,1,1,1 )
    angles = []
    for xyz in legXYZ:
      angles.extend( pos2angles10thDeg( xyz, abc=abc ) )
    angles += [0,0,0,0,0] # Head & Pincers
    cmd = [angle*servoDir+offset for angle, servoDir, offset in zip(angles, servoDirs, self.servoOffset)]
    if STOP_SERVO in self.lastCmd:
      prev = cmd[:]
    else:
      prev = self.lastCmd

    # undo offset and direction
    prev = [(angle-offset)*servoDir for angle, servoDir, offset in zip(prev, servoDirs, self.servoOffset)]
    prevLegXYZ = []
    for angles in zip(prev[0:-5:3], prev[1:-5:3], prev[2:-5:3]):
      prevLegXYZ.append( angles10thDeg2pos( angles, abc=abc ) )
    for i in xrange(num):
      angles = []
      for xyz1, xyz2 in zip(prevLegXYZ, legXYZ):
        xyz = [((i+1)*new+(num-1-i)*old)/float(num) for old, new in zip(xyz1,xyz2)]
        angles.extend( pos2angles10thDeg( xyz, abc=abc ) )
      angles += [0,0,0,0,0] # Head & Pincers
      cmd = [angle*servoDir+offset for angle, servoDir, offset in zip(angles, servoDirs, self.servoOffset)]
      self.update( cmd )

  def standUp( self ):
    "prepare robot to walking height"
    for z in [-0.01*i for i in xrange(12)]:
      self.setLegsXYZ( [(0.1083, 0.0625, z),(0.125, 0.0, z),(0.1083, -0.0625, z)]*2 )

  def sitDown( self ):
    for z in [-0.01*i for i in xrange(11,0,-1)]:
      self.setLegsXYZ( [(0.1083, 0.0625, z),(0.125, 0.0, z),(0.1083, -0.0625, z)]*2 )

  def wait( self, duration ):
    cmd = self.servoPosRaw[:]
    startTime = self.time
    while self.time < startTime+duration:
      self.update( cmd )

  def walk( self, dist ):
    up,down = -0.02, -0.11
    s = 0.02 # step
    while dist > 0:
      self.setLegsXYZ( [(0.1083, 0.0625-s, down),(0.125, 0.0+s, up),(0.1083, -0.0625-s, down),
                        (0.1083, 0.0625+s, up),(0.125, 0.0-s, down),(0.1083, -0.0625+s, up)] )
      self.setLegsXYZ( [(0.1083, 0.0625-s, down),(0.125, 0.0+s, down),(0.1083, -0.0625-s, down),
                        (0.1083, 0.0625+s, down),(0.125, 0.0-s, down),(0.1083, -0.0625+s, down)] )
      self.setLegsXYZ( [(0.1083, 0.0625+s, up),(0.125, 0.0-s, down),(0.1083, -0.0625+s, up),
                        (0.1083, 0.0625-s, down),(0.125, 0.0+s, up),(0.1083, -0.0625-s, down)] )
      self.setLegsXYZ( [(0.1083, 0.0625+s, down),(0.125, 0.0-s, down),(0.1083, -0.0625+s, down),
                        (0.1083, 0.0625-s, down),(0.125, 0.0+s, down),(0.1083, -0.0625-s, down)] )
      dist -= 8*s

  def calibrate( self, duration=3.0 ):
    "verify servos center point calibration"
    cmd=[STOP_SERVO]*NUM_SERVOS
    startTime = self.time
    stat = []
    while self.time < startTime+duration:
      stat.append( self.update( cmd ) )
    newCalib = []
    for i in xrange(len(stat[0])):
      arr = [a[i] for a in stat]
      median = sorted(arr)[len(arr)/2]
      print "%d:\t%d\t%d\t%d\t%d" % (i-1, min(arr), max(arr), max(arr)-min(arr), median)
      newCalib.append( median )
    print tuple(newCalib[2:]) # first two readings are time and battery status


if __name__ == "__main__":
  if len(sys.argv) < 3 or sys.argv[2] not in ["calibrate", "walk"]:
    print __doc__
    sys.exit(-1)
  robotName = sys.argv[1]
  filename = None
  task = sys.argv[2]
  if len(sys.argv) > 3:
    replayAssert = True
    filename = sys.argv[3]
    if len(sys.argv) > 4:
      assert sys.argv[4] == 'F'
      replayAssert = False
  assert robotName in ['Uno', 'Due'], robotName

  if filename:
    com = ReplayLog( filename, assertWrite=replayAssert )
    verbose = False #True
  else:
    if sys.platform == 'linux2':
      com = LogIt( serial.Serial( '/dev/ttyUSB0', SERIAL_BAUD ) )
    else:
      com = LogIt( serial.Serial( {'Uno':"COM9", 'Due':"COM8"}[robotName], SERIAL_BAUD ) )
    verbose = False

  robot = FireAnt( robotName, com )
  print "Battery BEFORE", robot.power
  if task == "calibrate":
    robot.calibrate()
  elif task == "walk":
    robot.standUp()
    robot.walk(10.0)
    robot.sitDown()
    robot.stopServos()
  else:
    print "UNKNOWN TASK", task
  print "Battery AFTER", robot.power

