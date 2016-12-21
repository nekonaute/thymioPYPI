#!/usr/bin/env python

import io
import argparse
import os
import re
import shutil


def main(args) :
	if args.source == args.destination :
		print("Error: source and destination are the same.")
	else :
		if not os.path.isfile(args.source) :
			print("Error: source configuration file " + args.source + " does not exist !")
		else :
			classFileDestination = "Simulation" + args.destination
			folderDestination = args.destination
			configFileDestination = "config_" + args.destination + ".cfg"

			if os.path.isfile(configFileDestination) :
				print("Error: destination configuration file " + configFileDestination + " already exists !")
			else :
				if os.path.isdir(folderDestination) :
					print("Error: destination folder " + folderDestination + " already exists !")
				else :
					configFileSource = args.source
					folderSource = None
					simulationSource = None

					fileWrite = ""
					with open(configFileSource, "r") as fileRead :
						fileRead = fileRead.readlines()

						reName = re.compile(r"^\s*simulation_name\s*=\s*(\S+)$")
						rePath = re.compile(r"^\s*simulation_path\s*=\s*(\S+)$")
						for line in fileRead :
							s = reName.search(line)

							if s :
								simulationName = s.group(1)
								fileWrite += "simulation_name = Simulation" + args.destination + "\n"
							else :
								s = rePath.search(line)

								if s :
									simulationPath = s.group(1)
									split = simulationPath.split('.')
									folderSource = split[0]
									simulationSource = split[1]

									fileWrite += "simulation_path = " + folderDestination + "." + classFileDestination + "\n"
								else :
									fileWrite += line

					print("Duplicating configuration file " + configFileSource + " into " + configFileDestination + "...")
					with open(configFileDestination, "w") as fileOut :
						fileOut.write(fileWrite)

					print("Creating folder " + folderDestination + "...")
					os.mkdir(folderDestination)

					print("Creating __init__.py file...")
					os.mknod(os.path.join(folderDestination, "__init__.py"))

					print("Creating readme file...")
					with open(os.path.join(folderDestination, "readme.txt"), "w") as fileOut :
						codeFile = """This folder is for the experiment """ +  args.destination + """.

			--- DESCRIBE EXPERIMENT HERE ---"""

						fileOut.write(codeFile)

					print("Duplicating simulation file " + os.path.join(folderSource, simulationSource + ".py") + " into " + os.path.join(folderDestination, classFileDestination + ".py") + "...")
					shutil.copyfile(os.path.join(folderSource, simulationSource + ".py"), os.path.join(folderDestination, classFileDestination + ".py"))

					fileWrite = ""
					with open(os.path.join(folderDestination, classFileDestination + ".py"), "r") as fileRead :
						fileRead = fileRead.readlines()

						reClassName = re.compile(r"^class\s+\S+\(")
						for line in fileRead :
							s = reClassName.search(line)

							if s :
								fileWrite += "class " + classFileDestination + "(Simulation.Simulation) :\n"
							else :
								fileWrite += line

					with open(os.path.join(folderDestination, classFileDestination + ".py"), "w") as fileOut :
						fileOut.write(fileWrite)


if __name__ == "__main__" :
	parser = argparse.ArgumentParser()
	parser.add_argument('source', help = "Name of the source experiment.")
	parser.add_argument('destination', help = "Name of the destination experiment.")
	args = parser.parse_args()

	main(args)
