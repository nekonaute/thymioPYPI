import shutil

name_fic = "AllRobots.log"
fic = open(name_fic,"w")

date = "20170713_160648_pi3no0"

l = range(2,9)+[11]
list_fichier=[date+str(i)+"/MainController.log" if i!=11 else date[:-1]+str(i)+"/MainController.log" for i in l ]

for i in range(len(list_fichier)):
	fic.write("ROBOT "+str(l[i])+"\n")
	shutil.copyfileobj(open(list_fichier[i],'r'),fic)

fic.close()


