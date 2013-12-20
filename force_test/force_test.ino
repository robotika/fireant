// ----------------
// goal: find the piano keyboard
// more info at:
//       http://robotika.cz/robots/fireant/

#include <Orion.h>
#include <SPI.h>

#define LMC 20
#define LMF 19
#define LMT 18 

const unsigned char servoPins[] = { LMC, LMF, LMT };
const unsigned int NUM_SERVOS = sizeof(servoPins)/sizeof(unsigned char);

const uint8_t ECHO_CHAR = 'D'; // in memory of Daisy robot
const uint8_t PACKET_START = 0xAB;

struct ServoStatus
{
  int16_t position;
  int16_t force;
};

struct RobotStatus
{
  uint16_t time;
  uint16_t voltage;
  ServoStatus servo[NUM_SERVOS];
} robotStatus;

struct RobotCmd
{
};

void updateRobotStatus()
{
  int i;
  robotStatus.time = micros();
  robotStatus.voltage = Orion.queryVoltage();
  for( i = 0; i < NUM_SERVOS; i++ )
  {
    robotStatus.servo[i].position = Orion.queryFBAngle( servoPins[i] );    
    robotStatus.servo[i].force = Orion.queryForce( servoPins[i] );
  }
}

#define SEND8_WITH_CHECKSUM(X) Serial.write( (X) ); tmpSum += (X); 
#define SEND16_WITH_CHECKSUM(X) {Serial.write( (X>>8) ); tmpSum += (X>>8); Serial.write( (X & 0xFF) ); tmpSum += (X & 0xFF);}

void sendRobotStatus()
{
  int i;
  uint8_t tmpSum; 
  Serial.write( PACKET_START );
  SEND8_WITH_CHECKSUM( sizeof(RobotStatus) + 1 );
  SEND16_WITH_CHECKSUM( robotStatus.time );
  SEND16_WITH_CHECKSUM( robotStatus.voltage );
  for( i = 0; i < NUM_SERVOS; i++ )
  {
    SEND16_WITH_CHECKSUM( robotStatus.servo[i].position );    
    SEND16_WITH_CHECKSUM( robotStatus.servo[i].force );
  }
  Serial.write( -tmpSum );
}

void setup()
{
  Serial.begin( 9600 );
  Serial.print( "ForceServo test ...\n" );

  Orion.begin(); 
  Orion.tone(NOTE_C6,100); 
  Orion.tone(NOTE_D6,100); 
  Orion.tone(NOTE_E6,100); 
}

void loop()
{
  int i;
  updateRobotStatus();
  sendRobotStatus();
  if(Orion.checkLipo())
  {
    for( i = 0; i < NUM_SERVOS; i++ )
      Orion.stopPulse( servoPins[i] ); // it is by default, but this way it is more clear
    return; //Battery too low to do anything.
  }
}

