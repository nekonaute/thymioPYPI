# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt


"""
STAGE UPMC ISIR 2017
Encadrant : Nicolas Bredeche

@author Parham SHAMS

Analyse des résultats de la simulation FollowLightGenBis
"""

save = True
num_robot = [3,11]
"""
# ============ courbe de fitness pour FollowLightGenOnline (typical run)

for robot in num_robot:
	# on a les lignes
	f = open("../log/LOG-expericences-2017_05_10/online/"+str(robot)+".log","r")
	s = f.readlines()
	
	data_champ = []
	data_challeng = []
	data = []
	nb_gen = 0
		
	for i in range(len(s)):
		
		l = s[i].split(" ")
		
		if len(l)>6 and l[5][:4] == "chal":
			l_next = s[i+1].split(" ")
			
			if not (len(l_next)>6 and l_next[5][:3]=="new"):
				data_challeng.append((float(l[6]),nb_gen+1))
				data.append((float(l[6]),nb_gen+1))
				nb_gen+=1
		elif len(l)>6 and l[5][:3]=="new":
			data_champ.append((float(l[7]),nb_gen+1))
			data.append((float(l[7]),nb_gen+1))
			nb_gen+=1
		elif len(l)>6 and l[5][:4]=="cham":
			data_champ.append((float(l[6]),nb_gen+1))
			data.append((float(l[6]),nb_gen+1))
			nb_gen+=1		
			
	x = [ i[1] for i in data]
	y = [ i[0] for i in data]
	#plt.plot(x,y,color="blue")		
		
	x = [ i[1] for i in data_champ]
	y = [ i[0] for i in data_champ]
	plt.scatter(x,y,color="red",label="nouveaux champions")
	plt.plot(x,y,color="red",label='meilleure fitness actuelle')
	
	x = [ i[1] for i in data_challeng]
	y = [ i[0] for i in data_challeng]
	plt.scatter(x,y,color="blue",label='challengers')
	
	plt.title('robot '+str(robot))
	plt.xlabel('generation')
	plt.ylabel('fitness')
	plt.xticks(range(0,nb_gen+1,5), range(0,nb_gen+1,5))
	plt.legend(loc='best')
	if save:
		plt.savefig('__runOnRPI'+str(robot)+'-online.png')
	plt.show()
	
# ============ courbe de fitness pour FollowLightGen avec broadcast et leader
	
num_robot = [3,5,7,8,11]

# on a les lignes
f = open("../log/LOG-expericences-2017_05_10/distributed/broadcast_leader.log","r")
s = f.readlines()

data_leader = []	
data_others = []

curr_data=[]

for i in range(len(s)):
	
	l = s[i].split(" ")
	
	if l[0]=="ROBOT":
		if len(curr_data)>0:
			data_others.append(curr_data)
		
		curr_data=[]
	elif len(l)>6 and l[6]=="ended":
		curr_data.append(float(l[7]))
		
data_others.append(curr_data)
data_leader = data_others[num_robot.index(8)]

#print data_others

data_gene = []

for i in range(3):
	data_gene.append([])
	for j in range(len(data_others)):
		if j != num_robot.index(8):
			data_gene[i].append(data_others[j][i])
			
#print data_gene

# moyennes
means = []
for l in data_gene:
	s=0
	for v in l:
		s+=v
	s/=len(l)
	means.append(s)

x = range(1,4)

#plt.plot(x,data_leader,label="leader",color="red")	

plt.boxplot(data_gene)	
plt.plot(x,means,label="moyenne",color="green")

plt.title('')
plt.xlabel('generation')
plt.ylabel('fitness')
plt.xticks(x,x)
plt.legend(loc='best')
if save:
	plt.savefig('__broadcast_leader-distributed.png')
plt.show()
"""
# ============ courbe de fitness pour FollowLightGenBis avec leader
"""
num_robot = [2,3,4,5,6,7,8,9,11]

# on a les lignes
f = open("XP1/AllRobots.log","r")
s = f.readlines()

data_others = []
data_leader = []	

curr_data=[]

new_random_gen=[]

for i in range(len(s)):
	l = s[i].split(" ")
	
	if l[0]=="ROBOT":
		if len(curr_data)>0:
			data_others.append(curr_data)
		ind=0
		curr_data=[]
	elif len(l)>6 and l[6]=="ended":
		curr_data.append(float(l[7]))	
		ind+=1
	elif len(l)>8 and l[8]=="NEW":
		new_random_gen.append(ind)
		
data_others.append(curr_data)
data_leader = data_others[num_robot.index(2)]

data_gene = []

for i in range(60):
	data_gene.append([])
	for j in range(len(data_others)):
		if j != num_robot.index(2):
			data_gene[i].append(data_others[j][i])

data_leader = data_leader[:60]

# moyennes
means = []
for l in data_gene:
	s=0
	for v in l:
		s+=v
	s/=len(l)
	means.append(s)

data_gene = data_gene[:]

x = range(1,len(data_gene)+1)
print len(data_leader)
print len(x)

plt.boxplot(data_gene)	
#plt.plot(x,data_leader,label="leader",color="red")
plt.plot(x,means,label="moyenne",color="red")


#for i in range(len(data_gene)):
#	plt.scatter([i+1]*len(data_gene[i]),data_gene[i],color="black")


plt.title('')
plt.xlabel('generation')
plt.ylabel('fitness')
plt.legend(loc="best")
#plt.xticks(x,x)
list_color = ['red' if i in new_random_gen else 'black' for i in range(len(x))]
plt.xticks(x, rotation=90)
for ticklabel, tickcolor in zip(plt.gca().get_xticklabels(), list_color):
	ticklabel.set_color(tickcolor)
if save:
	plt.savefig('__neighbors_leader-distributed.png')
plt.show()

# ============ courbe de fitness pour FollowLightGenBis sans leader
"""

#num_robot = [2,3,4,5,6,7,8,9,11]

data_gene_fin = []

# on a les lignes
for z in xrange(1,3):
	name_fic = "min/XP"+str(z)+"_100gen"
	f = open(name_fic+"/AllRobots.log","r")
	s = f.readlines()

	data_others = []

	curr_data=[]

	new_random_gen =[]

	for i in range(len(s)):
		l = s[i].split(" ")
	
		if l[0]=="ROBOT":
			if len(curr_data)>0:
				data_others.append(curr_data)
				#print curr_data
			ind=0		
			curr_data=[]
		elif len(l)>6 and l[6]=="ended":
			#print str(float(l[7]))
			#curr_data.append(min(0.5,float(l[7])))
			curr_data.append(float(l[7]))
			ind+=1
		elif len(l)>8 and l[8]=="NEW":
			new_random_gen.append(ind)
		
	data_others.append(curr_data)

	data_gene = []

	for i in range(len(curr_data)): #nb generations
		data_gene.append([])
		for j in range(len(data_others)):
			data_gene[i].append(data_others[j][i])

	if z==1: # on le fait qu'une seule fois	
		for i in range(len(curr_data)): #nb generations
			data_gene_fin.append([])
		#data_gene_fin = [[] for zzz in xrange(len(curr_data))]

	# moyennes
	means = []
	maxes = []
	maxEver = []
	for l in range(len(data_gene)):
		s=0
		max_gen=max(data_gene[l])
		if len(maxEver)>0:
			maxx=max(maxEver[-1],max_gen)
		else:
			maxx=max_gen
		maxes.append(max_gen)
		maxEver.append(maxx)
		for v in data_gene[l]:
			s+=v
		s/=len(data_gene[l])
		means.append(s)
		#print(str(l) + str(len(data_gene_fin)))
		data_gene_fin[l].append(max_gen)

	data_gene = data_gene[:]

	x = range(1,len(data_gene)+1)

	#plt.boxplot(data_gene)	
	plt.figure()
	plt.plot(x,means,label="mean",color="red")
	plt.plot(x,maxes,label="max",color="green")
	plt.plot(x,maxEver,label="maxEver",color="purple")

	plt.title('')
	plt.xlabel('generation')
	plt.ylabel('fitness')
	plt.legend(loc="best")
	"""
	list_color = ['red' if i in new_random_gen else 'black' for i in range(len(x))]
	#print list_color
	#print new_random_gen
	plt.xticks(x, rotation=90)
	for ticklabel, tickcolor in zip(plt.gca().get_xticklabels(), list_color):
		ticklabel.set_color(tickcolor)
	"""

	plt.xticks(range(0,len(data_gene)+1,5))
	if save:
		plt.savefig(name_fic+'/courbe'+str(z)+'.png')
	#plt.show()
	
	f.close()
	
means = []
maxes = []
maxEver = []
for l in range(len(data_gene_fin)):
	s=0
	max_gen=max(data_gene_fin[l])
	if len(maxEver)>0:
		maxx=max(maxEver[-1],max_gen)
	else:
		maxx=max_gen
	maxes.append(max_gen)
	maxEver.append(maxx)
	for v in data_gene_fin[l]:
		s+=v
	s/=len(data_gene_fin[l])
	means.append(s)
	data_gene_fin[l].append(max_gen)

data_gene_fin = data_gene_fin[:]

x = range(1,len(data_gene_fin)+1)

#plt.boxplot(data_gene_fin)	
plt.figure()
plt.plot(x,means,label="mean",color="red")
plt.plot(x,maxes,label="max",color="green")
plt.plot(x,maxEver,label="maxEver",color="purple")

plt.title('')
plt.xlabel('generation')
plt.ylabel('fitness')
plt.legend(loc="best")
"""
list_color = ['red' if i in new_random_gen else 'black' for i in range(len(x))]
#print list_color
#print new_random_gen
plt.xticks(x, rotation=90)
for ticklabel, tickcolor in zip(plt.gca().get_xticklabels(), list_color):
	ticklabel.set_color(tickcolor)
"""

plt.xticks(range(0,len(data_gene_fin)+1,5))
if save:
	plt.savefig(name_fic+'/Multirun.png')
#plt.show()
