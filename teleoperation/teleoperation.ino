// This is simple example how feedback servos works
// First servo is in calibration mode and second repeats the motions
// More info at
//    http://robotika.cz/robots/fireant/

#include <Orion.h>
#include <SPI.h>

const int SERVO_MIN = -300;
const int SERVO_MAX = 300;

const int IN_SERVO_PIN = 0;
const int OUT_SERVO_PIN = 1;

const int BUTTON_PIN = 2;
bool calibrated;

int buttonState = 0;         // variable for reading the pushbutton status 

void setup()
{
  Serial.begin( 9600 );
  Serial.print( "TeleOperation test ...\n" );

  Orion.begin(); 
  Orion.tone(NOTE_C6,100); 
  Orion.stopPulse( IN_SERVO_PIN ); // it is by default, but this way it is more clear
  Orion.setAOffset( IN_SERVO_PIN, 0 );
  Orion.setServoMin( IN_SERVO_PIN, SERVO_MIN );
  Orion.setServoMax( IN_SERVO_PIN, SERVO_MAX );
  Orion.setAOffset( OUT_SERVO_PIN, 0 );
  Orion.setServoMin( OUT_SERVO_PIN, SERVO_MIN );
  Orion.setServoMax( OUT_SERVO_PIN, SERVO_MAX );
  
  pinMode( BUTTON_PIN, INPUT);   
  calibrated = true; // calibration disabled ... not working ... was false;
}

void loop()
{
  if(Orion.checkLipo())
  {
    Orion.stopPulse( OUT_SERVO_PIN );
    return; //Battery too low to do anything.
  }
  buttonState = digitalRead( BUTTON_PIN );
  if( calibrated )
  {
    int angle = Orion.queryFBAngle( IN_SERVO_PIN );
    
    if( angle < SERVO_MIN || angle > SERVO_MAX )
      Serial.println( angle );
    else
    {
      Orion.setTime( 1000 );
      Orion.setAngle( OUT_SERVO_PIN, angle );
      Orion.execute();
    }
  }
  else
  {
    Orion.red( true ); // some indication
    if( buttonState == LOW )
    {
      Orion.green( true );
      Orion.setAOffset( IN_SERVO_PIN, Orion.queryFBAngle( IN_SERVO_PIN ) );
      Orion.setServoMin( IN_SERVO_PIN, Orion.queryFBAngle( IN_SERVO_PIN ) - 300 );
      Orion.setServoMax( IN_SERVO_PIN, Orion.queryFBAngle( IN_SERVO_PIN ) + 300 );
      Orion.setAOffset( OUT_SERVO_PIN, Orion.queryFBAngle( OUT_SERVO_PIN ) );
      Orion.setServoMin( OUT_SERVO_PIN, Orion.queryFBAngle( OUT_SERVO_PIN ) - 300 );
      Orion.setServoMax( OUT_SERVO_PIN, Orion.queryFBAngle( OUT_SERVO_PIN ) + 300 );
      Orion.writeRegisters();
      Orion.red( false );
      calibrated = true;
    }
  }
}

