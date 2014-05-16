// software wire of MOSI/MISO to serial port
// mirror communication to green and red LEDs

#define GREENLED A1
#define REDLED A0

//#define RXD 0
//#define TXD 1

// Bluetooth pins
#define RXD 8
#define TXD 9

void setup()
{
  pinMode( GREENLED, OUTPUT );
  pinMode( REDLED, OUTPUT );
  pinMode( TXD, OUTPUT );
  pinMode( 1, OUTPUT );
  pinMode( RXD, INPUT );
  digitalWrite( RXD, HIGH ); // pullup required for Bluetooth module
}

void loop()
{
  if( digitalRead( 0 ) == LOW )
  {
    digitalWrite( GREENLED, LOW );
    digitalWrite( TXD, LOW );
  }
  else
  {
    digitalWrite( GREENLED, HIGH );
    digitalWrite( TXD, HIGH );
  }
  if( digitalRead( RXD ) == LOW )
  {
    digitalWrite( REDLED, LOW );
    digitalWrite( 1, LOW );
  }
  else
  {
    digitalWrite( REDLED, HIGH );
    digitalWrite( 1, HIGH );
  }
}

