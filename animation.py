from picamera import PiCamera
from time import sleep
from gpiozero import Button
from PIL import Image, ImageDraw
import os
import shutil

def write_frame(path, frame_number):
	frame_file = open(path, 'w')
	frame_file.write(str(frame_number))
	frame_file.flush()
	frame_file.close()

def initialize_frame_file():
	if not os.path.exists(os.path.dirname('/home/pi/Animation/anim/')):
		os.mkdir(os.path.dirname('/home/pi/Animation/'))
		os.chmod('/home/pi/Animation/', 777)
		os.mkdir(os.path.dirname('/home/pi/Animation/anim/'))
		os.chmod('/home/pi/Animation/anim', 777)
		os.mkdir(os.path.dirname('/home/pi/Animation/frame/'))
		os.chmod('/home/pi/Animation/frame', 777)
	frame_file = open(frame_file_path, 'w+')
	frame = 0
	prevframe = 0
	frame_file.write(str(frame))
	frame_file.flush()
	frame_file.close()
	os.chmod(frame_file_path, 777)

capture_button = Button(21)
reset_button = Button(20)
camera = PiCamera()
frame_file_path = '/home/pi/Animation/anim/frame_file.txt'
prevframe = 0
frame = 0

camera.start_preview()
#camera.start_preview(fullscreen=False, window = (100, 20, 640, 480))
camera.rotation = 180

try:
	frame_file = open(frame_file_path, 'r')
	frame = int(frame_file.read(4), 10)
	prevframe = frame - 1
	frame_file.close()
except FileNotFoundError:
	initialize_frame_file()

while True:
	try:
		if prevframe != frame:
			try:
				camera.remove_overlay(o)
			except Exception:
				pass

			try:
				im = Image.open('/home/pi/Animation/frame/frame%04d.jpg' % (frame - 1))
				o = camera.add_overlay(im.tobytes(), size = im.size, format = 'rgb')
				o.alpha = 128
				o.layer = 3
			except FileNotFoundError:
				pass

		prevframe = frame
		camera.annotate_text = '%05d/10000' % frame
		if capture_button.is_pressed:
			camera.annotate_text = ''
			camera.capture('/home/pi/Animation/frame/frame%04d.jpg' % frame, use_video_port = True, resize=(2592, 1458))
			sleep(1)
			frame += 1
			if frame > 9999:
				frame = 0
			write_frame(frame_file_path, frame)

		if reset_button.is_pressed:
			try:
				camera.remove_overlay(o)
			except Exception:
				pass
			shutil.rmtree('/home/pi/Animation')
			initialize_frame_file()

	except KeyboardInterrupt:
		camera.stop_preview()
		try:
			camera.remove_overlay(o)
		except Exception:
			pass
		break
