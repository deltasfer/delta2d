






import os
import random
from src import utils
import src.tile_utils as tut
import noise as ns
import perlin.perlin as p



DIC_OF_RULES = { 'water':[ [2], -1 ],
                 'dirt': [ [3,4,7,11,14,17,20,21,23,25,26,27,29,31] , 1,[32,33,34]+[48,49]+[35,36]+[50,51]],
                 'tree': [ [32,33,34] , -1 ],
                 'rock': [ [48,49] , -1 ],
                 'stripped wood': [ [51] , -1 ],
                 'wooden palet': [ [50] , 0, [2] ],
                 'stick': [ [35,36] , -1 ],
                 'empty':[ [0], 2 ]
                 }

## EXEMPLE : 'nom' : [  [differents nombres correspondants au skin de la tile] , valeur de surplombage , rien si valeur de surplombage == -1 ou 2 , tableu de surplombage sinon  ]
## valeur de surplombage:
#           si vaut -1: aucune tile ne sera acceptée par dessus celle là (exemple : eau)
#           si vaut 2: toutes les tiles sont acceptée par dessus (exemple: dirt)
#           si vaut 0: tableau de surplombage est une blacklist
#           si vaut 1: tableau de surplombage est une whitelist
## tableau de surplombage
#           si whitelist: c'est un tableau de toutes les tiles qui sont acceptée par dessus celle là
#           si blacklist: c'est un tableau de toutes les tiles qui sont refusées par dessus celle là (toutes les autres sont acceptées)

WALKTRGH = {'none':[0],
            'normal':[34,48,35,36,51],
            'swimming':[2],
            'being_a_ghost':[3,4,7,11,14,17,20,21,23,25,26,27,29,31,50]
            }

WALKON =   { 'walking':[3,4,7,11,14,17,20,21,23,25,26,27,29,31,50],
             'swimming':[2],
             'flying':[0]
            }

## WALKTRGH WALKON
#       chaque case est affectée à une compétence nécessaire pour marcher au travers et/ou par dessus
#       le perso doit avoir cette compétence (désignée par la specie et ses propres compétences) pour
#       marcher au travers et/ou par dessus



DIC_OF_STYLES = { 'water': 'ground' ,
                 'dirt': 'ground' ,
                 'tree': 'plant' ,
                 'rock': 'plant' ,
                 'stripped wood': 'plant',
                 'stick': 'plant',
                 'wooden palet': 'build',
                 'empty': 'empty'
                 }

REVERSE_DIC = {}
for name in DIC_OF_RULES:
    for x in DIC_OF_RULES[name][0]:
        if DIC_OF_RULES[name][1] == 2 or DIC_OF_RULES[name][1] == -1:
            REVERSE_DIC[x] = [ name , DIC_OF_RULES[name][1] ]
        else:
            REVERSE_DIC[x] = [ name , DIC_OF_RULES[name][1], DIC_OF_RULES[name][2] ]

REVERSE_STYLES = {}
for name in DIC_OF_STYLES:
    if DIC_OF_STYLES[name] not in REVERSE_STYLES:
        REVERSE_STYLES[DIC_OF_STYLES[name]] = [name]
    else:
        REVERSE_STYLES[DIC_OF_STYLES[name]].append(name)

ALL_GROUNDS = []
for name in REVERSE_STYLES['ground']:
    ALL_GROUNDS += DIC_OF_RULES[name][0]

#print('all_ground',ALL_GROUNDS)

ZONES = {'forest':[1,3,4,5,6,7],
        'jungle':[1,3,4,5,6,7],
        'river':[1,3,4,5,6,7],
        'plain':[1]+[i for i in range(3,9)]+[i for i in range(21,32)],
        'mountain':[i for i in range(14,22)],
        'ocean':[2],
        'desert':[25,26,27,10,11,12]
        }

ASSETS = ['forest','stone','palet']

saved_terrains = {}

frequency = 5*tut.SIZE_BIOM[0] , 5*tut.SIZE_BIOM[1]
freq = {}
freq['forest'] = tut.SIZE_BIOM[0] , tut.SIZE_BIOM[1]
freq['stone'] = tut.SIZE_BIOM[0] //2 , tut.SIZE_BIOM[1] //2
freq['palet'] = tut.SIZE_BIOM[0] //2 , tut.SIZE_BIOM[1] //2



# generator de terrains diverses et variés

# Fonction globale creation map

def createMap(size_terrain,size_biom,depth,style=0):

    w,h = size_terrain[0]*size_biom[0],size_terrain[1]*size_biom[1]

    tab_map , tab_land = [],[]

    nb_zones = ((w*h)//8000)+1
    print('nb_zones',nb_zones)

    if style == 0:
        global saved_terrains

        saved_terrains = {}
        color_list = DIC_OF_RULES['dirt'][0]
        for i in color_list:
            saved_terrains[i] = createPlatform(tut.SIZE_BIOM[0],tut.SIZE_BIOM[1],i,depth)

        all_bioms = generate_Biom_colors(*size_terrain)

        for biom in all_bioms:
            print(biom)
        #print(all_bioms)

        w,h = size_terrain

        for j in range(h):
            rangey = []
            rangeymap = []
            for i in range(w):
                choice = all_bioms[j][i]
                biom = modifyPlatform(saved_terrains[choice],(size_biom[0]-1),(size_biom[1]-1))
                rangey.append(biom)
                rangeymap.append(choice)

            tab_land.append(rangey)
            tab_map.append(rangeymap)
    elif style == 1:

        """"""

        print('creating first terrain with noise')
        terrain = create_terrain(nb_zones,size_terrain,size_biom,depth)
        #terrain = modifyPlatform(terrain,w-1,h-1)

        """"""
        terrain[1] = createZone(terrain[1],'stone',w,h)
        """"""
        terrain[1] = createZone(terrain[1],'palet',w,h)
        """"""
        terrain[1] = createZone(terrain[1],'forest',w,h)
        """"""

        terrain = verify(terrain)
        """"""
        print('splitting terrain')
        tab_map , tab_land = from_ter_to_bioms(terrain,size_terrain,size_biom,depth)

        """print('done')
        for y in tab_land[0][0][0]:
            print(y)"""

    return tab_map , tab_land

# Verifieur

def verify(plat):

    depth = len(plat)
    for lvl in range(depth):
        for y in range(len(plat[lvl])):
            for x in range(len(plat[lvl][y])):
                if REVERSE_DIC[plat[lvl][y][x]][1] == -1:
                    for i in range(lvl+1,depth):
                        plat[i][y][x] = 0
                else:
                    if REVERSE_DIC[plat[lvl][y][x]][1] == 0:
                        for i in range(lvl+1,depth):
                            if plat[i][y][x] in REVERSE_DIC[plat[lvl][y][x]][2]:
                                plat[i][y][x] = 0

                    elif REVERSE_DIC[plat[lvl][y][x]][1] == 1:
                        for i in range(lvl+1,depth):
                            if plat[i][y][x] not in REVERSE_DIC[plat[lvl][y][x]][2]:
                                plat[i][y][x] = 0
    return plat


# Fonctions tout-en-un

def createPlatform(w,h,key=1,depth=tut.DEPTH_BIOM):
    # Fonction appelée dans la section load() de l'appli
    # effectuée une seule fois, cela va permettre de sauvegarder la platforme originale

    platform = [ createBlank(0,w,h) for _ in range(depth) ]
    platform[0] = createBlank(key,w,h)
    #platform = addBlank(platform,5,1,1,1,1)
    #print(platform)

    #print(platform)

    return platform

def modifyPlatform(plat,w,h):
    # Fonction appelée dans events()
    # effectuée à chaque fois qu'on appuie sur la touche declencheur
    # permet de recreer une platforme ajoutée à celle originale

    """print(platform)

    for i in range(len(platform)):
        print('lvl',i)
        for y in platform[i]:
            print('     y: ',y)"""

    platform = utils.mycopy(plat)

    platform[1] = addMultForest(platform[1],random.choice(DIC_OF_RULES['tree'][0]))


    platform[0] = addMultForest(platform[0],random.choice(DIC_OF_RULES['water'][0]))
    #platform[0] = addRiver(platform[0],random.choice(DIC_OF_RULES['water'][0]),0,h//2,w,h//2)



    platform = verify(platform)

    return platform

def createZone(savedter,style,w,h,x=0,y=0):

    """
    DOCUMENTATION CREATION DES BIOMES:

    savedter (list) : le terrain de base, qui ne sera pas modifié
    #key (int) : la couleur de dirt considérée
    x,y (int,int) : position du biom généré intégré direct au terrain final
    w,h (int,int) : dimension du biom genéré
    style (str) : decrit le mode de creation du biom

    LISTE DES STYLES:

    forest
    ocean
    mountain
    plain
    river
    jungle
    desert

    FORMAT DU RETOUR:

    terrain (donc [ levels [ casey [ casex ] ] ] )
    avec:
    1 pour de la dirt
    0 pour du vide
    2,3,4.. pour des charactères spéciaux (eau,pierre,mineraux..) #voir DIC_ZONES_CREATION

    """

    tab = utils.mycopy(savedter)

    if style == 'forest':

        #freq = w , h
        keys = [0,0,-1]

        noise = get_diff_noised_list(w,h,len(keys),freq[style],2,3)
        """for n in noise:
            print(n)"""
        for j in range(len(noise)):
            for i in range(len(noise[j])):
                if keys[noise[j][i]] != 0:
                    #print(keys[noise[j][i]],tab[j+y][i+x])
                    try:
                        tab[j+y][i+x] = keys[noise[j][i]]
                        #print(i,j,'good')
                    except:
                        a=0
        ##print('coloring tree')

        v,w=0,0
        for j in range(-y,len(noise)-y):
            for i in range(-x,len(noise[j])-x):
                if tab[j+y][i+x] == -1:
                    #print('lets go pour la',w+1,'e fois','key=',DIC_OF_RULES['tree'][0][v])
                    color(tab,(i,j),DIC_OF_RULES['tree'][0][v])
                    v+=1
                    w+=1
                    if v >= len(DIC_OF_RULES['tree'][0]):
                        v=0

                if tab[j+y][i+x] in DIC_OF_RULES['tree'][0]:
                    if random.choice([False]*20+[True]):
                        tab[j+y][i+x] = random.choice(DIC_OF_RULES['stick'][0])

    if style == 'stone':

        #freq = w , h
        keys = [0,0,0,-1]

        noise = get_diff_noised_list(w,h,len(keys),freq[style],2,3)

        for j in range(len(noise)):
            for i in range(len(noise[j])):
                if keys[noise[j][i]] != 0:
                    try:
                        tab[j+y][i+x] = keys[noise[j][i]]
                    except:
                        a=0
        #print('coloring rock')

        v,w=0,0
        for j in range(-y,len(noise)-y):
            for i in range(-x,len(noise[j])-x):
                if tab[j+y][i+x] == -1:
                    #print('lets go pour la',w+1,'e fois','key=',DIC_OF_RULES['rock'][0][v])
                    color(tab,(i,j),DIC_OF_RULES['rock'][0][v])
                    v+=1
                    w+=1
                    if v >= len(DIC_OF_RULES['rock'][0]):
                        v=0
                if tab[j+y][i+x] == 49:
                    new_pos = [(i+x+1,j+y),(i+x,j+y-1),(i+x-1,j+y),(i+x,j+y+1),(i+x+1,j+y+1),(i+x+1,j+y-1),(i+x-1,j+y-1),(i+x-1,j+y+1)]

                    for k in range(len(new_pos)):
                        x2,y2 = new_pos[k]
                        if y2 >=0 and y2 < len(tab) and x2 >= 0 and x2 < len(tab[y2]):
                            if tab[y2][x2] != 49 and tab[y2][x2] != 48 :
                                tab[y2][x2] = 48

    if style == 'palet':

        #freq = w , h
        keys = [0,0,0,0,-1]

        noise = get_diff_noised_list(w,h,len(keys),freq[style],2,3)

        for j in range(len(noise)):
            for i in range(len(noise[j])):
                if keys[noise[j][i]] != 0:
                    try:
                        tab[j+y][i+x] = keys[noise[j][i]]
                    except:
                        a=0
        #print('coloring palet')

        v,w=0,0
        for j in range(-y,len(noise)-y):
            for i in range(-x,len(noise[j])-x):
                if tab[j+y][i+x] == -1:
                    #print('lets go pour la',w+1,'e fois','key=',DIC_OF_RULES['wooden palet'][0][v])
                    color(tab,(i,j),DIC_OF_RULES['wooden palet'][0][v])
                    v+=1
                    w+=1
                    if v >= len(DIC_OF_RULES['wooden palet'][0]):
                        v=0
                if tab[j+y][i+x] in DIC_OF_RULES['wooden palet'][0] and random.choice([False,False,False,True]) :
                    new_pos = [(i+x+1,j+y),(i+x,j+y-1),(i+x-1,j+y),(i+x,j+y+1),(i+x+1,j+y+1),(i+x+1,j+y-1),(i+x-1,j+y-1),(i+x-1,j+y+1)]
                    for k in range(len(new_pos)):
                        x2,y2 = new_pos[k]
                        if y2 >=0 and y2 < len(tab) and x2 >= 0 and x2 < len(tab[y2]):
                            if tab[y2][x2] not in DIC_OF_RULES['wooden palet'][0]+DIC_OF_RULES['stripped wood'][0]:
                                tab[y2][x2] = random.choice(DIC_OF_RULES['stripped wood'][0])



    return tab


# Fonctions de creation de map

def generate_Biom_colors(w,h):

    bioms = [ [0 for _ in range(w)] for _ in range(h)]

    colored_bioms = {}
    for i in range(random.randint(2,5)):
        biom = random.randint(0,w-1),random.randint(0,h-1)
        colored_bioms[biom] = random.choice(DIC_OF_RULES['dirt'][0])
        bioms[biom[1]][biom[0]] = colored_bioms[biom]

    allColored = False
    while allColored != True:

        nocol = 0
        for j in range(h):
            for i in range(w):
                if bioms[j][i] != 0:

                    for y in [-1,0,1]:
                        for x in [-1,0,1]:
                            if (x,y) != (0,0):
                                try:
                                    if bioms[j+y][i+x] == 0:
                                        index = DIC_OF_RULES['dirt'][0].index(bioms[j][i])+random.randint(-2,2)
                                        if index <= 0:
                                            index += len(DIC_OF_RULES['dirt'][0])
                                        elif index > len(DIC_OF_RULES['dirt'][0]):
                                            index -= len(DIC_OF_RULES['dirt'][0])
                                        bioms[j+y][i+x] = DIC_OF_RULES['dirt'][0][index]
                                except :
                                    a=0
                else:
                    nocol += 1
        allColored = (nocol == 0)
    return bioms

def from_ter_to_bioms(terrain,size_ter=tut.SIZE_TERRAIN,size_biom=tut.SIZE_BIOM,depth=tut.DEPTH_BIOM):

    bioms = []
    map = []
    for j in range(size_ter[1]):
        rangej = []
        mapj = []
        for i in range(size_ter[0]):
            rangei = []
            for lvl in range(depth):
                rangel = []
                for y in range(size_biom[1]):
                    rangey = []
                    for x in range(size_biom[0]):
                        rangey.append( terrain[lvl][ j*size_biom[1] + y ][ i*size_biom[0] + x ] )
                    rangel.append(rangey)
                rangei.append(rangel)
            mapj.append(get_map(rangei))
            rangej.append(rangei)
            #print('biom',i,j,'done')
        map.append(mapj)
        bioms.append(rangej)
    return map,bioms

def get_map(biom):

    occur = {}
    for l in range(len(biom)):
        for y in range(len(biom[l])):
            for x in range(len(biom[l][y])):
                if DIC_OF_STYLES[REVERSE_DIC[biom[l][y][x]][0]] == 'ground':
                    try:
                        occur[biom[l][y][x]] += 1
                    except:
                        occur[biom[l][y][x]] = 1
    maxkey = [0,0]
    for key in occur:
        if occur[key] >= maxkey[1]:
            maxkey = [key,occur[key]]
    return maxkey[0]

def create_terrain(nb_zones,size_ter=tut.SIZE_TERRAIN,size_biom=tut.SIZE_BIOM,depth=tut.DEPTH_BIOM):

    """"""
    w,h = size_ter[0]*size_biom[0] , size_ter[1]*size_biom[1]
    terrain = [ [ [0 for k in range(w)] for q in range(h) ] for _ in range(depth) ]

    #noise = [ [0 for k in range(w)] for q in range(h) ]

    all_grounds = []
    for name in REVERSE_STYLES['ground']:
        all_grounds += DIC_OF_RULES[name][0]

    grounds = []
    if len(all_grounds) > nb_zones:
        for i in range(nb_zones):
            key = random.choice(all_grounds)
            while key in grounds:
                key = random.choice(all_grounds)
            grounds.append(key)
    else:
        grounds = all_grounds
    print('grounds :',grounds)

    """"""

    terrain[0] = get_diff_noised_list(w,h,1,style=2)
    """"""
    #aff(terrain[0])
    #os.system('pause')
    #print('coloring terrain')

    v,w=0,0
    for j in range(len(terrain[0])):
        for i in range(len(terrain[0][j])):
            if terrain[0][j][i] == -1:
                #print('lets go pour la',w+1,'e fois','key=',grounds[v])
                color(terrain[0],(i,j),grounds[v])
                v+=1
                w+=1
                if v >= len(grounds):
                    v=0
            elif terrain[0][j][i] == 0:
                terrain[0][j][i] = 2

    return terrain

    #zones = [ random.choice(all_bioms) for _ in range(nb_zones) ]


# noise

def get_noised_list(w,h,nb):

    ter = [ [0 for _ in range(w)] for _ in range(h)]
    random.seed()
    z=random.random()
    octaves = random.random()
    freq = 16.0 * octaves
    for y in range(h):
        for x in range(w):
            #ter[y][x] = ns.pnoise2(x/freq, y / freq, 1)
            ter[y][x] = int(((ns.pnoise3(x/freq, y / freq,0.1, repeatx=1024, repeaty=1024, repeatz=1024)+1)/2) // (1/nb) )
            if ter[y][x] == nb:
                ter[y][x] = nb-1
            """if ter[y][x]>=1:
                ter[y][x]=1
            else:
                ter[y][x]=0"""
    """for y in ter:
        print(y)"""
    return ter

def get_diff_noised_list(w,h,nb,f=frequency,oct=4,style=1):

    tab = []

    manager = p.PerlinNoiseFactory(2,oct)

    for j in range(h):
        tabj = []
        u = []
        for i in range(w):
            noise = manager(float(i/f[0]),float(j/f[1]))
            u.append(utils.truncate(noise,3))

            if style == 1:
                tabj.append( int((noise // (1/nb) ) ))

            elif style == 2:

                if abs(noise) < 0.01*nb:
                    noise = 0
                else:
                    noise = -1
                """mid = nb//2
                noise2 =  int(((noise+1)/2) // (1/nb) )
                #print(mid,noise2)
                if noise2 != mid:
                    noise2 = -1
                else:
                    noise2 = 0"""
                tabj.append(noise)

            elif style == 3:
                tabj.append( int(((noise+1)/2) // (1/nb) ) )

        tab.append(tabj)
        #print(u)
    """for y in tab:
        print(y)"""
    return tab


def is_full(ter,pos,key,old=-1,style=1):

    x,y = pos
    if style==1:
        new_pos = [(x+1,y),(x,y-1),(x-1,y),(x,y+1)]
    else:
        new_pos = [(x+1,y),(x,y-1),(x-1,y),(x,y+1),(x+1,y+1),(x+1,y-1),(x-1,y-1),(x-1,y+1)]

    fulled = True
    #keys = [0,-2,key]

    for i in range(len(new_pos)):
        x,y = new_pos[i]
        if y >=0 and y < len(ter) and x >= 0 and x < len(ter[y]):
            if ter[y][x] == old:
                #if not ter[y][x] in keys:
                return False
    return True

def color(ter,pos,key,old=-1,style=1):

    """

    JE PENSE QU'ON PEUT AMELIORER CETTE FONCTION

    """

    x,y = pos
    tab = [(x,y)]
    ter[y][x] = -2

    good = False

    while not good:
        #print(x,y)
        #aff(ter)

        if style==1:
            new_pos = [(x+1,y),(x,y-1),(x-1,y),(x,y+1),(x,y)]
        else:
            new_pos = [(x+1,y),(x,y-1),(x-1,y),(x,y+1),(x+1,y+1),(x+1,y-1),(x-1,y-1),(x-1,y+1),(x,y)]

        added = False
        for i in range(len(new_pos)):
            x,y = new_pos[i]
            if y >=0 and y < len(ter) and x >= 0 and x < len(ter[y]):
                if ter[y][x] == old and not added:
                    ter[y][x] = -2
                    tab.append(new_pos[i])
                    added = True
                if ter[y][x] == -2 and is_full(ter,new_pos[i],key,old):
                    ter[y][x] = key
                    if (x,y) in tab:
                        tab.remove((x,y))

        try:
            x,y = tab[-1]
        except:
            good=True

# Fonctions premieres

def createBlank(key,weight,height):
    terrain = []

    for i in range(height):
        line = []
        for j in range(weight):
            line.append(key)
        terrain.append(line)
    #print(terrain)

    return terrain

def addBlank(savedter,key,weight,height,x,y):

    terrain = utils.mycopy(savedter)

    for i in range(len(terrain)):
        for j in range(len(terrain[0])):
            if j>=x and  j<x+weight and i>=y and i<y+height:
                terrain[i][j] = key
    return terrain

def addForest(savedter,key,w,h,x,y,dt=random.randint(2,4),dtlinear=2):
    # dt determine le nombre de rectangles de foret créé
    # dtlinear determine la facon dont sera créée la foret :
    #       plus dtlinear est petit, plus les rectangles seront linéaires

    #terrain = addBlank(terrain,0,w,h,x,y)

    terrain = utils.mycopy(savedter)

    for k in range(dt):
        x_forest = random.randint(x,x+w-1-dtlinear)
        y_forest = random.randint(y,y+h-1-dtlinear)
        #terrain = addBlank(terrain,9,w-(x_forest-x),h-(y_forest-y),x_forest,y_forest)

        w_forest = random.randint(1+dtlinear,w-(x_forest-x))
        h_forest = random.randint(1+dtlinear,h-(y_forest-y))

        terrain = addBlank(terrain,key,w_forest,h_forest,x_forest,y_forest)

    return terrain

def addMultForest(savedter,key):

    #print(savedter)
    terrain = utils.mycopy(savedter)

    #for y in terrain:
    #    print('     y: ',y)

    w_blank = len(terrain[0])
    h_blank = len(terrain)

    if w_blank//10 > 2:
        delta_w = w_blank//10
    elif w_blank//10 == 0:
        return terrain
    else:
        delta_w = 3

    if h_blank//10 > 2:
        delta_h = h_blank//10
    elif h_blank//10 == 0:
        return terrain
    else:
        delta_h = 3


    nb_forest = random.randint(1,w_blank//10 + h_blank//10)

    #print(w_blank,h_blank,nb_forest)

    for i in range(nb_forest):
        x=random.randint(0,w_blank-delta_w)
        y=random.randint(0,h_blank-delta_h)

        w = random.randint(delta_w,w_blank-x)
        h = random.randint(delta_h,h_blank-y)
        #print(x,y,w,h)

        terrain = addForest(terrain,key,w,h,x,y)

    return terrain

def addRiver(savedter,key,x_dep,y_dep,x_ar,y_ar):


    terrain = utils.mycopy(savedter)

    #terrain = addBlank(terrain,5,x_ar-x_dep+1,y_ar-y_dep+1,x_dep,y_dep)

    points = [[x_dep,y_dep]]
    nbx,nby = (x_ar-x_dep)//10-1 , (y_ar-y_dep)//20-1
    if nbx < 0:
        nbx = 0
    if nby < 0:
        nby = 0
    x_dabord = nbx >= nby
    ix,iy = 0,0

    #print(x_dabord,nbx,nby)

    while not ( nbx == 0 and nby == 0 ):
        if x_dabord:
            if nbx > 0:
                y = random.randint(-5,5)
                points.append([x_dep+(ix+1)*10,(y_ar+y_dep)//2+y])
                ix+=1
                nbx-=1
                #print(nbx,nby,points)
            x_dabord = False
        else:
            if nby > 0:
                x = random.randint(-5,5)
                points.append([y_dep+(iy+1)*20,(x_ar+x_dep)//2+x])
                iy+=1
                nby-=1
                #print(nbx,nby,points)
            x_dabord = True
    """
    for i in range((x_ar-x_dep)//10-1):
        y = random.randint(-5,5)
        points.append([x_dep+(i+1)*10,(y_ar-y_dep//2)+y])
        """
    points.append([x_ar,y_ar])

    #print(points)

    path = []

    for i in range(len(points)-1):
        path += drawPath(points[i][0],points[i][1],points[i+1][0],points[i+1][1])

    for i in range(len(terrain)):
        for j in range(len(terrain[0])):
            if [j,i] in path:
                terrain[i][j] = key

    return terrain

def drawPath(xd,yd,xa,ya):
    path = [[xd,yd]]
    nb_x,nb_y = xa - xd, ya - yd

    x,y = xd,yd

    while x != xa or y != ya:
        if nb_x !=0 and nb_y !=0:
            x_ou_y = random.randint(0,1)
            if x_ou_y:
                if nb_x > 0:
                    x+=1
                    nb_x -= 1
                else:
                    x-=1
                    nb_x += 1
            else:
                if nb_y >0:
                    y+=1
                    nb_y -= 1
                else:
                    y-=1
                    nb_y += 1
        elif nb_x ==0:
            if nb_y >0:
                y+=1
                nb_y -= 1
            else:
                y-=1
                nb_y += 1
        else:
            if nb_x > 0:
                x+=1
                nb_x -= 1
            else:
                x-=1
                nb_x += 1
        path.append([x,y])

    return path


## UTILS


def aff(ter):

    for y in ter:
        to_p = ''
        for w in y:

            if w == 0:
                x = ' '
            else:
                x = '*'

            """if type(x) != type(' '):
                a = str(x)
            else:
                a = x
            b = ''
            for i in range(2-len(a)):
                b+=' '"""
            to_p+=(x)
        print(to_p)






