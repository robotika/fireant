"""
  FireAnt battery status
  usage:
         ./battery.py <logfile>
"""

import sys
import os
from fireant import FireAnt, STOP_SERVO, NUM_SERVOS

sys.path.append( ".."+os.sep+"serial_servo") 
from serial_servo import LogIt, ReplayLog, ReplyLogInputsOnly, LogEnd


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(-1)
    filename = sys.argv[1]
    com = ReplyLogInputsOnly( filename )
    robot = FireAnt( "Due", com, runInit=False )
    try:  
        while robot.power is None:
            robot.update( cmd=[STOP_SERVO]*NUM_SERVOS )
        print "Battery BEFORE", robot.power
        while True:
            robot.update( cmd=[STOP_SERVO]*NUM_SERVOS )
    except LogEnd:
        pass
    print "Battery AFTER", robot.power

# vim: expandtab sw=4 ts=4 

