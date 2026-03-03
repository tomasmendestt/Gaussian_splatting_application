import pyzed.sl as sl
import sys
import cv2
import tkinter as tk
from tkinter import messagebox

def grab_frames(num_frames):
    # Create a Camera object
    zed = sl.Camera()

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.AUTO # Use HD720 opr HD1200 video mode, depending on camera type.
    init_params.camera_fps = 30  # Set fps at 30

    # Open the camera
    err = zed.open(init_params)
    if err > sl.ERROR_CODE.SUCCESS:
        print("Camera Open : "+repr(err)+". Exit program.")
        exit()


    # Capture 50 frames and stop
    i = 0
    image = sl.Mat()
    runtime_parameters = sl.RuntimeParameters()
    while i < num_frames:
        # Grab an image, a RuntimeParameters object must be given to grab()
        if zed.grab(runtime_parameters) <= sl.ERROR_CODE.SUCCESS:
            # A new image is available if grab() returns ERROR_CODE.SUCCESS or a WARNING (an error_code lower than ERROR_CODE.SUCCESS)
            zed.retrieve_image(image, sl.VIEW.LEFT)
            timestamp = zed.get_timestamp(sl.TIME_REFERENCE.CURRENT)  # Get the timestamp at the time the image was captured
            print("Image resolution: {0} x {1} || Image timestamp: {2}\n".format(image.get_width(), image.get_height(),
                  timestamp.get_milliseconds()))
            
            # Convert the ZED image to OpenCV format and save it as a PNG file
            
            path = r"D:\Images"
            image_path = path + "\\ZED_Image_" + str(i) + ".png" 
            cv_image = image.get_data()
            cv2.imwrite(image_path, cv_image)
            #cv2.waitKey(1)

            i = i + 1

    

    # Close the camera
    zed.close()

if __name__ == "__main__":

    print("Choose photo mode (0) or video mode (1) (default is 0): ")

    try:
        mode = int(input())
    except ValueError:
        mode = 0


    print("Please insert number of frames to grab (default is 50): ")
    try:
        num_frames = int(input())
    except ValueError:
        num_frames = 50
    
    if mode  == 0:
        grab_frames(num_frames)
    #else
