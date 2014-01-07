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

const int16_t STOP_SERVO = -32768;

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
  uint16_t executeAt; // TODO
  uint16_t watchDog; // TODO
  uint16_t servoTime;
  int16_t servoAngle[NUM_SERVOS];
} robotCmd;

void updateRobotStatus()
{
  int i;
  robotStatus.time = micros()/1000; // ms instead of us ... even that loooks bit strange
  robotStatus.voltage = Orion.queryVoltage();
  for( i = 0; i < NUM_SERVOS; i++ )
  {
    robotStatus.servo[i].position = Orion.queryFBAngle( servoPins[i] );    
    robotStatus.servo[i].force = Orion.queryForce( servoPins[i] );
  }
}

void sendRobotStatus()
{
  int i;
  uint8_t tmpSum; 
  Serial.write( PACKET_START );
  Serial.write( sizeof(RobotStatus) );
  tmpSum = sizeof(RobotStatus);
  for( i = 0; i < sizeof(RobotStatus); i++ )
  {
    Serial.write( ((uint8_t*)&robotStatus)[i] );
    tmpSum += ((uint8_t*)&robotStatus)[i];
  }
  Serial.write( -tmpSum );
}


int blockedRead()
{
  // not good solution ... just quick wrapper
  int b;
  b = Serial.read();
  while( b < 0 )
    b = Serial.read();
  return b;
}

void receiveRobotCmd()
{
  int i, b, packetSize;
  uint8_t tmpSum; 
  Orion.green( true );
  b = blockedRead();
  while( true )
  {
    while( b != PACKET_START )
      b = blockedRead();
    packetSize = blockedRead();
    tmpSum = packetSize; // checksum is with length included
    if( packetSize != sizeof( RobotCmd ) )
    {
      Orion.red( true );
      Orion.tone(NOTE_F6,100); 
      continue;
    }
    for( i = 0; i < packetSize; i++ )
      tmpSum += ((uint8_t*)&robotCmd)[i] = blockedRead();
    tmpSum += blockedRead();
    if( tmpSum != 0 )
    {
      // checksum error
      Orion.red( true );
      Orion.tone(NOTE_G6,100); 
      continue;
    }
    break;
  }
  Orion.green( false );
}

void executeRobotCmd()
{
  Orion.setTime( robotCmd.servoTime );
  int i;
  for( i = 0; i < NUM_SERVOS; i++ )
    if( robotCmd.servoAngle[i] == STOP_SERVO )
      Orion.stopPulse( servoPins[i] );
    else
      Orion.setAngle( servoPins[i], robotCmd.servoAngle[i] );
  Orion.execute();
}

//----------------------------------------------------

void setup()
{
  Serial.begin( 38400 );
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
  receiveRobotCmd();
  if(Orion.checkLipo())
  {
    for( i = 0; i < NUM_SERVOS; i++ )
      Orion.stopPulse( servoPins[i] ); // it is by default, but this way it is more clear
    return; //Battery too low to do anything.
  }
  executeRobotCmd();
}

