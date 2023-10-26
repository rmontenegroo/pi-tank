#!/usr/bin/env python
# coding: utf-8

import RPi.GPIO as GPIO
import time

FanPin = 2

GPIO.setmode(GPIO.BCM)
GPIO.setup(FanPin, GPIO.OUT) 
GPIO.setwarnings(False)

loops = 10

GPIO.output(FanPin, GPIO.LOW)

while loops > 0:
    # GPIO.output(FanPin, GPIO.HIGH)
    time.sleep(3)
    # GPIO.output(FanPin, GPIO.LOW)
    loops -= 1


GPIO.output(FanPin, GPIO.HIGH)

