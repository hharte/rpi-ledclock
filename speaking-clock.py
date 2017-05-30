#!/usr/bin/python
##############################################################################
# Copyright, 2017 Howard M. Harte, WZ2Q
#
# Python Speaking clock based on sound files from the TIM-2015 project:
#   http://www.samhallas.co.uk/repository/tim_2015.htm
#
#
##############################################################################
import time
import datetime
import signal
import sys
from subprocess import call
from shutil import copyfile
import os.path

def signal_handler(signal, frame):
        sys.exit(0)

# for Cygwin, write the .wav file to /dev/dsp to play.
def play_wav(filename):
	copyfile(filename, "/dev/dsp")
	
# Hook SIGINT and SIGTERM, unfortunately we can't hook SIGKILL
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

debug = 1
use_utc = 0
use_12hr_format = 0
iterations = 0;

# Select one voice to use for the speaking clock.
#voice = "01_Pat_Simmons"
#voice = "02_Gordon_Gow"
#voice = "03_Gordon_Gow"
#voice = "04_John_Doyle"
#voice = "05_Sam_Hallas"
voice = "06_Pat_Fleet"

# Perform speaking clock function forever...
while(True):
  # Determine how long to sleep until the next 8-second offset
  now = datetime.datetime.utcnow() # UTC time

  second = now.second + (now.microsecond / 1000000.0)
  second = second % 10
  if (iterations == 0):
    sleeptime = 11.0 - second
  else:
    sleeptime = 8.0 - second
    if (sleeptime < 0):
      sleeptime += 10

  if (debug == 1):
    print "Now: " + str(now) + ", Sleeping for " + str(sleeptime)

  time.sleep(sleeptime)

  # On all but the first iteration, play beeps or tone.
  if (iterations >= 1):
    play_wav("Sounds/" + str(voice) + "/080.wav")

  iterations += 1;

  if use_utc == 1:
    now = datetime.datetime.utcnow() # UTC time
  else:
    now = datetime.datetime.now() # local time

  now += datetime.timedelta(seconds=9)
  hour = now.hour
  minute = now.minute
  second = now.second

  if (debug == 1):
    print "Announcement: %02d" % hour + ":%02d" %minute + ":%02d" % second

  # if there is a greeting, use it.
  if (os.path.isfile("Sounds/" + str(voice) + "/084.wav")):
    # determine morning, afternoon, evening
    if (hour >= 17):
      greetingfile = "Sounds/" + str(voice) + "/084.wav" # Good evening
    elif (hour >= 12):
      greetingfile = "Sounds/" + str(voice) + "/083.wav" # Good afternoon
    else:
      greetingfile = "Sounds/" + str(voice) + "/082.wav" # Good morning

    play_wav(greetingfile)

  # if a 24-hour speaking clock is selected, make sure that the 24-hour files are available.
  if ((use_12hr_format == 1) or (not os.path.isfile("Sounds/" + str(voice) + "/013.wav"))):
    # Convert 24-hour format to 12-hour format
    if (hour == 0):
      hour = 12
    elif (hour > 12):
      hour -= 12;

  # At the tone, the time will be n (hour)
  hourfile = "Sounds/" + str(voice) + "/0%02d" % hour + ".wav"

  # Minutes
  minfile = "Sounds/" + str(voice) + "/1%02d" % minute + ".wav"

  # Seconds
  secfile = "Sounds/" + str(voice) + "/2%02d" % second + ".wav"

  if (debug == 1):
    print hourfile
    print minfile
    print secfile

  play_wav(hourfile)
  play_wav(minfile)
  play_wav(secfile)



