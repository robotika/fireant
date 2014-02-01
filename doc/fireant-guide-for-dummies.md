FireAnt Guide for Dummies
written by 
Martin Dlouhy

When I received the package with FireAnt Kit I did not find any "Getting
started" sheet of paper, which could direct my first steps. I was going to post
many stupid questions, but in mean time I found some answers here on the forum,
some answered Nathan by email, and some were answered by painful experience  ;)
... so feel free to correct this "guide".

[b]Battery[/b]

FireAnt Kit is shipped without battery. You will need to buy one, where voltage
corresponds to 7.4V for servos. This means 2 cells for LiPo. Recommended is
[url]http://www.hobbyking.com/hobbyking/store/__9459__Turnigy_2200mAh_2S_30C_Lipo_Pack.html[/url]
You do not need extra board for checking battery voltage - it can be measured
on analog pin A2. Default SW has limit set to 6.2V.

[b]Default Firmware[/b]

The DaVinci board is preprogrammed with firmware for control via cable of
PlayStation2 (PS2). You will hear beep after power up. No need to worry about
programming at the first stage. Calibration procedure and meaning of various
controls is listed at the end of construction manual. Note, that PS2 is not
part of the FireAnt Kit.

[b]Programming[/b]

If you decide you want to program the board, be prepared for troubles with
drivers on Windows OS. The USB chip is FTDI, but it has modified EEPROM to
VID_0403&amp;PID_A559, so original drivers won't work for you. You have to edit
INF files (both ftdiport.inf and ftdibus.inf) replace PID number and remove
all other alternatives. Then it may work.

Once is your COM port working you may use Arduino programming environment. Use
C: drive only - mapped drivers do not work. The board "DaVinci" has nothing to
do with "Leonardo" - you must select "Duemilanove" (on some older boards "Uno"
was used). Correct pins are listed in Serve Shield datasheet: LEDs A0,A1,
buttons 2,4, tone generator 3, voltage reference A2.

(edit) If you want to restore original firmware, the simplest way is to uzip
[url=http://downloads.orionrobotics.com/downloads/code/arduino.zip]Arduino
Libraries[/url] directly into [b]arduino-1.0.x\libraries[/b] folder so that you
do not have to import them one-by-one.

[b]Power[/b] (edit)

If you want to power FireAnt from single battery, make sure that jumpers JP6
are parallel with buttons. Some boards are shipped with jumpers perpendicular
to buttons. Servo Shield doc does not describe JP6, but you may find a note in
[url=http://downloads.orionrobotics.com/downloads/datasheets/Nomad_Shield_R0407.pdf]Nomad_Shield_R0407.pdf[/url]


[b]Calibration[/b]

Calibration is time consuming process. Be prepared for troubles. Once you flash
the default FireAnt firmware make sure that first you calibrate [u]RANGE[/u]
and then [u]OFFSET[/u]!!! If you do it in wrong order you will never be able to
fix it ... you have to write fist small program which will reset the registers.
Some future version of firmware may fix this problem.

... correct me if I am wrong. What a waste of the time ;). The explanation is simple once you know the Servo Shield code. Be aware that there are two types of angles/values:
1) rawValues
2) modifiedAngles (with offset and direction)
If you use queryFKAngle() you get modifiedAngles. In the calibration routine servo min & max is computed based on results from queryFBAngle(), which is already modified by offset. And once you save your wrong offsets there is no way out (reset registry would do). Quick workaround would be setting the setAOffset() to zero even before the range calibration (with saving original values). The same trouble is probably also for direction, which should be set to positive, otherwise you measure wrong limits.

Note, that this is quite mood-killing-feature ;) ... you can repeat the calibration how many times you want. If it was once bad, it will be always bad!

Edit 2014-1-31:
I was wrong - the min/max angles are linked to offset (they are not "physical min/max" but rather "logical"), so it is critical to first calibrate center and then range!

[b]Jumper Pins on Servo Shield[/b]

Make sure that you have jumpers on Servo Headers set to VS. Otherwise the
servos will be powered by the Arduino on board regulator. You will see robot
constantly resetting ...




http://forums.orionrobotics.com/walking-robots-f6/fireant-guide-for-dummies-t76.html

