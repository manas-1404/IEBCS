# Joubert Damien, 03-02-2020 - updated by AvS 22-02-2024
"""
    Script converting a video into events. 
    The framerate of the video might not be the real framerate of the original video. 
    The user specifies this parameter at the beginning.
    Please run get_video_youtube.py before executing this script.
"""
import cv2
import sys
# Note: the "./" path is for running this script from the root of the repository. 
# Change here and the others below if you're running it from the script directory.
sys.path.append("./src") 
from event_buffer import EventBuffer
from dvs_sensor import DvsSensor
from event_display import EventDisplay
from tqdm import tqdm

filename = "./data/video/See Hummingbirds Fly Shake Drink in Amazing Slow Motion  National Geographic.mp4"
th_pos = 0.3
th_neg = 0.3
th_noise= 0.01
lat = 100
tau = 300
jit = 10
bgnp = 0.1
bgnn = 0.01
ref = 100

cap = cv2.VideoCapture(filename)

dvs = DvsSensor("MySensor")
dvs.set_shape(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
dvs.set_dvs_sensor(th_pos=th_pos, th_neg=th_neg, th_n=th_noise, lat=lat, tau=tau, jit=jit, bgnp=bgnp, bgnn=bgnn, ref=ref)
# dvs.init_bgn_hist("./data/noise_pos_161lux.npy", "./data/noise_neg_161lux.npy")

dt = 1000  # FPS must be 1 kHz
time = 0
for i in range(50): # Skip the first 50 frames of the video to remove video artifacts
    ret, im = cap.read()
im = cv2.cvtColor(im, cv2.COLOR_RGB2LUV)[:, :, 0] / 255.0 * 1e4
dvs.init_image(im)
ev_full = EventBuffer(1)
ed = EventDisplay("Events", cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT), 1 * dt, 0)

if cap.isOpened():
    for frame in tqdm(range(20), desc="Converting video to events"):
        ret, im = cap.read()
        if im is None:
            break
        im = cv2.cvtColor(im, cv2.COLOR_RGB2LUV)[:, :, 0] / 255.0 * 1e4
        ev = dvs.update(im, dt)
        ed.update(ev, dt)
        ev_full.increase_ev(ev)

cap.release()
ev_full.write('ev_{}_{}_{}_{}_{}_{}.dat'.format(lat, jit, ref, tau, th_pos, th_noise))