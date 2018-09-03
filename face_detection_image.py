#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Camera inference face detection demo code.

Runs continuous face detection on the VisionBonnet and prints the number of
detected faces.

Example:
face_detection_camera.py --num_frames 10
"""
import argparse
import collections
import contextlib
import io
import logging
import math
import os
import queue
import signal
import sys
import threading
import time
import http.client, urllib.request, urllib.parse, urllib.error, base64

from aiy.vision.leds import Leds
from aiy.vision.leds import Pattern
from aiy.vision.leds import PrivacyLed
from aiy.vision.leds import RgbLeds

from aiy.vision.inference import CameraInference
from aiy.vision.models import face_detection
# from aiy.vision.annotator import Annotator
from picamera import PiCamera


JOY_COLOR = (255, 70, 0)
SAD_COLOR = (0, 0, 64)

RED = (0xFF, 0x00, 0x00)
GREEN = (0x00, 0xFF, 0x00)
YELLOW = (0xFF, 0xFF, 0x00)
BLUE = (0x00, 0x00, 0xFF)
PURPLE = (0xFF, 0x00, 0xFF)
CYAN = (0x00, 0xFF, 0xFF)
WHITE = (0xFF, 0xFF, 0xFF)


def avg_joy_score(faces):
    if faces:
        return sum(face.joy_score for face in faces) / len(faces)
    return 0.0

class Service:

    def __init__(self):
        self._requests = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while True:
            request = self._requests.get()
            if request is None:
                break
            self.process(request)
            self._requests.task_done()

    def process(self, request):
        pass

    def submit(self, request):
        self._requests.put(request)

    def close(self):
        self._requests.put(None)
        self._thread.join()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

class Player(Service):
    """Controls buzzer."""

    def __init__(self, gpio, bpm):
        super().__init__()
        self._toneplayer = TonePlayer(gpio, bpm)

    def process(self, sound):
        self._toneplayer.play(*sound)

    def play(self, sound):
        self.submit(sound)

class Animator(Service):
    """Controls RGB LEDs."""

    def __init__(self, leds):
        super().__init__()
        self._leds = leds

    def process(self, joy_score):
        if joy_score > 0:
            self._leds.update(Leds.rgb_on(blend(JOY_COLOR, SAD_COLOR, joy_score)))
        else:
            self._leds.update(Leds.rgb_off())

    def update_joy_score(self, joy_score):
        self.submit(joy_score)



def GetFaceId(image):
    headers = {
        # Request headers
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': '',
    }

    params = urllib.parse.urlencode({
        # Request parameters
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'true',
        'returnFaceAttributes': 'age,gender',
    })

    body = ""

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/detect?%s" % params, image, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()

        return data

    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror)) 


def main():
    """Face detection camera inference example."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_frames', '-n', type=int, dest='num_frames', default=None,
        help='Sets the number of frames to run for, otherwise runs forever.')
    args = parser.parse_args()

    leds = Leds()
    leds.reset()
    leds.update(Leds.privacy_on())


    with PiCamera(sensor_mode=4, resolution=(1640, 1232)) as camera:
    # with PiCamera(sensor_mode=4, resolution=(1640, 1232), framerate=30) as camera:
    # with PiCamera() as camera:
        camera.start_preview()

        with CameraInference(face_detection.model()) as inference:
            for result in inference.run():
                if len(face_detection.get_faces(result)) >= 1:
                    leds.update(Leds.rgb_on(RED))
                    stream = io.BytesIO()
                    camera.capture(stream, format='jpeg')
                    stream.seek(0)

                    print(GetFaceId(bytearray(stream)))
                    # image = Image.open(stream)
                    break
                else:
                    leds.update(Leds.rgb_on(GREEN))

        camera.stop_preview()

    leds.reset()

    # for _ in range(3):
    #     print('Privacy: On (brightness=default)')
    #     leds.update(Leds.privacy_on())
    #     time.sleep(1)
    #     print('Privacy: Off')
    #     leds.update(Leds.privacy_off())
    #     time.sleep(1)
        # player = stack.enter_context(Player(gpio=BUZZER_GPIO, bpm=10))
        # animator = stack.enter_context(leds)
        # stack.enter_context(PrivacyLed(leds))
        # camera = stack.enter_context(PiCamera(sensor_mode=4, resolution=(1640, 1232), framerate=30))

        # # Forced sensor mode, 1640x1232, full FoV. See:
        # # https://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-modes
        # # This is the resolution inference run on.
        # # with PiCamera(sensor_mode=4, resolution=(1640, 1232), framerate=30) as camera:
        # camera.start_preview()

        # # Annotator renders in software so use a smaller size and scale results
        # # for increased performace.
        # annotator = Annotator(camera, dimensions=(320, 240))
        # scale_x = 320 / 1640
        # scale_y = 240 / 1232

        # # Incoming boxes are of the form (x, y, width, height). Scale and
        # # transform to the form (x1, y1, x2, y2).
        # def transform(bounding_box):
        #     x, y, width, height = bounding_box
        #     return (scale_x * x, scale_y * y, scale_x * (x + width),
        #             scale_y * (y + height))


         # with CameraInference(face_detection.model()) as inference:
         #    for result in inference.run():
         #        if len(face_detection.get_faces(result)) >= 1:
         #            camera.capture('faces.jpg')
         #            break


        # with ImageInference(face_detection.model()) as inference:
        #     while true:
        #         stream = io.BytesIO()
        #         camera.capture(stream, format='jpeg')
        #         stream.seek(0)
        #         image = Image.open(stream)

        #         for result in inference.run(im_crop)

            # with CameraInference(face_detection.model()) as inference:
            #     for result in inference.run(args.num_frames):
            #         faces = face_detection.get_faces(result)

            #         if len(faces) >= 1:
            #             camera.capture('faces.jpg')
            #             break

                    # annotator.clear()
                    # for face in faces:
                    #     annotator.bounding_box(transform(face.bounding_box), fill=0)
                    # annotator.update()

                    # print('#%05d (%5.2f fps): num_faces=%d, avg_joy_score=%.2f' %
                    #     (inference.count, inference.rate, len(faces), avg_joy_score(faces)))

            # camera.stop_preview()


if __name__ == '__main__':
    main()
