// FireAnt servo test
//   robotika.cz
#include <BMServo.h>
#include <Orion.h>
#include <SPI.h>


const int ARDUINO_SERVO_PIN = 10;
const int SPI_SERVO_PIN = 0;


const int BUTTON_PIN = 2;
const int ledPin =  A1;      // the number of the LED pin


// variables will change:
int buttonState = 0;         // variable for reading the pushbutton status

BMServo servo( ARDUINO_SERVO_PIN );

void setup()
{
  pinMode(ledPin, OUTPUT);
  pinMode( BUTTON_PIN, INPUT);
  servo.begin();
  
  Orion.begin(); 
  Orion.tone(NOTE_C6,100); 
  Orion.setServoMin( SPI_SERVO_PIN, -900 );
  Orion.setServoMax( SPI_SERVO_PIN, 900 );
}

void loop()
{
  if(Orion.checkLipo())
  {
    Orion.stopPulse( SPI_SERVO_PIN );
    servo.stopPulse();
    return; //Battery too low to do anything.
  }
  servo.update();

  buttonState = digitalRead( BUTTON_PIN );

  Orion.setTime( 1000 );
  if (buttonState == HIGH) {     
    // turn LED on:    
    digitalWrite(ledPin, HIGH);  
    servo.setAngle( 200, 1000 );
    Orion.setAngle( SPI_SERVO_PIN, 900 );
  } 
  else {
    // turn LED off:
    digitalWrite(ledPin, LOW); 
    servo.setAngle( -200, 1000 );
    Orion.setAngle( SPI_SERVO_PIN, -900 );
  }
  Orion.execute();
}

