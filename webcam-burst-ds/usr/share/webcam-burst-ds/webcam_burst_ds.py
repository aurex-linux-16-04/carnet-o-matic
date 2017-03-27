#! /usr/bin/python
# -*- coding: utf-8 -*-

import cv
import sys
from time import sleep
  
from datetime import datetime

import glob, os
import gtk
#from gi.repository import Gtk
import numpy
 
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw  
import PIL.ImageOps  
from ConfigParser import SafeConfigParser
import xmlrpclib
import MySQLdb
import getopt
import ssl

import Tkinter as tk
import socket
import time
import random

from webcam_dialogs import error_dialog, info_dialog, get_student, get_guest, yesno_dialog, info_dialog, get_credentials

def usage(param=''):
	if param:
		print "Undefined parameter: "+param

	print 'Usage: '+sys.argv[0]+' -s DATASTORE_SERVER_URI'


def get_text(parent, message, default=''):
    """
    Display a dialog with a text entry.
    Returns the text, or None if canceled.
    """
    d = gtk.MessageDialog(parent,
                          gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                          gtk.MESSAGE_QUESTION,
                          gtk.BUTTONS_OK_CANCEL,
                          message)
    entry = gtk.Entry()
    entry.set_text(default)
    entry.show()
    d.vbox.pack_end(entry)
    entry.connect('activate', lambda _: d.response(gtk.RESPONSE_OK))
    d.set_default_response(gtk.RESPONSE_OK)

    r = d.run()
    text = entry.get_text().decode('utf8')
    d.destroy()
    if r == gtk.RESPONSE_OK:
        return text
    else:
        return None



# ================


# ===============


def detect_faces(image):

    # may be this can be detected from image?
    dpi_factor=72
    # required size in mm
    xmm=25.0
    ymm=32.0
    target_ratio=xmm/ymm
    # conversion factor (1 mm in inches)
    m2i=0.039370
    # dots per milimeter conversion factor
    dpm_factor=dpi_factor*m2i

    faces = []
    detected = cv.HaarDetectObjects(image, cascade, storage, 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (100,100))
    if detected:
        for (x,y,w,h),n in detected:
#            faces.append((x,y,w,h))
            # fix aspect ratio
            det_ratio=w/h
            if det_ratio > target_ratio:
                #wnew=w*fx
                wnew=w*fzoom
                hnew=wnew/target_ratio
                # print "fx"
            else:
                #hnew=h*fy
                hnew=h*fzoom
                wnew=hnew*target_ratio
                # print "fy"

            xnew=int(xoffset+x-(wnew-w)/2)
            ynew=int(yoffset+y-(hnew-h)/2)

            faces.append((xnew,ynew,int(wnew),int(hnew)))
    return faces

def on_mouse(event, x, y, flag, param):
	global usercount
	global demo_mode
	global saved_list
        if(event == cv.CV_EVENT_LBUTTONDOWN):
            #print x,y
#            runCapture = False
#            print  imagefile + str(param) + '.jpg'
            if not demo_mode:
                apenom = get_guest("Introduzca nombre")
            else:
                apenom = ""
	
            if demo_mode or apenom:
                usercount=usercount+1
                user_id = user_id_base +str(usercount)
	        if apenom:
                    os.rename( imagefile + str(param) + '.jpg', user_id + '.jpg')
                    with open(user_id+".jpg", "rb") as handle:
                        binary_data = xmlrpclib.Binary(handle.read())
                    handle.close()
                    if server.put_file(USERNAME, PASSWORD, datastore_space, user_id + '.jpg', binary_data):
			#print "foto subida"
                        #put in database
                        try:
                            # connect
                            db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname)
                            cur = db.cursor()
#                            try:
                            cur.execute("INSERT INTO fotos_jornadas (foto, user_id, nombre_comp) VALUES ('%s', '%s', '%s');" % (user_id + ".jpg", user_id, apenom))
     		            db.commit()
#                            except:
#                                # Rollback in case there is any error
#                                db.rollback()
                            cur.close()
                            db.close()
                            info_dialog("Foto de " + apenom + " grabada correctamente")
                            saved_list.append(user_id)
                        except:
                            #print dbhost+ " - "+ dbuser + " - "+ dbpass + " - "+ dbname
                            error_dialog("Error grabando foto")
                    else:
                        error_dialog("Error mandando foto")
		else:
                    os.rename( imagefile + str(param) + '.jpg', user_id + '.jpg')
		    info_dialog("Foto Seleccionada")

                cv.DestroyWindow('crop' + str(param))

        elif(event == cv.CV_EVENT_RBUTTONDOWN):
            cv.DestroyWindow('crop' + str(param)) 
            
def clear_tmpfiles():
    filelist = glob.glob(imagefile + "*.jpg")
    for f in filelist:
        os.remove(f)	

        
if __name__ == '__main__':
    
        nface=0
        ycam=0
        xcam=0
        #ycrop=600
	# get maximum screen size (including multiple monitor config)
	root_window = tk.Tk()
	screen_width = root_window.winfo_screenwidth()
	screen_height = root_window.winfo_screenheight()

	demo_mode = False
	user_id_base = ""
	for i in range(3):
		user_id_base=user_id_base + str(random.randint(0,9))

	user_id_base=user_id_base+"-"+str(int(time.time()))
	user_count = 0
        ycrop=0
        xcrop=screen_width
        maxcropwindows=5

	demo_mode = False

        # correction factors
  #     fx=1.3
  #     fy=1.8
        fzoom0=1.3
        xoffset0=0
        yoffset0=0

        fzoom=fzoom0
        xoffset = xoffset0
        yoffset = yoffset0

	#face_min_width = 200
	#face_min_height = 260
	face_min_height = 150
	face_min_x = 0
	face_min_y = 0

	usercount=0

	USERNAME = ''
	PASSWORD = ''
	server = None

	datastore_uri = ''
	datastore_space = 'opendoors'
	dbhost = ''
	dbname = ''
	dbpass = ''
	dbuser = ''

	webcam = -1
	resolution = ''
	conf_file = '/etc/carnet-o-matic/carnet-o-matic.conf'
	new_apenom = ''
	new_email = ''
	new_type = ''
	new_type="ALUMNO"


	nia = 'Captura'


	(USERNAME, PASSWORD) = get_credentials()
        if not USERNAME or USERNAME.upper == "DEMO" or not PASSWORD :
		demo_mode = True
		nia = "DEMO"
                info_dialog("El programa funcionará únicamente en modo DEMO")

	burst_size = 0

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hs:c:r:", ["help", "server=", "cam=", "res="])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
		
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ( "-s", "--server"):
			datastore_uri = arg
		elif opt in ( "-c", "--cam"):
			webcam = int(arg)
		elif opt in ( "-r", "--res"):
			resolution = arg

        parser = SafeConfigParser()
        parser.read(conf_file)
	if not datastore_uri:
		try:
			datastore_uri = parser.get('datastore', 'uri')
		except:
			usage('datastore.uri')
			sys.exit()

	if (webcam == -1 ):
		try:
			webcam = int(parser.get('webcam', 'cam'))
		except:
			webcam = 0
		
	if not resolution:
		try:
			resolution = parser.get('webcam', 'res')
		except:
			resolution = ''

	# access datastore
	if not demo_mode:
		try:
			# avoid python 2.7.9 certificate validation
			if sys.version_info[0]*100 + sys.version_info[1]*10 + sys.version_info[2] >= 279 :
				ssl._create_default_https_context = ssl._create_unverified_context
			server = xmlrpclib.Server(datastore_uri)
			dbhost = server.get_value(USERNAME, PASSWORD, datastore_space, 'dbhost')
			dbname = server.get_value(USERNAME, PASSWORD, datastore_space, 'dbname')
			dbuser = server.get_value(USERNAME, PASSWORD, datastore_space, 'dbuser')
			dbpass = server.get_value(USERNAME, PASSWORD, datastore_space, 'dbpass')
		except:
#			usage('Error accessing datastore server')
			error_dialog('Error accessing datastore server')
			sys.exit

		if not dbhost or not dbname or not dbpass:
#			usage('Error retrieving mysql parameters')
			error_dialog('Error retrieving mysql parameters')
			sys.exit()

		#connect to database
		try:
			db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname)
		except:
			usage('Error accessing database')
			sys.exit()


	runForever = True
	saved_list = []
	while runForever:
        	capture = cv.CaptureFromCAM(webcam)
		if resolution:
			(xres,yres) = resolution.split("x")
			cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_WIDTH, int(xres))
			cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_HEIGHT, int(yres));

        	cv.NamedWindow(nia)
        	cv.MoveWindow(nia, xcam, ycam)
        	storage = cv.CreateMemStorage()
		cascade = cv.Load('/usr/share/webcam-ds-common/haarcascade_frontalface_alt.xml')

		# get current limits
		face_max_x = int(cv.GetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_WIDTH))
		face_max_y = int(cv.GetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_HEIGHT))

        	faces = []
		correct_faces = []

        	i=0
	        numrows = 1
        	xcropnext=xcrop 
        	nface=0
        	imagefile=datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss%f') + '-'
        	runCapture = True
		burst = 0

		face_size_correct = False

        	while runCapture:
			frame = cv.QueryFrame(capture)
            	# Only run the Detection algorithm every 5 frames to improve performance
			if i%5==0:
				faces = detect_faces(frame)

			face_size_correct = False
			correct_faces = []
			for (x,y,w,h) in faces:
				rcolor = (0, 255, 0)
				if (h < face_min_height) or (y < face_min_y) or (y+h > face_max_y) or (x < face_min_x) or (x+w > face_max_x):
#						#face_size_correct = False
					rcolor = (0, 0, 255)
				else:
					correct_faces.append((x,y,w,h))
					face_size_correct = True

				cv.Rectangle(frame, (x-1,y-1), (x+w+2,y+h+2), rcolor)

			cv.ShowImage(nia, frame)
			i += 1
			c = cv.WaitKey(10) % 256
        
			if c == 27:
				# ESC pressed. Finish the program
				runCapture = False
		                #break
			elif c == 48 or c == 176 or c == 158:
				# 0 pressed, reset parameters
				fzoom=fzoom0
				xoffset = xoffset0
				yoffset = yoffset0
			elif c == 82 or c == 184 or c == 151:
				# up arrow pressed, y--
				yoffset -= 10
			elif c == 84 or c == 178 or c == 153:
				# down arrow pressed, y++
				yoffset += 10
			elif c == 83 or c == 182 or c == 152:
				# -> arrow pressed, x++
				xoffset += 10
			elif c == 81 or c == 180 or c == 150:
				# <- arrow pressed, x--
				xoffset -= 10
			elif c == 43 or c == 171:
				# + pressed
				fzoom += 0.1
			elif c == 45 or c == 173:
				# - pressed
				fzoom -= 0.1
			elif ( c == 10 or c == 141 ) and face_size_correct:
				# ENTER pressed. Store image to disk
				#imagefile=datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss%f') + '.jpg'
				#cv.SaveImage(imagefile, frame)
				#image = Image.open(imagefile)
				#image.show()
					
				for (x,y,w,h) in correct_faces:
					#cropfile = imagefile + str(nface) + '.jpg'
					#cv.SaveImage(cropfile, frame[y:y+h, x:x+w])
					#crop = Image.open(cropfile)
					#crop.show()
					if nface == numrows*maxcropwindows:
						xcropnext=xcrop 
						numrows += 1
						ycrop += int(h/4)
			
					xcropnext=xcropnext - int(2*w/3)
					cv.ShowImage('crop' + str(nface),frame[y:y+h, x:x+w])
					cv.SaveImage( imagefile + str(nface) + '.jpg', frame[y:y+h, x:x+w])
					cv.SetMouseCallback("crop" + str(nface),on_mouse, param = nface)
					cv.MoveWindow("crop" + str(nface), xcropnext, ycrop)
					#xcropnext = xcropnext + w + 4
					nface += 1
#				sleep(1)
				#face_size_correct = False

			#else:
	                #print str(c)
    
		
        	clear_tmpfiles()
        	capture = None
        	cv.DestroyAllWindows()
		if nface == 0 and yesno_dialog("Terminar el programa?"):
			runForever = False
			
	if saved_list:
		csv_file = datastore_space+"-"+user_id_base+".csv"
		try:
			csv = open(csv_file, "w")
			csv.write('"user_id","nombre_comp","foto"\r\n')
			# connect
			db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname)
			cur = db.cursor()
			#read
			for id in saved_list:
				cur.execute("SELECT user_id, nombre_comp, foto from fotos_jornadas where user_id='%s';" % (id))
				row = cur.fetchone()
				while row is not None:
					csv.write('"'+row[0]+'","'+ row[1]+'","'+row[2]+'"\r\n')
					row = cur.fetchone()

			cur.close()
			db.close()
			csv.close()

			with open(csv_file, "rb") as handle:
				binary_data = xmlrpclib.Binary(handle.read())
				handle.close()
			if not server.put_file(USERNAME, PASSWORD, datastore_space, csv_file, binary_data):
				error_dialog("Error enviando csv")

		except:
			error_dialog("Error generando csv")


