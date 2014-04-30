"""
  SERVO SHIELD FireAnt control via USB cable
  usage:
         ./fireant.py <Uno|Due> [calibrate|walk|readTest] [<input logfile> [F]]
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
sys.path.append( ".."+os.sep+"ver0") 
from triangle import pos2angles10thDeg, angles10thDeg2pos

verbose = False

NUM_SERVOS = 24
SERIAL_BAUD = 38400

PACKET_START = chr(0xAB)
STOP_SERVO = -30000+258  # -32768 # 0x8000
SERVO_DEGREE = 176  # ??? servo units/degree maybe x10??

# servoPins[] = { LFC, LFF, LFT,   LMC, LMF, LMT,   LRC, LRF, LRT, 
#                 RFC, RFF, RFT,   RMC, RMF, RMT,   RRC, RRF, RRT,
#                 HeadRollPin, HeadYawPin, HeadPitchPin, PincerLPin, PincerRPin }; 
servoPin = [ 23,22,21,  20,19,18,  17,16,0,
             15,14,13,  12,11,10,  9,8,1,
             7,6,5,4,3 ]


calibration = {
    'Uno': [0]*NUM_SERVOS,
    'Due': (-81, 447, 420, -35, 471, 487, -39, -32, 531, -119, -449, -580, -37, -228, -935, 247, -659, -654,
          -174, -130, -285, -266, 7),
    }

class FireAnt:
  def __init__( self, name, com, runInit=True ):
    self.servoOffset = calibration[name]
    self.com = com
    self.servoUpdateTime = 0.1
    self.time = 0.0
    self.tickTime = 0
    self.servoPosRaw = None
    self.power = None
    self.lastCmd = None
    self.cmdId = 0
    self.receivedCmdId = None
    if runInit:
      self.init()

  def readStatus( self ):
    c = self.com.read(1)
    while c != PACKET_START:
      print c,
      c = self.com.read(1)
    size = ord(self.com.read(1))
    chSum = size;
    buf = self.com.read( size + 1 ) # read data + checksum
    assert (size+sum([ord(x) for x in buf])) % 256 == 0, [hex(ord(x)) for x in buf]
    assert size-4-2 == 2*2*NUM_SERVOS, (size, NUM_SERVOS)
    raw = struct.unpack_from( "HHH"+"hH"*NUM_SERVOS, buf ) # big indian
    self.receivedCmdId = raw[0]
    if verbose:
      print raw
      print "TIME\t%d" % raw[1]
    self.tickTime = raw[1]
    self.time = self.tickTime/1000.0 # TODO 16bit overflow
    self.power = raw[2]*5/1024.
    self.servoPosRaw = [raw[3::2][i]*10/SERVO_DEGREE for i in servoPin]
    return raw
  
  def writeCmd( self, cmd ):
    self.cmdId += 1
    if verbose:
      print "SEND", self.time
    executeAt = (self.tickTime + int(self.servoUpdateTime*1000)) & 0xFFFF
    servoTime = int(self.servoUpdateTime*1000)
    cmd2 = [STOP_SERVO]*NUM_SERVOS
    for i,v in zip(servoPin, cmd): # reindexing
      if v != None and v != STOP_SERVO:
        cmd2[i] = v*SERVO_DEGREE/10
    buf = struct.pack( "HH"+"h"*NUM_SERVOS, self.cmdId & 0xFFFF, executeAt, *cmd2 )
    self.com.write( PACKET_START )
    self.com.write( chr(len(buf)) )
    self.com.write( buf )
    self.com.write( chr( (-sum([ord(x) for x in buf])-len(buf)) % 256 ) )
    self.lastCmd = cmd[:]

  def update( self, cmd ):
    "wrapper for read-write pair"
    status = self.readStatus()
    self.writeCmd( cmd )
#    print "%d\t%d\t%d\t%d\t%d\t%d" % (status[2:5] + tuple(cmd[:3]))
    return status

  def init( self ):
    "skip invalid reading at the beginning"
    for i in xrange(5):
      self.update( cmd=[STOP_SERVO]*NUM_SERVOS )

  def stopServos( self ):
    "stop all servos"
    self.update( cmd=[STOP_SERVO]*NUM_SERVOS )


  def setLegsXYZG( self, legXYZ, num=20 ):
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
      yield cmd

  def interpolateAngleCmdG( self, old, new, steps ):
    for i in xrange(1,steps+1):
      cmd = [(i*n+(steps-i)*o)/steps for o,n in zip(old,new)]
      yield cmd

  def setLegsXYZ( self, legXYZ, num=20 ):
    for cmd in self.setLegsXYZG( legXYZ, num=num ):
      self.update( cmd )

  def standUp( self, interpolateFirst=True ):
    "prepare robot to walking height"
    for z in [-0.001*i for i in xrange(120)]:
      for cmd in self.setLegsXYZG( [(0.1083, 0.0625, z),(0.125, 0.0, z),(0.1083, -0.0625, z)]*2 ):
        if interpolateFirst: # make sure you are close to initial position
          old = self.servoPosRaw[:]
          new = cmd[:]
          maxAngle = max( [abs(o-n) for o,n in zip(old,new) ] )
          print "Int:", maxAngle
          for cmd in self.interpolateAngleCmdG( old, new, steps=maxAngle/5 ):
            self.update( cmd )
          interpolateFirst = False
      self.update( cmd )

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

  def readTest( self, numBytes = 1000 ):
    for i in xrange( numBytes ):
      ch = self.com.read(1)
      if ch == chr(0xAB):
        print
      print hex(ord(ch)),

if __name__ == "__main__":
  if len(sys.argv) < 3 or sys.argv[2] not in ["calibrate", "walk", "readTest"]:
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

  if task == "readTest":
    robot = FireAnt( robotName, com, runInit=False )
    #robot.readTest()
    cmdOrig = [STOP_SERVO]*NUM_SERVOS
    for i in xrange(30):
      #robot.readStatus()
      cmd = cmdOrig[:]
      cmd[1] = 0
      cmd[2] = -300
      robot.update( cmd=cmd )
      print robot.time, robot.cmdId, robot.receivedCmdId, robot.servoPosRaw[:4]
    sys.exit(0)

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

