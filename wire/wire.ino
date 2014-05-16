// software wire of MOSI/MISO to serial port
// mirror communication to green and red LEDs

#define GREENLED A1
#define REDLED A0

#define RXD 0
#define TXD 1

// Bluetooth pins
#define BT_RXD 8
#define BT_TXD 9

void setup()
{
  pinMode( GREENLED, OUTPUT );
  pinMode( REDLED, OUTPUT );
  pinMode( TXD, OUTPUT );
  pinMode( BT_TXD, OUTPUT );
  pinMode( MOSI, OUTPUT );
  pinMode( BT_RXD, INPUT );
  digitalWrite( BT_RXD, HIGH ); // pullup required for Bluetooth module
  pinMode( RXD, INPUT );
  digitalWrite( RXD, HIGH ); // pullup (to handle not connected pin(?))  
}

void loop()
{
  if( digitalRead( MISO ) == LOW )
  {
    digitalWrite( TXD, LOW );
    digitalWrite( BT_TXD, LOW );
    digitalWrite( GREENLED, HIGH );
  }
  else
  {
    digitalWrite( TXD, HIGH );
    digitalWrite( BT_TXD, HIGH );
    digitalWrite( GREENLED, LOW );
  }
  if( digitalRead( RXD ) == LOW || digitalRead( BT_RXD ) == LOW )
  {
    digitalWrite( MOSI, LOW );
    digitalWrite( REDLED, HIGH );
  }
  else
  {
    digitalWrite( MOSI, HIGH );
    digitalWrite( REDLED, LOW );
  }
}

