; first experiment with Assembler

BEGINASMSUB
asm{
	bsr _init
_main:
	bsr _step
	bra _main

_init:
	push.w r1
	sub.b r1l,r1l ; clear R1L
	mov.b r1l,@SCR3
	mov #15,r1l
	mov.b r1l,@BRR ; 38400 at 20MHz
	mov.w #0x115,r1
_initWait:
	dec.w #1,r1
	bne _initWait	
	mov.b #0x30,r1l
	mov.b r1l,@SCR3
	bset.b #1,@PMR1
	pop.w r1
	rts

_step:
	push.l	er0						;10
	mov.b #0x41,r0l
	bsr _sendByte
	pop.l	er0
	rts

_sendByte:
	btst.b #7,@SSR
	beq _sendByte
	mov.b r0l,@TDR
	bclr.b #7,@SSR
	rts
}
ENDASMSUB
