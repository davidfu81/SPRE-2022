import pyrealsense2 as rs
import cv2 as cv
from controller import PIDController as PID
import time
import numpy as np

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

# Establish depth stream
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

# Start streaming
pipeline.start(config)

# DRONE PARAMETERS

stopDist = 0.5  # Distance in meters away from an object that prevents the drone from moving forward
lastTime = time.time()

try:
    while True:

        # Wait for a depth frame
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame:
            continue

        # Convert image to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        [IMG_HEIGHT, IMG_WIDTH] = np.shape(depth_image)

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv.applyColorMap(cv.convertScaleAbs(depth_image, alpha=0.03), cv.COLORMAP_JET)

        # Find closest and furthest pixels: y is left-right, z is up-down (x is forward-back)
        furthest_id = np.argmax(depth_image)  # find index of furthest pixel
        furthest_y, furthest_z = np.unravel_index(furthest_id, (IMG_HEIGHT, IMG_WIDTH))
        furthest = depth_image[furthest_y, furthest_z]  # find depth of furthest pixel

        closest_id = np.argmin(depth_image)  # find index of closest pixel
        closest_y, closest_z = np.unravel_index(closest_id, (IMG_HEIGHT, IMG_WIDTH))
        closest = depth_image[closest_y, closest_z]  # find depth of closest pixel

        # Add circles on closest and furthest points
        cv.circle(depth_colormap, (furthest_y, furthest_z), 5, (0, 255, 0), 3)
        cv.circle(depth_colormap, (closest_y, closest_z), 5, (0, 0, 255), 3)

        # y_controller = PID(IMG_WIDTH / 2, 1, 1, 1, 0)
        # z_controller = PID(IMG_HEIGHT / 2, 1, 1, 1, 0)

        # thisTime = time.time()
        # y_controller.updateError(furthest_y, thisTime - lastTime)
        # z_controller.updateError(furthest_z, thisTime - lastTime)
        # lastTime = thisTime

        depth_colormap_dim = depth_colormap.shape

        # Show image
        cv.namedWindow("DepthMap", cv.WINDOW_AUTOSIZE)
        cv.imshow("DepthMap", depth_colormap)
        cv.imshow("RGB", color_image)

        cv.waitKey(1)

finally:

    # Stop streaming
    pipeline.stop()
