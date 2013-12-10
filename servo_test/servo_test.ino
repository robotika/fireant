
// FireAnt servo test
//   robotika.cz
#include <BMServo.h>

const int SERVO_PIN = 10;

const int BUTTON_PIN = 2;
const int ledPin =  A1;      // the number of the LED pin


int angle = 0;

// variables will change:
int buttonState = 0;         // variable for reading the pushbutton status

BMServo servo( SERVO_PIN );

void setup()
{
  pinMode(ledPin, OUTPUT);
  pinMode( BUTTON_PIN, INPUT);
  servo.begin();
  servo.setAngle( angle, 1000 );
}

void loop()
{
  servo.update();

  buttonState = digitalRead( BUTTON_PIN );

  if (buttonState == HIGH) {     
    // turn LED on:    
    digitalWrite(ledPin, HIGH);  
    servo.setAngle( 200, 1000 );
  } 
  else {
    // turn LED off:
    digitalWrite(ledPin, LOW); 
    servo.setAngle( -200, 1000 );
  }
}

