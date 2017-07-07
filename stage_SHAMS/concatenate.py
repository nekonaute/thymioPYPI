import shutil

name_fic = "AllRobots.log"
fic = open(name_fic,"w")

for i in list_fichier:
	shutil.copyfileobj(open(i,'r'),fic)

fic.close()


