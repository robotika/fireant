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

void loopSlow()
{
  noInterrupts();
  for(;;)
  { 
//   digitalWrite( BT_TXD, digitalRead( MISO ));
//   digitalWrite( MOSI, digitalRead( BT_RXD ));

//   digitalWrite( BT_TXD, digitalRead( RXD ));
//   digitalWrite( TXD, digitalRead( BT_RXD ));

   digitalWrite( TXD, digitalRead( RXD ));
  }
}

void loop()
{
  // syntax taken from http://www.nongnu.org/avr-libc/user-manual/inline_asm.html
  // PD0 = RXD ... PIND=0x09, PORTD=0x0B
  // PD1 = TXD
  // PB3 = MOSI
  // PB4 = MISO
  asm volatile (
    "cli"  "\n\t" // disable interrupts
   "1:" " sbis 0x9,0"   "\n\t"
    "cbi 0xB,1"    "\n\t"
    "sbic 0x9,0"   "\n\t"
    "sbi 0xB,1"    "\n\t"
    "rjmp 1b" "\n\t"
    ::);
}

