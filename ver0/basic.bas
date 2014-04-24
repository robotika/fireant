; Experimental code for direct servo control over serial port

STOP_SERVO con -30000+258

servoindex var byte
time var word ; unknown units, but it seems that 16bit TCNT counter is running
battery var word

servopos var word(24)
servopwr var word(24)


LIPOCUTOFF con		620*1024/500	;62*1024/5.0
ADCSR = 0x30	;start scanning AD conversion

HSERVOFEEDBACK
sethserial1 h38400

gosub stopAllServos

main
	gosub readServoStatus
	gosub sendServoStatus
	goto main

;-------------------------------
stopAllServos
	for servoindex = 0 to 23
		hservo[servoindex\STOP_SERVO]
	next
	return

readServoStatus
	time = TCB1
	battery = ADDRA>>4
	for servoindex = 0 to 23
		servopos( servoindex ) = hservofbpos( servoindex )
		servopwr( servoindex ) = hservofbpwr( servoindex )
	next
	return

PACKET_START con 0xAB
	
sendServoStatus
	chSum var byte
	chSum = 0
	hserout s_out, [PACKET_START, 2+24*2*2]
	hserout s_out, [time]
	hserout s_out, [battery]
	for servoindex = 0 to 23
		hserout s_out, [servopos( servoindex )]
		hserout s_out, [servopwr( servoindex )]
	next
	; TODO compute chSum
	hserout s_out, [chSum]
	return
