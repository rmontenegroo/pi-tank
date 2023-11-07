import RPi.GPIO as GPIO
import socket
from os import system

#Definition of  motor pin 
IN1 = 20
IN2 = 21
IN3 = 19
IN4 = 26
ENA = 16
ENB = 13
  
UDP_IP = "0.0.0.0"
UDP_PORT = 5050
INITIAL_SPEED = 25
MIN_SPEED = 5
MAX_SPEED = 50
DIFERENTIAL_FACTOR = 0.5

#Set the GPIO port to BCM encoding mode
GPIO.setmode(GPIO.BCM)

#Ignore warning information
GPIO.setwarnings(False)


def decrease_speed():
    global currentSpeed
    global movementState

    if currentSpeed - 1 >= MIN_SPEED:
        currentSpeed -= 1

    move()
    
    print(f'Current speed: {currentSpeed}')


def increase_speed():
    global currentSpeed
    global movementState

    if currentSpeed + 1 <= MAX_SPEED:
        currentSpeed += 1

    move()

    print(f'Current speed: {currentSpeed}')


def leftSpeed():
    global directionState 
    global currentSpeed

    if directionState == -1:
        return currentSpeed
    elif directionState == 1:
        return round(currentSpeed * DIFERENTIAL_FACTOR)
        
    return currentSpeed


def rightSpeed():
    global directionState 
    global currentSpeed

    if directionState == 1:
        return currentSpeed
    elif directionState == -1:
        return round(currentSpeed * DIFERENTIAL_FACTOR)
        
    return currentSpeed


def move():
    
    global movementState
    global pwm_ENA
    global pwm_ENA

    if movementState == 1:
        # esta indo para frente
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH) 

    elif movementState == -1:
        # esta indo para tras
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)

    else:
        # esta parado
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)


    pwm_ENA.ChangeDutyCycle(rightSpeed())
    pwm_ENB.ChangeDutyCycle(leftSpeed())


def move_forward():
        global movementState

        movementState = 1

        print("Robot Move Forward")
        move()


def move_backward():
        global movementState

        movementState = -1

        print("Robot Move Backward")
        move()


def turn_left():
    global directionState

    directionState = -1

    print('Robot turn left')
    move()

def turn_right():
    global directionState

    directionState = 1

    print('Robot turn right')
    move()


def rotate_left():
        global pwm_ENB
        global pwm_ENA
        global currentSpeed

        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH) 
        pwm_ENA.ChangeDutyCycle(currentSpeed)
        pwm_ENB.ChangeDutyCycle(currentSpeed)
        print("Robot Rotate Right")
        
def rotate_right():
        global pwm_ENB
        global pwm_ENA
        global currentSpeed

        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW) 
        pwm_ENA.ChangeDutyCycle(currentSpeed)
        pwm_ENB.ChangeDutyCycle(currentSpeed)
        print("Robot Rotate Left")

def stop():
        global pwm_ENB
        global pwm_ENA
        global currentSpeed
        global movementState

        movementState = 0

        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)
        pwm_ENA.ChangeDutyCycle(currentSpeed)
        pwm_ENB.ChangeDutyCycle(currentSpeed)
        print("Robot Stop")

def init_speed():
        global currentSpeed

        currentSpeed = INITIAL_SPEED

def init_motors():
        global pwm_ENA
        global pwm_ENB
        global movementState
        global directionState

        directionState = 0
        movementState = 0

        GPIO.setup(ENA,GPIO.OUT,initial=GPIO.HIGH)
        GPIO.setup(IN1,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(IN2,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(ENB,GPIO.OUT,initial=GPIO.HIGH)
        GPIO.setup(IN3,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(IN4,GPIO.OUT,initial=GPIO.LOW)
            
        #Set the PWM pin and frequency is 2000hz
        pwm_ENA = GPIO.PWM(ENA, 2000)
        pwm_ENB = GPIO.PWM(ENB, 2000)
        pwm_ENA.start(0)
        pwm_ENB.start(0)


if __name__ == "__main__":
        
        global pwm_ENA
        global pwm_ENB
        global currentSpeed 
        global movementState
        global directionState
        
        init_speed()

        init_motors()

        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
        sock.bind((UDP_IP, UDP_PORT))

        while True:
            raw, addr = sock.recvfrom(1024)

            msg = raw.decode().lower()

            if msg == 'forward_pressed':
                move_forward()
          
            elif msg == "stop_pressed":
                stop()

            elif msg == "backward_pressed":
                move_backward()
                
            elif msg == "right_pressed":
                turn_right()

            elif msg == "left_pressed":
                turn_left()            

            elif msg == "rotate_right_pressed":
                rotate_right()

            elif msg == "rotate_left_pressed":
                rotate_left()
            
            elif msg == "increase_speed":
                increase_speed()

            elif msg == "decrease_speed":
                decrease_speed()

            elif msg.startswith("testing:"):
                print(msg, addr)
                sock.sendto(raw, addr)
                
            elif msg == "shutdown":
                print("Shutdown")
                system("sudo shutdown -h now")                

            else:
                print(msg, addr)

sock.close()
