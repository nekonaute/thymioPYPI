import os
import re
import sys, traceback
import logging

params = None

class Params :
	def __init__(self, configFile, mainLogger) :
		self.__mainLogger = mainLogger

		self.setParams(configFile)

	def setParams(self, configFile) :
		self.__mainLogger.debug('Params - Parsing configuration file.')

		self.__params = {}
		if(os.path.isfile(configFile)) :
			reLine = re.compile(r"^((int|float|str)\s+)?\S+\s*=\s*\S+$")
			with open(configFile, 'r') as configFile :
				configFile = configFile.readlines()

				# We get a list of tuple, each one of them being as follows : ([type, ]name, value)
				configFile = [tuple(re.sub('\s+', ' ', re.sub('=', ' ', line.rstrip('\n'))).split(' ')) for line in configFile if (line[0] != '#' and reLine.search(line))]

				try :
					for param in configFile :
						if len(param) > 1 :
							value = param[-1]

							if len(param) == 3 :
								if param[0] == 'int' :
									value = int(param[-1])
								elif param[0] == 'float' :
									value = float(param[-1])

							self.__params[param[-2]] = value
				except :
					self.__mainLogger.critical('Params - Unexpected error : ' + str(sys.exc_info()[0]) + ' - ' + traceback.format_exc())



	def checkParam(self, param) :
		if param in self.__params.keys() :
			return True
		else :
			return False

	def __getattr__(self, name) :
		if self.checkParam(name) :
			return self.__params[name]
		else :
			self.__mainLogger.critical("Params - No parameter " + name + " found.")
			return None



if __name__ == "__main__" :
	mainLogger = logging.getLogger()
	mainLogger.setLevel(logging.DEBUG)

	consoleHandler = logging.StreamHandler()
	consoleHandler.setLevel(logging.DEBUG)
	mainLogger.addHandler(consoleHandler)
	params = Params("./default_simulation.cfg", mainLogger)
	print("simulation_name : " + params.simulation_name)
	print("simulation_path : " + params.simulation_path)
