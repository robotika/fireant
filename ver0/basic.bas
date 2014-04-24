; Experimental code for direct servo control over serial port

servoindex var byte
pos var word
pwr var word
timeMs var word

LIPOCUTOFF con		620*1024/500	;62*1024/5.0
ADCSR = 0x30	;start scanning AD conversion

HSERVOFEEDBACK

serout s_out, i9600, ["BASIC ver0", 13]
pause 10

servoindex = 21
timeMs = 0

; this is causing error characters on serial line ... ONINTERRUPT HSERVOINT,servohandler

main
	hservo[servoindex\-30000+258]
	pos = hservofbpos( servoindex )
	pwr = hservofbpwr( servoindex )
	serout s_out, i9600, [DEC timeMs, " : ", DEC (ADDRA>>4)," SERVO ", DEC pos, " FORCE ", DEC pwr, 13]
	pause 200
	goto main

;---------------------
servohandler
	; TODO check battery and turn off servos
	timeMs = timeMs + 20
	resume
