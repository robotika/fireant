; Experimental code for direct servo control over serial port

servoindex var byte
tmp var word

sethserial1 H38400  ;Sets UART 1 to 38400 Baud

hserout s_out,["BASIC ver0", 13]

servoindex = 21

main
	tmp = hservofbpos( servoindex )
	hserout s_out,[tmp]
	hserin s_in,[tmp]
	hservo [servoindex\tmp]
	goto main
