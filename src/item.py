



from src import tile_utils as tut
from src.utils import *
from src.TerrainCreator import REVERSE_DIC

class Item():

    def __init__(self,key, name):

        self.key = key
        self.name = name
        self.sprid = ''
        self.has_sprid = False
        self.is_stockable = False
        self.amount = 1

        self.time = [None,None]

    def set_spr(self,id):

        self.sprid = id
        self.has_sprid = True

    def del_sprid(self):
        self.sprid = ''
        self.has_sprid = False
        
    def act(self,case):

        #print(self.name,'acting on the',case,'case')
        return 0

    def ract(self,case):

        #print(self.name,'racting on the',case,'case')
        return 0

class Hand(Item):

    def __init__(self,perso,key=0, name='Hand'):

        super(Hand,self).__init__(key, name)
        self.perso = perso

        self.time = [10,0]

    def act(self,case):

        #print('grabbing',case)
        self.perso.grab(case)
        return 1

    def ract(self,case):

        #print(case)

        #print('This is',REVERSE_DIC[self.perso.terrain.get_case(case,case.l)][0])
        return 0

class Stackable(Item):

    def __init__(self,perso,key,name,amount=1,max=64):

        super(Stackable,self).__init__(key, name)

        self.perso = perso
        self.max_amount = max
        self.amount = amount
        self.is_stockable = True
        self.sprid_amount = ''
        self.amt_changed = False

        self.time = [None,0]

    def set_spr(self,id,amt_id):

        super(Stackable,self).set_spr(id)
        self.sprid_amount = amt_id

    def add(self,amt):

        if self.amount == self.max_amount and amt>0:
            return True,amt

        a = self.amount + amt
        if a < 0:
            old = self.amount
            self.amount = 0
            self.amt_changed = True
            return False,a-old
        elif a == 0:
            self.amount = a
            self.amt_changed = True
            return False,0
        elif a > self.max_amount:
            self.amount = self.max_amount
            self.amt_changed = True
            return True,a-self.max_amount
        else:
            self.amount = a
            self.amt_changed = True
            return True,0

    def ract(self,case):

        self.perso.place(case)
        return 1

    def del_sprid(self):

        super(Stackable,self).del_sprid()
        self.sprid_amount = ''



