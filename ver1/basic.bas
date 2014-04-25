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

updateTime
	prev var byte
	curr var byte
	prev = time & 0xFF
	curr = TCB1
	time = time - prev + curr
	if curr < prev then
		time = time + 256	
	endif
	return


readServoStatus
	gosub updateTime
	battery = ADDRA>>4
	for servoindex = 0 to 23
		servopos( servoindex ) = hservofbpos( servoindex )
		servopwr( servoindex ) = hservofbpwr( servoindex )
	next
	return

PACKET_START con 0xAB
	
sendServoStatus
	chSum var byte
	dataLen var byte
	dataLen = 2+2+24*2*2
	chSum = 0
	hserout s_out, [PACKET_START, dataLen]
	hserout s_out, [time &0xFF, time>>8 ]
	hserout s_out, [battery & 0xFF, battery >> 8]
	chSum = chSum + dataLen + (time & 0xFF) + ((time >> 8)&0xFF) + (battery & 0xFF) + ((battery >> 8)&0xFF)
	for servoindex = 0 to 23
		hserout s_out, [servopos( servoindex )&0xFF, servopos( servoindex )>>8]
		chSum = chSum + (servopos( servoindex ) & 0xFF) + (servopos( servoindex ) >> 8)
		hserout s_out, [servopwr( servoindex )&0xFF, servopwr( servoindex )>>8]
		chSum = chSum + (servopwr( servoindex ) & 0xFF) + (servopwr( servoindex ) >> 8)
	next
	hserout s_out, [-chSum]
	return
