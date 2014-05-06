; first experiment with Assembler
tmp var Byte
	gosub init
main
	gosub step
	goto main

init
	SMR = 0x00	; 8bits, no parity, 1stop bit
	SCR3 = 0x00 ; TODO interrupts
	BRR = 15; 38400 at 20MHz
	; wait 1bit - is 0.41ms enough?
	tmp = TCB1
	while tmp = TCB1
	wend
	tmp = TCB1
	while tmp = TCB1
	wend
	SMR = 0x30; TE, RE - Transmit/Receive Enable
	pmr1.bit1 = 1
	return

badstep
	;SEROUT s_out, i38400, ["A"]
;	SEROUT s_out, i38400, [HEX SSR," ", HEX BRR, 13]	
	tmp = SSR
	if tmp & 0x80 <> 0 then  ; TDRE	
;		SEROUT s_out, i38400, ["B"]
		TDR = 67; '0'
		tmp = SSR
		SEROUT s_out, i38400, [HEX tmp, " "]
	endif
;	SEROUT s_out, i38400, [HEX tmp, hex (tmp&0x80)]
	return

BEGINASMSUB
asminit
asm{
	push.w r1
	mov #15,r1l
	mov.b r1l,@BRR ; 38400 at 20MHz
	mov.b #0x30,r1l
	mov.b r1l,@SMR
	mov.b #0x02,r1l
	mov.b r1l,@PMR1
	pop.w r1
	rts
}

step
asm{								;20
	push.l	er0						;10
	btst #7,@SSR:16
	beq _skip:16
	mov.b #0x41,r0l
	mov.b r0l,@TDR:16
_skip:	
	pop.l	er0
	rts
}
ENDASMSUB
