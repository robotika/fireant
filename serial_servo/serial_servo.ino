// Simple experiment with servo controlled over serial connection
// - ignored details about timing
// - no checksums in communication
// more info at:
//       http://robotika.cz/robots/fireant/

#include <Orion.h>
#include <SPI.h>

const unsigned char START_BLOCK = 0x80;
const unsigned char END_BLOCK = 0x81;
const unsigned char STOP_SERVO = 0x82;
const unsigned char SERVO_OUT_OF_RANGE = 0x83;
const int SERVO_MIN = -1200; // ... are converted to -120..120 over serial
const int SERVO_MAX = 1200;

// copy from FireAnt
#define RMC 12  // Right Middle Coxa
#define RMF 11  // Right Front Femur
#define RMT 10  // Right Front Tibia

#define LMC 20
#define LMF 19
#define LMT 18 

const unsigned char servoPins[] = { LMC, LMF, LMT };
const unsigned int NUM_SERVOS = sizeof(servoPins)/sizeof(unsigned char);

void setup()
{
  Serial.begin( 9600 );
  Serial.print( "SerialServo test ...\n" );

  Orion.begin(); 
  Orion.tone(NOTE_F6,100); 
  int i;
  for( i = 0; i < NUM_SERVOS; i++ )
  { 
    Orion.stopPulse( servoPins[i] ); // it is by default, but this way it is more clear
    Orion.setServoMin( servoPins[i], SERVO_MIN );
    Orion.setServoMax( servoPins[i], SERVO_MAX );
  }
}

void loop()
{
  int i;
  if(Orion.checkLipo())
  {
    for( i = 0; i < NUM_SERVOS; i++ )
      Orion.stopPulse( servoPins[i] ); // it is by default, but this way it is more clear
    return; //Battery too low to do anything.
  }
  
  Serial.write( START_BLOCK );
  for( i = 0; i < NUM_SERVOS; i++ )
  {
    int angle = Orion.queryFBAngle( servoPins[i] );    
    if( angle < SERVO_MIN || angle > SERVO_MAX )
      Serial.write( SERVO_OUT_OF_RANGE );
    else
      Serial.write( (unsigned char)(angle/10) );
  }
  
  Serial.write( END_BLOCK );
}

