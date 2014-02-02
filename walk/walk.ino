// Simple FireAnt walk example without external communication
// - this example uses only Servo Shield servos (i.e. ignoring FireAnt tail servos)
// - copy & paste from official FireAnt firmware from Orion Robotics
//
// more info at:
//       http://robotika.cz/robots/fireant/ 
//
/////////////////////////////////////////////////////////////////////

#include <Orion.h> 
#include <SPI.h> 

#define LFC 23
#define LFF 22 
#define LFT 21
#define LMC 20
#define LMF 19
#define LMT 18
#define LRC 17
#define LRF 16
#define LRT 0 

#define RFC 15
#define RFF 14
#define RFT 13
#define RMC 12
#define RMF 11
#define RMT 10
#define RRC 9
#define RRF 8
#define RRT 1

// only for on/off
#define HeadRollPin 7
#define HeadYawPin 6
#define HeadPitchPin 5
#define PincerLPin 4
#define PincerRPin 3  

//Maximum body movement offsets
#define MAXX 625
#define MAXY 2000
#define MAXZ 550
#define MAXR 175
#define MAXBODYYAW 300
#define MAXBODYROLL 300
#define MAXBODYPITCH 300

const int BUTTON_PIN = 2; 

const unsigned char servoPins[] = { LFC, LFF, LFT,   LMC, LMF, LMT,   LRC, LRF, LRT, 
                                    RFC, RFF, RFT,   RMC, RMF, RMT,   RRC, RRF, RRT,
                                    HeadRollPin, HeadYawPin, HeadPitchPin, PincerLPin, PincerRPin }; 
const unsigned int NUM_SERVOS = sizeof(servoPins)/sizeof(unsigned char); 

//Robot Initial Positions(1/10 mm units)
const int DefBodyPosX[6] = {706,706,706,-706,-706,-706};
const int DefBodyPosY[6] = {-370,-370,-370,-370,-370,-370};
const int DefBodyPosZ[6] = {841,0,-841,841,0,-841};
const int DefLegPosX[6] = {1083,1250,1083,-1083,-1250,-1083};
const int DefLegPosY[6] = {0,0,0,0,0,0};
const int DefLegPosZ[6] = {625,0,-625,625,0,-625};


// blinking green LED
bool walking;
boolean heartbeat; 
long lastbeat;

// FireAnt body
unsigned char Gait;
int Rate;

int Xdist;
int Ydist;
int Zdist;
int Rdist;
int BodyOffsetX;
int BodyOffsetY;
int BodyOffsetZ;
int BodyRotOffsetZ;
int BodyYaw;
int BodyPitch;
int BodyRoll;
int XLegAdj;
int ZLegAdj; 

void StopServos()
{
  int i;
  for( i = 0; i < NUM_SERVOS; i++ )
    Orion.stopPulse( servoPins[i] ); // it is by default, but this way it is more clear 
}

void InitState()
{
//  RightJoystickMode=0;
//  ReturnToCenter=0;
//  RotateMode=0;
  Rate=11;
  Xdist=0;
  Ydist=MAXY/4;
  Zdist=0;
  Rdist=0;
  BodyOffsetX=0;
  BodyOffsetY=0;
  BodyOffsetZ=0;
  BodyRotOffsetZ=0;
  BodyYaw=0;
  BodyPitch=0;
  BodyRoll=0;
  XLegAdj=0;
  ZLegAdj=0; 

  for( int i=0; i<6; i++ )
  {
    Orion.setBodyPos(i,DefBodyPosX[i],DefBodyPosY[i],DefBodyPosZ[i]);
    Orion.setLegPos(i,DefLegPosX[i],DefLegPosY[i],DefLegPosZ[i]);
  }

  Gait = OrionClass::TRI4;
  Orion.gaitSelect((OrionClass::GAITTYPE)Gait); 
}

void setup()
{
  walking = false;
  heartbeat = true;
  lastbeat = millis();
  
  Orion.begin();
  Orion.green( heartbeat );
  Orion.red(false); 
  Orion.tone(NOTE_C6,100);  
  Orion.tone(NOTE_D6,100);  
  Orion.tone(NOTE_E6,100);  
  Orion.tone(NOTE_F6,100);  

  StopServos();

  Orion.setBalanceMode(0x2);
  Orion.setBalanceTransRate(50);
  Orion.setBalanceAngleRate(200); 

  InitState(); 
  
  Orion.tone(NOTE_G5,200); 
  Orion.tone(NOTE_G5,200); 
}

void loop()
{
  if(Orion.checkLipo())
  {
    StopServos();
    return; //Battery too low to do anything.
  } 
  
  if( !walking )
  {
    if( digitalRead( BUTTON_PIN ) == LOW )
      walking = true;
    return;
  }
  
  //Heart beat LED
  long time = millis() - lastbeat;
  if( time > 200 )
  {
    lastbeat = millis();
    heartbeat ^= heartbeat;
    Orion.green( heartbeat );
  } 

  //Sends new commands to Orion if there are any changes
  Orion.execGait(BodyYaw,
                 BodyRoll,
                 BodyPitch,
                 BodyOffsetX,
                 BodyOffsetY,
                 0, //hack DefBodyRotOffset[RotateMode],
                 BodyOffsetX,
                 BodyOffsetY,
                 BodyOffsetZ,
                 Xdist,
                 Ydist,
                 Zdist,
                 Rdist,
                 XLegAdj,
                 ZLegAdj,
                 16-Rate,
                 false); 
}

