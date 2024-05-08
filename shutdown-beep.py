#!/bin/python3 

import time

import RPi.GPIO as GPIO


buzzerPin = 8

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
        
# buzzer
GPIO.setup(buzzerPin, GPIO.OUT)
GPIO.output(buzzerPin, GPIO.HIGH)

beeps = 3
interval = 0.2

while beeps > 0:

    GPIO.output(buzzerPin, GPIO.LOW)
    time.sleep(interval)
    GPIO.output(buzzerPin, GPIO.HIGH)
    time.sleep(interval)

    beeps -= 1

GPIO.output(buzzerPin, GPIO.HIGH)


