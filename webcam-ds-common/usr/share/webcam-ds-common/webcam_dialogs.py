#!/usr/bin/python
# -*- coding: utf-8 -*-

import gtk
import os
import stat
import sys

USERNAME = ''
PASSWORD = ''

STUDENTFULLNAME = ''
STUDENTEMAIL = ''
LASTTYPE='ALUMNO'

# ================


class UserDialog(gtk.Window):

    def close(self,widget,event,data = None):
        self.hide()
        gtk.main_quit()
        return gtk.FALSE

    def prep(self,widget,option):
        print widget, option
	global USERNAME
	global PASSWORD

        USERNAME = self.userentry.get_text()
        PASSWORD = self.passentry.get_text()
        self.hide()
        gtk.main_quit()
#        return gtk.FALSE
 
    def __init__(self):
        super(UserDialog, self).__init__()

        self.set_title("Acceso a WebCam Datastore")
        self.set_size_request(350, 160)
        self.set_position(gtk.WIN_POS_CENTER)
        
        win = gtk.Fixed()

        self.userlabel = gtk.Label("Usuario:")
        self.userentry = gtk.Entry()
        
        self.passlabel = gtk.Label("Password:")
        self.passentry = gtk.Entry()
        self.passentry.set_visibility(False)
        
        self.runbutton = gtk.Button("Conectar")
	self.runbutton.set_flags(gtk.CAN_DEFAULT)
        self.exitbutton = gtk.Button("Salir")

        self.exitbutton.connect("clicked", self.close, "Exit")
        self.runbutton.connect("clicked", self.prep, "Run")

        #win.put(self.urllabel, 50, 30)
        #win.put(self.urlentry, 150, 25)
        
        win.put(self.userlabel, 50, 30)
        win.put(self.userentry, 150, 25)
        
        win.put(self.passlabel, 50, 70)
        win.put(self.passentry, 150, 65)
        
        win.put(self.runbutton, 250, 110)
        win.put(self.exitbutton, 50, 110)
                        
        self.add(win)
        
        self.connect("destroy", gtk.main_quit)
        self.show_all()


def get_credentials():
	UserDialog()
	gtk.main()
	return (USERNAME, PASSWORD)

def error_dialog(txt):
	md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, txt)
	md.run()
	md.destroy()

def info_dialog(txt):
	md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, txt)
	md.run()
	md.destroy()

def yesno_dialog(txt):
	md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, txt)
	r=md.run()
	md.destroy()
	if r == gtk.RESPONSE_YES: 
		return True
	else:
		return False

# ===============

class StudentDialog(gtk.Window):

    def close(self,widget,event,data = None):
        self.hide()
        gtk.main_quit()
        return gtk.FALSE

    def prep(self,widget,option):
        print widget, option
	global STUDENTFULLNAME
	global STUDENTEMAIL
	global STUDENTTYPE

        STUDENTFULLNAME = self.fullnameentry.get_text()
        STUDENTEMAIL = self.emailentry.get_text()
	for r in self.studentbutton.get_group():
		if r.get_active():
			STUDENTTYPE = r.get_label()


        self.hide()
        gtk.main_quit()
#        return gtk.FALSE
 
    def __init__(self, txt):
        super(StudentDialog, self).__init__()
	global LASTTYPE
#	try:
#		foo = LASTTYPE
#	except NameError:
#		LASTTYPE = "ALUMNO"

        self.set_title(txt)
#        self.set_size_request(600, 160)
        self.set_size_request(600, 200)
        self.set_position(gtk.WIN_POS_CENTER)
        
        win = gtk.Fixed()

        self.fullnamelabel = gtk.Label("Apellidos, Nombre:")
        self.fullnameentry = gtk.Entry()
	self.fullnameentry.set_width_chars(60)
        
        self.emaillabel = gtk.Label("email:")
        self.emailentry = gtk.Entry()
        self.emailentry.set_width_chars(40)

#	box1 = gtk.VBox(False, 0)
#	self.add(box1)
#	box1.show()
#	box2 = gtk.VBox(False, 10)
#	box2.set_border_width(10)
#	box1.pack_start(box2, True, True, 0)
#	box2.show()

        self.typelabel = gtk.Label("tipo:")
	self.studentbutton = gtk.RadioButton(None, "ALUMNO")
#	box2.pack_start(self.studentbutton, True, True, 0)
#	self.studentbutton.show()

	self.teacherbutton = gtk.RadioButton(self.studentbutton, "PROFESOR")
	if LASTTYPE == "ALUMNO":
		self.studentbutton.set_active(True)
	else:
		self.teacherbutton.set_active(True)

#	box2.pack_start(self.teacherbutton, True, True, 0)
#	self.teacherbutton.show()

        self.runbutton = gtk.Button("Guardar")
	self.runbutton.set_flags(gtk.CAN_DEFAULT)

	self.runbutton.grab_default()

        self.exitbutton = gtk.Button("Cancelar")

        self.exitbutton.connect("clicked", self.close, "Exit")
        self.runbutton.connect("clicked", self.prep, "Run")

        #win.put(self.urllabel, 50, 30)
        #win.put(self.urlentry, 150, 25)
        
        win.put(self.fullnamelabel, 20, 30)
        win.put(self.fullnameentry, 140, 25)
        
        win.put(self.emaillabel, 20, 70)
        win.put(self.emailentry, 140, 65)
        
        win.put(self.typelabel, 20, 110)
        win.put(self.studentbutton, 140, 110)
        win.put(self.teacherbutton, 250, 110)
        
#        win.put(self.runbutton, 340, 110)
#        win.put(self.exitbutton, 140, 110)
        win.put(self.runbutton, 340, 150)
        win.put(self.exitbutton, 140, 150)

        self.add(win)
	self.runbutton.grab_default()
        
        self.connect("destroy", gtk.main_quit)
        self.show_all()


def get_student(txt, ltype):
	global LASTTYPE
	LASTTYPE=ltype
	StudentDialog(txt)
	gtk.main()
	return (STUDENTFULLNAME, STUDENTEMAIL, STUDENTTYPE)

# ===============
