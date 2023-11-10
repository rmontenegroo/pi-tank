import time
import cv2
from os import environ
from flask import Flask, Response

PORT = int(environ.get('STREAMER_PORT', '5555'))

streamer = None

app = Flask(__name__)

@app.route("/")
def index():
    return """
    <body>
        <img src="/mjpeg" />
    </body>
    """

@app.route("/mjpeg")
def mjpeg():
    global streamer
    return Response(streamer.generate_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


class Streamer(object):

    def __init__(self, source=0, width=640, height=480, sleepTime=0.1):

        self.cam = cv2.VideoCapture(source)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self.sleepTime = sleepTime


    def generate_frame(self):

        while True:

            time.sleep(self.sleepTime)
            _, img = self.cam.read()
            _, frame = cv2.imencode('.jpg', img)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame.tobytes() + b'\r\n')


if __name__ == "__main__":

    streamer = Streamer()
    app.run(host='0.0.0.0', port=PORT, threaded=True)
