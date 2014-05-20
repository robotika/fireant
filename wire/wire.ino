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
    digitalWrite( TXD, digitalRead( MISO ));
    digitalWrite( MOSI, digitalRead( RXD ));

//   digitalWrite( BT_TXD, digitalRead( MISO ));
//   digitalWrite( MOSI, digitalRead( BT_RXD ));

//   digitalWrite( BT_TXD, digitalRead( RXD ));
//   digitalWrite( TXD, digitalRead( BT_RXD ));

//   digitalWrite( TXD, digitalRead( RXD ));
  }
}


// syntax taken from http://www.nongnu.org/avr-libc/user-manual/inline_asm.html
// PD0 = RXD ... PIND=0x09, PORTD=0x0B
// PD1 = TXD
// PB3 = MOSI ... PINB=0x03, PORTB=0x05
// PB4 = MISO
// PB0 = 8 BT_RXD
// PB1 = 9 BT_TXD

// Bluetooth <-> Servo Shield
void loopBTver0()
{
  asm volatile (
    "cli"  "\n\t" // disable interrupts
   "1:" " sbis 0x3,0"   "\n\t"
    "cbi 0x5,3"    "\n\t"
    "sbic 0x3,0"   "\n\t"
    "sbi 0x5,3"    "\n\t"
    
    "sbis 0x3,4"   "\n\t"  // 1/2/3
    "cbi 0x5,1"    "\n\t"  // 2
    "sbic 0x3,4"   "\n\t"
    "sbi 0x5,1"    "\n\t" // 2
    "rjmp 1b" "\n\t" // 2
    ::);
}

void loop()
{
  asm volatile (
    "cli"  "\n\t" // disable interrupts
    "in r20, 0x5"   "\n\t" // 1
   "1:"
    "in r21, 0x3"   "\n\t" // 1
    
    "cbr r20,(1<<3)|(1<<1)"    "\n\t" // 1
    "sbrc r21,0"        "\n\t" // 1/2/3
    "sbr r20,(1<<3)"    "\n\t" // 1
    
    "sbrc r21,4"   "\n\t"  // 1/2/3
    "sbr r20,(1<<1)"    "\n\t"  // 1
    
    "out 0x5, r20"  "\n\t" // 1
    
    "rjmp 1b" "\n\t" // 2
    ::);
}



// setup BT
void loopSetupBT()
{
  asm volatile (
    "cli"  "\n\t" // disable interrupts
   "1:" " sbis 0x9,0"   "\n\t"
    "cbi 0x5,1"    "\n\t"
    "sbic 0x9,0"   "\n\t"
    "sbi 0x5,1"    "\n\t"
    
    "sbis 0x3,0"   "\n\t"
    "cbi 0xB,1"    "\n\t"
    "sbic 0x3,0"   "\n\t"
    "sbi 0xB,1"    "\n\t"
    "rjmp 1b" "\n\t"
    ::);
}

