import requests
import argparse
import cv2
import os

ap = argparse.ArgumentParser()
ap.add_argument("-u","--urls",required=True,
        help="locatiion of url file")
ap.add_argument("-o","--output",required=True,
        help="Directory in which to place images")
args = vars(ap.parse_args())

rows = open(args["urls"]).read().strip().split("\n")
total = 0

for i,url in enumerate(rows):
    try:
        r = requests.get(url,timeout=60)
        p = os.path.sep.join([args["output"],"{}.jpg".format(
            str(total).zfill(8))])
        f = open(p,"wb")
        f.write(r.content)
        f.close()
        total+= 1
        print("Download Successful"+str(total))

    except:
        print("Error Downloading a file")
