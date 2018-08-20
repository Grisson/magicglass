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

from aiy.vision.inference import CameraInference
from aiy.vision.models import face_detection
#from aiy.vision.annotator import Annotator
from picamera import PiCamera
import http.client, urllib.request, urllib.parse, urllib.error, base64
import io
import time
import threading

done = False
hasCustomer = False
lock = threading.Lock()
pool = []


class ImageProcessor(threading.Thread):
    def __init__(self):
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.start()

    def run(self):
        # This method runs in a separate thread
        global done
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    self.stream.seek(0)

                    print("Start to identify face")
                    # Read the image and do some processing on it
                    #Image.open(self.stream)
                    #...
                    #...
                    # Set done to True if you want the script to terminate
                    # at some point
                    #done=True
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    # Return ourselves to the pool
                    with lock:
                        pool.append(self)


    def detect_face():
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

        #load image
        body = "" 
        with open("C:\\Users\\Grisson\\Pictures\\Camera Roll\\test.JPG", "rb") as f:
            body = f.read()


        try:
            conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
            conn.request("POST", "/face/v1.0/detect?%s" % params, body, headers)
            response = conn.getresponse()
            data = response.read()
            print(data)
            conn.close()
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))

    def identify_face():
        headers = {
            # Request headers
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': '',
        }

        params = urllib.parse.urlencode({})

        body = '{"personGroupId":"everyone","faceIds":["97819840-8000-4fdf-a0a4-663e8e6832d3"],"maxNumOfCandidatesReturned":1,"confidenceThreshold":0.5}'

        try:
            conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
            conn.request("POST", "/face/v1.0/identify?%s" % params, body, headers)
            response = conn.getresponse()
            data = response.read()
            print(data)
            conn.close()
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))
            pass


def avg_joy_score(faces):
    if faces:
        return sum(face.joy_score for face in faces) / len(faces)
    return 0.0


def streams():
    while not done and hasCustomer:
        print("Pop processor") 
        with lock:
            if pool:
                processor = pool.pop()
            else:
                processor = None
        if processor:
            yield processor.stream
            processor.event.set()
        else:
            # When the pool is starved, wait a while for it to refill
            # time.sleep(0.1)
            # ignore the frame
            pass


def main():
    """Face detection camera inference example."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_frames', '-n', type=int, dest='num_frames', default=None,
        help='Sets the number of frames to run for, otherwise runs forever.')
    args = parser.parse_args()


    pool = [ImageProcessor() for i in range(4)]

    # Forced sensor mode, 1640x1232, full FoV. See:
    # https://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-modes
    # This is the resolution inference run on.
    with PiCamera(sensor_mode=4, resolution=(1640, 1232), framerate=30) as camera:
        camera.start_preview()
        time.sleep(2)
        camera.capture_sequence(streams(), use_video_port=True)

        # Annotator renders in software so use a smaller size and scale results
        # for increased performace.
        # annotator = Annotator(camera, dimensions=(320, 240))
        scale_x = 320 / 1640
        scale_y = 240 / 1232

        # Incoming boxes are of the form (x, y, width, height). Scale and
        # transform to the form (x1, y1, x2, y2).
        def transform(bounding_box):
            x, y, width, height = bounding_box
            return (scale_x * x, scale_y * y, scale_x * (x + width),
                    scale_y * (y + height))

        with CameraInference(face_detection.model()) as inference:
            for result in inference.run(args.num_frames):
                faces = face_detection.get_faces(result)
                # annotator.clear()
                for face in faces:
                    annotator.bounding_box(transform(face.bounding_box), fill=0)
                # annotator.update()
                if len(faces) > 0:
                    # start to identify the person
                    print("Has Customer")
                    hasCustomer = True
                else:
                    print("No Customer")
                    hasCustomer = False



                print('#%05d (%5.2f fps): num_faces=%d, avg_joy_score=%.2f' %
                    (inference.count, inference.rate, len(faces), avg_joy_score(faces)))

        camera.stop_preview()



if __name__ == '__main__':
    main()

    while pool:
        with lock:
            processor = pool.pop()
            processor.terminated = True
            processor.join()