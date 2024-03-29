import time
import cv2
import gluoncv as gcv
import mxnet as mx
import numpy as np
import matplotlib.pyplot as plt

#Create an instance of a multi object tracker to start off with. Every time you need a new tracker it can be added to the multi object tracker
threshold = 0.8
detect_interval = 20
detect_counter = 0
classes = ['Visa','Powerade','Hyundai','Coke','Adidas']
stats = np.zeros(len(classes))

net = gcv.model_zoo.get_model('ssd_512_mobilenet1.0_custom', classes = classes, pretrained_base=False)
net.load_parameters('logos.params')
#net.collect_params().reset_ctx([mx.gpu(0)])
cap = cv2.VideoCapture('soccer.mp4')
#out = cv2.VideoWriter('detected.avi',cv2.VideoWriter_fourcc(*'DIVX'),15,size)
axes = None
NUM_FRAMES = 1000
img_array = []
#tracker = cv2.TrackerCSRT_create()
trackers = cv2.MultiTracker_create()
bbs = []
new_scores = []
new_classes = []
saveheight = 0
savewidth = 0
for i in range(NUM_FRAMES):
    print(i)
    try:
        ret,frame = cap.read()
    except:
        break
    if (detect_counter)%detect_interval==0:
        trackers = cv2.MultiTracker_create()
        print("DETECT")
        #Detect the objects and set up trackers for them
        detect_counter = 1
        frame = mx.nd.array(frame).astype('uint8')
        rgb_nd,frame = gcv.data.transforms.presets.ssd.transform_test(frame,short=512,max_size=700)
        #rgb_nd = rgb_nd.as_in_context(mx.gpu(0))
        class_IDs,scores,bounding_boxes = net(rgb_nd)
        #print(bounding_boxes[0])
        bbs = []
        new_scores = []
        new_classes = []
        for j in range(len(scores[0])):
            if scores[0][j] >= threshold:
                thisClass = int(class_IDs[0][j].asnumpy())
                stats[thisClass] += 1.0
                test = bounding_boxes[0][j].asnumpy()
                bbs.append(test)
                new_scores.append(scores[0][j].asnumpy())
                new_classes.append(class_IDs[0][j].asnumpy())
                tracker = cv2.TrackerMOSSE.create()
                #print(bounding_boxes[0][j].asnumpy())
                tracker_bb = (test[0],test[1],test[2]-test[0],test[3]-test[1])
                trackers.add(tracker,frame,tracker_bb)
            else:
                break
        #img = gcv.utils.viz.cv_plot_bbox(frame,bbs,new_scores,new_classes,class_names=net.classes,thresh=threshold)

        #height,width,layers = img.shape
        #size = (width,height)
        #img_array.append(img)
        #out.write(img)
        #cv2.imshow('image',img)
        #gcv.utils.viz.cv_plot_image(img)
        #cv2.waitKey(1)
        for box in bbs:
            (x,y,w,h) = [int(v) for v in box]
            print(x,y,w,h)
            cv2.rectangle(frame,(x,y),(w,h),(0,255,0),2)

    else:
        #Update the trackers
        print("TRACK")
        detect_counter += 1

        #frame = mx.nd.array(frame).astype('uint8')
        #rgb_nd,frame = gcv.data.transforms.presets.ssd.transform_test(frame,short=512,max_size=700)
        frame = cv2.resize(frame,(savewidth,saveheight))
        (success,bbs) = trackers.update(frame)
        #img = gcv.utils.viz.cv_plot_bbox(frame,bbs,new_scores,new_classes,class_names=net.classes,thresh=threshold)

        #height,width,layers = img.shape
        #size = (width,height)
        #img_array.append(img)
        #gcv.utils.viz.cv_plot_image(img)

        #cv2.imshow('image',img)
        #cv2.waitKey(1)


        for box in bbs:
            (x,y,w,h) = [int(v) for v in box]
            print(x,y,x+w,y+h)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
    height,width,layers = frame.shape
    size = (width,height)
    saveheight = height
    savewidth = width
    img_array.append(frame)


    #Check for a scene change - automatic object detection


x = np.arange(len(classes))
y = stats
plt.bar(x,y,edgecolor='k',linewidth=2,color=['black','red','green','blue','yellow'])
plt.tick_params(axis='both',which='major',labelsize=12)
plt.xticks(x,classes,fontsize=8)
plt.ylabel("Appearances",fontsize=14)
plt.savefig("Plot.png")

out = cv2.VideoWriter('tracked.avi',cv2.VideoWriter_fourcc(*'DIVX'),60,size)

for i in range(len(img_array)):
    out.write(img_array[i])
cap.release()
out.release()
cv2.destroyAllWindows()

