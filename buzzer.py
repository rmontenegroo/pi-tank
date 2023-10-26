#!/usr/bin/env python
# coding: utf-8

# In[1]:


import RPi.GPIO as GPIO
import time

BuzzerPin = 8

GPIO.setmode(GPIO.BCM)
GPIO.setup(BuzzerPin, GPIO.OUT) 
GPIO.setwarnings(False)

bipes = 10

while bipes > 0:
    GPIO.output(BuzzerPin, GPIO.HIGH)
    time.sleep(0.4)
    GPIO.output(BuzzerPin, GPIO.LOW)
    time.sleep(0.1)
    bipes -= 1


# In[2]:


GPIO.output(BuzzerPin, GPIO.HIGH)

