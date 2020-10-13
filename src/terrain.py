





import pyglet,random
from src import utils
import src.tile_utils as tut
import src.TerrainCreator as ter

class Biom():

    def __init__(self, ground):

        self.ground = []
        #print(len(ground))
        for i in range(len(ground)):
            self.ground.append(ground[i])

    def set_ground(self,lvl,tab):

        self.ground[lvl] = tab

    def get_case(self,bcx_pos,lvl=None):

        #print('case demandée :')
        if lvl == None:
            lvl = bcx_pos.l
        b,c,x = bcx_pos.bcx()
        return self.ground[lvl][c[1]][c[0]]

    def set_case(self,bcx_pos,val):

        lvl = bcx_pos.l
        b,c,x = bcx_pos.bcx()
        self.ground[lvl][c[1]][c[0]] = val

class TerManager():

    def __init__(self,size,size_biom,name):

        self.name = name
        self.Bioms = []
        self.map = []

        if name != None:

            biom=emptyBiom(size_biom)

            for i in range(size[1]):
                tab = []
                keys = []
                for j in range(size[0]):
                    tab.append(biom)
                    keys.append(0)
                self.Bioms.append(tab)
                self.map.append(keys)

    def set_Biom(self,x,y,biom,key):
        self.Bioms[y][x] = biom
        self.map[y][x] = key

    def get_case(self,bcx_pos,lvl=None):
        b,c,x = bcx_pos.bcx()
        if tut.biom_in_terrain(b):
            return self.Bioms[b[1]][b[0]].get_case(bcx_pos,lvl)
        else:
            return 0

    def set_case(self,bcx_pos,val):
        b,c,x = bcx_pos.bcx()
        self.Bioms[b[1]][b[0]].set_case(bcx_pos,val)

    def verify(self,bcx_pos,key):

        #b,c,x = bcx_pos.bcx() ## par dessus cette case on veut poser key

        if bcx_pos.l == -1:
            return True
        elif bcx_pos.l >= tut.DEPTH_BIOM -1:
            return False
        else:
            oldkey = self.get_case(bcx_pos)

            if ter.REVERSE_DIC[oldkey][1] == 2:
                return True
            elif ter.REVERSE_DIC[oldkey][1] == -1:
                return False
            elif ter.REVERSE_DIC[oldkey][1] == 1:
                return key in ter.REVERSE_DIC[oldkey][2]
            elif ter.REVERSE_DIC[oldkey][1] == 0:
                return not (key in ter.REVERSE_DIC[oldkey][2])

    def get_random_case(self,lvl=utils.choice([i for i in range(tut.DEPTH_BIOM)])):
        b = [random.randint(0,tut.SIZE_TERRAIN[0]-1),random.randint(0,tut.SIZE_TERRAIN[1]-1)]
        c = [random.randint(0,tut.SIZE_BIOM[0]-1),random.randint(0,tut.SIZE_BIOM[1]-1)]
        return tut.BCX_Pos(b,c,l=lvl)


def emptyBiom(biom):

    x = [0]*biom[0]
    tab = [[x]*biom[1]]
    eB = Biom(tab*tut.DEPTH_BIOM)
    return eB



