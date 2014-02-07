#include <BMSerial.h>
#include <BMPS2X.h>

BMPS2 ps2x(6,100);

void setup()
{
  Serial.begin(625000);
  //Clears pressed/released states
  ps2x.explicitReadsOnly();
  ps2x.read_ps2(true);
  delay(100);
  ps2x.read_ps2(true);
}

void loop()
{
  // Get the new PS2 state. - Wait for a PS2 cycle time?
  ps2x.read_ps2(true);
}

