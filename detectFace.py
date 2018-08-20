########### Python 3.2 #############
import http.client, urllib.request, urllib.parse, urllib.error, base64

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
#load image
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

##b'[{"faceId":"97819840-8000-4fdf-a0a4-663e8e6832d3","faceRectangle":{"top":466,"left":729,"width":381,"height":381},"faceLandmarks":{"pupilLeft":{"x":831.3,"y":572.9},"pupilRight":{"x":998.7,"y":559.7},"noseTip":{"x":919.8,"y":673.2},"mouthLeft":{"x":853.6,"y":754.2},"mouthRight":{"x":994.6,"y":741.0},"eyebrowLeftOuter":{"x":769.0,"y":523.3},"eyebrowLeftInner":{"x":875.4,"y":523.9},"eyeLeftOuter":{"x":799.7,"y":575.6},"eyeLeftTop":{"x":828.5,"y":565.8},"eyeLeftBottom":{"x":827.9,"y":583.0},"eyeLeftInner":{"x":857.0,"y":575.2},"eyebrowRightInner":{"x":936.6,"y":516.4},"eyebrowRightOuter":{"x":1050.9,"y":497.5},"eyeRightInner":{"x":970.8,"y":566.0},"eyeRightTop":{"x":996.4,"y":551.6},"eyeRightBottom":{"x":996.9,"y":568.4},"eyeRightOuter":{"x":1020.5,"y":557.2},"noseRootLeft":{"x":888.6,"y":575.1},"noseRootRight":{"x":938.1,"y":572.9},"noseLeftAlarTop":{"x":875.4,"y":645.3},"noseRightAlarTop":{"x":955.3,"y":638.1},"noseLeftAlarOutTip":{"x":854.6,"y":682.6},"noseRightAlarOutTip":{"x":976.4,"y":671.4},"upperLipTop":{"x":921.2,"y":732.2},"upperLipBottom":{"x":922.1,"y":751.9},"underLipTop":{"x":922.8,"y":755.6},"underLipBottom":{"x":926.2,"y":781.1}},"faceAttributes":{"gender":"male","age":35.0}}]'