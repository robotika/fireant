; Experimental code for direct servo control over serial port

servoindex var byte
pos var word
pwr var word
time var word ; unknown units, but it seems that 16bit TCNT counter is running

LIPOCUTOFF con		620*1024/500	;62*1024/5.0
ADCSR = 0x30	;start scanning AD conversion

HSERVOFEEDBACK

servoindex = 21
time = 0

sethserial1 h38400

TCRV0 = 0x03  ;Sets Timer V to count once every 128 OSC clocks
TCRV1 = 0x01

main
	hservo[servoindex\-30000+258]
	time = TCB1
	pos = hservofbpos( servoindex )
	pwr = hservofbpwr( servoindex )
	hserout s_out, [DEC time, " : ", DEC (ADDRA>>4)," SERVO ", DEC pos, " FORCE ", DEC pwr, 13]
	goto main
