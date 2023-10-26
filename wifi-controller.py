import RPi.GPIO as GPIO
import socket
import csv

"""
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(33,GPIO.OUT)
GPIO.setup(11,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)
GPIO.setup(29,GPIO.OUT)
GPIO.setup(31,GPIO.OUT)

GPIO.output(29,True)
GPIO.output(31,True)
"""

UDP_IP = "0.0.0.0"
UDP_PORT = 5050

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
sock.bind((UDP_IP, UDP_PORT))

while True:
    raw, addr = sock.recvfrom(1024)

    msg = raw.decode().lower()

    if msg == "forward_pressed":
        """
        GPIO.output(33,True)
        GPIO.output(11,False)
        GPIO.output(13,True)
        GPIO.output(15,False)
        """
        print("Robot Move Forward")
  
  
    elif msg == "stop_pressed":
        """
        GPIO.output(33,False)
        GPIO.output(11,False)
        GPIO.output(13,False)
        GPIO.output(15,False)
        """
        print("Robot Stop")

    elif msg.endswith("_released"):
        """
        GPIO.output(33,False)
        GPIO.output(11,False)
        GPIO.output(13,False)
        GPIO.output(15,False)
        """
        print("Robot Stop")
    

    elif msg == "backward_pressed":
        """
        GPIO.output(33,False)
        GPIO.output(11,True)
        GPIO.output(13,False)
        GPIO.output(15,True)
        """
        print("Robot Move Backward")

    elif msg == "left_pressed":
        """
        GPIO.output(33,False)
        GPIO.output(11,True)
        GPIO.output(13,True)
        GPIO.output(15,False)
        """
        print("Robot Move Left")

    elif msg == "right_pressed":
        """
        GPIO.output(33,True)
        GPIO.output(11,False)
        GPIO.output(13,False)
        GPIO.output(15,True)
        """
        print("Robot Move Right")

    elif msg == "rotate_right_pressed":
        """
        GPIO.output(33,True)
        GPIO.output(11,False)
        GPIO.output(13,False)
        GPIO.output(15,True)
        """
        print("Robot Rotate Right")

    elif msg == "rotate_left_pressed":
        """
        GPIO.output(33,True)
        GPIO.output(11,False)
        GPIO.output(13,False)
        GPIO.output(15,True)
        """
        print("Robot Rotate Left")

    elif msg.startswith("testing:"):
        print(msg, addr)
        sock.sendto(raw, addr)

    else:
        print(msg, addr)
        """
        GPIO.output(33,False)
        GPIO.output(11,False)
        GPIO.output(13,False)
        GPIO.output(15,False)
        """
        # print("STOP")

sock.close()
