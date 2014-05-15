// software wire of MOSI/MISO to serial port
// mirror communication to green and red LEDs

#define GREENLED A1
#define REDLED A0

#define RXD 0
#define TXD 1

void setup()
{
  pinMode( GREENLED, OUTPUT );
  pinMode( REDLED, OUTPUT );
  pinMode( TXD, OUTPUT );
  pinMode( MOSI, OUTPUT );
}

void loop()
{
  if( digitalRead( MISO ) == LOW )
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
    digitalWrite( MOSI, LOW );
  }
  else
  {
    digitalWrite( REDLED, HIGH );
    digitalWrite( MOSI, HIGH );
  }
}

