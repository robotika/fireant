// Experiment with Bluetooth module
// console for mirroing input and output

#include <BMSerial.h>

BMSerial bluetooth(8,9);

void setup()
{
  Serial.begin( 9600 );
  Serial.println( "BlueTooth TEST" ); 
  bluetooth.begin( 9600 );
}

void loop()
{
  if( bluetooth.available() )
    Serial.write( bluetooth.read() );
    
  int b;
  b = Serial.read(); 
  if( b >= 0 )
    bluetooth.write( b );
}

