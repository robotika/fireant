# FireAnt Guide for Dummies
written by 
Martin Dlouhy

----

When I received the package with FireAnt Kit I did not find any "Getting
started" sheet of paper, which could direct my first steps. I was going to post
many stupid questions, but in mean time I found some answers here on the forum,
some answered Nathan by email, and some were answered by painful experience  ;)
... so feel free to correct this "guide".

## Battery
FireAnt Kit is shipped without battery. You will need to buy one, where voltage
corresponds to 7.4V for servos. This means 2 cells for LiPo. Recommended is
http://www.hobbyking.com/hobbyking/store/__9459__Turnigy_2200mAh_2S_30C_Lipo_Pack.html
You do not need extra board for checking battery voltage - it can be measured
on analog pin A2. Default SW has limit set to 6.2V.

## Default Firmware

The DaVinci board could be preprogrammed with firmware for control via cable of
PlayStation2 (PS2). You will hear beep after power up. No need to worry about
programming at the first stage. Calibration procedure and meaning of various
controls is listed at the end of construction manual. Note, that PS2 is not
part of the FireAnt Kit.

## Programming

If you decide you want to program the board, be prepared for troubles with
drivers on Windows OS. The USB chip is FTDI, but it has modified EEPROM to
VID_0403&amp;PID_A559, so original drivers won't work for you. You have to edit
INF files (both ftdiport.inf and ftdibus.inf) replace PID number and remove
all other alternatives. Then it may work.

Once is your COM port working you may use Arduino programming environment. Use
C: drive only - mapped drivers do not work. The board "DaVinci" has nothing to
do with "Leonardo" - you must select "Duemilanove" (on some other kits board "Uno"
is used). Correct pins are listed in Serve Shield datasheet: LEDs A0,A1,
buttons 2,4, tone generator 3, voltage reference A2.

If you want to restore original firmware, the simplest way is to uzip
(http://downloads.orionrobotics.com/downloads/code/arduino.zip Arduino
Libraries) directly into **arduino-1.0.x\libraries** folder so that you
do not have to import them one-by-one.

## Power

If you want to power FireAnt from single battery, make sure that jumpers JP6
are parallel with buttons. Some boards are shipped with jumpers perpendicular
to buttons. Servo Shield doc does not describe JP6, but you may find a note in
(http://downloads.orionrobotics.com/downloads/datasheets/Nomad_Shield_R0407.pdf Nomad_Shield_R0407.pdf)

## Servo Jumpers

Make sure that you have jumpers on Servo Headers set to VS. Otherwise the
servos will be powered by the Arduino on board regulator. You will see robot
constantly resetting ...

## Calibration

Calibration is time consuming process. Once you flash
the default FireAnt firmware make sure that first you calibrate CENTER
and then RANGE!!! The min/max angles are linked to offset (they are not "physical min/max" but rather "logical"), so it is critical to first calibrate center and then range!




Dissussion about this topic is at Orion Robotics forum:
http://forums.orionrobotics.com/walking-robots-f6/fireant-guide-for-dummies-t76.html

