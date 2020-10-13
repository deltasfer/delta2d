"""""
programme recuperation de fichiers sources
"""""

# pour le projet delta2d ça marche pour les saved >= alpha 1.0338

version = 3
autosav = True

import os

#path2 = 'Z:/DESKTOP/Coder/Projets/delta2D/tests/saved_alpha_1_1192'

### FONCTIONS

def detect_savd():

	files = os.listdir()
	saves = []
	for file in files:
		if file[-5:] == '.savd':
			saves.append(file)

	return saves

def chose_savd(saves):

	print('quel_fichier souhaitez vous recup ?\n')
	for i in range(len(saves)):
		sav = saves[i][6:-5]
		print('  ',i,' - ',sav)
	return saves[int(input())]

def get(path2):


	print('\n\nrecuperation des sources du fichier de sauvegarde \''+path2+'\'..\n\n')

	## initialisation rapide verif du str path2

	currentpath = path2.split('\\')[-1]
	currentpath = currentpath.split('/')[-1]
	currentpath = path2[:(len(path2)-len(currentpath))]

	## lecture du fichier de sauvegarde

	all =[]
	with open(path2,'r') as f:
	    all = f.readlines()

	## détermination des fichiers à extraire

	files = {}
	titles = [0]
	file = []
	for line in all:
	    if '_newfile_ :' in line and line[-4:] == '.py\n':
	        name = line[len('_newfile_ :'):]
	        names = name.split('\\')
	        names2 = []

	        for nam in names:
	            for naam in nam.split('/'):
	                names2.append(naam)
	                name = ('/').join(names2[-2:])

	        files[titles[-1]] = file
	        titles.append(name[:-1])
	        file = []
	    else:
	        file.append(line)

	files[titles[-1]] = file

	## init rapide pour l'extraction

	path3 = 'getback_'+path2[:-5]+'/'
	path4 = currentpath+path3

	## creation du dossier principal dans lequel le code sera extrait

	if (path4 and path4[:-1]) not in os.listdir():
		os.makedirs(path4)

	## creation du fichier 'version' dans le cas où une autosav à été mise en place sur le code (voir le projet delta2d pour des questions)
	## (l'autosav est mise en place dans le fichier utils.py normalement)

	if autosav and 'saved_' == path2[:6]:
		if 'autosav' not in os.listdir(path4):
			os.mkdir(path4+'autosav')
		with open(path4+'autosav/version.txt','w') as f:
			f.write(path2[6:-5])
		if 'version' in os.listdir(path4+'autosav'):
			os.remove(path4+'autosav/version')
		os.rename(path4+'autosav/version.txt',path4+'autosav/version')
		print(path4+'autosav/version')

	## extraction des fichiers de code dans le dossier et les sous dossiers correspondants

	for name in files:
		print(str(path3)+str(name))
		if name != 0:
			try:
				with open(path4+name,'w') as f:
					for line in files[name]:
						f.write(line)
			except :
				file = name.split('/')[0]
				os.makedirs(path4+file)
				with open(path4+name,'w') as f:
					for line in files[name]:
						f.write(line)


### MAIN

print('outil de recuperation de sauvegarde du code')
print('version '+str(version)+'\n\n')

saves = detect_savd()
sav_chosed = chose_savd(saves)

# autosav = input('Une autosav est-elle en place sur ce fichier de recup ? (0 non/1 oui)\n')
get(sav_chosed)

input('Appuyez sur ENTER pour continuer...')
#print(files)
