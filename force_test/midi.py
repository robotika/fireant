"""
  MIDI logging using pygame
  usage:
    ./midi.py <output file>
"""

import pygame.midi 
import sys

def logMIDI( filename ):
  f = open( filename, "w" )
  pygame.midi.init()
  inputID = pygame.midi.get_default_input_id() 
  print inputID
  midi = pygame.midi.Input( inputID ) 
  while True:
    if midi.poll():
      arr = midi.read(10)
      f.write( str(arr) + '\n' )
      assert len(arr) == 1, arr
      assert len(arr[0]) == 2, arr  # data and timestamp
      assert len(arr[0][0]) == 4, arr
      tmp, tone, cmd, zero = arr[0][0]
      if tone > 90:
        break
  del midi
  f.close()
  pygame.midi.quit()


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print __doc__
    sys.exit(-1)
  logMIDI( sys.argv[1] )
