// ServoMin/Max test
// more info at:
//       http://robotika.cz/robots/fireant/ 

#include <Orion.h>
#include <SPI.h> 

#define SERVO_PIN 21 

void warning( int tone=NOTE_C6, int num=10 )
{
  int i;
  for( i = 0; i < num; i++ )
  {
    Orion.red( true );
    Orion.tone( tone,100 ); 
    Orion.red( false );
    delay(100); 
  }
}

void setServo( int servoPin, int servoMin, int servoMax, int servoOffset, int servoDir )
{
  Orion.setServoMin( servoPin, servoMin );
  Orion.setServoMax( servoPin, servoMax );
  Orion.setAOffset( servoPin, servoOffset );
  Orion.setServoDir( servoPin, servoDir );
  if( Orion.queryServoMin( servoPin ) != servoMin )
    warning( NOTE_C6, 3 );
  if( Orion.queryServoMax( servoPin ) != servoMax )
    warning( NOTE_D6, 5 ); 
  if( Orion.queryAOffset( servoPin ) != servoOffset )
    warning( NOTE_E6, 7 );
}

void setup()
{
  Orion.begin(); 
  Orion.tone(NOTE_C6,100); 
  Orion.tone(NOTE_E6,100); 
  delay(100); 
  setServo( SERVO_PIN, -2000, 2000, 100, 1 );
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
  Orion.setAngle( SERVO_PIN, 200 );
  Orion.execute(); 
  delay(10); 
}

