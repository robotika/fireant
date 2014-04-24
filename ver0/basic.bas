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
	serout s_out, i9600, ["Hello Word!",13]
	pause 10
	serout s_out, i9600, [DEC ADDRA,13]
	pause 10
	tmp = hservofbpos( servoindex )
	serout s_out, i9600, ["SERVO", DEC tmp, 13]
	pause 10
	goto main
hservo[1\0] ; just that it pass "Linking ..."