#!/usr/bin/env/python

import Simulation

import traceback
import sys
import picamera
import termios
import tty

class Getch:
    def __init__(self):
    	pass

    def __call__(self):
      fd = sys.stdin.fileno()
      old_settings = termios.tcgetattr(fd)

      try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
      finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

      return ch

class SimulationSpyBot(Simulation.Simulation) :
	def __init__(self, controller, mainLogger) :
		Simulation.Simulation.__init__(self, controller, mainLogger)

		self.__camera = picamera.PiCamera()
		self.__getch = Getch()

	def preActions(self) :
		self.__camera.start_preview()

	def step(self) :
		try :
			# User input
			char = self.__getch()

			if char.lower() == 'q' or char.lower() == 'x' :
				self.__camera.stop_preview()
				self.stop()
			elif char.lower() == 'z' :
				self.tController.writeMotorsSpeedRequest([300, 300])
			elif char.lower() == 's' :
				self.tController.writeMotorsSpeedRequest([-300, -300])
			elif char.lower() == 'q' :
				self.tController.writeMotorsSpeedRequest([-300, 300])
			elif char.lower() == 'd' :
				self.tController.writeMotorsSpeedRequest([300, -300])
			else :
				self.mainLogger.error("SimulationSpyBot - Not a correct character : " + char)

			self.waitForControllerResponse()
		except :
			self.mainLogger.critical('SimulationSpyBot - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())
