#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv
import sys
  
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

from webcam_dialogs import get_credentials, error_dialog, info_dialog

def usage(param=''):
	if param:
		print "Undefined parameter: "+param

	print 'Usage: '+sys.argv[0]+' -s DATASTORE_SERVER_URI'



def draw_card(nia):
    return True
    
    background = Image.open("student-card-bg.png")
    transbg=Image.new('RGBA',background.size)
#    transbg.save('print-image.png')
    foreground = Image.open(nia + ".jpg")
    foreground.thumbnail((145,181))

    #transbg.paste(foreground, (462, 75), mask=foreground)
    transbg.paste(foreground, (462, 75))
    draw = ImageDraw.Draw(transbg)
    font = ImageFont.truetype("/usr/share/fonts/truetype/msttcorefonts/arial.ttf", 24)
    nombre="Luis"
    apellidos="García Gisbert"
    nompos=(160,188)
    apepos=(160,236)
    niapos=(160,286)
    draw.text(nompos,nombre.decode('utf-8'),(0,0,0),font=font)
    draw.text(apepos,apellidos.decode('utf-8'),(0,0,0),font=font)
    draw.text(niapos,nia.decode('utf-8'),(0,0,0),font=font)
    #barcode0 = code128_image(nia.decode('utf-8'), height=60)
    #barcode = PIL.ImageOps.invert(barcode0)
    bar_text="Garcia Gisbert"
    #barcode = code128_image(bar_text.decode('utf-8'), height=60).convert("RGBA")

    ## make white trnsparent
    #pixdata = barcode.load()
    #for y in xrange(barcode.size[1]):
    #    for x in xrange(barcode.size[0]):
    #        if pixdata[x, y] == (255, 255, 255, 255):
    #            pixdata[x, y] = (255, 255, 255, 0)
    #
    #
    #transbg.paste(barcode,(100,300),mask=barcode)
    background.paste(transbg, (0, 0), mask=transbg)
    transbg.save(nia + '-print-image.png')
#    transbg.show()
    background.save(nia + '-preview-image.png')
    # create a cv window instead of PIL to show the image
    #background.show()
#image = Image.open(“ponzo.jpg”)   # image is a PIL image
    background_cv = cv.LoadImage(nia + '-preview-image.png')
    cv.ShowImage("carnet", background_cv)
    c=255
    while c == 255:
        c = cv.WaitKey(10) % 256


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
        global runCapture
        if(event == cv.CV_EVENT_LBUTTONDOWN):
            #print x,y
            runCapture = False
            #print  imagefile + str(param) + '.jpg'
            os.rename( imagefile + str(param) + '.jpg', nia + '.jpg')
            with open(nia+".jpg", "rb") as handle:
                binary_data = xmlrpclib.Binary(handle.read())
            handle.close()
            if server.put_file(USERNAME, PASSWORD, datastore_space, nia + '.jpg', binary_data):
		info_dialog("Foto de " + nia + " grabada correctamente")
            else:
		error_dialog("Error grabando foto")

            clear_tmpfiles()
            draw_card(nia)

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
        ycrop=0
        xcrop=602
        maxcropwindows=3

        # correction factors
  #     fx=1.3
  #     fy=1.8
        fzoom0=1.3
        xoffset0=0
        yoffset0=0

        fzoom=fzoom0
        xoffset = xoffset0
        yoffset = yoffset0

	USERNAME = ''
	PASSWORD = ''
	server = None

	datastore_uri = ''
	datastore_space = 'matricula'
	dbhost = ''
	dbname = ''
	dbpass = ''
	dbuser = ''

	webcam = -1
	conf_file = '/etc/carnet-o-matic/carnet-o-matic.conf'
	real_nia = ''

	(USERNAME, PASSWORD) = get_credentials()
	if not USERNAME or not PASSWORD:
		quit()

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hs:c:", ["help", "server=", "cam="])
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
		
	# access datastore
	try:
		server = xmlrpclib.Server(datastore_uri)
		dbhost = server.get_value(USERNAME, PASSWORD, datastore_space, 'dbhost')
		dbname = server.get_value(USERNAME, PASSWORD, datastore_space, 'dbname')
		dbuser = server.get_value(USERNAME, PASSWORD, datastore_space, 'dbuser')
		dbpass = server.get_value(USERNAME, PASSWORD, datastore_space, 'dbpass')
	except:
#		usage('Error accessing datastore server')
		error_dialog('Error accessing datastore server')
		sys.exit

	if not dbhost or not dbname or not dbpass:
#		usage('Error retrieving mysql parameters')
		error_dialog('Error retrieving mysql parameters')
		sys.exit()

	#connect to database
	try:
		db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname)
	except:
		usage('Error accessing database')
		sys.exit()
	while True:
        	nia = get_text(None, 'Introduzca el NIF/NIE:')
		if not nia:
            		quit()

		nia = nia.upper()
		nia = nia.strip()
		if not ( len(nia) == 10 ):
			if nia[0].isdigit():
				prenia = ''
			else:
				prenia = nia[:1]
				nia = nia[1:]

			while (len(prenia+nia) < 10):
				nia = "0"+nia

			nia = prenia + nia
				
		#search in database
		try:
			# connect
			db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname)
			cur = db.cursor()
			cur.execute("SELECT nombre_comp, NIA FROM admitaca WHERE dni='%s';" % (nia))
			first_row =(cur.fetchall())[0]
			cur.close()
			db.close()
			info_dialog(first_row[0]+'\nDNI: '+nia+'\nNIA: '+first_row[1])
		except:
			real_nia=get_text(None, nia+' no encontrado\nIntroduzca el NIA para seguir:')
			if not real_nia:
				continue

	
        	capture = cv.CaptureFromCAM(webcam)
	  #      cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_WIDTH,1280)
	  #      cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_HEIGHT, 960);

        	cv.NamedWindow(nia)
        	cv.MoveWindow(nia, xcam, ycam)
        	storage = cv.CreateMemStorage()
        	cascade = cv.Load('/usr/share/webcam-datastore/haarcascade_frontalface_alt.xml')
        	faces = []

        	i=0
	        numrows = 1
        	xcropnext=xcrop 
        	imagefile=datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss%f') + '-'
        	runCapture = True


        	while runCapture:
			frame = cv.QueryFrame(capture)
            	# Only run the Detection algorithm every 5 frames to improve performance
			if i%5==0:
				faces = detect_faces(frame)

			for (x,y,w,h) in faces:
				cv.Rectangle(frame, (x-1,y-1), (x+w+2,y+h+2), 255)

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
			elif c == 10 or c == 141:
				# ENTER pressed. Store image to disk
				#imagefile=datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss%f') + '.jpg'
				#cv.SaveImage(imagefile, frame)
				#image = Image.open(imagefile)
				#image.show()
		
				for (x,y,w,h) in faces:
					#cropfile = imagefile + str(nface) + '.jpg'
					#cv.SaveImage(cropfile, frame[y:y+h, x:x+w])
					#crop = Image.open(cropfile)
					#crop.show()
					if nface == numrows*maxcropwindows:
						xcropnext=xcrop 
						numrows += 1
						ycrop += 15

#                    if  nface >= numrows:
#                        cv.DestroyWindow("crop" +str(nface-maxcropwindows*(numrows-1)))

					cv.ShowImage('crop' + str(nface),frame[y:y+h, x:x+w])
					cv.SaveImage( imagefile + str(nface) + '.jpg', frame[y:y+h, x:x+w])
					cv.SetMouseCallback("crop" + str(nface),on_mouse, param=nface)
					cv.MoveWindow("crop" + str(nface), xcropnext, ycrop)
					xcropnext = xcropnext + w + 4
					nface += 1
			#else:
	                #print str(c)
    
		
        	clear_tmpfiles()
        	capture = None
        	cv.DestroyAllWindows()

 
