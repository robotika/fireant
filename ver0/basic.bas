; Experimental code for direct servo control over serial port

servoindex var byte
tmp var word

LIPOCUTOFF con		620*1024/500	;62*1024/5.0
ADCSR = 0x30	;start scanning AD conversion

HSERVOFEEDBACK

serout s_out, i9600, ["BASIC ver0", 13]
pause 10

servoindex = 21

main
	hservo[servoindex\0]
	tmp = hservofbpos( servoindex )
	serout s_out, i9600, [DEC ADDRA," SERVO ", DEC tmp, 13]
	pause 200
	goto main
