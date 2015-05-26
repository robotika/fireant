"""
  Debug communication failures
  usage:
         ./debugcom.py <log file>
"""
import sys

def debugCommunication( data ):
    packet = ""
    for d,val in zip( data[::2], data[1::2] ):
        assert ord(d) in [0,1], ord(d)
        if ord(d) == 0:
            packet += "%02X" % (ord(val))
        else:
            if packet:
                print packet
                packet = ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(-1)
    debugCommunication( open(sys.argv[1], "rb").read() )

# vim: expandtab sw=4 ts=4 

