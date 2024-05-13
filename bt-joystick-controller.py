import evdev
import sys
# import json
import time
import multiprocessing
# import math

import logging
logging.getLogger().setLevel('DEBUG')

import RPi.GPIO as GPIO

from os import system, environ
from threading import Thread
from time import sleep


def _shutdown():

    for i in range(3):
        logging.info('.')
        time.sleep(1)

    logging.info('Shutting down...')
    system("sudo shutdown -h now")                

    

class PiTank(Thread):
    
    IN1 = 20
    IN2 = 21
    IN3 = 19
    IN4 = 26
    ENA = 16
    ENB = 13

    buzzerPin = 8

    lightsPin = 22, 24, 27

    FORWARD = 1
    STOPPED = 0
    BACKWARD = -1
    ROTATERIGHT = 2
    ROTATELEFT = -2

    RIGHT = 1
    CENTER = 0
    LEFT = -1

    def __init__(self, input_device, sleepTime = 0.1, initialSpeed = 25, minSpeed = 5, maxSpeed = 50, diferentialFactor = 0.2, args = ..., kwargs = {}):
        super().__init__(group=None, target=None, name=None, args=args, kwargs=kwargs, daemon=False)

        self.idev = input_device
        self.__shutdownProcess = None

        self.sleepTime = sleepTime
        self.running = True

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # motores
        GPIO.setup(self.ENA,GPIO.OUT,initial=GPIO.HIGH)
        GPIO.setup(self.IN1,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(self.IN2,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(self.ENB,GPIO.OUT,initial=GPIO.HIGH)
        GPIO.setup(self.IN3,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(self.IN4,GPIO.OUT,initial=GPIO.LOW)
           
        self.pwm_ENA = GPIO.PWM(self.ENA, 2000)
        self.pwm_ENB = GPIO.PWM(self.ENB, 2000)
        self.pwm_ENA.start(0)
        self.pwm_ENB.start(0)

        self.currentSpeed = initialSpeed
        self.diferentialFactor = diferentialFactor
        self.minSpeed = minSpeed
        self.maxSpeed = maxSpeed
      
        self.directionState = PiTank.CENTER
        self.movementState = PiTank.STOPPED

        self.movementThread = Thread(target = self.move, daemon=True)
        self.movementThread.start()

        # buzzer
        GPIO.setup(self.buzzerPin, GPIO.OUT)
        GPIO.output(self.buzzerPin, GPIO.HIGH)
        # self.buzzing = False
        self.__beep(3)

        # self.buzzingThread = Thread(target = self.buzz, daemon = True)
        # self.buzzingThread.start()

        # lights
        GPIO.setup(self.lightsPin[0], GPIO.OUT)
        GPIO.setup(self.lightsPin[1], GPIO.OUT)
        GPIO.setup(self.lightsPin[2], GPIO.OUT)
        GPIO.output(self.lightsPin[0], GPIO.HIGH)
        GPIO.output(self.lightsPin[1], GPIO.HIGH)
        GPIO.output(self.lightsPin[2], GPIO.HIGH)

        logging.info('Running...')


    def startShutdownCountdown(self):
        
        if self.__shutdownProcess is None:
            self.__shutdownProcess = multiprocessing.Process(target=_shutdown)

        self.__shutdownProcess.start()


    def stopShutdownCountdown(self):

        if self.__shutdownProcess is not None:
            self.__shutdownProcess.terminate()
            self.__shutdownProcess = multiprocessing.Process(target=_shutdown)


    def __beep(self, beeps=2, interval=0.2):

        while beeps > 0:

            GPIO.output(self.buzzerPin, GPIO.LOW)
            sleep(interval)
            GPIO.output(self.buzzerPin, GPIO.HIGH)
            sleep(interval)

            beeps -= 1

            
        GPIO.output(self.buzzerPin, GPIO.HIGH)


    # def buzz(self):

    #     while self.running:

    #         if self.buzzing:
    #             GPIO.output(self.buzzerPin, GPIO.LOW)
    #             logging.info('Buzzing!')
            
    #         else:
    #             GPIO.output(self.buzzerPin, GPIO.HIGH)
            
    #         sleep(self.sleepTime)

    #     GPIO.output(self.buzzerPin, GPIO.HIGH)


    def move(self):

        while self.running:
            
            if self.movementState == PiTank.FORWARD:
                # esta indo para frente
                GPIO.output(self.IN1, GPIO.LOW)
                GPIO.output(self.IN2, GPIO.HIGH)
                GPIO.output(self.IN3, GPIO.LOW)
                GPIO.output(self.IN4, GPIO.HIGH)

            elif self.movementState == PiTank.BACKWARD:
                # esta indo para tras
                GPIO.output(self.IN1, GPIO.HIGH)
                GPIO.output(self.IN2, GPIO.LOW)
                GPIO.output(self.IN3, GPIO.HIGH)
                GPIO.output(self.IN4, GPIO.LOW)

            elif self.movementState == PiTank.STOPPED:
                GPIO.output(self.IN1, GPIO.LOW)
                GPIO.output(self.IN2, GPIO.LOW)
                GPIO.output(self.IN3, GPIO.LOW)
                GPIO.output(self.IN4, GPIO.LOW)
        
            elif self.movementState == PiTank.ROTATERIGHT:
                GPIO.output(self.IN1, GPIO.LOW)
                GPIO.output(self.IN2, GPIO.HIGH)
                GPIO.output(self.IN3, GPIO.HIGH)
                GPIO.output(self.IN4, GPIO.LOW)

            elif self.movementState == PiTank.ROTATELEFT:
                GPIO.output(self.IN1, GPIO.HIGH)
                GPIO.output(self.IN2, GPIO.LOW)
                GPIO.output(self.IN3, GPIO.LOW)
                GPIO.output(self.IN4, GPIO.HIGH) 

            self.pwm_ENA.ChangeDutyCycle(self.leftSpeed())
            self.pwm_ENB.ChangeDutyCycle(self.rightSpeed())

            sleep(self.sleepTime)


    def setSpeed(self, val):
        _speed = (abs(val)/32767) * (self.maxSpeed - self.minSpeed) + self.minSpeed
        if _speed < self.maxSpeed and _speed > self.minSpeed:
            self.currentSpeed = _speed


    def rightSpeed(self):
        if self.directionState == PiTank.RIGHT:
            return self.currentSpeed * self.diferentialFactor
        return self.currentSpeed


    def leftSpeed(self):
        if self.directionState == PiTank.LEFT:
            return self.currentSpeed * self.diferentialFactor
        return self.currentSpeed
    

    def run(self) -> None:

        while self.running:

            for ev in self.idev.read_loop():

                msg, value = (ev.type, ev.code), ev.value
            
                # forward or backward or stop
                if msg == (3, 1):

                    value -= 32768

                    # forward
                    if value < 0:

                        self.movementState = PiTank.FORWARD
                        self.setSpeed(value)
                        # self.directionState = PiTank.CENTER

                    # backward
                    elif value > 0:
                        self.movementState = PiTank.BACKWARD
                        self.setSpeed(value)
                        # self.directionState = PiTank.CENTER

                    # stop
                    else:
                            self.movementState = PiTank.STOPPED
                            # self.directionState = PiTank.CENTER                            

                # rotate right/left
                elif msg == (3, 0):

                    value -= 32768

                    # right
                    if value > 0:
                        self.movementState = PiTank.ROTATERIGHT
                        
                    # left
                    elif value < 0:
                        self.movementState = PiTank.ROTATELEFT
                    
                    # center
                    else:
                        self.directionState = PiTank.CENTER

                # soft turn left/right
                elif msg == (3,2):
                    
                    if value == 0:
                        self.directionState = PiTank.CENTER
                    else:
                        self.directionState = PiTank.LEFT

                elif msg == (3,5):

                    if value == 0:
                        self.directionState = PiTank.CENTER
                    else:
                        self.directionState = PiTank.RIGHT        

                elif msg == (1,311):

                    if value == 1:
                        self.startShutdownCountdown()

                    else:
                        self.stopShutdownCountdown()

                # event not mapped
                else:
                    logging.debug(f'msg: {msg} value: {value}')
            
            logging.info('Main thread shutting down...')


if __name__ == "__main__":

    idev = None

    try:
        idev = evdev.InputDevice(sys.argv[1])
    except:
        for _idev in [evdev.InputDevice(i) for i in evdev.list_devices()]:
            # if _idev.name == 'Microsoft X-Box 360 pad':
            if _idev.name == 'Wireless Controller':
                idev = _idev
                break

    if not idev:
        sys.exit('No controller device found!')

    mainThread = PiTank(input_device=idev)

    try:
        mainThread.start()
        while mainThread.is_alive():
            sleep(0.1)
            
    except KeyboardInterrupt:
        mainThread.running = False
