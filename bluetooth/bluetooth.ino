// Experiment with Bluetooth module
// console for mirroing input and output

#include <BMSerial.h>
#include <Orion.h>
#include <SPI.h> 

BMSerial bluetooth(8,9);

void setup()
{
  Serial.begin( 9600 );
  Serial.println( "BlueTooth TEST" ); 
  Orion.begin();
  Orion.tone(NOTE_C4,100);  
  Orion.tone(NOTE_D4,100);
  bluetooth.begin( 38400 );
}

void loop()
{
  if(Orion.checkLipo())
  {
    return; //Battery too low to do anything.
  } 
  if( bluetooth.available() )
    Serial.write( bluetooth.read() );
    
  int b;
  b = Serial.read(); 
  if( b >= 0 )
  {
    Serial.write( b ); // ECHO
    bluetooth.write( b );
  }
}

