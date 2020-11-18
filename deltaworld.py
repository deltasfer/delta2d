

#newversion



import pyglet
import PIL as pil
import time,os,json,random
from pyglet.window import key

from src.TerrainCreator import *
from src.utils import *
import src.graphic as graphic
import src.terrain as terrain
import src.drawable as drawable
import src.tile_utils as tut
import src.positions as pup
import src.perso as pso
import src.getsave as gs


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__)) # fopatouché
if ' ' in CURRENT_PATH:
    print('Le chemin d\'acces contient un espace. Le programme va BUGUER SA MERE.')
    print('Changez le programme de place pour un path sans espace svp.')

SAVES_PATH = '/saves/' # sous dossier principal où seront stockées les sauvegardes des mondes

SIZE_TERRAIN = 4,4 # en bioms  ## si c'est au dessus de 27*27 ya au moins 1 min de loading au début !! aoutch
SIZE_BIOM = 32,32 # en cases ## à modifier comme tu le souhaites
SIZE_TILE = 32 # en px ## à pas toucher sinon ça CRASH TOUT

tut.set_var(SIZE_TERRAIN,SIZE_BIOM,(SIZE_TILE,SIZE_TILE))

TAKE_DIRECT_SCREEN = False

NB_BOTS_CREATE = 20

class App(pyglet.window.Window):


    ### INIT FUNCTIONS

    def __init__(self):

        super(App, self).__init__()

        self.path = CURRENT_PATH

        icon1 = pyglet.image.load(self.path+'/item/logo16.png')
        icon2 = pyglet.image.load(self.path+'/item/logo32.png')
        self.set_icon(icon1, icon2)

        ### screens

        #self.screens = pyglet.window.get_platform().get_default_display().get_screens()
        display = pyglet.canvas.get_display()
        self.screens = display.get_screens()
        #print('screens',self.screens)
        used_screen = self.get_current_screen()

        self.size_scr = 1000,800
        self.size_fullscr = [used_screen.width,used_screen.height]

        self.fscreen = True
        self.set_size(self.size_scr[0],self.size_scr[1])
        self.set_fullscreen(self.fscreen,screen=used_screen)
        self.current_size_scr = self.size_fullscr
        #self.on_my_resize()

        # loading fonts
        font_path = 'item/fonts/'
        self.fonts = ['Modular Amplitude','starguard','starguard3d','starguardcond','starguardhalf']
        self.font = ['Star Guard','Star Guard 3D','Star Guard Halftone']
        for ft in self.fonts:
            try:
                pyglet.resource.add_font(font_path+ft+'.otf')
                #print(ft,'done')
            except:
                try:
                    pyglet.resource.add_font(font_path+ft+'.ttf')
                except :
                    pyglet.resource.add_font('arial.ttf')
                #print(ft,'ttf done')

        ### managers

        self.manager = graphic.MainManager(CURRENT_PATH)
        self.group_manager = graphic.GroupManager()
        self.graphic = graphic.GraphManager(self.manager,self.group_manager)
        self.labman = graphic.LabelManager(self.manager,self.group_manager,self.font[0])
        self.cmd = graphic.CmdManager((20 , self.size_fullscr[1] - 50))
        self.specMan = graphic.SpecialManager(self.manager,self.current_size_scr)

        self.aff_cmd = False


        #self.load()

    def init(self):

        self.in_land = False

        # CREATION TERRAIN partie 1
        self.color_list = [1,3,4,5,6,7,8,9,10,11,12,13,14,15]
        self.generated_terrains = 1


        ## DECLARATION ET SEPARATIONS DES IMAGES
        elapsed_time =time.time()

        self.textids = {}

        self.textids['ground'] = self.manager.loadImSeq('ground','back.png',512,512)
        self.textids['persos'] = self.manager.loadImSeq('perso','perso.png',512,512)
        self.textids['effects'] = self.manager.loadImSeq('effects','effects.png',512,512)
        self.textids['number'] = self.manager.loadImSeq('number','number.png',512,512)
        self.effectMan = graphic.EffectManager(self.graphic,self.textids['effects'])

        self.textids['title'] = self.manager.loadIm('title','titre.png')
        self.textids['target'] = self.manager.loadIm('target','target.png')
        #self.textids['blur'] = self.manager.loadIm('blur','flou.png')
        self.textids['inventory_hud'] = self.manager.loadIm('inventory_hud','inventory.png')
        self.textids['game_over'] = self.manager.loadIm('game_over','gameover.png')
        self.textids['hud'] = self.manager.loadImSeq('hud','hud.png',512,512)

        print('   -CHARGEMENT DES TEXTURES :',truncate((time.time() - elapsed_time),3))

        self.effects = []

        # DECLARATION DES TAB DE SPRITES

        self.sprids = {}
        self.sprids['target'] = self.graphic.addSpr(self.textids['target'],vis=False,static=True)
        self.graphic.addToGroup(self.sprids['target'],['up'])

        self.aff_target = False
        self.nb_spr_to_draw = [(self.current_size_scr[0]+32*2)//32,(self.current_size_scr[1]+32*2)//32]

        self.sprids['inventory_hud'] = self.graphic.addSpr(self.textids['inventory_hud'],pup.BOX['hud_inventory'][0].pos(),vis=False,static=True)
        #self.inventory_box = ( (31,190) , (550,791) )
        #self.graphic.createGroup('hud-1',11)
        self.graphic.addToGroup(self.sprids['inventory_hud'],['hud'],-1)

        self.selection = 'normal'

        # CREATION SPRITES PARTICULIER (affichage GAME OVER)

        size_game_over_spr = 834,192
        pos_game_over_spr = self.current_size_scr[0]/2-size_game_over_spr[0]/2,self.current_size_scr[1]/2-size_game_over_spr[1]/2
        self.sprids['game_over'] = self.graphic.addSpr(self.textids['game_over'],pos_game_over_spr,vis=False,static=True)
        self.graphic.addToGroup(self.sprids['game_over'],['up'],-1)

        # DECLARATION DES TAB DE LABELS

        self.lblids = {}
        self.lblids['hud'] = {}

        ## CREATION EFFETS
        elapsed_time =time.time()
        self.create_effects()
        print('   -CREATION DES EFFETS :',truncate((time.time() - elapsed_time),3))


        ## INIT

        # keys
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)

        # clicks
        self.clicks = {'L':False,'R':False,'M':[0,0]}
        self.mouse_speed = 0


        self.goodkeys = {key.SPACE : ' ',key.EXCLAMATION : '!',key.DOUBLEQUOTE : '\"',key.HASH : "#"
                        ,key.POUND : '£',key.DOLLAR : '$',key.PERCENT : '%',key.AMPERSAND : '*'
                        ,key.APOSTROPHE : '\'',key.PARENLEFT : '(',key.PARENRIGHT : ')',key.ASTERISK : '*'
                        ,key.PLUS : '+',key.COMMA : '*',key.MINUS : '*',key.PERIOD : '*',key.SLASH : '\\',key._0 : '0'
                        ,key._1 : '1',key._2 : '2',key._3 : '3',key._4 : '4',key._5 : '5',key._6 : '6',key._7 : '7',key._8 : '8',key._9 : '9'
                        ,key.COLON : '*',key.SEMICOLON : '*',key.LESS : '-',key.EQUAL : '=',key.GREATER : '*',key.QUESTION : '?',key.AT : '@'
                        ,key.BRACKETLEFT : '[',key.BACKSLASH : '/',key.BRACKETRIGHT : ']',key.ASCIICIRCUM : '*',key.UNDERSCORE : '_',key.GRAVE : '`'
                        ,key.QUOTELEFT : '<',key.A : 'a',key.B : 'b',key.C : 'c',key.D : 'd',key.E : 'e',key.F : 'f',key.G : 'g',key.H : 'h',key.I : 'i'
                        ,key.J : 'j',key.K : 'k',key.L : 'l',key.M : 'm',key.N : 'n',key.O : 'o',key.P : 'p',key.Q : 'q',key.R : 'r',key.S : 's'
                        ,key.T : 't',key.U : 'u',key.V : 'v',key.W : 'w',key.X : 'x',key.Y : 'y',key.Z : 'z',key.BRACELEFT : '{',key.BAR : '|'
                        ,key.BRACERIGHT : '}',key.ASCIITILDE : '*'
                        ,key.NUM_0 : '0',key.NUM_1 : '1',key.NUM_2 : '2',key.NUM_3 : '3',key.NUM_4 : '4',key.NUM_5 : '5',key.NUM_6 : '6'
                        ,key.NUM_7 : '7',key.NUM_8 : '8',key.NUM_9 : '9',

                        }

        # actions
        self.playing = True
        self.actions = ['menu','loading','showing','nothing','showing2','creating']
        self.action = 0
        self.security = 'admin'

        self.cmd.add(' ',self.actions[self.action])
        #print(self.actions[self.action])


        self.init_menu()

        self.nb = 0

        pyglet.clock.schedule_interval(self.gameloop,0.0000001)
        pyglet.app.run()

    def create_effects(self):

        # CREATION BIG BLUR FOR ALL SCREEN

        self.nb_spr_to_draw_x = self.current_size_scr[0]//tut.SIZE_TILE[0] + 1
        self.nb_spr_to_draw_y = self.current_size_scr[1]//tut.SIZE_TILE[0] + 1


        blur_spending1 = random.choice([i for i in range(5)])
        blur_spending2 = random.choice([i for i in range(blur_spending1+2,11)])

        #print(blur_spending1,blur_spending2)
        terrain = []
        for i in range(self.nb_spr_to_draw_y):
            taby = []
            for j in range(self.nb_spr_to_draw_x):
                taby.append(random.choice([i for i in range(blur_spending1,blur_spending2)]))
            terrain.append(taby)
        self.effects.append(self.effectMan.addEffect('blur%_allscr',terrain,(0,0),-10))

        terrain = []
        for i in range(self.nb_spr_to_draw_y):
            taby = []
            for j in range(self.nb_spr_to_draw_x):
                taby.append(random.choice([i for i in range(blur_spending1,blur_spending2)]))
            terrain.append(taby)
        self.effects.append(self.effectMan.addEffect('blur%2_allscr',terrain,(10,10),-9))

        terrain = []
        for i in range(self.nb_spr_to_draw_y):
            taby = []
            for j in range(self.nb_spr_to_draw_x):
                taby.append(random.choice([1,2,3]))
            terrain.append(taby)
        self.effects.append(self.effectMan.addEffect('blur25_allscr',terrain,(0,0),-8))

        # CREATION WHITE BLUR NEW MAP

        nbx = (3*self.current_size_scr[0]//4)//tut.SIZE_TILE[0]
        nby = (self.current_size_scr[1]//2)//tut.SIZE_TILE[0]
        posx = self.current_size_scr[0]/8
        posy = self.current_size_scr[1]/6

        effect_terrain = []

        #blur_color = random.choice([i for i in range(1,10)])
        for j in range(nby):
            taby = []
            for i in range(nbx):
                taby.append(10)
            effect_terrain.append(taby)

        self.effects.append(self.effectMan.addEffect('blur70_newland',effect_terrain,(posx,posy),-7))
        self.effectMan.unhide('blur70_newland',True)

    def init_menu(self):

        ## OKLM

        self.buttons = {}
        self.actions_menu = ['main','maps','newmap','pause']
        self.action_menu = 0


        ## CREATION SPRITES ET DIFFERENTS LABELS / BUTTONS / WRITINGS

        self.sprids['menu'] = {}
        self.sprids['menu']['all_maps'] = {}

        self.sprids['menu']['title'] = self.specMan.addSpr(self.textids["title"],self.current_size_scr[0]//2-1011//2,(self.current_size_scr[1]//4)*3,'title')
        #thg = #,color=(70, 110, 180,255))
        self.sprids['menu']['play_btn'] = self.specMan.addThg(drawable.LabelButton(self.choice_land,(300,100),'PLAY',
                                                            self.font[0],
                                                            96,
                                                            self.current_size_scr[0]//2,
                                                            self.current_size_scr[1]//2 +100),'play_btn')

        self.sprids['menu']['quickplay_btn'] = self.specMan.addThg(drawable.LabelButton(self.all_in_one,(300,70),'QUICKPLAY',
                                                            self.font[0],
                                                            70,
                                                            self.current_size_scr[0]//2,
                                                            200,
                                                            param='quickplay'),'quickplay_btn')

        self.sprids['menu']['resume_btn'] = self.specMan.addThg(drawable.LabelButton(self.navigate,(300,100),'RESUME',
                                                            self.font[0],
                                                            96,
                                                            self.current_size_scr[0]//2,
                                                            self.current_size_scr[1]//2 +100,
                                                            param='showing'),'resume_btn')

        self.sprids['menu']['quit_btn'] = self.specMan.addThg(drawable.LabelButton(self.get_out,(300,100),'QUIT',
                                                            self.font[1],
                                                            96,
                                                            self.current_size_scr[0]//2,
                                                            self.current_size_scr[1]//2 -150),'quit_btn')

        self.sprids['menu']['main_menu_btn'] = self.specMan.addThg(drawable.LabelButton(self.quit_land,(300,100),'MAIN',
                                                            self.font[0],
                                                            96,
                                                            self.current_size_scr[0]//2,
                                                            self.current_size_scr[1]//2 -400),'main_menu_btn')

        self.sprids['menu']['return_btn'] = self.specMan.addThg(drawable.LabelButton(self.navigate,(200,50),'RETURN',
                                                            self.font[1],
                                                            70,
                                                            3*(self.current_size_scr[0]//4),
                                                            80,(False,'menu')),'return_btn')

        self.sprids['menu']['new_map_btn'] = self.specMan.addThg(drawable.LabelButton(self.navigate,(250,50),'CREATE MAP',
                                                            self.font[0],
                                                            70,
                                                            self.current_size_scr[0]//4,
                                                            80,
                                                            param=('newmap','menu')),'new_map_btn')

        self.sprids['menu']['create_btn'] = self.specMan.addThg(drawable.LabelButton(self.all_in_one,(250,50),'CREATE',
                                                            self.font[0],
                                                            70,
                                                            self.current_size_scr[0]//4,
                                                            80,
                                                            param='creating'),'create_btn')

        self.sprids['menu']['chargement_desc'] = self.specMan.addLabel('... LOADING MAP ASPECTS ...',
                                                            self.font[2],
                                                            30,
                                                            self.current_size_scr[0]//2,
                                                            20,'chargement_desc')


        v = gs.get_version(self.path)
        text = '__ DELTAWORLD version  '+ v + ' __'

        self.sprids['menu']['description'] = self.specMan.addLabel(text.upper(),
                        self.font[2],
                        30,
                        self.current_size_scr[0]//2,
                        20,'description')


        ## WRITTING BAR


        self.sprids['menu']['new_map_wrtgbar'] = self.specMan.addThg(drawable.WritingBar(self.verify_name,(300,100),'enter name here',
                                                            self.font[0],
                                                            96,
                                                            self.current_size_scr[0]//2,
                                                            self.current_size_scr[1]//2),'new_map_wrtgbar')

        self.text_size_land_menu = ['HOLY SHIT IT\'S TOO SMALL 1*1','MINUS 4*4','SMALL 8*8','NORMAL 10*10','FAT 12*12','HUGE 20*20','LEGEND 30*30','hmm.. SERIOUS ? 50*50']
        self.text_size_land_menu_colors = [(50, 225, 175,255),(150,255,150,255),(100,100,255,255),(75,75,75,255),(35,35,35,255),(0,0,0,255),(50, 175, 225,255),(200,100,100,255)]
        self.text_size_land_menu_val = [(1,1),(4,4),(8,8),(10,10),(12,12),(20,20),(30,30),(50,50)]
        self.text_size_land_menu_sel = 0

        self.sprids['menu']['size_land'] = self.specMan.addLabel(self.text_size_land_menu[self.text_size_land_menu_sel],
                                            self.font[0],
                                            96,
                                            self.current_size_scr[0]//2,
                                            self.current_size_scr[1]//2-250,'size_land',self.text_size_land_menu_colors[self.text_size_land_menu_sel])

        self.sprids['menu']['up_size_btn'] = self.specMan.addThg(drawable.LabelButton(self.change_size_land,(75,75),'-',
                                                            self.font[0],
                                                            100,
                                                            self.current_size_scr[0]//4-125,
                                                            self.current_size_scr[1]//2-200,param=False,nobig=True),'up_size_btn')

        self.sprids['menu']['down_size_btn'] = self.specMan.addThg(drawable.LabelButton(self.change_size_land,(75,75),'+',
                                                            self.font[0],
                                                            100,
                                                            3*(self.current_size_scr[0]//4)+125,
                                                            self.current_size_scr[1]//2-200,nobig=True),'down_size_btn')

        ## DECLARATION DES BOUTTONS A AFFICHER LORS DES DIFF MENUS


        self.buttons['main'] = ['play_btn','quit_btn','quickplay_btn']
        self.buttons['maps'] = ['return_btn','new_map_btn']
        self.buttons['newmap'] = ['return_btn','new_map_wrtgbar','create_btn','up_size_btn','down_size_btn']
        self.buttons['pause'] = ['resume_btn','quit_btn','main_menu_btn']



    ### MAIN FUNCTIONS

    def navigate(self,level,threw='game'):

        #print(self.action_menu)

        if threw == 'game':
            if type(level) == type('sdq') and level != self.actions[self.action]:
                while self.actions[self.action] != level:
                    self.action +=1
                    if self.action >= len(self.actions):
                        self.action=0

            elif type(level) == type(True):
                if level:
                    self.action += 1
                    if self.action >= len(self.actions):
                        self.action=0
                else:
                    self.action -= 1
                    if self.action < 0:
                        self.action=len(self.actions)-1
            elif type(level) == type(self.action):
                self.action = level

            #print(self.actions[self.action])

        elif threw == 'menu':


            if type(level) == type('sdq'):
                while self.actions_menu[self.action_menu] != level:
                    self.action_menu += 1
                    if self.action_menu >= len(self.actions_menu):
                        self.action_menu = 0

            elif type(level) == type(True):
                if level:
                    self.action_menu += 1
                    if self.action_menu >= len(self.actions_menu):
                        self.action_menu=0
                else:
                    self.action_menu -= 1
                    if self.action_menu < 0:
                        self.action_menu=len(self.actions_menu)-1

            else:
                self.action_menu = level
            #print(self.action_menu)
            if self.actions_menu[self.action_menu] == 'newmap':
                #print('okilm')
                self.effectMan.unhide('blur70_newland',False)
            else:
                self.effectMan.unhide('blur70_newland',True)

        #print(self.action_menu)

    def all_in_one(self,style,plus=None):

        name = ''

        if style == 'creating':
            if not self.specMan.to_draw['new_map_wrtgbar'].validated:
                print('Name already in use !! you can\'t create antoher land like that !')
                return 0
            else:

                self.effectMan.unhide('blur70_newland',True)
                name = self.specMan.to_draw['new_map_wrtgbar'].text
                self.specMan.to_draw['new_map_wrtgbar'].put_to_zero()

        if style == 'loading' or style == 'quickplay':
            global TAKE_DIRECT_SCREEN,SAVES_PATH
            TAKE_DIRECT_SCREEN = False

            if style == 'loading':
                name = plus
            else:
                name = 'quickplay'


        self.loading = {'name':name}
        self.load_to_do = ['extracting game data',
                        'initialisation of loading',
                        'initialisating sprites and labels',
                        'loading persos',
                        'initialisating hud elements',
                        'initialisating camera',
                        'creating sprites', #GE
                        'creating blur effect map',
                        'resetting camera',
                        'finishing loading',
                        ]
        self.loading['style'] = style

        if style == 'quickplay':

            SAVES_PATH = '/'
            if self.verify_name('quickplay'):
                self.loading['style'] = 'creating'
                self.loading['size'] = (1,1)
            else:
                self.loading['style'] = 'loading'
        elif style == 'creating':

            self.loading['size'] = None

        if self.loading['style'] == 'creating':

            self.creating = {}
            self.create_to_do = ['initialisating creation',
                                'choosing zones',
                                'choosing grounds',
                                'creating noise',
                                'coloring terrain', #GE
                                'placing assets', #GE
                                'verifing terrain',
                                'splitting terrain',
                                'creating persos',
                                'creating bots', #GE
                                'finishing creating',
                                ]
            self.creating['state'] = 0
            self.loading['state'] = 1

            #print(len(self.create_to_do))

        else:
            self.loading['state'] = 0


        self.loading['aff_map'] = [1,1]

        if style == 'quickplay':
            self.loading['aff_map'] = [0,1]


        anc = [*pup.POS['loading_bar']]
        size_lifebar = pup.SIZ['loading_bar'][0]

        self.sprids['loading'] = {}
        self.sprids['loading']['l'] = self.graphic.addSpr(self.textids['hud'][3],anc)
        self.sprids['loading']['r'] = self.graphic.addSpr(self.textids['hud'][3],(anc[0]+size_lifebar,anc[1]))
        self.sprids['loading']['mid'] = self.graphic.addSpr(self.textids['hud'][2],anc)
        self.graphic.modify(self.sprids['loading']['mid'],scale=(size_lifebar/SIZE_TILE,1))
        self.graphic.addToGroup(self.sprids['loading']['l'],['map'],2)
        self.graphic.addToGroup(self.sprids['loading']['r'],['map'],2)
        self.graphic.addToGroup(self.sprids['loading']['mid'],['map'],2)

        self.sprids['loading']['fill'] = self.graphic.addSpr(self.textids['hud'][5],anc)
        self.graphic.modify(self.sprids['loading']['fill'],scale=(0,1))
        self.graphic.addToGroup(self.sprids['loading']['fill'],['map'],1)


        self.loadbar = {}
        self.loadbar['percent'] = 0
        self.loadbar['plus'] = ''

        self.loadbar['nb_ope'] = len(self.load_to_do)
        if self.loading['style'] == 'creating':
            self.loadbar['nb_ope']+= len(self.create_to_do)
            self.loadbar['nb_ope']-=1

        pos = pup.GEN['ax']/2,anc[1]+pup.SIZ['loading_bar'][1]
        self.lblids['loading'] = self.labman.addLabel(self.load_to_do[self.loading['state']],pos \
                        ,font_size=32*pup.GEN['1y'],font_name=self.font[0],anchor=('center','bottom'),color=(0,0,0,255))

        self.labman.addToGroup(self.lblids['loading'],['map'],2)


        self.all_times = {}
        for todo in self.load_to_do:
            self.all_times[todo] = 0
        if self.loading['style'] == 'creating':
            del self.all_times['extracting game data']
            for todo in self.create_to_do:
                self.all_times[todo] = 0

        self.total_time_loading = time.time()

        self.navigate(self.loading['style'])


    ### IN MENU : SELECTION LAND

    def choice_land(self):


        ## DRAW MAPS CHOICES


        # search all lands
        self.all_lands = []

        #verify the existence of saves directory
        if SAVES_PATH[1:-1] not in os.listdir():
            os.makedirs(self.path+SAVES_PATH)

        #adding all lands
        cmdd = os.popen('dir '+self.path+'\\'+SAVES_PATH[1:-1] +' /B /TA /O-D',)
        #print('dir '+self.path+'\\'+SAVES_PATH[1:-1] +' /B /TA /O-D')
        total = cmdd.read().split('\n')
        cmdd.close()
        #print(total)

        for name in total:
            self.all_lands.append(name)



        not_a_land = []
        #print('all_lands',self.all_lands)
        for name in self.all_lands:
            try:
                with open(self.path+SAVES_PATH+name+'/perso','r'):
                    #print(name,'successful')
                    a=0
            except:
                not_a_land.append(name)
                #print(name,'not there')

        for name in not_a_land:
            self.all_lands.remove(name)


        # creating btns
        self.buttons['maps'] = ['return_btn','new_map_btn']

        for name in self.sprids['menu']['all_maps']:
            self.specMan.to_draw[self.sprids['menu']['all_maps'][name]].delete()

        self.sprids['menu']['all_maps']={}

        self.defil_menu = 0

        if len(self.all_lands) > 5:

            self.sprids['menu']['defil_btn_R'] = self.specMan.addThg(drawable.LabelButton(self.defil_lands,(200,200),'>',
                                                                self.font[0],
                                                                96,
                                                                4*self.current_size_scr[0]//5,
                                                                self.current_size_scr[1]//2,
                                                                param=1),'defil_btn_R')
            self.sprids['menu']['defil_btn_L'] = self.specMan.addThg(drawable.LabelButton(self.defil_lands,(200,200),'<',
                                                                self.font[0],
                                                                96,
                                                                self.current_size_scr[0]//5,
                                                                self.current_size_scr[1]//2,
                                                                param=-1),'defil_btn_L')
            self.buttons['maps'].append('defil_btn_R')
            self.buttons['maps'].append('defil_btn_L')

        if self.all_lands == []:

            self.sprids['menu']['all_maps']['map'+str(0)+'_btn'] = self.specMan.addLabel('NO MAPS',
                                                                self.font[0],
                                                                96,
                                                                self.current_size_scr[0]//2,
                                                                self.current_size_scr[1]//2,'map'+str(0)+'_btn')
            self.buttons['maps'].append('map'+str(0)+'_btn')
        else:
            for i in range(len(self.all_lands)):
                self.sprids['menu']['all_maps']['map'+str(i)+'_btn'] = self.specMan.addThg(drawable.LabelButton(self.all_in_one,(200,60),self.all_lands[i],
                                                            self.font[0],
                                                            70,
                                                            self.current_size_scr[0]//2,
                                                            self.current_size_scr[1]//2 +200 - (i%5)*150,
                                                            param=['loading',self.all_lands[i]]),'map'+str(i)+'_btn')
                if i < 5:
                    self.buttons['maps'].append('map'+str(i)+'_btn')

        self.navigate(1,'menu')

    def defil_lands(self,n):
        self.defil_menu += n
        if self.defil_menu <0:
            self.defil_menu = len(self.all_lands)//5
        elif self.defil_menu > len(self.all_lands)//5:
            self.defil_menu = 0
        self.buttons['maps'] = ['return_btn','new_map_btn','defil_btn_R','defil_btn_L']

        for i in range(self.defil_menu*5,len(self.all_lands)):
            if i< self.defil_menu*5 + 5:
                self.buttons['maps'].append('map'+str(i)+'_btn')

        #print(self.buttons['maps'])

    def change_size_land(self,plus=True):

        #print('plus',plus)
        key = self.text_size_land_menu_sel
        if plus:
            key+=1
            if key >= len(self.text_size_land_menu):
                key=0
        else:
            key-=1
            if key < 0:
                key=len(self.text_size_land_menu)-1
        self.text_size_land_menu_sel = key
        self.sprids['menu']['size_land'] = self.specMan.addLabel(self.text_size_land_menu[key],
                                                self.font[0],
                                                96,
                                                self.current_size_scr[0]//2,
                                                self.current_size_scr[1]//2-250,'size_land',self.text_size_land_menu_colors[key])

    def verify_name(self,name):

        ## renvoie True si il n'y a pas déjà de map avec ce nom
        ## False sinon

        try :
            f = open(self.path+SAVES_PATH+name+'/perso','r')
            f.close()
            return False
        except:
            return True


    ### IN LOADING : CREATING/LOADING T4ABS

    def load_land(self,name):

        #name = self.terrain.name

        elapsed_time = time.time()
        # LOADING TERRAIN

        tab_perso = []
        tab_map = []
        tab_land = []

        with open(self.path+SAVES_PATH+name+'/perso','r') as f:
            tab_perso = json.load(f)

        with open(self.path+SAVES_PATH+name+'/card','r') as f:
            tab_map = json.load(f)

        #self.terrain.Bioms = []
        with open(self.path+SAVES_PATH+name+'/land','r') as f:
            tab_land = json.load(f)


        print('   -CHARGEMENT DU TERRAIN :',truncate((time.time() - elapsed_time),3))
        #print(tab_perso,'\n', tab_map ,'\n', tab_land,'\n', name)
        return tab_perso, tab_map , tab_land, name


    ### IN LOADING : USING T4ABS

    def create_biom_sprites(self,biom):


        i,j = biom

        for lvl in range(len(self.terrain.Bioms[j][i].ground)):
            for y in range(len(self.terrain.Bioms[j][i].ground[lvl])):
                for x in range(len(self.terrain.Bioms[j][i].ground[lvl][y])):
                    #print(self.terrain.Bioms[j][i].ground[lvl])
                    if self.terrain.Bioms[j][i].ground[lvl][y][x] != 0:

                        #posx = self.admin_cam[0] -self.camera[0] + self.cursor_x +tut.SIZE_TILE[0]*x + i*tut.SIZE_BIOM[0]*tut.SIZE_TILE[0]
                        #posy = self.admin_cam[1] -self.camera[1] + self.cursor_y + tut.Y_DEP - tut.SIZE_TILE[0]*y + tut.Y_DEP_BIOM - j*tut.SIZE_BIOM[1]*tut.SIZE_TILE[0]

                        #print(tut.from_bcx_to_xy(tut.BCX_Pos((i,j),(x,y))))
                        #print(tut.from_pxpos_to_realpos( tut.from_bcx_to_xy(tut.BCX_Pos((i,j),(x,y)))))
                        pos = tut.from_bcx_to_pxx((i,j),(x,y))
                        #print( (posx,posy) == pos.xy()  )

                        self.sprids['bioms'][i,j][lvl][x,y] = self.graphic.addSpr(self.textids['ground'][self.terrain.Bioms[j][i].ground[lvl][y][x]],pos,vis=False)
                        #print(self.sprids['bioms'][i,j][x,y])
                        if not (i,j) in self.bioms_to_print:
                            self.graphic.sprites[self.sprids['bioms'][i,j][lvl][x,y]].visible=False
                        self.graphic.addToGroup(self.sprids['bioms'][i,j][lvl][x,y],[None,None,lvl])

    ### AFTER PLAYING : SAVE, QUITING LAND

    def save_land(self):

        #t = [1,1,1,1,0,0,{}]
        elapsed_time = time.time()
        success = True


        tab_perso = []

        for perso in self.persos:

            dic = {}

            dic['name'] = self.persos[perso].name
            dic['life'] = (self.persos[perso].life,self.persos[perso].max_life)

            dic['pos'] = []
            for x in self.persos[perso].pos.bcx():
                dic['pos']+= [*x]
            dic['pos']+= [self.persos[perso].pos.lvl()]

            if type(self.persos[perso]) == pso.Perso:
                dic['type'] = 'Perso'
            else:
                dic['type'] = 'Living'

            dic['specie'] = self.persos[perso].specie
            dic['skin_dic'] = self.persos[perso].skin_dic

            if perso == self.perso:
                dic['inventory'] = self.persos[perso].get_inv()
                dic['main'] = True
            else:
                dic['main'] = False

            dic['id'] = perso

            tab_perso.append(dic)

        try :
            with open(self.path+SAVES_PATH+self.terrain.name+'/perso','w') as f:
                json.dump(tab_perso,f)
        except:
            os.makedirs(self.path+SAVES_PATH+self.terrain.name)
            with open(self.path+SAVES_PATH+self.terrain.name+'/perso','w') as f:
                json.dump(tab_perso,f)

        otre_save_path = SAVES_PATH[1:-1]

        os.system('mkdir '+self.path+'\\'+otre_save_path+'\\'+self.terrain.name+ '\\t') #afin de mettre la map en dernière modifiée
        os.system('rmdir '+self.path+'\\'+otre_save_path+'\\'+self.terrain.name+ '\\t')

        with open(self.path+SAVES_PATH+self.terrain.name+'/card','w') as f:
            json.dump(self.terrain.map,f)
        with open(self.path+SAVES_PATH+self.terrain.name+'/land','w') as f:
            terrain = []
            for j in range(len(self.terrain.Bioms)):
                rangey = []
                for i in range(len(self.terrain.Bioms[j])):
                    biom = self.terrain.Bioms[j][i]
                    biom_ter = []
                    for lvl in range(len(biom.ground)):
                        biom_ter.append(biom.ground[lvl])

                    """if i == 0 and j == 0:
                        print(biom_ter)"""
                    rangey.append(biom_ter)
                terrain.append(rangey)
                #f.write('\n')
            json.dump(terrain,f)
            #print(terrain)


        print('   -SAUVEGARDE DE LA PARTIE :',truncate((time.time() - elapsed_time),3))
        """if success:
            print('La partie',self.terrain.name,'a bien été sauvegardée')
        else:
            print('Echec de sauvegarde de',self.terrain.name)"""

    def quit_land(self,save=True):
        global SAVES_PATH

        self.navigate('menu')
        self.navigate('main','menu')
        if save:
            self.save_land()

        # on efface tous les sprites qui ne sont pas statiques ni effets
        self.graphic.delete()
        #print(self.graphic.sprites)

        #print(get_key_from_values(self.sprids,errors))

        if 'inventory_hud' in self.sprids:
            self.graphic.unhide(self.sprids['inventory_hud'],True)

        if self.effectMan.hasEffect('blur50_map'):
            self.effectMan.unhide('blur50_map',True)


        if hasattr(self, 'creating'):
            del self.creating
            del self.create_to_do
            del self.loading
            del self.load_to_do
            self.graphic.delete(self.sprids['loading'])
            self.labman.delete(self.lblids['loading'])
            del self.sprids['loading']
            del self.lblids['loading']

        elif hasattr(self, 'loading'):
            del self.loading
            del self.load_to_do
            self.graphic.delete(self.sprids['loading'])
            self.labman.delete(self.lblids['loading'])
            del self.sprids['loading']
            del self.lblids['loading']


        #print(errors)

        # on efface les labels du hud qui étaient affichés
        #print(self.lblids)
        self.labman.delete(self.lblids['hud'])

        # on supprime le terrain
        self.terrain = terrain.TerManager(0,0,None)

        # on supprime les persos
        self.persos = {}

        # on supprime les ids de sprites en mémoire
        self.sprids['persos'] = {}
        self.sprids['bioms'] = {}
        self.sprids['map'] = {}
        self.sprids['hud'] = {}

        # on supprime les ids de labels en mémoire
        self.lblids['hud'] = {}

        SAVES_PATH = '/saves/'
        self.in_land = False

        #print(self.actions[self.action])

    ### ONCE FUNCTIONS

    def create_image(self):
        global TAKE_DIRECT_SCREEN

        print('creation de l\'image')
        elapsed_time = time.time()
        bigmap = pil.Image.new('RGBA',(tut.SIZE_TILE[0]*tut.SIZE_BIOM[0]*tut.SIZE_TERRAIN[0],tut.SIZE_TILE[1]*tut.SIZE_BIOM[1]*tut.SIZE_TERRAIN[1]),(0,0,0,0))

        for j in range(tut.SIZE_TERRAIN[1]):
            for i in range(tut.SIZE_TERRAIN[0]):
                #print(i,j)
                for lvl in range(tut.DEPTH_BIOM):
                    #print('   ',lvl)
                    for y in range(tut.SIZE_BIOM[1]):
                        for x in range(tut.SIZE_BIOM[0]):

                            bcx_pos = tut.BCX_Pos((i,j),(x,y),l=lvl)
                            if self.terrain.get_case(bcx_pos) != 0:
                                xx,yy = tut.from_bcx_to_xy(bcx_pos).xy()
                                data = self.manager.rawdata[self.textids['ground'][self.terrain.get_case(bcx_pos)]]
                                im = pil.Image.frombytes('RGBA', tut.SIZE_TILE, data)
                                #print(xx,yy)
                                bigmap.alpha_composite(im,(xx,yy))

        """try :
            with open(self.path+SAVES_PATH+self.terrain.name+'/perso','w') as f:
                a=0
        except:
            os.makedirs(self.path+SAVES_PATH+self.terrain.name)"""

        if self.terrain.name not in os.listdir(self.path+SAVES_PATH):
            os.makedirs(self.path+SAVES_PATH+self.terrain.name+'/')

        #imag_path = self.path+SAVES_PATH+'maps/'

        bigmap = bigmap.transpose(pil.Image.FLIP_TOP_BOTTOM)
        ## Z:\DESKTOP\CODING\delta2D\saves\maps\genv3
        if TAKE_DIRECT_SCREEN:
            TAKE_DIRECT_SCREEN = False

        bigmap.save(self.path+SAVES_PATH+self.terrain.name+'/'+self.terrain.name+'.png')

        print('   -CREATION DU SCREENSHOT :',truncate((time.time() - elapsed_time),3))
        print(self.terrain.name+'.png','saved well')

    def nothing(self):
        a=0

    def get_out(self):
        if self.in_land:
            #self.create_image()
            self.save_land()
        self.playing = False

    def verif(self,biom):

        err = 0
        for lvl in range(len(self.terrain.Bioms[biom[1]][biom[0]].ground)):
            for y in range(len(self.terrain.Bioms[biom[1]][biom[0]].ground[lvl])):
                for x in range(len(self.terrain.Bioms[biom[1]][biom[0]].ground[lvl][y])):

                    case = False
                    spr = False
                    if self.terrain.get_case(tut.BCX_Pos(biom,(x,y)),lvl) != 0:
                        case = True
                    if self.sprids['bioms'][biom][lvl][(x,y)] != 0:
                        spr = True

                    if not spr==case:
                        err += 1
                        print('verif',biom,':  lvl',lvl,'xy',x,y,'   case',self.terrain.get_case(tut.BCX_Pos(biom,(x,y)),lvl),'  spr',self.sprids['bioms'][biom][lvl][(x,y)] ,'  ',spr==case )
        print('verif biom',biom,':',err,'errors')

    def clear_sprites(self,biom):

        #self.verif(biom)

        i,j = biom
        for lvl in self.sprids['bioms'][i,j]:
            for cas in self.sprids['bioms'][i,j][lvl]:
                if self.sprids['bioms'][i,j][lvl][cas] != 0:
                    self.graphic.delete(self.sprids['bioms'][i,j][lvl][cas])

        self.sprids['bioms'][i,j] = {}
        for lvl in range(tut.DEPTH_BIOM):
            self.sprids['bioms'][i,j][lvl] = {}
            for x in range(tut.SIZE_BIOM[0]):
                for y in range(tut.SIZE_BIOM[1]):
                    self.sprids['bioms'][i,j][lvl][x,y] = 0

    def reset_camera(self,dir):

        #objx , objy = self.camera_obj
        objx , objy = self.camera.obj.xy()
        #objtilex,objtiley = self.camera_obj_tile

        if 'x' in dir:

            if self.persos[self.perso].px_pos.x > self.camera.pos.x:
                delta = self.current_size_scr[0]//6
            else:
                delta = -self.current_size_scr[0]//6

            objx = self.persos[self.perso].px_pos.x+delta
            #objtilex = [self.persos[self.perso].pos.x[0],self.persos[self.perso].pos.x[1],self.persos[self.perso].pos.x[2]]

        if 'y' in dir:

            if self.persos[self.perso].px_pos.y > self.camera.pos.y:
                delta = self.current_size_scr[1]//6
            else:
                delta = -self.current_size_scr[1]//6

            objy = self.persos[self.perso].px_pos.y+delta
            #objtiley = [self.persos[self.perso].pos.y[0],self.persos[self.perso].pos.y[1],self.persos[self.perso].pos.y[2]]

        if 'ulti' in dir:

            objx = self.persos[self.perso].px_pos.x
            objy = self.persos[self.perso].px_pos.y
            #objtilex = [thg[0] for thg in self.persos[self.perso].pos.bcx()]
            #objtiley = [thg[1] for thg in self.persos[self.perso].pos.bcx()]
            #self.camera_tile = [objtilex,objtiley]

        self.camera.obj = tut.XY_Vec(objx,objy)
        #self.camera_obj = [objx,objy]
        #self.camera_obj_tile = [objtilex,objtiley]

    def reset_biom(self,biom):

        i,j = biom
        self.clear_sprites((i,j))

        #biom = terrain.emptyBiom(tut.SIZE_BIOM)
        #choice = random.choice(range(len(self.saved_terrains)))
        #biom.ground = modifyPlatform(self.saved_terrains[choice],(tut.SIZE_BIOM[0]-1),(tut.SIZE_BIOM[1]-1))
        #print(biom.ground)

        #p,map,biom,n = self.create_land('',(1,1))
        map,biom = createMap((1,1),tut.SIZE_BIOM,tut.DEPTH_BIOM,style=1)
        #print(biom[0][0])
        biom = terrain.Biom(biom[0][0])
        #print(self.terrain.Bioms[j][i].ground)

        self.terrain.set_Biom(i,j,biom,map[0][0])

        self.generated_terrains+=1
        print(self.generated_terrains,'generated bioms')

        for lvl in range(len(self.terrain.Bioms[j][i].ground)):
            for y in range(len(self.terrain.Bioms[j][i].ground[lvl])):
                for x in range(len(self.terrain.Bioms[j][i].ground[lvl][y])):
                    if self.terrain.Bioms[j][i].ground[lvl][y][x] != 0:

                        #posx = self.admin_cam[0] -self.camera[0] + self.cursor_x +tut.SIZE_TILE[0]*x + i*tut.SIZE_BIOM[0]*tut.SIZE_TILE[0]
                        #posy = self.admin_cam[1] -self.camera[1] + self.cursor_y + tut.Y_DEP - tut.SIZE_TILE[0]*y + tut.Y_DEP_BIOM - j*tut.SIZE_BIOM[1]*tut.SIZE_TILE[0]

                        pos = tut.from_bcx_to_pxx((i,j),(x,y))
                        #print( (posx,posy) == pos.xy()  )

                        self.sprids['bioms'][i,j][lvl][(x,y)] = self.graphic.addSpr(self.textids['ground'][self.terrain.Bioms[j][i].ground[lvl][y][x]],pos)
                        self.graphic.addToGroup(self.sprids['bioms'][i,j][lvl][x,y],[None,None,lvl])

        # reset map miniature
        self.graphic.delete(self.sprids['map'][i,j])
        self.sprids['map'][i,j] = self.graphic.addSpr(self.textids['ground'][self.terrain.map[j][i]],tut.get_pos_map_biom((i,j),self.current_size_scr),vis=self.aff_map[0])
        self.graphic.addToGroup(self.sprids['map'][i,j],['map'])

        #self.start_playing()

        #self.verif((i,j))

    def selector_modify(self,pos,btn,test=False,val=-1):

        pos = tut.from_real_to_pxpos(tut.XY_Pos(*pos))
        b,c,p = tut.from_xy_to_bcx(pos).bcx()

        valfin = None

        if not test:
            if self.selector[2] == btn and self.selector[1] == [b,c] and val== -1:
                self.selector[0] += 1
            elif val != -1:
                self.selector[0] = val
            else:
                self.selector = [0,[b,c],btn]

            time_nec = self.persos[self.perso].get_action_time(btn)
            if self.selector[0] >= time_nec:
                self.persos[self.perso].act(pos,btn)
                self.selector[0] = 0

            instant = (time_nec/8)
            if instant != 0:
                nb_skin = int(self.selector[0]//instant)
                valfin = nb_skin
                if nb_skin != (self.selector[0]-1)//(time_nec/8):
                    if (b,c) in self.sprids['cursors']['select']:
                        self.sprids['cursors']['select'][b,c].set_text(16+nb_skin)
                        #self.graphic.set_text(self.sprids['cursors']['select'][(b,c)],self.textids['effects'][16+nb_skin])
            else:
                if (b,c) in self.sprids['cursors']['select']:
                    if self.clicks[btn] != False:
                        self.sprids['cursors']['select'][b,c].set_text(16+7)
                        valfin = 7
                        #self.graphic.set_text(self.sprids['cursors']['select'][(b,c)],self.textids['effects'][16+7])
                    else:
                        self.sprids['cursors']['select'][b,c].set_text(16)
                        valfin = 0
                        #self.graphic.set_text(self.sprids['cursors']['select'][(b,c)],self.textids['effects'][16])

        else:

            valfin = None
            if not self.selector[1] == [b,c]:
                self.selector[0],self.selector[1] = 0,[b,c]

        return (b,c),valfin

    def get_current_screen(self):

        x,y = self.get_location()
        for i in range(len(self.screens)):
            scr = self.screens[i]
            if (x >= scr.x and x <= scr.x + scr.width) and (y >= scr.y and y <= scr.y + scr.height):
                return scr
        return self.screens[0]


    # ONCE FUNCTIONS GAMEPLAY

    def init_hud(self):

        """
        ELEMENTS DU HUD:

            -Nom du perso
            -Barre de vie

        +Nametags

        """

        anc = pup.POS['hud_healthbar']

        size_lifebar = SIZE_TILE*(self.persos[self.perso].max_life/10)
        size_fill = SIZE_TILE*(self.persos[self.perso].life/10)

        self.sprids['hud']['life_bar'] = {}
        self.sprids['hud']['life_bar']['l'] = self.graphic.addSpr(self.textids['hud'][3],anc,vis=self.aff_hud)
        self.sprids['hud']['life_bar']['r'] = self.graphic.addSpr(self.textids['hud'][3],(anc[0]+size_lifebar,anc[1]),vis=self.aff_hud)
        self.sprids['hud']['life_bar']['mid'] = self.graphic.addSpr(self.textids['hud'][2],anc,vis=self.aff_hud)
        self.graphic.modify(self.sprids['hud']['life_bar']['mid'],scale=(size_lifebar/SIZE_TILE,1))
        self.graphic.addToGroup(self.sprids['hud']['life_bar']['l'],['hud'])
        self.graphic.addToGroup(self.sprids['hud']['life_bar']['r'],['hud'])
        self.graphic.addToGroup(self.sprids['hud']['life_bar']['mid'],['hud'])

        self.sprids['hud']['life_bar']['fill'] = self.graphic.addSpr(self.textids['hud'][4],anc,vis=self.aff_hud)
        self.graphic.modify(self.sprids['hud']['life_bar']['fill'],scale=(size_fill/SIZE_TILE,1))
        self.graphic.addToGroup(self.sprids['hud']['life_bar']['fill'],['hud'],-1)


        diff = 1*pup.GEN['1y'] # difference de hauteur
        pos = (anc[0],anc[1]+self.graphic.spr(self.sprids['hud']['life_bar']['l']).height+diff)
        self.lblids['hud']['perso_name'] = self.labman.addLabel(self.persos[self.perso].name,pos,vis=self.aff_hud,font_size=32*pup.GEN['1y'],font_name=choice(self.font))
        self.labman.addToGroup(self.lblids['hud']['perso_name'],['hud'],1)
        #self.labman.unhide(self.lblids['hud']['perso_name'],True)

    def actualise_hud(self):

        anc = pup.POS['hud_healthbar']

        size_lifebar = SIZE_TILE*(self.persos[self.perso].max_life/10)
        size_fill = SIZE_TILE*(self.persos[self.perso].life/10)


        self.graphic.unhide(self.sprids['hud'],not self.aff_hud)
        self.labman.unhide(self.lblids['hud'],not self.aff_hud)
        self.labman.set_text(self.lblids['hud']['perso_name'],self.persos[self.perso].name)
        self.graphic.modify(self.sprids['hud']['life_bar']['r'],(anc[0]+size_lifebar,anc[1]))
        self.graphic.modify(self.sprids['hud']['life_bar']['fill'],scale=(size_fill/SIZE_TILE,1))
        self.graphic.modify(self.sprids['hud']['life_bar']['mid'],scale=(size_lifebar/SIZE_TILE,1))

    def game_over(self):
        print('game over sale noob')
        #self.navigate('gameover')

    ### PYGLET FUNCTIONS

    def on_key_press(self,symbol,modifiers):

        if not (self.actions[self.action] == 'menu' and self.actions_menu[self.action_menu] == 'newmap' and self.specMan.to_draw['new_map_wrtgbar'].selected):

            #toggle fullscreen
            if symbol == key.F11:
                #print(self.fscreen)
                if self.fscreen:
                    self.fscreen = False
                    self.set_fullscreen(False)
                    self.set_size(self.size_scr[0],self.size_scr[1])
                    self.current_size_scr = self.size_scr
                    self.on_my_resize()
                else:
                    self.fscreen = True
                    used_screen=self.get_current_screen()
                    self.set_fullscreen(screen=used_screen)
                    self.size_fullscr = [used_screen.width,used_screen.height]
                    self.current_size_scr = self.size_fullscr
                    self.on_my_resize()

                self.nb_spr_to_draw = [(self.current_size_scr[0]+32*2)//32,(self.current_size_scr[1]+32*2)//32]

            #toggle the cmd
            elif symbol == key.LALT:
                self.aff_cmd = not self.aff_cmd

            #toggle target
            elif symbol == key.T:
                self.aff_target = not self.aff_target
                self.graphic.unhide(self.sprids['target'],not self.aff_target)

            #defil mode (un peu broken)
            elif symbol == key.A:
                if False:

                    if self.keys[key.LSHIFT]:
                        self.action -= 1
                        if self.action < 0:
                            self.action = len(self.actions) - 1

                    else:
                        self.action += 1
                        if self.action >= len(self.actions):
                            self.action = 0

                    print(self.actions[self.action])
                    self.cmd.add(' ',self.actions[self.action])

            #affiche les différents OrderedGroup d'affichage
            elif symbol == key.G:

                print('\nYOU ASKED TO PRINT GROUPS AND THEIR ORGANISATION:')

                print('  will be displayed in descending order like that : order,name\n')

                tab = []

                orders_sorted = sorted(self.group_manager.names_wo,reverse=True)

                for order in orders_sorted:

                    say = str(order)
                    say += (6-len(say))*' '
                    say +=self.group_manager.names_wo[order]
                    print(say)
                print('')

            #renouvelle les effets
            elif symbol == key.M:
                a=0
                self.create_effects()

            #print la position de la souris
            elif symbol == key.K:
                print(self.clicks['M'])

            #affiche quel écran est utilisé
            elif symbol == key.L:
                print('screen :',self.get_current_screen())
                print('size :',self.get_size())


            elif self.in_land:
                #cree un screenshot de la map entière
                if symbol == key.F3:
                    self.create_image()

                #ajoute enleve de la vie au perso aleatoirement
                elif symbol == key.V:
                    self.persos[self.perso].adelife((random.random()*2 -1)*self.persos[self.perso].max_life)

                #ajoute enleve de la maxvie au perso aleatoirement
                elif symbol == key.B:
                    self.persos[self.perso].adelife_max((random.random() -0.5)*20)

                elif symbol == key.R:

                    self.persos[self.perso].name = input('\nEntrez un nouveau nom pour le personnage : ')

                elif symbol == key.N:

                    print('nothing yet')


        if self.actions[self.action] == 'showing' or self.actions[self.action] == 'showing2' :

            if symbol == key.ESCAPE:
                self.navigate('pause','menu')
                self.navigate('menu')

            elif symbol == key.TAB:
                self.aff_map[0] = not self.aff_map[1]

            elif symbol == key.U:
                self.admin_cam.pos = tut.XY_Vec(0,0)

            elif symbol == key.W:
                for pers in self.persos:
                    self.persos[pers].show_line = not self.persos[pers].show_line
                    for typ in self.sprids['persosplus']:
                        for sprid in self.sprids['persosplus'][typ]:
                            self.graphic.unhide(sprid,not self.persos[pers].show_line)

            elif symbol == key.I:
                #print(self.persos[self.perso].aff_inv)
                self.graphic.unhide(self.sprids['inventory_hud'],self.persos[self.perso].aff_inv)
                self.sprids['cursors']['invent_select'].unhide(self.persos[self.perso].aff_inv)
                if not self.persos[self.perso].aff_inv:
                    if self.selection == 'inventory':
                        for thg in self.sprids['cursors']['inv_select']:
                            self.sprids['cursors']['inv_select'][thg].unhide(self.persos[self.perso].aff_inv)
                else:
                    for thg in self.sprids['cursors']['inv_select']:
                        self.sprids['cursors']['inv_select'][thg].unhide(self.persos[self.perso].aff_inv)
                #self.graphic.unhide(self.sprids['hud']['inv_select'],self.persos[self.perso].aff_inv)

                self.persos[self.perso].toggle_inv()

        elif self.actions[self.action] == 'menu':

            if symbol == key.ESCAPE:
                if self.actions_menu[self.action_menu] == 'pause':
                    self.navigate('showing')
                elif self.actions_menu[self.action_menu] == 'main':
                    self.get_out()
                else:
                    self.navigate(False,'menu')

            if self.actions_menu[self.action_menu] == 'newmap' and self.specMan.to_draw['new_map_wrtgbar'].selected:

                if symbol in self.goodkeys:
                    result = ''
                    if self.keys[key.LSHIFT]:
                        result = self.goodkeys[symbol].upper()
                    else:
                        result = self.goodkeys[symbol].lower()
                    self.specMan.to_draw['new_map_wrtgbar'].add_letter(result)

                elif symbol == key.BACKSPACE:
                    self.specMan.to_draw['new_map_wrtgbar'].del_letter()
                elif symbol == key.RETURN:
                    self.specMan.to_draw['new_map_wrtgbar'].he_tried_to_validate_XO()

        elif self.actions[self.action] in ['loading','creating']:
            if symbol == key.ESCAPE:
                self.quit_land(False)

    def on_mouse_motion(self,x,y,dx,dy):

        self.clicks['M'] = [x,y]
        self.mouse_speed = module(dx,dy)
        #print(module(dx,dy))

        if self.actions[self.action] == 'menu':

            self.boxes_boutons = []
            for name in self.buttons[self.actions_menu[self.action_menu]]:
                if type(self.specMan.to_draw[name]) == drawable.LabelButton:
                    self.boxes_boutons.append(self.specMan.to_draw[name].get_box())
                else:
                    self.boxes_boutons.append([0,0,-10,-10])

            if self.keys[key.W]:
                print(self.boxes_boutons,(x,y))

            selected = tut.colli_ABP_mult(self.boxes_boutons,(x,y))
            if selected == None: #aucun boutton selectionné
                for name in self.buttons[self.actions_menu[self.action_menu]]:
                    if type(self.specMan.to_draw[name]) == drawable.LabelButton:
                        self.specMan.to_draw[name].the_mouse_is_not_here_anymore()
            else: #un bouton selected
                nameSel = self.buttons[self.actions_menu[self.action_menu]][selected]
                for name in self.buttons[self.actions_menu[self.action_menu]]:
                    if name == nameSel:
                        self.specMan.to_draw[name].the_mouse_is_here()
                    else:
                        if type(self.specMan.to_draw[name]) == drawable.LabelButton:
                            self.specMan.to_draw[name].the_mouse_is_not_here_anymore()

        elif self.actions[self.action] == 'showing' and self.in_land:


            if self.persos[self.perso].aff_inv and (tut.colli_ABP_XY(pup.BOX['hud_inventory'][0],(x,y)) or tut.colli_ABP_XY(pup.BOX['hud_inventory'][1],(x,y))):
                if self.selection != 'inventory':
                    self.selection = 'inventory'
                for thg in self.sprids['cursors']['select']:
                    self.sprids['cursors']['select'][thg].unhide(True)
            elif self.selection != 'normal':
                self.selection = 'normal'
                for thg in self.sprids['cursors']['inv_select']:
                    self.sprids['cursors']['inv_select'][thg].unhide(True)

            pos = tut.from_real_to_pxpos(tut.XY_Pos(x,y))
            if self.selection == 'normal':
                self.persos[self.perso].select(pos)
            elif self.selection == 'inventory':
                self.persos[self.perso].in_inv_select((x,y))

            oldskin = self.persos[self.perso].skin
            self.persos[self.perso].update_skin(pos)

            #print('bouging')

    def on_mouse_drag(self,x, y, dx, dy, buttons, modifiers):

        self.clicks['M'] = [x,y]
        if self.actions[self.action] == 'showing':


            if self.persos[self.perso].aff_inv and (tut.colli_ABP_XY(pup.BOX['hud_inventory'][0],(x,y)) or tut.colli_ABP_XY(pup.BOX['hud_inventory'][1],(x,y))):
                if self.selection != 'inventory':
                    self.selection = 'inventory'
                for thg in self.sprids['cursors']['select']:
                    self.sprids['cursors']['select'][thg].unhide(True)
                #self.graphic.unhide(self.sprids['cursors']['select'],True)
            elif self.selection != 'normal':
                self.selection = 'normal'
                for thg in self.sprids['cursors']['inv_select']:
                    self.sprids['cursors']['inv_select'][thg].unhide(True)
                #self.graphic.unhide(self.sprids['hud']['inv_select'],True)

            pos = tut.from_real_to_pxpos(tut.XY_Pos(x,y))
            if self.selection == 'normal':
                self.persos[self.perso].select(pos)
                self.selector_modify((x,y),None,True)
            elif self.selection == 'inventory':
                self.persos[self.perso].in_inv_select((x,y))

            oldskin = self.persos[self.perso].skin
            self.persos[self.perso].update_skin(pos)

        if buttons == pyglet.window.mouse.RIGHT :
            self.clicks['R'] = [x,y]
        elif buttons == pyglet.window.mouse.LEFT :
            self.clicks['L'] = [x,y]

    def on_mouse_press(self,x, y, button, modifiers):

        if button == pyglet.window.mouse.RIGHT :
            self.clicks['R'] = [x,y]
        elif button == pyglet.window.mouse.LEFT :
            self.clicks['L'] = [x,y]


        if self.actions[self.action] == 'menu':
            for name in self.buttons[self.actions_menu[self.action_menu]]:
                if type(self.specMan.to_draw[name]) == drawable.LabelButton:
                    if self.specMan.to_draw[name].here:
                        self.specMan.to_draw[name].i_am_pressed()
                elif type(self.specMan.to_draw[name]) == drawable.WritingBar:
                    if not (x>= self.specMan.to_draw[name].x - self.specMan.to_draw[name].box[0] and x<= self.specMan.to_draw[name].x + self.specMan.to_draw[name].box[0] and y>= self.specMan.to_draw[name].y - self.specMan.to_draw[name].box[1] and y<= self.specMan.to_draw[name].y + self.specMan.to_draw[name].box[1] ):
                        if self.specMan.to_draw[name].selected:
                            self.specMan.to_draw[name].he_tried_to_validate_XO()

        elif self.actions[self.action] == 'showing':
            if button == pyglet.window.mouse.LEFT and self.selection == 'inventory':
                self.persos[self.perso].in_inv_grab()

    def on_mouse_release(self,x, y, button, modifiers):

        if button == pyglet.window.mouse.RIGHT :
            self.clicks['R'] = False
        elif button == pyglet.window.mouse.LEFT :
            self.clicks['L'] = False

        if self.actions[self.action] == 'menu':
            for name in self.buttons[self.actions_menu[self.action_menu]]:
                if type(self.specMan.to_draw[name]) == drawable.LabelButton:
                    if self.specMan.to_draw[name].pressed == True:
                        #print(name,type(self.specMan.to_draw[name]),type(self.specMan.to_draw['new_map_wrtgbar']))
                        self.specMan.to_draw[name].i_am_released()

                        ## on reverifie si la souris est encore sur un btn après validation de l'autre
                        self.on_mouse_motion(*self.clicks['M'],0,0)


                elif type(self.specMan.to_draw[name]) == drawable.WritingBar:
                    #print(name,type(self.specMan.to_draw[name]),type(self.specMan.to_draw['new_map_wrtgbar']))
                    if x>= self.specMan.to_draw[name].x - self.specMan.to_draw[name].box[0] and x<= self.specMan.to_draw[name].x + \
                    self.specMan.to_draw[name].box[0] and y>= self.specMan.to_draw[name].y - self.specMan.to_draw[name].box[1] and y<= self.specMan.to_draw[name].y + self.specMan.to_draw[name].box[1]:
                        self.specMan.to_draw[name].i_am_selected()

        if self.actions[self.action] == 'showing':
            if button == pyglet.window.mouse.LEFT and self.selection == 'inventory':
                self.persos[self.perso].in_inv_drop()
            """
            if button == pyglet.window.mouse.RIGHT and self.selection == 'normal':
                self.cmd.add('verif_R',self.selector_modify((x,y),'R',val=0))
            elif button == pyglet.window.mouse.LEFT and self.selection == 'normal':
                self.cmd.add('verif_L',self.selector_modify((x,y),'L',val=0))
                #self.selector_modify((x,y),'L',val=0)"""

    def on_mouse_scroll(self,x, y, scroll_x, scroll_y):

        if type(scroll_y) != int:
            scroll_y = int(scroll_y)

        if self.actions[self.action] == 'showing':
            #self.cmd.add('scrolling',scroll_y)
            self.persos[self.perso].scroll_tool(-scroll_y)

    ### MY EVENTS (bcz pyglet is not very ouf)

    def on_my_resize(self):
        w,h = self.get_size()
        print('I\'ve been resized, my new size is',w,h)
        pup.set_size_screen((w,h))


    ### REFRESH FUNCTIONS

    def refresh_persos(self):

        t = time.time()

        for perso in self.persos:

            ## APPLYING BOT BEHAVIOUR
            if perso != self.perso:
                self.persos[perso].being_a_bot()

            ## ACTUALISE DATA OF PERSO
            self.persos[perso].actualise_general()

            if perso == self.perso:
                if self.persos[perso].dead:
                    self.graphic.unhide(self.sprids['game_over'])

                else:
                    self.graphic.unhide(self.sprids['game_over'],True)

            ## ACTUALISE POSITION OF PERSO

            #1st layer of position
            real_pos =  tut.from_pxpos_to_realpos(self.persos[perso].px_pos,False)

            if perso == self.perso:
                # updating camera
                tab = []
                if real_pos.x > 3*(self.current_size_scr[0]//4) or real_pos.x < self.current_size_scr[0]//4:
                    tab.append('x')
                if real_pos.y > 3*(self.current_size_scr[1]//4) or real_pos.y < self.current_size_scr[1]//4:
                    tab.append('y')
                if tab != []:
                    self.reset_camera(tab)

                # updating inventory selection
                if not 'invent_select' in self.sprids['cursors']:
                    self.sprids['cursors']['invent_select'] = graphic.Cursor('invent_select',self.graphic,self.textids['effects'],51,['hud'],2,self.persos[perso].invent_pxx[self.persos[perso].tool],vis=self.persos[perso].aff_inv)
                    #print('oklmmmm')
                else:
                    if [*self.sprids['cursors']['invent_select'].get_pos()] != self.persos[perso].invent_pxx[self.persos[perso].tool]:
                        self.sprids['cursors']['invent_select'].set_pos(self.persos[perso].invent_pxx[self.persos[perso].tool])
                    #print(self.graphic.sprites[self.sprids['cursors']['invent_select']].x , self.graphic.sprites[self.sprids['cursors']['invent_select']].y)

            #2nd and final layer of position
            real_pos = tut.xy_add(real_pos,self.admin_cam.pos,-1)

            if perso == self.perso:
                # updating cursor selection
                if self.selection == 'normal':

                    #self.graphic.unhide(self.sprids['hud']['inv_select'],True)
                    to_del = []
                    for (b,c) in self.sprids['cursors']['select']:
                        inthere = False
                        for box in self.persos[perso].selection:
                            biom,case,pos,lvl = box.pos()
                            if (biom,case) == (b,c):
                                inthere = True
                                break
                        if not inthere:
                            to_del.append((b,c))
                    for thg in to_del:
                        self.sprids['cursors']['select'][thg].delete()
                        del self.sprids['cursors']['select'][thg]

                    for box in self.persos[perso].selection:
                        b,c,p,l = box.pos()
                        #sprid = self.sprids['bioms'][b][l][c]
                        if not (b,c) in self.sprids['cursors']['select']:
                            #self.cmd.add('adding',box)
                            self.sprids['cursors']['select'][b,c] = graphic.Cursor('select_'+str(b)+'_'+str(c),self.graphic,self.textids['effects'],16,[None,None,l],1,tut.from_pxpos_to_realpos(tut.from_bcx_to_xy(box.Pos())).xy())

                            #self.graphic.addSpr(self.textids['effects'][16],tut.from_pxpos_to_realpos(tut.from_bcx_to_xy(box.Pos())).xy())
                            #self.graphic.addToGroup(self.sprids['cursors']['select'][b,c],[None,None,l],1)
                            #self.cmd.add('selectspr',self.graphic.sprites[self.sprids['cursors']['select'][(b,l,c)]])
                        else:
                            newp = tut.from_pxpos_to_realpos(tut.from_bcx_to_xy(box.Pos())).xy()
                            if self.sprids['cursors']['select'][b,c].get_pos() != newp:
                                self.sprids['cursors']['select'][b,c].set_pos(newp)

                elif self.selection == 'inventory':

                    #self.graphic.unhide(self.sprids['cursors']['select'],True)
                    to_del = []
                    for thg in self.sprids['cursors']['inv_select']:
                        inthere = False
                        for thg2 in self.persos[self.perso].inv_selection:
                            if thg == thg2:
                                inthere = True
                                break
                        if not inthere:
                            to_del.append(thg)
                    for thg in to_del:
                        self.sprids['cursors']['inv_select'][thg].delete()
                        del self.sprids['cursors']['inv_select'][thg]

                    for thg in self.persos[perso].inv_selection:

                        if not thg in self.sprids['cursors']['inv_select']:
                            #self.cmd.add('adding',box)
                            self.sprids['cursors']['inv_select'][thg] = graphic.Cursor('inv_select'+str(thg),self.graphic,self.textids['effects'],49,['hud'],2,self.persos[perso].invent_pxx[thg])

                                #self.graphic.addSpr(self.textids['effects'][32],self.persos[perso].invent_pxx[thg])
                                #self.graphic.addToGroup(self.sprids['hud']['inv_select'][thg],['hud'],2)


            ## ACTUALISE INVENTORY AND UPDATE TERRAIN WITH/WITHOUT CASES BROKEN
            if perso == self.perso:
                #selection
                pos = tut.from_real_to_pxpos(tut.XY_Pos(*self.clicks['M']))
                self.persos[self.perso].select(pos)

            if type(self.persos[perso]) == pso.Perso:
                # update list of cases that perso has broken
                for case in self.persos[perso].updatelist:
                    i,j,x,y = case.ijxy()
                    key = self.terrain.get_case(case)
                    if key != 0:
                        self.sprids['bioms'][i,j][case.l][x,y] = self.graphic.addSpr(self.textids['ground'][key],tut.from_bcx_to_pxx((i,j),(x,y)))
                        self.graphic.addToGroup(self.sprids['bioms'][i,j][case.l][x,y],[None,None,case.l])
                    else:
                        if self.sprids['bioms'][i,j][case.l][x,y] != 0:
                            self.graphic.delete(self.sprids['bioms'][i,j][case.l][x,y])
                            self.sprids['bioms'][i,j][case.l][x,y] = 0

                self.persos[perso].updatelist = []


            # creating persos sprites and nametags if it's not done and updating positions if already created
            if not perso in self.sprids['persos']:

                #REAL PERSO
                self.sprids['persos'][perso] = self.graphic.addSpr(self.textids['persos'][self.persos[perso].skin],real_pos.xy())
                self.graphic.addToGroup(self.sprids['persos'][perso],[None,None,self.persos[perso].pos.lvl()])

                self.sprids['persosplus']['actual'] = []
                self.sprids['persosplus']['near'] = []

                #ACTUAL CASES
                for case in self.persos[perso].px_actual_cases:

                    real_pos_plus =  tut.from_pxpos_to_realpos(case,False)
                    real_pos_plus = tut.xy_add(real_pos_plus,self.admin_cam.pos,-1)
                    self.sprids['persosplus']['actual'].append(self.graphic.addSpr(self.textids['persos'][self.persos[perso].plusposskin[0]],real_pos_plus.xy(),vis=False))
                    self.graphic.addToGroup(self.sprids['persosplus']['actual'][-1],['front'],-1)

                #NEAR CASES
                for case in self.persos[perso].px_near_cases:

                    real_pos_plus =  tut.from_pxpos_to_realpos(case,False)
                    real_pos_plus = tut.xy_add(real_pos_plus,self.admin_cam.pos,-1)
                    self.sprids['persosplus']['near'].append(self.graphic.addSpr(self.textids['persos'][self.persos[perso].plusposskin[1]],real_pos_plus.xy(),vis=False))
                    self.graphic.addToGroup(self.sprids['persosplus']['near'][-1],['front'],-1)

                #NAMETAG

                pos = [*real_pos.xy()]
                pos[0] += (tut.SIZE_TILE[0]/2)*pup.GEN['1x']
                pos[1] += tut.SIZE_TILE[1]*pup.GEN['1y']
                self.lblids['hud']['nametags'][perso] = self.labman.addLabel(self.persos[perso].name,pos,vis=not self.aff_hud,font_size=10*pup.GEN['1y'],font_name='arial',anchor=('center','bottom'))
                self.labman.addToGroup(self.lblids['hud']['nametags'][perso],['hud'])

            else:

                #UPDATE SKIN
                self.graphic.set_text(self.sprids['persos'][perso],self.textids['persos'][self.persos[perso].skin])

                #REAL PERSO
                self.graphic.modify(self.sprids['persos'][perso],real_pos.xy(),group=[[None,None,self.persos[perso].pos.lvl()]])

                #ACTUAL CASES
                for i in range(len(self.persos[perso].px_actual_cases)):
                    real_pos_plus =  tut.from_pxpos_to_realpos(self.persos[perso].px_actual_cases[i],False)
                    real_pos_plus = tut.xy_add(real_pos_plus,self.admin_cam.pos,-1)
                    self.graphic.modify(self.sprids['persosplus']['actual'][i],real_pos_plus.xy())

                #NEAR CASES
                for i in range(len(self.persos[perso].px_near_cases)):
                    real_pos_plus =  tut.from_pxpos_to_realpos(self.persos[perso].px_near_cases[i],False)
                    real_pos_plus = tut.xy_add(real_pos_plus,self.admin_cam.pos,-1)
                    self.graphic.modify(self.sprids['persosplus']['near'][i],real_pos_plus.xy())

                #NAMETAG
                self.labman.set_text(self.lblids['hud']['nametags'][perso],self.persos[perso].name)
                pos = [*real_pos.xy()]
                pos[0] += (tut.SIZE_TILE[0]/2)*pup.GEN['1x']
                pos[1] += tut.SIZE_TILE[1]*pup.GEN['1y']
                self.labman.modify(self.lblids['hud']['nametags'][perso],pos)

            ## ACTUALISE HUD
            if perso == self.perso:
                self.actualise_hud()

        return time.time()-t

    ### LOOP FUNCTIONS

    def events(self):

        if self.actions[self.action] == 'showing' or self.actions[self.action] == 'showing2':

            if self.keys[key.O]:

                biom = self.persos[self.perso].pos.x[0],self.persos[self.perso].pos.y[0]
                self.reset_biom(biom)

            moved = False
            if self.keys[key.Z]:
                self.persos[self.perso].move([0,1],self.keys[key.LSHIFT],self.keys[key.SPACE])
                moved = True
            if self.keys[key.S]:
                self.persos[self.perso].move([0,-1],self.keys[key.LSHIFT],self.keys[key.SPACE])
                moved = True
            if self.keys[key.Q]:
                self.persos[self.perso].move([-1,0],self.keys[key.LSHIFT],self.keys[key.SPACE])
                moved = True
            if self.keys[key.D]:
                self.persos[self.perso].move([1,0],self.keys[key.LSHIFT],self.keys[key.SPACE])
                moved = True

            #if moved:
            #    self.graphic.set_text(self.sprids['persos'][self.perso],self.textids['persos'][self.persos[self.perso].skin])

            if self.keys[key.M]:
                print(' ',self.terrain.terrains['ground'][self.persos[self.perso].pos.y[1]-1][self.persos[self.perso].pos.x[1]])
                print(self.terrain.terrains['ground'][self.persos[self.perso].pos.y[1]][self.persos[self.perso].pos.x[1]-1],self.terrain.terrains['ground'][self.persos[self.perso].pos.y[1]][self.persos[self.perso].pos.x[1]],self.terrain.terrains['ground'][self.persos[self.perso].pos.y[1]][self.persos[self.perso].pos.x[1]+1])
                print(' ',self.terrain.terrains['ground'][self.persos[self.perso].pos.y[1]+1][self.persos[self.perso].pos.x[1]])
                print('')

            if self.clicks['L'] != False and self.selection == 'normal':
                self.selector_modify(self.clicks['L'],'L')
            if self.clicks['R'] != False and self.selection == 'normal':
                self.selector_modify(self.clicks['R'],'R')

            if self.security == 'admin':

                reset_cam = True
                if self.keys[key.UP]:
                    self.admin_cam.move(tut.XY_Vec(0,-60))
                    #self.admin_cam[1]-=60
                    reset_cam = False
                if self.keys[key.DOWN]:
                    self.admin_cam.move(tut.XY_Vec(0,60))
                    #self.admin_cam[1]+=60
                    reset_cam = False
                if self.keys[key.RIGHT]:
                    self.admin_cam.move(tut.XY_Vec(-60,0))
                    #self.admin_cam[0]-=60
                    reset_cam = False
                if self.keys[key.LEFT]:
                    self.admin_cam.move(tut.XY_Vec(60,0))
                    #self.admin_cam[0]+=60
                    reset_cam = False

                if reset_cam:
                    #self.admin_cam = [0,0]
                    self.admin_cam.pos = tut.XY_Vec()

        """elif self.actions[self.action] in ['loading','creating']:
            if self.keys[key.ESCAPE]:
                self.quit_land(False)"""

    def refresh(self):

        #time1,time2,time3,time4 = 0,0,0,0
        t = {}

        if self.actions[self.action] == 'showing' or self.actions[self.action] == 'showing2':

            elapsed_time = time.time()

            ### CAMERA'S CONTROL
            self.camera.update()

            ### MOUSE
            self.mouse_speed = self.mouse_speed/15
            if self.mouse_speed < 0.2:
                self.mouse_speed = 0

            t['TCamMouse'] = time.time()-elapsed_time

            ### REFRESH PERSOS
            t['TPerso'] = self.refresh_persos()


            ### REFRESH MAP
            titime = time.time()
            if not 'map_crsr' in self.sprids['cursors']:
                self.sprids['cursors']['map_crsr'] = graphic.Cursor('map_crsr',self.graphic,self.textids['effects'],51,['map'],1,tut.get_pos_map_biom(self.persos[self.perso].get_biom(),self.current_size_scr))
                self.sprids['cursors']['map_crsr'].set_ani([64]*100+[i for i in range(64,73)]+[72]*100+[i for i in range(72,63,-1)])
                self.sprids['cursors']['map_crsr'].set_text(50)
            else:
                if self.sprids['cursors']['map_crsr'].is_visible():
                    self.sprids['cursors']['map_crsr'].up_skin()
                    self.sprids['cursors']['map_crsr'].set_pos(tut.get_pos_map_biom(self.persos[self.perso].get_biom(),self.current_size_scr))

            if self.aff_map[0] and not self.aff_map[1] :
                self.aff_map[1] = 1
                self.effectMan.unhide('blur50_map')
                self.sprids['cursors']['map_crsr'].unhide()
                self.graphic.unhide(self.sprids['map'])
                #for (i,j) in self.sprids['map']:
                #    self.graphic.sprites[self.sprids['map'][i,j]].visible = True

            elif self.aff_map[1] and not self.aff_map[0]:
                self.aff_map[1] = 0
                self.effectMan.unhide('blur50_map',True)
                self.sprids['cursors']['map_crsr'].unhide(True)
                self.graphic.unhide(self.sprids['map'],True)
                #for (i,j) in self.sprids['map']:
                #    self.graphic.sprites[self.sprids['map'][i,j]].visible = False

            t['TMap'] = time.time()-titime

            ### REFRESH TERRAIN
            big_time = time.time()

            self.cmd.add("nb_spr_to_draw",self.nb_spr_to_draw)
            first_spr = []

            if self.actions[self.action] == 'showing3':
                """VIEUUUUUX CA MAAAARCHE PAAAAS"""

                #self.old_spr_to_print = self.spr_to_print
                #self.spr_to_print = []

                ## listage de tous les sprites présents sur l'écran : donc à afficher
                time1 = time.time()
                #print(x_on_scr,y_on_scr)
                first_spr_x = self.persos[self.perso].pos.x[1] - ((x_on_scr - self.persos[self.perso].pos.x[2])//tut.SIZE_TILE[0] +1)
                first_spr_y = self.persos[self.perso].pos.y[1] - ((y_on_scr - self.persos[self.perso].pos.y[2])//tut.SIZE_TILE[0] +1)

                biomi = self.persos[self.perso].pos.x[0] + first_spr_x//tut.SIZE_BIOM[0],self.persos[self.perso].pos.y[0] + first_spr_y//tut.SIZE_BIOM[1]
                casei = first_spr_x - (first_spr_x//tut.SIZE_BIOM[0])*tut.SIZE_BIOM[0],first_spr_y - (first_spr_y//tut.SIZE_BIOM[1])*tut.SIZE_BIOM[1]
                posi = -self.persos[self.perso].pos.x[2] , self.current_size_scr[1]+self.persos[self.perso].pos.y[2]
                #print(biomi,casei,posi)
                biomf,casef = [],[]

                diff = [biomi[0] - self.old_spr_limit[0][0],biomi[1] - self.old_spr_limit[0][1],casei[0] - self.old_spr_limit[0][2],casei[1] - self.old_spr_limit[0][3]]

                ii,jj = 0,0

                time1 = time.time() - time1


                # on parcourt maitenant tous les sprites depuis le premier à afficher jusqu'au premier + la longueur de la liste à afficher
                for k in range(self.nb_spr_to_draw_y):
                    ii=0
                    for p in range(self.nb_spr_to_draw_x):

                        elapsed_time = time.time()
                        x,y = casei[0] + p - ii*tut.SIZE_BIOM[0] , casei[1] + k - jj*tut.SIZE_BIOM[1]
                        if x == tut.SIZE_BIOM[0]:
                            ii += 1
                            x = 0
                        if y == tut.SIZE_BIOM[1]:
                            jj += 1
                            y = 0

                        i,j = biomi[0] + ii , biomi[1] + jj


                        posx,posy = posi[0]+ p*tut.SIZE_TILE[0] , posi[1] - k*tut.SIZE_TILE[0]

                        time2 += time.time() - elapsed_time

                        try :
                            elapsed_time = time.time()
                            self.graphic.sprites[self.sprids['bioms'][i,j][x,y]].x = posx
                            self.graphic.sprites[self.sprids['bioms'][i,j][x,y]].y = posy

                            to_print = False

                            if diff[0] > 0 and i > self.old_spr_limit[1][0]:
                                to_print = True
                            elif diff[0] == 0 and x > self.old_spr_limit[1][2]:
                                to_print = True


                            elif diff[0] < 0 and i < self.old_spr_limit[0][0]:
                                to_print = True
                            elif diff[0] == 0 and x < self.old_spr_limit[0][2]:
                                to_print = True


                            elif diff[1] > 0 and j > self.old_spr_limit[1][1]:
                                to_print = True
                            elif diff[1] == 0 and y > self.old_spr_limit[1][3]:
                                to_print = True

                            elif diff[1] < 0 and j < self.old_spr_limit[0][1]:
                                to_print = True
                            elif diff[1] == 0 and y < self.old_spr_limit[0][3]:
                                to_print = True


                            if to_print:
                                self.graphic.sprites[self.sprids['bioms'][i,j][x,y]].visible = True


                            time3 += time.time() - elapsed_time

                        except :
                            a=0
                            #print(first_spr_x,first_spr_y, '    ' ,k,p,'     ',i,j,'     ',x,y)

                            print('x:',x,'\n',
                                    'casei:',casei,'\n',
                                    'p:',p,'\n',
                                    'ii:',ii,'\n',
                                    'tut.SIZE_BIOM[0]:',tut.SIZE_BIOM[0],'\n',
                                    )

                            print(self.nb_spr_to_draw_x , "=" ,self.current_size_scr[0],"//",tut.SIZE_TILE[0] , "+ 1\n",
                                        #print(x_on_scr,y_on_scr)
                                        first_spr_x , "=" ,self.persos[self.perso].pos.x[1] , "-" ,"((",x_on_scr , "-" ,self.persos[self.perso].pos.x[2],")","//",tut.SIZE_TILE[0] , "+1",")\n",

                                        biomi , "=" ,self.persos[self.perso].pos.x[0] , "+" ,first_spr_x,"//",tut.SIZE_BIOM[0],"\n",
                                        casei , "=" ,first_spr_x , "-" ,"(",first_spr_x,"//",tut.SIZE_BIOM[0],")","*",tut.SIZE_BIOM[0],"\n",
                                        posi , "= -" ,self.persos[self.perso].pos.x[2],"\n",

                                        "p,k =",k,p,
                                        "x,y =",x,y,
                                        "i,j =",i,j

                                        )

                            print(self.nb_spr_to_draw_x , "=" ,self.current_size_scr[0],"//",tut.SIZE_TILE[0] , "+ 1\n",
                                        self.nb_spr_to_draw_y , "=" ,self.current_size_scr[1],"//",tut.SIZE_TILE[0] , "+1\n",
                                        #print(x_on_scr,y_on_scr)
                                        first_spr_x , "=" ,self.persos[self.perso].pos.x[1] , "-" ,"((",x_on_scr , "-" ,self.persos[self.perso].pos.x[2],")","//",tut.SIZE_TILE[0] , "+1",")\n",
                                        first_spr_y , "=" ,self.persos[self.perso].pos.y[1] , "-" ,"((",y_on_scr , "-" ,self.persos[self.perso].pos.y[2],")","//",tut.SIZE_TILE[0] , "+1",")\n",

                                        biomi , "=" ,self.persos[self.perso].pos.x[0] , "+" ,first_spr_x,"//",tut.SIZE_BIOM[0],",",self.persos[self.perso].pos.y[0] , "+" ,first_spr_y,"//",tut.SIZE_BIOM[1],"\n",
                                        casei , "=" ,first_spr_x , "-" ,"(",first_spr_x,"//",tut.SIZE_BIOM[0],")","*",tut.SIZE_BIOM[0],",",first_spr_y , "-" ,"(",first_spr_x,"//",tut.SIZE_BIOM[1],")","*",tut.SIZE_BIOM[1],"\n",
                                        posi , "= -" ,self.persos[self.perso].pos.x[2] , ", -" ,self.persos[self.perso].pos.y[2],"\n",

                                        "p,k =",k,p,
                                        "x,y =",x,y,
                                        "i,j =",i,j

                                        )

                            #self.playing = False
                            #break

                        if k == self.nb_spr_to_draw_y-1 and p == self.nb_spr_to_draw_x-1:
                            print('jtebez')
                            biomf =[i,j]
                            casef = [x,y]

                for [i,j,x,y] in self.old_spr_to_print:
                    self.graphic.sprites[self.sprids['bioms'][i,j][x,y]].visible = False


                #   Pas fini bordel
                #   c'est relou pcq faut encore selectionner les sprites qui ont été affichés au tour d'avant mais qui ne sont plus sur l'écran
                #   et donc qu'on doit rendre invisible sinon ça part en couille...
                #   Seulement le truc c'est que ya bcp trop de possibilités à traiter et j'ai la flemme surtout que je suis pas convaincu du rendement
                #   niveau fps... donc booooh pour le moment go utiliser 'showing' au lieu de 'showing2' hein ?

                if diff[0] == 0 and diff[1] == 0:  ### ATTENTION ON IMPLEMENTE PAS LE CAS OU ON CHANGERAIT COMPLETEMENT DE BIOME INSTANT'
                    if diff[2] > 0 :
                        for x in range(self.old_spr_limit[0][2],casei[0]):
                            if diff[3] > 0:
                                for y in range(self.old_spr_limit[0][3],biomi[1]):
                                    self.graphic.sprites[self.sprids['bioms'][biomi][x,y]].visible = False
                            else:
                                for y in range(casef[1],self.old_spr_limit[1][3]):
                                    self.graphic.sprites[self.sprids['bioms'][biomi][x,y]].visible = False
                    else:
                        for x in range(casef[0],self.old_spr_limit[1][2]):
                            if diff[3] > 0:
                                for y in range(self.old_spr_limit[0][3],biomi[1]):
                                    self.graphic.sprites[self.sprids['bioms'][biomi][x,y]].visible = False
                            else:
                                for y in range(casef[1],self.old_spr_limit[1][3]):
                                    self.graphic.sprites[self.sprids['bioms'][biomi][x,y]].visible = False



                self.old_spr_limit = [  [biomi[0],biomi[1],casei[0],casei[1]] , [biomf[0],biomf[1],casef[0],casef[1]]  ]

                """elif self.actions[self.action] == 'showing2':


                a=0"""

            else:


                self.old_bioms_to_print = self.bioms_to_print
                #self.old_bioms_to_print = mycopy(self.bioms_to_print)
                self.bioms_to_print = []

                for i in range(self.persos[self.perso].pos.x[0]-1,self.persos[self.perso].pos.x[0]+2):
                    for j in range(self.persos[self.perso].pos.y[0]-1,self.persos[self.perso].pos.y[0]+2):
                        if i >= 0 and j >= 0 and i < tut.SIZE_TERRAIN[0] and j < tut.SIZE_TERRAIN[1]:
                            self.bioms_to_print.append((i,j))
                #print(bioms_to_print)

                nb_spr_on_scr = 0
                first_spr , last_spr = [],[]

                t['TN']=0# , t['TL1'] ,t['TL2'] = 0,0,0

                for (i,j) in self.bioms_to_print:

                    elapsed_time = time.time()
                    for lvl in range(len(self.terrain.Bioms[j][i].ground)):
                        for y in range(len(self.terrain.Bioms[j][i].ground[lvl])):
                            for x in range(len(self.terrain.Bioms[j][i].ground[lvl][y])):
                                if self.terrain.Bioms[j][i].ground[lvl][y][x] != 0:

                                    #little_time = time.time()
                                    posx,posy = tut.from_bcx_to_pxx((i,j),(x,y))
                                    #posx,posy = tut.from_pxpos_to_realpos(tut.from_bcx_to_xy( tut.BCX_Pos((i,j),(x,y)) )).xy()

                                    #t['TL1']+=time.time()-little_time
                                    #little_time = time.time()

                                    if posx > -tut.SIZE_TILE[0] and posx < self.current_size_scr[0]+tut.SIZE_TILE[0] and posy > -tut.SIZE_TILE[0] and posy < self.current_size_scr[1]+tut.SIZE_TILE[0]:

                                        """nb_spr_on_scr+=1
                                        if first_spr != []:
                                            if first_spr[0] >= posx and first_spr[1] >= posy:
                                                first_spr = [posx,posy]
                                        else:
                                            first_spr = [posx,posy]

                                        if last_spr != []:
                                            if last_spr[0] <= posx and last_spr[1] <= posy:
                                                last_spr = [posx,posy]
                                        else:
                                            last_spr = [posx,posy]"""

                                        if not self.graphic.sprites[self.sprids['bioms'][i,j][lvl][x,y]].visible:
                                            self.graphic.sprites[self.sprids['bioms'][i,j][lvl][x,y]].visible = True
                                        self.graphic.sprites[self.sprids['bioms'][i,j][lvl][x,y]].position = posx,posy
                                    elif self.graphic.sprites[self.sprids['bioms'][i,j][lvl][x,y]].visible:
                                        self.graphic.sprites[self.sprids['bioms'][i,j][lvl][x,y]].visible = False

                                    #t['TL2']+=time.time()-little_time

                    #self.verif((i,j))

                    t['TN']+=time.time()-elapsed_time

                for (i,j) in self.old_bioms_to_print:
                    elapsed_time = time.time()
                    if (i,j) not in self.bioms_to_print:
                        #print(i,j)
                        #print(self.sprids['bioms'][i,j])
                        for lvl in self.sprids['bioms'][i,j]:
                            for cas in self.sprids['bioms'][i,j][lvl]:
                                if self.sprids['bioms'][i,j][lvl][cas] != 0:
                                    if self.graphic.sprites[self.sprids['bioms'][i,j][lvl][cas]].visible:
                                        self.graphic.sprites[self.sprids['bioms'][i,j][lvl][cas]].visible = False

                    #self.verif((i,j))

                self.cmd.add('    ','')
                self.cmd.add('sprites on screen :','')
                self.cmd.add('   count',nb_spr_on_scr)
                self.cmd.add('   first',first_spr )
                self.cmd.add('   last',last_spr)

            t['TTerrain'] = time.time()-big_time

        elif self.actions[self.action]  == 'creating':

            local_time = time.time()

            load = self.creating

            state = load['state']

            go_on = False
            add_per = False

            # all the differents states
            if state == 0: #'initialisating creation'
                #print(SIZE_BIOM)

                #size_terrain = SIZE_TERRAIN
                if self.loading['size'] != None:
                    size_terrain = self.loading['size']
                else:
                    size_terrain = self.text_size_land_menu_val[self.text_size_land_menu_sel]

                tut.set_var(size_terrain,SIZE_BIOM,(SIZE_TILE,SIZE_TILE))

                go_on = True
                add_per = True

            elif state == 1: #choosing zones

                load['w'],load['h'] = tut.SIZE_TERRAIN[0]*tut.SIZE_BIOM[0],tut.SIZE_TERRAIN[1]*tut.SIZE_BIOM[1]

                load['tab_map'] , load['tab_land'] = [],[]

                load['nb_zones'] = ((load['w']*load['h'])//8000)+1

                go_on = True
                add_per = True

            elif state == 2: #choosing grounds

                load['terrain'] = [ [ [0 for k in range(load['w'])] for q in range(load['h']) ] for _ in range(tut.DEPTH_BIOM) ]

                load['grounds'] = []

                if len(ALL_GROUNDS) > load['nb_zones']:

                    grounds = randmultint(load['nb_zones'],len(ALL_GROUNDS))

                    for k in grounds:
                        load['grounds'].append(ALL_GROUNDS[k])
                else:
                    load['grounds'] = ALL_GROUNDS

                go_on = True
                add_per = True

            elif state == 3: #creating noise

                load['terrain'][0] = get_diff_noised_list(load['w'],load['h'],1,style=2)

                go_on = True
                add_per = True

                #self.loadbar['nb_ope'] = self.loadbar['nb_ope'] -1 + len(load['terrain'][0][0])*len(load['terrain'][0])

            elif state == 4: #coloring terrain

                v=0
                for j in range(len(load['terrain'][0])):
                    for i in range(len(load['terrain'][0][j])):
                        if load['terrain'][0][j][i] == -1:
                            #print('lets go pour la',w+1,'e fois','key=',grounds[v])
                            color(load['terrain'][0],(i,j),load['grounds'][v])
                            v+=1
                            if v >= len(load['grounds']):
                                v=0
                        elif load['terrain'][0][j][i] == 0:
                            load['terrain'][0][j][i] = 2

                go_on = True
                self.loadbar['nb_ope'] = self.loadbar['nb_ope'] -1 + len(ASSETS)
                load['coloring_asset'] = 0
                self.loadbar['plus'] = ' '+ASSETS[load['coloring_asset']]

            elif state == 5: #placing assets

                load['terrain'][1] = createZone(load['terrain'][1],ASSETS[load['coloring_asset']],load['w'],load['h'])

                load['coloring_asset']+=1
                if load['coloring_asset'] >= len(ASSETS):
                    go_on = True
                add_per = True

                if go_on:
                    self.loadbar['plus'] = ''
                else:
                    self.loadbar['plus'] = ' '+ASSETS[load['coloring_asset']]

            elif state == 6: #verifing terrain

                load['terrain'] = verify(load['terrain'])

                go_on = True
                add_per = True

            elif state == 7: #splitting terrain

                load['tab_map'] , load['tab_land'] = from_ter_to_bioms(load['terrain'],tut.SIZE_TERRAIN,tut.SIZE_BIOM,tut.DEPTH_BIOM)

                go_on = True
                add_per = True

            elif state == 8: #creating persos

                # CREATION PERSOS
                load['tab_perso'] = []
                dic = {}
                dic['name'] = None
                dic['life'] = None
                dic['pos'] = [tut.SIZE_TERRAIN[0]//2,tut.SIZE_TERRAIN[1]//2,1,1,0,0,1]
                dic['type'] = 'Perso'
                dic['specie'] = 'human'
                dic['skin_dic'] = None
                dic['inventory'] = {}
                dic['main'] = True
                dic['id'] = get_id('perso')

                load['tab_perso'].append(dic)

                #load['nb_bots_to_create'] = 10

                go_on = True
                add_per = True


                load['nb_bots_per_row'] = 1000
                load['nb_row_bots_to_go'] = NB_BOTS_CREATE//load['nb_bots_per_row'] +1

                self.loadbar['nb_ope'] = self.loadbar['nb_ope'] -1 + load['nb_row_bots_to_go']

            elif state == 9: #creating bots

                if not 'row_bot_creating' in load:
                    load['row_bot_creating'] = 0

                nb_bot_row = load['nb_bots_per_row']

                if NB_BOTS_CREATE - load['row_bot_creating']*load['nb_bots_per_row'] < load['nb_bots_per_row']:
                    nb_bot_row = NB_BOTS_CREATE - load['row_bot_creating']*load['nb_bots_per_row']

                for i in range(nb_bot_row):

                    dic = {}
                    dic['name'] = None
                    dic['life'] = None
                    #pos = random.randint(0,tut.SIZE_BIOM[0]),random.randint(0,tut.SIZE_BIOM[1])
                    #dic['pos'] = [tut.SIZE_TERRAIN[0]//2,tut.SIZE_TERRAIN[1]//2,*pos,0,0,1]
                    dic['pos'] = None
                    dic['type'] = 'Living'
                    dic['specie'] = 'loutre'
                    dic['skin_dic'] = None
                    dic['main'] = False
                    dic['id'] = get_id('perso')

                    load['tab_perso'].append(dic)

                load['row_bot_creating']+=1
                if load['row_bot_creating'] >= load['nb_row_bots_to_go']:
                    go_on =True
                add_per = True

            elif state == 10: #finishing creating
                self.loading['tab_perso'],self.loading['tab_map'],self.loading['tab_land'] = \
                            load['tab_perso'],load['tab_map'],load['tab_land']
                self.navigate('loading')
                self.created = True

                go_on = True
                add_per = True

            # upgrading state
            if add_per:
                add = (100 - self.loadbar['percent'])/self.loadbar['nb_ope']
                self.loadbar['percent'] += add
                self.loadbar['nb_ope'] -= 1

            self.all_times[self.create_to_do[load['state']]] += time.time()-local_time

            # upgrading state
            if go_on:
                self.creating['state']+= 1
                if self.creating['state'] >= len(self.create_to_do):
                    del self.creating
                    del self.create_to_do

                    #if 'creating' in self.sprids:
            if hasattr(self, 'creating'):
                ## refresh loading bar + label
                size_fill = pup.SIZ['loading_bar'][0]*self.loadbar['percent']/100
                self.labman.set_text(self.lblids['loading'],self.create_to_do[load['state']]+self.loadbar['plus'])
                self.graphic.modify(self.sprids['loading']['fill'],scale=(size_fill/SIZE_TILE,1))
            else:
                ## refresh loading bar + label
                size_fill = pup.SIZ['loading_bar'][0]*self.loadbar['percent']/100
                self.labman.set_text(self.lblids['loading'],self.load_to_do[self.loading['state']]+self.loadbar['plus'])
                self.graphic.modify(self.sprids['loading']['fill'],scale=(size_fill/SIZE_TILE,1))

        elif self.actions[self.action]  == 'loading':

            local_time = time.time()

            load = self.loading

            state = load['state']

            go_on = False
            add_per = False

            # all the differents states
            if state == 0: ## 'extracting data from files'

                load['tab_perso'],load['tab_map'],load['tab_land'],load['name'] = self.load_land(load['name'])
                go_on = True
                add_per = True

            elif state == 1: ## 'initialisation of loading'


                ## mise en forme sizes
                size_terrain = len(load['tab_map'][0]) , len(load['tab_map'])
                size_biom = len(load['tab_land'][0][0][0][0]) , len(load['tab_land'][0][0][0])
                tut.set_var(size_terrain,size_biom)

                self.loadbar['nb_ope'] = self.loadbar['nb_ope'] -1 + tut.SIZE_TERRAIN[0]*tut.SIZE_TERRAIN[1]

                ## creation du terrain et mise dedans des bons bioms
                self.terrain = terrain.TerManager(tut.SIZE_TERRAIN,tut.SIZE_BIOM,load['name'])

                self.terrain.Bioms,self.terrain.map = [],[]
                for rangey in load['tab_land']:
                    y_for_real = []
                    for biom in rangey:
                        new_biom = terrain.emptyBiom(tut.SIZE_BIOM)
                        for lvl in range(len(biom)):
                            new_biom.set_ground(lvl,biom[lvl])
                        y_for_real.append(new_biom)
                    self.terrain.Bioms.append(y_for_real)
                self.terrain.map = load['tab_map']

                go_on = True
                add_per = True

            elif state == 2: ## initialisating sprites and labels'

                ## gestion des sprites
                self.sprids['persos'] = {}
                self.sprids['persosplus'] = {}
                self.sprids['bioms'] = {}
                self.sprids['map'] = {}
                self.sprids['hud'] = {}
                self.sprids['cursors'] = {}
                self.sprids['cursors']['select'] = {}
                self.sprids['cursors']['inv_select'] = {}

                for i in range(tut.SIZE_TERRAIN[0]):
                    for j in range(tut.SIZE_TERRAIN[1]):
                        self.sprids['bioms'][i,j] = {}
                        for lvl in range(tut.DEPTH_BIOM):
                            self.sprids['bioms'][i,j][lvl] = {}
                            for x in range(tut.SIZE_BIOM[0]):
                                for y in range(tut.SIZE_BIOM[1]):
                                    self.sprids['bioms'][i,j][lvl][x,y] = 0

                        self.sprids['map'][i,j] = 0

                self.aff_map = load['aff_map']

                ## gestion des labels
                self.lblids['hud'] = {}

                go_on = True
                add_per = True

            elif state == 3: ## 'loading persos'

                # GENEARTION PERSOS
                self.persos = {}

                for dic in load['tab_perso']:

                    if dic['pos'] != None:
                        init_pos = tut.BCX_Pos([dic['pos'][0],dic['pos'][1]],[dic['pos'][2],dic['pos'][3]],[dic['pos'][4],dic['pos'][5]],dic['pos'][6])
                        persobox = tut.BCX_Box(*init_pos.bcx(),init_pos.lvl(),c2=[1,1])
                    else:
                        persobox = None

                    if dic['main']:

                        self.perso = dic['id']

                    if dic['type'] == 'Perso':

                        self.persos[dic['id']] = pso.Perso(self.textids['ground'],self.textids['number'],self.graphic, self.terrain \
                                                            ,self.cmd,persobox,specie=dic['specie'],name=dic['name'],skin_seq=dic['skin_dic'])

                        self.selector = [0,[0,0],0]
                        self.persos[self.perso].set_inv(dic['inventory'])

                    elif dic['type'] == 'Living':

                        self.persos[dic['id']] = pso.LivingBot( self.terrain,self.cmd,persobox,specie=dic['specie'],name=dic['name'],skin_seq=dic['skin_dic'])

                    if dic['life'] != None:
                        self.persos[dic['id']].life,self.persos[dic['id']].max_life = dic['life']

                go_on = True
                add_per = True

            elif state == 4: ## 'initialisating hud elements'

                self.aff_hud = False

                self.init_hud()
                self.lblids['hud']['nametags'] = {}


                go_on = True
                add_per = True

            elif state == 5: ## 'initialisating camera'

                # INIT CAMERA

                posx,posy = self.current_size_scr[0]//2,self.current_size_scr[1]//2

                self.camera , self.admin_cam = tut.get_cam(tut.XY_Vec(posx,posy),8)
                tut.set_cam(self.camera , self.admin_cam)

                go_on = True
                add_per = True

            elif state == 6: ## 'creating sprites'

                posx_dep_map = self.current_size_scr[0]//2 - (tut.SIZE_TERRAIN[0]*tut.SIZE_TILE[0])//2
                posy_dep_map = self.current_size_scr[1]//2 + (tut.SIZE_TERRAIN[1]*tut.SIZE_TILE[0])//2


                # CREATION SPRITES DU TERRAIN + MAP
                self.old_spr_to_print = []
                self.old_spr_limit = []
                self.bioms_to_print = []

                if not 'loading_biom' in load:
                    load['loading_biom'] = [0,0]

                i,j = load['loading_biom']
                self.create_biom_sprites((i,j))

                posx2 = posx_dep_map + i*tut.SIZE_TILE[0]
                posy2 = posy_dep_map - (j+1)*tut.SIZE_TILE[0]
                self.sprids['map'][i,j] = self.graphic.addSpr(self.textids['ground'][self.terrain.map[j][i]],(posx2,posy2))
                self.graphic.addToGroup(self.sprids['map'][i,j],['map'])

                load['loading_biom'][0]+=1
                if load['loading_biom'][0] >= tut.SIZE_TERRAIN[0]:
                    load['loading_biom'][0] = 0
                    load['loading_biom'][1]+= 1
                    if load['loading_biom'][1] >= tut.SIZE_TERRAIN[1]:
                        go_on = True

                add_per = True

                self.loadbar['plus'] = ' '+str([load['loading_biom'][0]+1,load['loading_biom'][1]+1])
                if go_on:
                    self.loadbar['plus'] = ''

            elif state == 7: ## 'creating blur effect map'

                # CREATION BLUR EFFECT MAP

                posx_effect = self.current_size_scr[0]//2 - (tut.SIZE_TERRAIN[0]*tut.SIZE_TILE[0])//2 - tut.SIZE_TILE[0]*2
                posy_effect = self.current_size_scr[1]//2 - (tut.SIZE_TERRAIN[1]*tut.SIZE_TILE[0])//2 - tut.SIZE_TILE[0]*2

                effect_terrain = []

                blur_color = random.choice([i for i in range(1,10)])
                for j in range(tut.SIZE_TERRAIN[1]+4):
                    taby = []
                    for i in range(tut.SIZE_TERRAIN[0]+4):
                        taby.append(blur_color)
                    effect_terrain.append(taby)

                self.effects.append(self.effectMan.addEffect('blur50_map',effect_terrain,(posx_effect,posy_effect),self.group_manager.orders['map']-1))
                self.effectMan.unhide('blur50_map',False)

                go_on = True
                add_per = True

            elif state == 8: ## 'resetting camera'

                self.reset_camera('ulti')

                go_on = True
                add_per = True

            elif state == 9: ## 'finishing loading'

                self.in_land = True
                self.aff_hud = True
                self.navigate('showing')
                if hasattr(self, 'created'):
                    print('TOTAL TIME CREATING/LOADING GAME :',truncate(time.time()-self.total_time_loading,3))
                    del self.created
                else:
                    print('TOTAL TIME LOADING GAME :',truncate(time.time()-self.total_time_loading,3))

                if TAKE_DIRECT_SCREEN:
                    self.create_image()

                go_on = True
                add_per = True

            #print('     state',state,truncate(time.time()-local_time,3))

            # upgrading state
            if add_per:
                add = (100 - self.loadbar['percent'])/self.loadbar['nb_ope']
                self.loadbar['percent'] += add
                self.loadbar['nb_ope'] -= 1
            self.all_times[self.load_to_do[load['state']]] += time.time()-local_time

            if go_on:
                self.loading['state']+= 1
                if self.loading['state'] >= len(self.load_to_do):
                    del self.loading
                    del self.load_to_do
                    self.graphic.delete(self.sprids['loading'])
                    self.labman.delete(self.lblids['loading'])
                    del self.sprids['loading']
                    del self.lblids['loading']
                    """print('\n')
                    for tim in self.all_times:
                        print(tim,':',self.all_times[tim])"""

            if 'loading' in self.sprids:
                ## refresh loading bar + label
                size_fill = pup.SIZ['loading_bar'][0]*self.loadbar['percent']/100
                self.labman.set_text(self.lblids['loading'],self.load_to_do[load['state']]+self.loadbar['plus'])
                self.graphic.modify(self.sprids['loading']['fill'],scale=(size_fill/SIZE_TILE,1))

        return t

    def draw(self):

        if self.actions[self.action] != 'nothing':

            self.manager.draw()

            if self.actions[self.action] == 'menu':
                self.specMan.draw(['title'])
                self.specMan.draw(self.buttons[self.actions_menu[self.action_menu]])

                if self.actions_menu[self.action_menu] == 'main':
                    self.specMan.draw(['description'])
                elif self.actions_menu[self.action_menu] == 'newmap':
                    self.specMan.draw(['size_land'])


        if self.aff_cmd:
            self.cmd.draw()

    def gameloop(self,dt):


        pyglet.clock.tick()


        if self.nb == 0:

            self.lblids['fps'] = self.labman.addLabel('FPS',(20*pup.GEN['1x'],pup.GEN['ay']-50*pup.GEN['1y']),font_size=32*pup.GEN['1y'],font_name='arial')
            self.labman.addToGroup(self.lblids['fps'],['up'],1)

        self.nb+=1
        self.labman.set_text(self.lblids['fps'],'FPS : '+str(int(pyglet.clock.get_fps())))


        if self.playing:

            #print(self.action)
            self.cmd.add(' ',self.actions[self.action])

            elapsed_time = time.time()
            ### EVENTS
            self.events()
            self.cmd.add("events",time.time() - elapsed_time)

            elapsed_time = time.time()
            ### CLEAR
            self.clear()
            self.cmd.add("clear",time.time() - elapsed_time)

            elapsed_time = time.time()
            ### refresh
            t = self.refresh()
            self.cmd.add("refresh",time.time() - elapsed_time)

            for lbl in t:
                self.cmd.add("REF "+lbl,t[lbl])

            elapsed_time = time.time()
            ### DRAW
            self.draw()
            self.cmd.add("draw",time.time() - elapsed_time)


            if self.actions[self.action] == 'showing':
                self.cmd.add('   ','')
                self.cmd.add('perso :','')
                self.cmd.add('   pos',self.persos[self.perso].pos)
                self.cmd.add('   px_pos',self.persos[self.perso].px_pos)


                self.cmd.add('    ','')
                self.cmd.add('camera :','')
                self.cmd.add('   cam',self.camera.pos )
                #self.cmd.add('   y',self.camera[1])
                self.cmd.add('   obj',self.camera.obj)
                #self.cmd.add('   objy',self.camera.obj.y)
                #self.cmd.add('   tile x',self.camera_tile[0] )
                #self.cmd.add('   tile y',self.camera_tile[1])
                #self.cmd.add('   tile obj x',self.camera_obj_tile[0] )
                #self.cmd.add('   tile obj y',self.camera_obj_tile[1])

        else:
            print('\n\nNumber of lines :',compt(self.path))
            gs.save_files(self.path)

            self.close()

def main():

    app = App()
    app.init()

if __name__ == '__main__':
    main()
