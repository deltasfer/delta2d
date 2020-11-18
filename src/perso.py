




import random,time
import src.tile_utils as tut
import src.positions as pup
import src.species as sp
from src.utils import *
import src.item as item
import src.TerrainCreator as tc


CMD = False

## VIVANTS GENERAUX

class Living():

    def __init__(self,terrain,labman,bcx_box=None,specie='loutre',name=None,skin_seq=None):

        self.terrain = terrain
        self.labman = labman

        ## GENERAL
        if name != None:
            self.name = name
        else:
            self.name = choice(sp.dic[specie]['names'])
        self.life = sp.dic[specie]['life']
        self.max_life = sp.dic[specie]['life']
        self.dead = False

        self.specie = specie



        ## POS
        if bcx_box == None:
            self.pos = self.terrain.get_random_case(1)
            self.size = tut.from_xy_to_bcx(tut.XY_Size(*sp.dic[specie]['size']))
            self.box = tut.BCX_Box(*self.pos.bcx(),self.pos.lvl(),*self.size.bcx())
        else:
            self.pos = bcx_box.Pos()
            self.size = bcx_box.Size()   #(c=(1,1))#),p=(32-6,0)) ## le perso est un peu plus petit qu'une tile pour des raisons pratiques
            self.box = bcx_box

        self.coll_box = []


        ## SKINS
        self.dirs = {(0,1):'up',(0,-1):'down',(1,0):'right',(-1,0):'left'}

        if skin_seq == None:
            self.skin_dic = sp.dic[self.specie]['skin_seq']
        else:
            self.skin_dic = skin_seq
        self.skin_seq = 'down'
        self.skin_var = 0
        self.skin_time = time.time()
        self.skin_changing_time = 0.1
        self.skin = self.skin_dic['down'][0]

        self.plusposskin = [32,33]
        self.show_line = False

        ## SPEED
        self.speed = sp.dic[self.specie]['speed']

        ## SKILLS
        self.skills = sp.dic[self.specie]['skills']

        ## WALKABLE
        self.WALKON = {}
        self.WALKTRGH = {}
        for skill in self.skills:
            if skill in tc.WALKON:
                self.WALKON[skill] = tc.WALKON[skill]
            if skill in tc.WALKTRGH:
                self.WALKTRGH[skill] = tc.WALKTRGH[skill]

        self.actualise_pos()


    ## fonctions generales

    def actualise_general(self):

        if self.life <= 0:
            self.dead = True
        else:
            self.dead = False
        if CMD:
            self.infos()

    def infos(self):

        s = ''
        #s+= "infos de "
        #s+=str(self.name)
        s+="\n vie : "
        s+=str(self.life)+' / '+str(self.max_life)
        #s+= "\n pos : "+str(self.pos)
        #print(s)
        self.labman.add('infos de '+self.name,s)

    ## fonctions GAMEPLAY

    def adelife(self,qty):

        self.life = float(truncate(self.life+qty))
        if self.life < 0:
            self.life = 0
        elif self.life > self.max_life:
            self.life = self.max_life

    def adelife_max(self,qty,fill=False):
        self.max_life = float(truncate(self.max_life+qty))
        if fill or self.life > self.max_life:
            self.life = self.max_life


    ## fonctions MOVING, POSITION ...

    def actualise_pos(self):

        """ya mooyen c'est pas optimizé au maax"""


        ## PARTIE PX POS

        self.px_pos = tut.from_bcx_to_xy(self.pos)

        ## PARTIE ACTUALS CASES

        self.actual_cases = []
        self.px_actual_cases = []
        self.coll_box = []


        for i in range(2):
            for j in range(2):
                vec = tut.BCX_Vec(c=[i,j])
                pos_case = tut.bcx_add(self.pos,vec)
                pos_case.x[2] = 0
                pos_case.y[2] = 0

                if pos_case.x[0] >= 0 and pos_case.x[0] < tut.SIZE_TERRAIN[0] and pos_case.y[0] >= 0 and pos_case.y[0] < tut.SIZE_TERRAIN[1]:
                    coll = False
                    for lvl in [self.pos.lvl(),self.pos.lvl()-1]:
                        if lvl >= 0:
                            #print(i,j,lvl,'    :::',self.terrain.get_case(pos_case,lvl))
                            if lvl == self.pos.lvl():
                                if self.terrain.get_case(pos_case,lvl) != 0 or (self.terrain.get_case(pos_case,lvl) == 0 and lvl == 0):
                                    #if not self.terrain.get_case(pos_case,lvl) in tc.SOLIDITE[0]: ### SI ON ARRIVE PAS A MARCHER DEDANS car pas les skills
                                    #    #self.labman.add(str(i)+' '+str(j)+'  '+str(lvl)+'::: solid',tc.REVERSE_DIC[self.terrain.get_case(pos_case,lvl)][0])
                                    if not self.can_walk_through(self.terrain.get_case(pos_case,lvl)):
                                        coll = True
                            else:
                                if self.terrain.get_case(pos_case,lvl) != 0 or (self.terrain.get_case(pos_case,lvl) == 0 and lvl == 0):
                                    #if not self.terrain.get_case(pos_case,lvl) in tc.WALKABLE[0]: ### SI ON ARRIVE PAS A MARCHER DESSUS car pas les skills
                                    #    #self.labman.add(str(i)+' '+str(j)+'  '+str(lvl)+'::: not walkable',tc.REVERSE_DIC[self.terrain.get_case(pos_case,lvl)][0])
                                    if not self.can_walk_on(self.terrain.get_case(pos_case,lvl)):
                                        coll = True
                        else:
                            coll = True



                    if coll:
                        self.coll_box.append( tut.from_bcx_to_xy(tut.BCX_Box(*pos_case.bcx(),pos_case.lvl(),[0,0],[1,1],[0,0])))
                        #self.coll_box.append( tut.from_bcx_to_xy(tut.BCX_Box(*pos_case.bcx(),pos_case.lvl(),c2=[1,1])))
                else:
                    self.coll_box.append( tut.from_bcx_to_xy(tut.BCX_Box(*pos_case.bcx(),pos_case.lvl(),[0,0],[1,1],[0,0])))

                self.actual_cases.append(pos_case)
                px_pos = tut.from_bcx_to_xy(pos_case)
                self.px_actual_cases.append(px_pos)

        #self.labman.add('actual_cases',(len(self.actual_cases),self.actual_cases))
        ## PARTIE NEAR CASES


        self.near_cases = {}
        self.px_near_cases = []
        tab = [ (0,2),(0,1),(1,3),(1,0), (2,0),(2,3),(3,1),(3,2) ]
        for k in range(len(tab)):

            i,j = tab[k]

            pos_case = tut.BCX_Pos()
            vec = tut.BCX_Vec()

            d = 1
            if i%2 == j%2:
                if i%2 != 0:
                    d = -1
                vec = tut.BCX_Vec(c=[0,-d])
            else:
                if i < 2:
                    d = -1
                vec = tut.BCX_Vec(c=[d,0])


            pos_case = tut.bcx_add(self.actual_cases[i],vec)
            if pos_case.x[0] >= 0 and pos_case.x[0] < tut.SIZE_TERRAIN[0] and pos_case.y[0] >= 0 and pos_case.y[0] < tut.SIZE_TERRAIN[1]:
                coll = False
                for lvl in [self.pos.lvl(),self.pos.lvl()-1]:
                    if lvl >= 0:
                        #print(i,j,lvl,'    :::',self.terrain.get_case(pos_case,lvl))
                        #self.labman.add(str(i)+' '+str(j)+'  '+str(lvl)+':::',(not self.terrain.get_case(pos_case,lvl) in self.good_ground,self.terrain.get_case(pos_case,lvl) != '0'))
                        if lvl == self.pos.lvl():
                            if self.terrain.get_case(pos_case,lvl) != 0 or (self.terrain.get_case(pos_case,lvl) == 0 and lvl == 0):
                                #if not self.terrain.get_case(pos_case,lvl) in tc.SOLIDITE[0]:
                                if not self.can_walk_through(self.terrain.get_case(pos_case,lvl)):
                                    coll = True
                        else:
                            if self.terrain.get_case(pos_case,lvl) != 0 or (self.terrain.get_case(pos_case,lvl) == 0 and lvl == 0):
                                #if not self.terrain.get_case(pos_case,lvl) in tc.WALKABLE[0]:
                                if not self.can_walk_on(self.terrain.get_case(pos_case,lvl)):
                                    coll = True
                    else:
                        coll = True

                if coll:
                    self.coll_box.append( tut.from_bcx_to_xy(tut.BCX_Box(*pos_case.bcx(),pos_case.lvl(),[0,0],[1,1],[0,0])))
            else:
                self.coll_box.append( tut.from_bcx_to_xy(tut.BCX_Box(*pos_case.bcx(),pos_case.lvl(),[0,0],[1,1],[0,0])))

            self.near_cases[(i,j)] = pos_case
            px_pos = tut.from_bcx_to_xy(pos_case)
            self.px_near_cases.append(px_pos)

        self.box = tut.BCX_Box(*self.pos.bcx(),self.pos.lvl(),*self.size.bcx())
        #self.labman.add('FCKKYE',choice([0,1]))

    def actualise_skin(self):


        if self.skin_var >= len(self.skin_dic[self.skin_seq]):
            self.skin_var = 1
        elif self.skin_var < 0:
            self.skin_var = len(self.skin_dic[self.skin_seq])-1

        if self.skin != self.skin_dic[self.skin_seq][self.skin_var]:
            self.skin = self.skin_dic[self.skin_seq][self.skin_var]

    def move(self,dir,speedup=False,admin=False):

        if CMD:
            self.labman.add('       collbox : ',self.coll_box)
            self.labman.add('       collnb : ',str(len(self.coll_box))+' collisions')

        if speedup:
            speed = int(self.speed*1.5)
        else:
            speed = self.speed

        vec_depl = tut.XY_Vec(dir[0]*speed,dir[1]*speed)

        if not self.dead:
            self.skin_seq = self.dirs[(dir[0],dir[1])]
            t = time.time()
            if t-self.skin_time >= self.skin_changing_time:
                self.skin_var+=1
                self.skin_time = t

            if self.name == 'Legend':
                self.labman.add('skin Legend set to :',self.dirs[(dir[0],dir[1])])
            self.actualise_skin()

        moving = False

        if admin:
            moving = True
        else:

            go = True
            for collibox in self.coll_box:
                if not tut.algo_colli_XY(tut.from_bcx_to_xy(self.box),vec_depl,collibox):

                    x,y = 0,0
                    continu = True

                    while x < abs(vec_depl.x) and continu:
                        if not tut.algo_colli_XY(tut.from_bcx_to_xy(self.box),tut.XY_Vec(sign(vec_depl.x)*x,vec_depl.y),collibox):
                            if x != 0:
                                vec_depl.x = sign(vec_depl.x)*x -sign(vec_depl.x)*1
                            continu = False
                        x+=1

                    continu = True

                    while y < abs(vec_depl.y) and continu:
                        if not tut.algo_colli_XY(tut.from_bcx_to_xy(self.box),tut.XY_Vec(vec_depl.x,sign(vec_depl.y)*y),collibox):
                            if y!=0:
                                vec_depl.y = sign(vec_depl.y)*y -sign(vec_depl.y)*1
                            continu = False
                        y+=1

                    if x == 1 and y == 1:
                        go = False


            if go:
                moving = True


        if moving and not self.dead:
            self.pos = tut.bcx_add(self.pos,tut.from_xy_to_bcx(vec_depl))
            self.actualise_pos()

    def can_walk_on(self,cas):

        for skill in self.WALKON:
            if cas in self.WALKON[skill]:
                return True
        return False

    def can_walk_through(self,cas):

        for skill in self.WALKTRGH:
            if cas in self.WALKTRGH[skill]:
                return True
        return False

    ## fonctions speciales sauvegarde

    def get_biom(self):
        return self.pos.bcx()[0]

class Perso(Living):

    def __init__(self,textids,nb_textids,graphic,terrain,labman,bcx_box=None,specie='human',name=None,skin_seq=None):

        super(Perso,self).__init__(terrain,labman,bcx_box,specie,name,skin_seq)

        ## TEXTIDS GRAPH LABM TERR
        self.textids = textids
        self.numbers_textids = nb_textids
        self.graphic = graphic


        ## SELECTION
        self.selection = []
        self.limit_sel = 1
        self.inv_selection = []

        ## INVENTORY
        self.updatelist = []
        self.hand = item.Hand(self)
        self.tool = 0

        self.size_invent = 10,10
        self.inventory = {}
        self.invent_pxx = {}
        self.invent_pxx_box = {}
        self.flemmetavu = [i for i in range(self.size_invent[0])]
        for j in range(self.size_invent[1]):
            for i in range(self.size_invent[0]):
                if j==0:
                    self.inventory[i] = 0
                    self.invent_pxx[i] = pup.POS['hud_inventory_cursor_bar'][0] + 5*i*pup.GEN['10x'],pup.POS['hud_inventory_cursor_bar'][1]
                    self.invent_pxx_box[i] = tut.XY_Box(pup.POS['hud_inventory_cursor_bar'][0] + 5*i*pup.GEN['10x'],pup.POS['hud_inventory_cursor_bar'][1],*pup.SIZ['hud_inventory_selection'])
                self.flemmetavu.append((i,j))
                self.inventory[(i,j)] = 0
                self.invent_pxx[(i,j)] = pup.POS['hud_inventory_cursor_big'][0] + 5*i*pup.GEN['10x'],pup.POS['hud_inventory_cursor_big'][1]+j*5*pup.GEN['10y']
                self.invent_pxx_box[(i,j)] = tut.XY_Box(pup.POS['hud_inventory_cursor_big'][0] + 5*i*pup.GEN['10x'],pup.POS['hud_inventory_cursor_big'][1]+j*5*pup.GEN['10y'],*pup.SIZ['hud_inventory_selection'])

        self.aff_inv = False
        self.portee = 400

    ## fct selectives

    def select(self,thg):

        #print(thg)
        bcx_pos = tut.BCX_Pos()
        if type(thg) == tut.XY_Pos:
            bcx_pos = tut.from_xy_to_bcx(thg)

            lvl = tut.DEPTH_BIOM-1
            while lvl > 0 and self.terrain.get_case(bcx_pos,lvl) == 0 :
                lvl -=1

            if lvl >= 0:
                bcx_pos.l = lvl

        elif type(thg) == tut.BCX_Pos:
            bcx_pos = thg

        bcx_pos.x[2] = 0
        bcx_pos.y[2] = 0

        #bcx_size =tut.BCX_Size(c=(1,1))

        #self.labman.add('selected',(bcx_pos,self.terrain.get_case(bcx_pos)))
        if tut.biom_in_terrain([bcx_pos.x[0],bcx_pos.y[0]]):
            box = tut.BCX_Box(*bcx_pos.bcx(),bcx_pos.lvl(),[0,0],[1,1],[0,0])
            if not box in self.selection:
                self.selection.append(box)
                while len(self.selection) > self.limit_sel:
                    self.selection = self.selection[1:]
                return True
            else:
                return False
            #self.labman.add('invent',self.selection)

    def in_inv_select(self,rlpos):

        if type(rlpos) != tut.XY_Pos:
            rlpos = tut.XY_Pos(*rlpos)

        for thg in self.inventory:
            if tut.colli_ABP_XY(self.invent_pxx_box[thg],rlpos):
                if not thg in self.inv_selection:
                    self.inv_selection = [thg]
                    return True
                else:
                    return False

    def update_skin(self,mouse_pos):
        if not self.dead:
            x,y = tut.xy_add(mouse_pos,tut.from_bcx_to_xy(self.pos),-1).xy()
            if y == 0:
                y=1
            #self.labman.add('vec moved mouse',vec)

            dif = abs(x / y)

            if dif >=1:
                if x >= 0:
                    self.skin_seq = 'right'
                else:
                    self.skin_seq = 'left'
            else:
                if y >= 0:
                    self.skin_seq = 'up'
                else:
                    self.skin_seq = 'down'
            self.actualise_skin()

    def in_inv_grab(self):
        if self.inv_selection != []:
            self.inv_sel_grabbed = [*self.inv_selection]
            #print('GRAABEDD',self.inv_sel_grabbed)


    def in_inv_drop(self):
        if self.inv_sel_grabbed != [] and self.inv_selection != []:
            init_pos = self.inv_sel_grabbed[0]
            end_pos = self.inv_selection[0]

            if self.inventory[init_pos] != 0 and self.inventory[init_pos].has_sprid:
                self.graphic.delete(self.inventory[init_pos].sprid)
                if self.inventory[init_pos].is_stockable:
                    self.graphic.delete(self.inventory[init_pos].sprid_amount)
                self.inventory[init_pos].del_sprid()

            if self.inventory[end_pos] != 0 and self.inventory[end_pos].has_sprid:
                self.graphic.delete(self.inventory[end_pos].sprid)
                if self.inventory[end_pos].is_stockable:
                    self.graphic.delete(self.inventory[end_pos].sprid_amount)
                self.inventory[end_pos].del_sprid()



            self.inventory[init_pos],self.inventory[end_pos] = self.inventory[end_pos],self.inventory[init_pos]
            #print('SWAAP',init_pos,'and',end_pos)




            self.check_inventory(end_pos)
        self.check_inventory(init_pos)

    ## fct des actions

    def get_action_time(self,act):

        #print(self.inventory[self.tool].time,self.hand.time)
        if not self.dead:
            if act == 'L':
                if self.inventory[self.tool] != 0:
                    if self.inventory[self.tool].time[0] != None:
                        return self.inventory[self.tool].time[0]
                    else:
                        return self.hand.time[0]
                else:
                    return self.hand.time[0]
            elif act == 'R':
                if self.inventory[self.tool] != 0:
                    if self.inventory[self.tool].time[1] != None:
                        return self.inventory[self.tool].time[1]
                    else:
                        return self.hand.time[1]
                else:
                    return self.hand.time[1]
        else:
            return 0

    def act(self,xy_pos,way='L'):

        if not self.dead:

            bcx_pos = tut.from_xy_to_bcx(xy_pos)
            bcx_pos.x[2],bcx_pos.y[2] =0,0
            xy_pos = tut.from_bcx_to_xy(bcx_pos)
            xy_vec = tut.XY_Vec(  xy_pos.x-tut.from_bcx_to_xy(self.pos).x , xy_pos.y-tut.from_bcx_to_xy(self.pos).y  )
            #print(tut.module_XY(xy_vec))

            lvl = tut.DEPTH_BIOM-1
            while lvl > 0 and self.terrain.get_case(bcx_pos,lvl) == 0 :
                lvl -=1
            if lvl >= 0:
                bcx_pos.l = lvl

            #print(bcx_pos)

            if way == 'L':
                if tut.module_XY(xy_vec) <= self.portee:
                    #print(self.inventory[self.tool])
                    if self.inventory[self.tool] != 0:
                        ok = self.inventory[self.tool].act(bcx_pos)
                        if ok == 0:
                            self.hand.act(bcx_pos)
                    else:
                        self.hand.act(bcx_pos)
                    #self.labman.add('acting',bcx_pos)
                #else:
                #    self.labman.add('acting','too far !')

            elif way == 'R':
                if tut.module_XY(xy_vec) <= self.portee:
                    #print(self.inventory[self.tool])
                    if self.inventory[self.tool] != 0:
                        ok = self.inventory[self.tool].ract(bcx_pos)
                        if ok == 0:
                            self.hand.ract(bcx_pos)
                    else:
                        self.hand.ract(bcx_pos)
                    #self.labman.add('racting',bcx_pos)
                #else:
                #    self.labman.add('racting','too far !')

    def grab(self,bcx_pos):

        if tut.biom_in_terrain([bcx_pos.x[0],bcx_pos.y[0]]):

            lvl = tut.DEPTH_BIOM-1
            while lvl >= 0 and self.terrain.get_case(bcx_pos,lvl) == 0 :
                lvl -=1
            if lvl >= 0:
                bcx_pos.l = lvl
            else:
                return 0

            grabbed = item.Stackable(self,self.terrain.get_case(bcx_pos,lvl),get_id(tc.REVERSE_DIC[self.terrain.get_case(bcx_pos)][0]))
            to_up = self.add_to_inventory(grabbed)
            #print(to_up)
            for thg in to_up:
                self.check_inventory(thg)

            #print('ahah!3')
            if len(to_up) > 0:
                self.updatelist.append(bcx_pos)
                self.terrain.set_case(bcx_pos,0)
            else:
                print('no place left in the inventory !')

    def place(self,bcx_pos):

        if tut.biom_in_terrain([bcx_pos.x[0],bcx_pos.y[0]]):

            lvl = tut.DEPTH_BIOM-1
            while lvl >= 0 and self.terrain.get_case(bcx_pos,lvl) == 0 :
                lvl -=1
            if lvl >= 0:
                bcx_pos.l = lvl
            else:
                bcx_pos.l = -1
            #print('lvl =',lvl)


            if self.inventory[self.tool].amount > 0:

                if self.terrain.verify(bcx_pos,self.inventory[self.tool].key):
                    bcx_pos.l += 1
                    self.terrain.set_case(bcx_pos,self.inventory[self.tool].key)
                    self.updatelist.append(bcx_pos)

                    if self.inventory[self.tool].is_stockable:
                        self.inventory[self.tool].add(-1)
                    else:
                        self.inventory[self.tool].amount = 0
                    #self.labman.add('Placing',(bcx_pos,self.inventory[self.tool].amount))


            self.check_inventory(self.tool)

    ## fct de l'inventaire

    def add_to_inventory(self,item):

        to_update = []
        if item.is_stockable:

            stacks = []
            for thg in self.flemmetavu:
                if self.inventory[thg] != 0:
                    if item.key == self.inventory[thg].key:
                        stacks.append(thg)
            for thg in stacks:
                to_update.append(thg)
                ok , item.amount = self.inventory[thg].add(item.amount)
                if (ok,item.amount) == (True,0):
                    return to_update

        for thg in self.flemmetavu:
            if self.inventory[thg] == 0:
                self.inventory[thg] = item
                to_update.append(thg)
                return to_update
        return to_update

    def check_inventory(self,thg):

        if self.inventory[thg] != 0:

            if self.inventory[thg].amount <= 0 :
                if self.inventory[thg].has_sprid:
                    self.graphic.delete(self.inventory[thg].sprid)
                    if self.inventory[thg].is_stockable:
                        self.graphic.delete(self.inventory[thg].sprid_amount)
                self.inventory[thg] = 0
            else:
                if not self.inventory[thg].has_sprid:
                    sprid = self.graphic.addSpr( self.textids[self.inventory[thg].key], self.invent_pxx[thg],vis=self.aff_inv)
                    self.graphic.addToGroup(sprid,['hud'])

                    if self.inventory[thg].is_stockable:
                        sprid2 = self.graphic.addSpr( self.numbers_textids[self.inventory[thg].amount], self.invent_pxx[thg],vis=self.aff_inv)
                        self.graphic.addToGroup(sprid2,['hud'],4)
                        self.inventory[thg].set_spr(sprid,sprid2)
                    else:
                        self.inventory[thg].set_spr(sprid)
                else:
                    if self.inventory[thg].is_stockable:
                        if self.inventory[thg].amt_changed:
                            self.graphic.delete(self.inventory[thg].sprid_amount)
                            self.inventory[thg].sprid_amount = self.graphic.addSpr( self.numbers_textids[self.inventory[thg].amount], self.invent_pxx[thg],vis=self.aff_inv)
                            self.graphic.addToGroup(self.inventory[thg].sprid_amount,['hud'],4)
                            self.inventory[thg].amt_changed = False

    def toggle_inv(self):
        if self.aff_inv:
            for thg in self.flemmetavu:
                if self.inventory[thg] != 0:
                    self.graphic.sprites[self.inventory[thg].sprid].visible = False
                    if self.inventory[thg].is_stockable:
                        self.graphic.sprites[self.inventory[thg].sprid_amount].visible = False
        else:
            for thg in self.flemmetavu:
                if self.inventory[thg] != 0:
                    self.graphic.sprites[self.inventory[thg].sprid].visible = True
                    if self.inventory[thg].is_stockable:
                        self.graphic.sprites[self.inventory[thg].sprid_amount].visible = True
        self.aff_inv = not self.aff_inv

    def scroll_tool(self,nb):

        self.tool += nb
        if self.tool < 0:
            self.tool += self.size_invent[0]
        elif self.tool >= self.size_invent[0]:
            self.tool -= self.size_invent[0]

    ## fonctions speciales sauvegarde

    def get_inv(self):

        dic = {}
        for pos in self.inventory:
            if self.inventory[pos] != 0:
                if type(pos) == int:
                    pos2 = str(pos)
                else:
                    pos2 = str(pos[0])+','+str(pos[1])
                dic[pos2] = [self.inventory[pos].key ,self.inventory[pos].amount]

        return dic

    def set_inv(self,dic):

        #print(self.inventory)
        for pos in dic:
            #print('pos',pos)
            if not ',' in pos:
                pos2 = int(pos)
            else:
                pos2 = pos.split(',')
                pos2 = (int(pos2[0]),int(pos2[1]))
            self.inventory[pos2] = item.Stackable(self,dic[pos][0],get_id(tc.REVERSE_DIC[dic[pos][0]][0]),dic[pos][1])
            self.check_inventory(pos2)

## CLASSES DERIVEES EXPRES POUR LES BOTS

class LivingBot(Living):

    def __init__(self,terrain,labman,bcx_box=None,specie='loutre',name=None,skin_seq=None):

        super(LivingBot,self).__init__(terrain,labman,bcx_box,specie=specie,name=name,skin_seq=skin_seq)

        self.possible_actions = ['nothing','choice_destination','walk','sleep']
        self.current_main_action = None

        self.choosen_destination = None

    def being_a_bot(self):



        if self.current_main_action == None:
            ## le bot n'a aucune main action en cours
            self.do(choice(self.possible_actions))
        else:
            ## le bot a une main action en cours
            if choice([True]+[False]*99):
                ## mais finalement change d'avis -> permet d'insérer un peu d'aléatoire
                self.current_main_action = None
            else:
                ## fait son action
                self.do(self.current_main_action)


        if self.choosen_destination != None:
            self.labman.add(self.name+' main_acting : ',str(self.current_main_action)+ '   '+str(self.choosen_destination.bcx()))
        else:
            self.labman.add(self.name+' main_acting : ',str(self.current_main_action))

    def do(self,action):

        self.current_action = action
        if self.current_main_action == None:

            if action == 'choice_destination':

                self.choosen_destination = self.terrain.get_random_case(self.pos.lvl())
                self.current_main_action = 'walk'

            elif action == 'walk':
                self.move(choice(self.dirs))

            elif action == 'nothing':
                self.current_main_action = 'nothing'

            elif action == 'sleep':
                self.current_main_action = 'sleep'

        else:
            if action == 'walk':

                dir = []
                xy_pos = tut.from_bcx_to_xy(self.choosen_destination)
                xy_pos2 = tut.from_bcx_to_xy(self.pos)
                vx,vy = tut.xy_add(xy_pos,xy_pos2).xy()
                if vy == 0:
                    self.current_main_action = None
                else:
                    if abs(vx/vy) >= 1:
                        # les x gagnent
                        if vx > 0:
                            dir = [1,0]
                        else:
                            dir = [-1,0]
                    else:
                        # les y gagnent
                        if vy > 0:
                            dir = [0,1]
                        else:
                            dir = [0,-1]

                    self.move(dir)

        #self.labman.add(self.name+' acting : ',self.current_action)
