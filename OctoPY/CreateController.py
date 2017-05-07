#!/usr/bin/env python

import argparse
import os

"""
OCTOPY : CreateController.py

Script used to create a configuration file (.cfg file) and folder containing 
a file with basic code for a controller.
"""

def main(args) :
	CONTROLLERS_FOLDER = "controllers"
	subfolder = args.controller
	folder = os.path.join(CONTROLLERS_FOLDER,subfolder)
	configFile = "config_" + args.controller + ".cfg"
	classFile = "Controller" + args.controller
	mainClass = classFile

	if not os.path.isdir(folder) :
		# Creation of the experiment folder
		print("Creating folder " + folder + " ...")
		os.mkdir(folder)

		# Creation of the configuration file
		print("Creating configuration file " + configFile + " ...")
		with open(CONTROLLERS_FOLDER+"/"+configFile, "w") as fileOut :
			codeFile = """# Class name of the controller
controller_name = """ + mainClass + """

# Path of controller
controller_path = """ + subfolder + """.""" + classFile

			fileOut.write(codeFile)

		# Creation of the __init__.py file
		print("Creating __init__.py file ...")
		os.mknod(os.path.join(folder, "__init__.py"))

		# Creation of the Simulation file
		print("Creating controller file " + classFile + ".py ...")
		with open(os.path.join(folder, classFile + ".py"), "w") as fileOut :
			codeFile = """#!/usr/bin/env/python

import Controller
import Params

class """ + mainClass + """(Controller.Controller) :
	def __init__(self, octoPYInstance, detached) :
		Controller.Controller.__init__(self, octoPYInstance, detached)

	def preActions(self) :
		pass

	def postActions(self) :
		pass

	def step(self) :
		pass

	def notify(self, **params) :
		pass"""

			fileOut.write(codeFile)
	else :
		print("Experiment folder " + folder + " exists already !")


if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('controller', help = "Name of the controller.")
	args = parser.parse_args()

	main(args)