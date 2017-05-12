# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import math


"""
P_ANDROIDE UPMC 2017
Encadrant : Nicolas Bredeche

@author Tanguy SOTO
@author Parham SHAMS

Analyse des résultats de la simulation FollowLightGenOnline et FollowLightGen
"""


num_robot = [3,11]

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
	#plt.savefig('runOnRPI'+str(robot)+'-online.png')
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

plt.plot(x,data_leader,label="leader",color="red")	

plt.boxplot(data_gene)	
plt.plot(x,means,label="moyenne",color="green")

plt.title('')
plt.xlabel('generation')
plt.ylabel('fitness')
plt.xticks(x,x)
plt.legend(loc='best')
#plt.savefig('broadcast_leader-distributed.png')
plt.show()

# ============ courbe de fitness pour FollowLightGen avec neighbors et leader
	
num_robot = [3,5,7,8,11]

# on a les lignes
f = open("../log/LOG-expericences-2017_05_10/distributed/neighbors_leader.log","r")
s = f.readlines()

data_others = []
data_leader = []	

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

data_gene = []

for i in range(18):
	data_gene.append([])
	for j in range(len(data_others)):
		if j != num_robot.index(8):
			data_gene[i].append(data_others[j][i])

data_gene.reverse()
data_leader.reverse()

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

plt.boxplot(data_gene)	
plt.plot(x,data_leader,label="leader",color="red")
plt.plot(x,means,label="moyenne",color="green")

plt.title('')
plt.xlabel('generation')
plt.ylabel('fitness')
plt.legend(loc="best")
plt.xticks(x,x)
#plt.savefig('neighbors_no_leader-distributed.png')
plt.show()

# ============ courbe de fitness pour FollowLightGen avec neighbors et sans leader
	
num_robot = [3,5,7,8,11]

# on a les lignes
f = open("../log/LOG-expericences-2017_05_10/distributed/neighbors_no_leader.log","r")
s = f.readlines()

data_others = []

curr_data=[]

for i in range(len(s)):
	l = s[i].split(" ")
	
	if l[0]=="ROBOT":
		if len(curr_data)>0:
			data_others.append(curr_data)
		
		curr_data=[]
	elif len(l)>6 and l[6]=="ended":
		curr_data.append(min(0.5,float(l[7])))
		
data_others.append(curr_data)

data_gene = []

for i in range(26):
	data_gene.append([])
	for j in range(len(data_others)):
		data_gene[i].append(data_others[j][i])

data_gene.reverse()

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

plt.boxplot(data_gene)	
plt.plot(x,means,label="moyenne",color="green")

plt.title('')
plt.xlabel('generation')
plt.ylabel('fitness')
plt.legend(loc="best")
plt.xticks(x,x)
#plt.savefig('neighbors_no_leader-distributed.png')
plt.show()