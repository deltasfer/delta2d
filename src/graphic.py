





import pyglet
from src import utils
import src.tile_utils as tut



#manager who rules groups to draw things in the right order u know
class GroupManager():

    def __init__(self):


        self.groups = {} ## give the group with the name

        self.names_wo = {} ## give the name with the order
        self.names_wl = {} ## give the name with the level

        self.orders = {} ## give the order with the name

        names = ['back','mid','front','hud','map','up']
        self.distance_btw = 8

        for i in range(len(names)):
            self.groups[names[i]] = pyglet.graphics.OrderedGroup(i*self.distance_btw)
            self.orders[names[i]] = i*self.distance_btw
            self.names_wo[i*self.distance_btw] = names[i]
            if i<tut.DEPTH_BIOM:
                self.names_wl[i] = names[i]

    def getOrderGroup(self,thg=['back',None,None],thg2=0):

        name=''

        if thg[0] != None: ## atteint un groupe particulier avec son nom
            name = thg[0]
        elif thg[1] != None: ## atteint un groupe particulier avec son order d'affichage
            return thg[1]
        elif thg[2] != None: ## atteint un groupe particulier en utilisant le level de l'objet à ajouter au groupe
            name = self.names_wl[thg[2]]

        if thg2 != 0:
            name += str(thg2)

        if name in self.groups:
            return self.orders[name]

        return None

    def getGroup(self,thg=['back',None,None],thg2=0):

        name = ''

        if thg[0] != None: ## atteint un groupe particulier avec son nom
            name = thg[0]
        elif thg[1] != None: ## atteint un groupe particulier avec son order d'affichage
            name = self.names_wo[thg[1]]
        elif thg[2] != None: ## atteint un groupe particulier en utilisant le level de l'objet à ajouter au groupe
            name = self.names_wl[thg[2]]

        if thg2 != 0:
            name +=str(thg2)

        if name in self.groups:
            return self.groups[name]

        return None #le groupe n'existe pas

    def createGroup(self,thg=['back',None,None],thg2=0,level_to_put_in=0):
        group = self.getGroup(thg,thg2)
        if group == None: ## pas encore de groupe créé

            if thg[0] != None:
                if thg2 == 0:
                    return self.quickCreateGroup(thg[0],level_to_put_in)
                else:
                    name = thg[0]+str(thg2)
                    return self.quickCreateGroup(name,self.orders[thg[0]]+thg2)
            elif thg[1] != None:
                try:
                    name = self.names_wo[thg[1]]+str(thg2)
                    return self.quickCreateGroup(name,thg[1]+thg2)
                except :
                    print('chien essaie de regler la creation dun groupe avec order')
            elif thg[2] != None:
                try:
                    name = self.names_wl[thg[2]]+str(thg2)
                    return self.quickCreateGroup(name,thg[2]*self.distance_btw + thg2)
                except :
                    print('chien essaie de regler la creation dun groupe avec level')

        # ah si on est là le groupe était créé
        return group

    def quickCreateGroup(self,name,order):
        if not name in self.groups:
            self.groups[name] = pyglet.graphics.OrderedGroup(order)
            self.orders[name] = order
            self.names_wo[order] = name
            return self.groups[name]
        return self.groups[name] # group was already created

#manager who init images
class MainManager():

    def __init__(self,path,size_tile=32):

        self.size_tile = size_tile

        self.textures = {}
        self.rawdata = {}

        self.ids = []

        self.batch = pyglet.graphics.Batch()
        self.path = path

    def loadImSeq(self,name,path2,sizex,sizey):

        path3 = '/item/'
        img = pyglet.image.load(self.path+path3+path2)
        textures = pyglet.image.ImageGrid(img, sizex//self.size_tile,sizey//self.size_tile)

        ids = []
        for txt in textures:
            id = utils.get_id('text')
            self.textures[id] = txt

            if name == 'ground':
                self.rawdata[id] = txt.get_data('RGBA', txt.width * len('RGBA'))

            self.ids.append(id)
            ids.append(id)
        return ids

    def loadIm(self,name,path2):

        path3 = '/item/'
        id = utils.get_id('img')
        img = pyglet.image.load(self.path+path3+path2)
        self.textures[id] = img
        self.ids.append(id)
        return id

    def draw(self):
        self.batch.draw()
        #print('hee')

#manager who rules normal sprites
class GraphManager():

    def __init__(self,textManager,group_manager,size_tile=32):

        self.size_tile = size_tile
        self.textManager = textManager

        ## GROUPES

        self.groups = group_manager

        ## SPRITES

        self.sprites = {}
        self.static_sprites = {}
        self.eff_sprites = {}

        self.ids = []

    def addSpr(self,textid,xy_pos=(0,0),alr_id=-1,vis=True,static=False,eff=False):

        if alr_id == -1:
            id = utils.get_id('spr')
            self.ids.append(id)
        else:
            id =alr_id

        if static:
            self.static_sprites[id] = pyglet.sprite.Sprite(self.textManager.textures[textid], batch=self.textManager.batch)
            self.static_sprites[id].position = xy_pos
            self.static_sprites[id].visible = vis
        elif eff:
            self.eff_sprites[id] = pyglet.sprite.Sprite(self.textManager.textures[textid], batch=self.textManager.batch)
            self.eff_sprites[id].position = xy_pos
            self.eff_sprites[id].visible = vis
        else:
            self.sprites[id] = pyglet.sprite.Sprite(self.textManager.textures[textid], batch=self.textManager.batch)
            self.sprites[id].position = xy_pos
            self.sprites[id].visible = vis

        #self.detect()

        return id

    def addToGroup(self,id,thg=['back',None,None],thg2=0,level_to_put_in=0,eff=False):

        group = self.groups.createGroup(thg,thg2,level_to_put_in)

        if not eff:
            try :
                self.sprites[id].group = group
            except:
                self.static_sprites[id].group = group
        else:
            self.eff_sprites[id].group = group

        #self.detect()

    def unhide(self,tabids,hide=False):
        ## unhide(machin) AFFICHE machin
        ## unhide(machin,True) N'AFFICHE PAS machin

        if type(tabids) == type([]):
            for id in tabids:
                try:
                    if self.sprites[id].visible != (not hide):
                        self.sprites[id].visible = (not hide)
                except:
                    try:
                        if self.static_sprites[id].visible != (not hide):
                            self.static_sprites[id].visible = (not hide)
                    except :
                        if self.eff_sprites[id].visible != (not hide):
                            self.eff_sprites[id].visible = (not hide)

        elif type(tabids) == type({}):
            for id in tabids:
                self.unhide(tabids[id],hide)

        else:
            try:
                if self.sprites[tabids].visible != (not hide):
                    self.sprites[tabids].visible = (not hide)
            except:
                try:
                    if self.static_sprites[tabids].visible != (not hide):
                        self.static_sprites[tabids].visible = (not hide)
                except :
                    if self.eff_sprites[tabids].visible != (not hide):
                        self.eff_sprites[tabids].visible = (not hide)

    def set_text(self,sprid,textid):
        if self.sprites[sprid].image != self.textManager.textures[textid]:
            self.sprites[sprid].image = self.textManager.textures[textid]

    def modify(self,sprid,pos=None,scale=None,group=None):

        # position
        x,y = None,None
        if pos != None and pos != (self.sprites[sprid].x,self.sprites[sprid].y):
            x,y = pos

        # scale
        scalex,scaley = None,None
        if scale != None and scale != (self.sprites[sprid].scale_x,self.sprites[sprid].scale_y):
            scalex,scaley = scale

        # updating group
        if group != None:
            group = self.groups.getGroup(*group)
            if group != self.sprites[sprid].group:
                self.sprites[sprid].group = group

        # final updating positon and scale
        self.sprites[sprid].update(x=x,y=y,scale_x = scalex,scale_y=scaley)

    def spr(self,id):

        if id in self.sprites:
            return self.sprites[id]
        elif id in self.static_sprites:
            return self.static_sprites[id]
        elif id in self.eff_sprites:
            return self.eff_sprites[id]

        return None

    def delete(self,tabids='all'):

        if tabids == 'all': # on delete tous les sprites affichés ingame
            for id in self.sprites:
                self.sprites[id].delete()
            self.sprites = {}
            #print('sprites deleted')

        elif type(tabids) == type('aa'): # on delete un seul sprite precis
            if tabids in self.sprites:
                self.sprites[tabids].delete()
                del self.sprites[tabids]
                #print(tabids,'deleted')

        elif type(tabids) == type([]): # on delete un tableau de sprite
            #print('deleting',tabids)
            for id in tabids:
                self.delete(id)

        elif type(tabids) == type({}): # on delete un dico de sprite
            #print('deleting',tabids)
            for lab in tabids:
                self.delete(tabids[lab])

    def detect(self):

        errorsS = []
        errorsV = []
        for id in self.sprites:
            if type(self.sprites[id]) != pyglet.sprite.Sprite:
                errorsS.append(id)
            else:
                if self.sprites[id]._vertex_list == None:
                    errorsV.append(id)
        if errorsS != []:
            print('noSprite',errorsS)
        if errorsV != []:
            print('noVertex',errorsV)


#manager who rules normal labels
class LabelManager():

    def __init__(self,textManager,group_manager,font):

        self.groups = group_manager
        self.textManager = textManager

        self.font = font

        self.labels = {}
        self.ids = []

    def addLabel(self,contenu,xy_pos=(0,0),alr_id=-1,vis=True,font_name=None,font_size=30,group=None,anchor = ('left','bottom'),color=(255,255,255,255)):

        if alr_id == -1:
            id = utils.get_id('lbl')
            self.ids.append(id)
        else:
            id =alr_id

        if not font_name:
            font_name = self.font


        anchor_x,anchor_y= anchor

        #group = self.groups.createGroup(['hud'])
        self.labels[id] = pyglet.text.Label(contenu,font_name=font_name,font_size=font_size,group=group, \
                        batch=self.textManager.batch,anchor_x= anchor_x,anchor_y= anchor_y,color=color)
        self.labels[id].x,self.labels[id].y = xy_pos
        self.unhide(id,not vis)
        #self.labels[id].visible = vis

        return id

    def addToGroup(self,id,thg=['back',None,None],thg2=0,level_to_put_in=0):

        group = self.groups.createGroup(thg,thg2,level_to_put_in)
        #print('GROUP IS',group)
        self.labels[id]._init_groups(group)
        self.labels[id]._update()

    def unhide(self,tabids,hide=False):
        ## unhide(machin) AFFICHE machin
        ## unhide(machin,True) N'AFFICHE PAS machin

        if type(tabids) == type([]):
            for id in tabids:
                self.unhide(id,hide)
        elif type(tabids) == type({}):
            for id in tabids:
                self.unhide(tabids[id],hide)
        else:
            if hide == False and self.labels[tabids].color[3] == 0:
                self.labels[tabids].color = [*self.labels[tabids].color[:3],255]
            elif hide == True and self.labels[tabids].color[3] != 0:
                self.labels[tabids].color = [*self.labels[tabids].color[:3],0]

    def set_text(self,lblid,contenu):
        if self.labels[lblid].text != contenu:
            self.labels[lblid].text = contenu

    def printGroup(self,lblid):
        print('\ttopgroup :',self.labels[lblid].top_group)
        print('\tbackgroup :',self.labels[lblid].background_group)
        print('\tforegroup :',self.labels[lblid].foreground_group)
        print('\tforegroupdeco :',self.labels[lblid].foreground_decoration_group)

    def modify(self,lblid,pos=None,scale=None):

        if scale != None and scale != (self.labels[lblid].scale_x,self.labels[lblid].scale_y):
            self.labels[lblid].update(scale_x = scale[0],scale_y=scale[1])
            #self.labels[lblid].scale_x,self.labels[lblid].scale_y = scale

        if pos != None and pos != (self.labels[lblid].x,self.labels[lblid].y):
            self.labels[lblid].x,self.labels[lblid].y = pos

    def delete(self,tabids='all'):

        if tabids == 'all': # on delete tous les labels affichés ingame
            for id in self.labels:
                self.labels[id].delete()
            self.labels = {}
            #print('labels deleted')

        elif type(tabids) == type('aa'): # on delete un seul label precis
            self.labels[tabids].delete()
            del self.labels[tabids]
            #print(tabids,'deleted')

        elif type(tabids) == type([]): # on delete un tableau de label
            #print('deleting',tabids)
            for id in tabids:
                self.delete(id)

        elif type(tabids) == type({}): # on delete un dico de label
            #print('deleting',tabids)
            for lab in tabids:
                self.delete(tabids[lab])

#special manager who rules effects sprites
class EffectManager():

    def __init__(self,graphic,textids,size_tile=32):

        self.effects = {}
        #self.groups = {}
        #self.sprites = {}

        self.sprids = {}

        self.size_tile = size_tile

        self.graphic = graphic
        self.textids = textids

    def addEffect(self,name,terrain,dep_pos,order):

        self.effects[name] = terrain
        #self.groups[name] = pyglet.graphics.OrderedGroup(order)

        """created = self.graphic.createGroup(name,order,eff=True)
        if not created:
            self.delete(name)"""

        self.sprids[name] = []

        for j in range(len(terrain)):
            for i in range(len(terrain[j])):
                posx = dep_pos[0] + i*self.size_tile
                posy = dep_pos[1] + j*self.size_tile
                id = self.graphic.addSpr(self.textids[terrain[j][i]],(posx,posy),eff=True)
                self.graphic.addToGroup(id,[name],0,order,True)
                #print('creating',name,id)
                self.sprids[name].append(id)
                #self.sprites[name].append(pyglet.sprite.Sprite(self.textManager.textures[] , batch = self.textManager.batch , group=self.groups[name], x=posx,y=posy  ))
        return name

    def unhide(self,name,hide=False):
        self.graphic.unhide(self.sprids[name],hide)

    def delete(self,name):
        #print(self.sprids[name])
        #print('deleting',name)
        for spr in self.sprids[name]:
            #print('deleting',name,spr)
            self.graphic.eff_sprites[spr].delete()

    def hasEffect(self,name):
        return name in self.effects

#special manager who rules labels I need to see what's wrong (it's my own cmd)
class CmdManager():

    def __init__(self,pos):

        self.batch = pyglet.graphics.Batch()

        self.data = {}
        self.pos = {}
        self.labels = {}
        self.name = ['main','main2']
        for name in self.name:
            self.data[name] = {}
            self.pos[name] = {}
            self.labels[name] = {}


        self.init_pos = pos

        self.font = 'arial'
        self.size_ft = 20

    def draw(self,name='main'):
        self.batch.draw()

    def add(self,lab,data,name='main'):

        already_in = False

        try:
            type(self.data[name][lab])
            already_in = True
        except :
            self.pos[name][lab] = [self.init_pos[0],self.init_pos[1]-25]
            self.init_pos = self.pos[name][lab]

        if type(data) == type(0.001):
            self.data[name][lab] = utils.truncate(data,3)
        else:
            self.data[name][lab] = data

        if not already_in:
            self.labels[name][lab] = pyglet.text.Label(lab+' '+str(self.data[name][lab]),
                            font_name=self.font,
                            font_size=self.size_ft,
                            x=self.pos[name][lab][0],
                            y=self.pos[name][lab][1],
                            batch=self.batch)
        else:
            self.labels[name][lab].text = lab+' '+str(self.data[name][lab])

#special manager for single uses : buttons in menu
class SpecialManager():

    def __init__(self,manager,scrsize):

        self.manager = manager
        self.screen = scrsize

        self.to_draw = {}
        #self.order = []

    def addSpr(self,textid,x,y,name=utils.get_id('spc')):

        thg = pyglet.sprite.Sprite(self.manager.textures[textid])
        thg.position = x,y

        self.to_draw[name] = thg

        return name

    def addLabel(self,text,font_name,font_size,x,y,name=utils.get_id('spc'),color=(0,0,0,255)):
        thg = pyglet.text.Label(text,
                        font_name=font_name,
                        font_size=font_size,
                        anchor_x= 'center',
                        color=color,
                        x=x,y=y)

        self.to_draw[name] = thg

        return name

    def addThg(self,thg,name=utils.get_id('spc')):

        self.to_draw[name] = thg
        return name

    def draw(self,tab):

        for name in tab:
            self.to_draw[name].draw()

## OTHER GRAPHICS CLASS

class Cursor():

    def __init__(self,name,graph,text,skin,thg,thg2=0,pos=(0,0),vis=True):

        self.name = name

        self.textids = text
        self.skin = skin
        self.manager = graph
        id = self.manager.addSpr(self.textids[self.skin],pos,vis=vis)
        self.manager.addToGroup(id,thg,thg2)
        self.order = self.manager.groups.getOrderGroup(thg,thg2)
        self.has_ani = False
        self.id = id

        #return id

    def set_pos(self,pos):
        self.manager.sprites[self.id].position = pos

    def get_pos(self):
        return self.manager.sprites[self.id].position

    def set_ani(self,ani,time=2,skin=0):
        self.has_ani = True
        self.ani = ani
        self.time=time
        self.temp = 0
        self.skin = skin
        self.maj_ani()

    def set_text(self,skin):
        self.has_ani = False
        self.skin = skin
        self.maj_ani()

    def up_skin(self,key=[1]):
        if self.has_ani:
            if key[0] != None:
                self.temp+=key[0]
                if self.temp >= self.time:
                    a = self.temp//self.time
                    self.temp-=(self.time*a)
                    self.skin+=a
                if self.skin >= len(self.ani):
                    self.skin -= len(self.ani)
                elif self.skin < 0:
                    self.skin += len(self.ani)
            elif key[1] != None:
                self.skin=key[1]
                if self.skin >= len(self.ani):
                    self.skin = len(self.ani) - 1
                elif self.skin < 0:
                    self.skin = 0


            self.maj_ani()

    def maj_ani(self):
        if self.manager.sprites[self.id].visible:
            if self.has_ani:
                self.manager.set_text(self.id,self.textids[self.ani[self.skin]])
            else:
                self.manager.set_text(self.id,self.textids[self.skin])

    def delete(self):
        self.manager.delete(self.id)

    def unhide(self,hide=False):
        self.manager.unhide(self.id,hide)

    def is_visible(self):
        return self.manager.sprites[self.id].visible






