import RPi.GPIO as GPIO
import socket
from os import system
from threading import Thread
from time import sleep

class PiTank(Thread):
    
    IN1 = 20
    IN2 = 21
    IN3 = 19
    IN4 = 26
    ENA = 16
    ENB = 13

    buzzerPin = 8

    FORWARD = 1
    STOPPED = 0
    BACKWARD = -1
    ROTATERIGHT = 2
    ROTATELEFT = -2

    RIGHT = 1
    CENTER = 0
    LEFT = -1

    def __init__(self, UDP_IP = "0.0.0.0", UDP_PORT = 5050, sleepTime = 0.1, initialSpeed = 25, minSpeed = 5, maxSpeed = 50, diferentialFactor = 0.5, args = ..., kwargs = {}):
        super().__init__(group=None, target=None, name=None, args=args, kwargs=kwargs, daemon=False)

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

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.socket.settimeout(2)
        self.socket.bind((UDP_IP, UDP_PORT))

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

        self.beeping = False
        GPIO.output(self.buzzerPin, GPIO.HIGH)

        self.beepingThread = Thread(target = self.beep, daemon = True)
        self.beepingThread.start()

        print('Running...')


    def beep(self):

        while self.running:

            if self.beeping:
                GPIO.output(self.buzzerPin, GPIO.HIGH)
                sleep(self.sleepTime)
                GPIO.output(self.buzzerPin, GPIO.LOW)
                sleep(self.sleepTime)

                print('Beep!')
            
            else:
                GPIO.output(self.buzzerPin, GPIO.HIGH)
                sleep(self.sleepTime)

        GPIO.output(self.buzzerPin, GPIO.HIGH)


    def move(self):

        while self.running:
            
            if self.movementState == PiTank.FORWARD:
                # esta indo para frente
                GPIO.output(self.IN1, GPIO.LOW)
                GPIO.output(self.IN2, GPIO.HIGH)
                GPIO.output(self.IN3, GPIO.LOW)
                GPIO.output(self.IN4, GPIO.HIGH)
                print('Forward')

            elif self.movementState == PiTank.BACKWARD:
                # esta indo para tras
                GPIO.output(self.IN1, GPIO.HIGH)
                GPIO.output(self.IN2, GPIO.LOW)
                GPIO.output(self.IN3, GPIO.HIGH)
                GPIO.output(self.IN4, GPIO.LOW)
                print('Backward')

            elif self.movementState == PiTank.STOPPED:
                # esta parado
                GPIO.output(self.IN1, GPIO.LOW)
                GPIO.output(self.IN2, GPIO.LOW)
                GPIO.output(self.IN3, GPIO.LOW)
                GPIO.output(self.IN4, GPIO.LOW)
                print('Stopped')
        
            elif self.movementState == PiTank.ROTATERIGHT:
                GPIO.output(self.IN1, GPIO.LOW)
                GPIO.output(self.IN2, GPIO.HIGH)
                GPIO.output(self.IN3, GPIO.HIGH)
                GPIO.output(self.IN4, GPIO.LOW)
                print('Rotate right')

            elif self.movementState == PiTank.ROTATELEFT:
                GPIO.output(self.IN1, GPIO.HIGH)
                GPIO.output(self.IN2, GPIO.LOW)
                GPIO.output(self.IN3, GPIO.LOW)
                GPIO.output(self.IN4, GPIO.HIGH) 
                print('Rotate left')

            print(f"Speed: {self.leftSpeed()} {self.rightSpeed()}")

            self.pwm_ENA.ChangeDutyCycle(self.rightSpeed())
            self.pwm_ENB.ChangeDutyCycle(self.leftSpeed())

            sleep(self.sleepTime)


    def increaseSpeed(self):
        if self.currentSpeed + 1 <= self.maxSpeed:
            self.currentSpeed += 1


    def decreaseSpeed(self):
        if self.currentSpeed - 1 >= self.minSpeed:
            self.currentSpeed -= 1


    def rightSpeed(self):
        if self.directionState == 1:
            return self.currentSpeed * self.diferentialFactor
        
        return self.currentSpeed


    def leftSpeed(self):
        if self.directionState == -1:
            return self.currentSpeed * self.diferentialFactor
    
        return self.currentSpeed


    def turnRight(self):
        if self.directionState + 1 <= PiTank.RIGHT:
            self.directionState += 1


    def turnLeft(self):
        if self.directionState - 1 >= PiTank.LEFT:
            self.directionState -= 1


    def run(self) -> None:

        while self.running:

            try:
                raw, addr = self.socket.recvfrom(1024)
            except socket.timeout:
                continue

            msg = raw.decode().lower()

            if msg == 'forward_pressed':
                self.movementState = PiTank.FORWARD
                self.directionState = PiTank.CENTER
        
            elif msg == "stop_pressed":
                self.movementState = PiTank.STOPPED
                self.directionState = PiTank.CENTER

            elif msg == "backward_pressed":
                self.movementState = PiTank.BACKWARD
                self.directionState = PiTank.CENTER

            elif msg == "increase_speed":
                self.increaseSpeed()

            elif msg == "decrease_speed":
                self.decreaseSpeed()
                
            elif msg == "right_pressed":
                self.turnRight()

            elif msg == "left_pressed":
                self.turnLeft()

            elif msg == "rotate_right_pressed":
                self.movementState = PiTank.ROTATERIGHT
                self.directionState = PiTank.CENTER

            elif msg == "rotate_left_pressed":
                 self.movementState = PiTank.ROTATELEFT
                 self.directionState = PiTank.CENTER
            
            elif msg.startswith("testing:"):
                print(msg, addr)
                self.socket.sendto(raw, addr)
                
            elif msg == "shutdown":
                system("sudo shutdown -h now")                

            elif msg == 'buzzer_pressed':
                self.beeping = True

            elif msg == 'buzzer_released':
                self.beeping = False

            else:
                print(msg, addr)

        self.socket.close()
        print('Shutdown')


if __name__ == "__main__":
                
    mainThread = PiTank()

    try:
        mainThread.start()
        while mainThread.is_alive():
            sleep(0.1)
            
    except KeyboardInterrupt:
        mainThread.running = False
