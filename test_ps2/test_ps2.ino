// Simple test of PlayStation2 interface
#include <BMSerial.h>
#include <BMPS2X.h>

BMPS2 ps2x(6,100);

void setup()
{
  Serial.begin(9600);
  //Clears pressed/released states
  ps2x.explicitReadsOnly();
  ps2x.read_ps2(true);
  delay(100);
  ps2x.read_ps2(true);
}

void loop()
{
  if (ps2x.read_ps2(true))
    Serial.print(".");
  else 
    Serial.print("E");
}

