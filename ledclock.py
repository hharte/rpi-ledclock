#!/usr/bin/python
##############################################################################
# Copyright, 2017 Howard M. Harte, WZ2Q
#
# 24-hour Raspberry Pi LED clock
#
# Displays the time in HH:MM:SS TZ format on a pair of Adafruit Industries
# 1.2" 4-digit 7-segment displays, see:
# https://learn.adafruit.com/adafruit-led-backpack/1-2-inch-7-segment-backpack
#
# The HH:MM LED Display is configured for address 0x70 (default.)
# The SS TZ LED Display is configured for address 0x71 (short A1 pads on PCB.)
#
# This clock will blink the colons between HH:MM:SS at 0.5Hz, if the kernel
# Pulse-Per-Second (PPS) is working, otherwise the colons will remain steadily
# lit.  This is useful for determining GPS lock when using a GPS receiver
# for NTP time sync, as per the following project:
#     http://www.satsignal.eu/ntp/Raspberry-Pi-quickstart.html
#
##############################################################################
import time
import datetime
import signal
import sys

# Map alphabet characters to bitmask:
ALPHA_VALUES = {
    ' ': 0x00,
    '-': 0x40,
    '_': 0x08,
    '+': 0x46,
    'A': 0x77,
    'B': 0x7C,
    'C': 0x39,
    'D': 0x5E,
    'E': 0x79,
    'F': 0x71,
    'G': 0x3D,
    'H': 0x76,
    'I': 0x06,
    'J': 0x1E,
    'K': 0x72,
    'L': 0x38,
    'M': 0x55,
    'N': 0x54,
    'O': 0x5C,
    'P': 0x73,
    'Q': 0x67,
    'R': 0x50,
    'S': 0x6D,
    'T': 0x78,
    'U': 0x3E,
    'Y': 0x6E
}

def set_digit_alpha(self, pos, alpha):
	self.set_digit_raw(pos, ALPHA_VALUES.get(str(alpha).upper(), 0x00))

def set_string_alpha(value):
        for i, ch in enumerate(value):
            if (i < 4):
              set_digit_alpha(seg1, i % 4, ch);
            else:
              set_digit_alpha(seg2, i % 4, ch);


def signal_handler(signal, frame):
	seg1.clear()
	seg2.clear()
	set_string_alpha("Stopped-");
	seg1.write_display()
	seg2.write_display()
        sys.exit(0)

# Hook SIGINT and SIGTERM, unfortunately we can't hook SIGKILL
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

use_utc = 0
pps_seq = ""
last_seq = ""

from Adafruit_LED_Backpack import SevenSegment

seg1 = SevenSegment.SevenSegment(address=0x70) # HH:MM
seg2 = SevenSegment.SevenSegment(address=0x71) # SS TZ

# Initialize the display. Must be called once before using the display.
seg1.begin()
seg2.begin()
seg1.clear()
seg2.clear()
set_string_alpha("Init GPS");
seg1.write_display()
seg2.write_display()

# Sync with GPS
# Unfortunately, NTP doesn't seem to sync with GPSD
# until at least one GPSD client is started.
from subprocess import call
call(["gpspipe", "-r", "-n2"])

# Continually update the time on an 8 char, 7-segment display
while(True):
  if use_utc == 1:
    now = datetime.datetime.utcnow() # UTC time
  else:
    now = datetime.datetime.now() # local time

  hour = now.hour
  minute = now.minute
  second = now.second

  # Set hours and minutes on first LED display
  seg1.set_digit(0, int(hour / 10))     # Hours Tens
  seg1.set_digit(1, hour % 10)          # Ones
  seg1.set_digit(2, int(minute / 10))   # Minutes Tens
  seg1.set_digit(3, minute % 10)        # Ones

  # Set seconds and timezone on second LED display
  seg2.set_digit(0, int(second / 10))   # Seconds Tens
  seg2.set_digit(1, second % 10)        # Ones

  if use_utc == 1:
    set_digit_alpha(seg2, 2, 'U');
    set_digit_alpha(seg2, 3, 't');
  else:
    set_digit_alpha(seg2, 2, 'P');
    set_digit_alpha(seg2, 3, 'd');

  # Check to make sure PPS sequence number is incrementing.
  # If it's not, then we don't have a GPS signal lock.
  last_seq = pps_seq
  file = open("/sys/class/pps/pps0/assert", "r")
  pps = file.read(80)
  pps_seq = pps.split("#",1)[1]

  # Blink colon at 0.5Hz if PPS is active, otherwise, leave it illuminated.
  if last_seq != pps_seq:
    setcolon = (second % 2);
  else:
    setcolon = 1;
  
  seg1.set_colon(setcolon)
  seg2.set_left_colon(setcolon)

  # Write the display buffer to the hardware.  This must be called to
  # update the actual display LEDs.
  seg1.write_display()
  seg2.write_display()

  # Determine how long to sleep until the next second.  Sleeping
  # the correct amount of time will allow the LED update to be
  # visually aligned with the PPS tick.
  microsecond = datetime.datetime.utcnow().microsecond
  sleeptime = float((1000000 - microsecond) / 1000000.0)
  time.sleep(sleeptime)
