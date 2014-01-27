// ServoMin/Max test
// more info at:
//       http://robotika.cz/robots/fireant/ 

#include <Orion.h>
#include <SPI.h> 

#define SERVO_PIN 21 


void setup()
{
  Orion.begin(); 
  Orion.tone(NOTE_C6,100); 
  Orion.tone(NOTE_E6,100); 
  delay(100); 
}

void loop()
{
  if(Orion.checkLipo())
  {
    Orion.stopPulse( SERVO_PIN );
    return;
  } 
  Orion.setTime( 100 ); 
  Orion.setAngle( SERVO_PIN, 0 );
  Orion.execute(); 
}

