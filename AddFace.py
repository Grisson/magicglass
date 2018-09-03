########### Python 3.2 #############
import http.client, urllib.request, urllib.parse, urllib.error, base64

headers = {
    # Request headers
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': '',
}

params = urllib.parse.urlencode({
    # # Request parameters
    # 'userData': '{string}',
    # 'targetFace': '{string}',
})

body = "" 
#load image
with open("C:\\Users\\Grisson\\Pictures\\Camera Roll\\9.JPG", "rb") as f:
    body = f.read()


try:
    conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
    conn.request("POST", "/face/v1.0/persongroups/everyone/persons/7807b563-7796-4d95-b0a3-a43b36692202/persistedFaces?%s" % params, body, headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))

####################################
# b'{"persistedFaceId":"62a7d0be-a80d-4296-acb5-ecbba73a3757"}'
# b'{"persistedFaceId":"7a3494ab-2921-434d-b488-95dd2a79106e"}'

# b'{"persistedFaceId":"39987112-d759-46cb-9030-7a43db8497fe"}'

# b'{"persistedFaceId":"24962f5b-e803-4873-9c52-b7c0aba459d9"}'
# b'{"persistedFaceId":"24962f5b-e803-4873-9c52-b7c0aba459d9"}'
# b'{"persistedFaceId":"ebca2310-fb5f-4107-95d5-ff436069fa06"}'
# b'{"persistedFaceId":"fdba763f-a52d-4979-99c9-dc867ea23cfd"}'
# b'{"persistedFaceId":"5f5ff7fe-e1a2-4515-beb5-0d51df7bbdfc"}'