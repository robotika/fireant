; Experimental code for direct servo control over serial port

STOP_SERVO con -30000+258

TIMEOUT con 100

servoindex var byte
time var word ; unknown units, but it seems that 16bit TCNT counter is running
battery var word
lastCmdId var word;

servopos var word(24)
servopwr var word(24)

inputbuf var byte(24*2+2+2+1) ; cmdId, execute at, servos position, 
executeAt var word
servoCmd var word(24)

chSum var byte
result var byte


LIPOCUTOFF con		620*1024/500	;62*1024/5.0
ADCSR = 0x30	;start scanning AD conversion

HSERVOFEEDBACK
sethserial1 h38400

gosub stopAllServos

lastCmdId = 0
main
	gosub readServoStatus
	gosub sendServoStatus
	gosub receiveServoCmd, result
	if result = 1 and battery >= LIPOCUTOFF then
		; TODO servo battery -> stopAllServos
		gosub executeServoCmd
	else
		gosub stopAllServos
	endif
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
	dataLen var byte
	dataLen = 2+2+2+24*2*2
	chSum = 0
	hserout s_out, [PACKET_START, dataLen]
	hserout s_out, [lastCmdId &0xFF, lastCmdId>>8 ]
	hserout s_out, [time &0xFF, time>>8 ]
	hserout s_out, [battery & 0xFF, battery >> 8]
	chSum = chSum + dataLen + (lastCmdId & 0xFF) + ((lastCmdId >> 8)&0xFF) + (time & 0xFF) + ((time >> 8)&0xFF) + (battery & 0xFF) + ((battery >> 8)&0xFF)
	for servoindex = 0 to 23
		hserout s_out, [servopos( servoindex )&0xFF, servopos( servoindex )>>8]
		chSum = chSum + (servopos( servoindex ) & 0xFF) + (servopos( servoindex ) >> 8)
		hserout s_out, [servopwr( servoindex )&0xFF, servopwr( servoindex )>>8]
		chSum = chSum + (servopwr( servoindex ) & 0xFF) + (servopwr( servoindex ) >> 8)
	next
	hserout s_out, [-chSum]
	return

receiveServoCmd
	tmp var byte
	i var byte
	packetSize var byte
	hserin s_in, timeoutException, TIMEOUT, [tmp]
	while tmp <> PACKET_START
		hserin s_in, timeoutException, TIMEOUT, [tmp]
	wend
	hserin s_in, timeoutException, TIMEOUT, [tmp]
	packetSize = tmp
	chSum = tmp; checksum is with length included
	if packetSize = 24*2+2+2 then
		for i = 0 to packetSize; including check sum
			hserin s_in, timeoutException, TIMEOUT, [tmp]
			inputbuf(i) = tmp
			chSum = chSum + tmp
		next
		if chSum = 0 then
			lastCmdId = inputbuf(0) + 256*inputbuf(1)
			executeAt = inputbuf(2) + 256*inputbuf(3)
			for i = 0 to 23
				servoCmd(i) = inputbuf(4+2*i) + 256*inputbuf(5+2*i)
			next
			return 1
		else
			hserout s_out, ["ERROR chSum"]
		endif
	else
		hserout s_out, ["ERROR packetSize"]
	endif
	return 0
timeoutException
	hserout s_out, ["ERROR timeout"]
	return 0


executeServoCmd0
		hservo[servoindex\servoCmd(21)]
	return
	
executeServoCmd
	diffTime var word
	gosub updateTime
	diffTime = time - executeAt
	while diffTime > 0x8000
		gosub updateTime
		diffTime = time - executeAt
	wend	
	
	for servoindex = 0 to 23
		hservo[servoindex\servoCmd(servoindex)]
	next
	return
