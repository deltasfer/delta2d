





import pyglet,graphic,utils,terrain,test2,perso,drawable
import time,os
from TerrainCreator import *
from pyglet.window import key

class App(pyglet.window.Window):


    ### INIT FUNCTIONS

    def __init__(self):

        super(App, self).__init__()

        self.size_scr = 1000,800
        self.set_size(self.size_scr[0],self.size_scr[1])
        self.current_size_scr = self.size_scr

        self.manager = graphic.MainManager()
        self.specMan = graphic.SpecialManager(self.manager,self.current_size_scr)


        # loading fonts
        font_path = 'item/fonts/'
        self.font = ['starguard','starguardhalf']
        for ft in self.font:
            try:
                pyglet.resource.add_font(font_path+ft+'.otf')
                print(ft,'done')
            except:
                pyglet.resource.add_font(font_path+ft+'.ttf')
                print(ft,'ttf done')
        self.font = ['Star Guard','Star Guard Halftone']

        self.size_tile = 32 # en px

        self.textids = {}

        self.sprids = {}
        self.sprids['menu'] = {}


    def init(self):

        #self.nb=0
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)

        self.playing = True
        self.actions = ['menu','showing','nothing']
        self.action = 0

        self.init_menu()

        pyglet.clock.schedule_interval(self.gameloop,0.0000001)
        pyglet.app.run()

    def init_menu(self):

        self.sprids['menu']['play_btn'] = self.specMan.addThg(drawable.LabelButton(self.bite,(300,100),'PLAY',
                                                            (self.font[0],self.font[0]),
                                                            96,
                                                            self.current_size_scr[0]//2,
                                                            self.current_size_scr[1]//2 +100,color=(255,255,255,255)),'play_btn')
        self.buttons = {}

        self.buttons[0] = ['play_btn']

        self.action_menu = 0

    def on_key_press(self,symbol,modifiers):

        if symbol == key.ESCAPE:
            self.close()
        elif symbol == key.RETURN:
            self.bite()
    """
    def on_mouse_motion(self,x,y,dx,dy):

        if self.actions[self.action] == 'menu':
            for name in self.buttons[self.action_menu]:
                if x+dx > self.specMan.to_draw[name][0].x - self.specMan.to_draw[name][0].box[0] and x+dx < self.specMan.to_draw[name][0].x + self.specMan.to_draw[name][0].box[0] and y+dy > self.specMan.to_draw[name][0].y - self.specMan.to_draw[name][0].box[1] and y+dy < self.specMan.to_draw[name][0].y + self.specMan.to_draw[name][0].box[1]:
                    self.specMan.to_draw[name][0].the_mouse_is_here()
                else:
                    self.specMan.to_draw[name][0].the_mouse_is_not_here_anymore()
                #elif x > self.specMan.to_draw[name][0].x - self.specMan.to_draw[name][0].box[0] and x < self.specMan.to_draw[name][0].x + self.specMan.to_draw[name][0].box[0] and y > self.specMan.to_draw[name][0].y - self.specMan.to_draw[name][0].box[1] and y < self.specMan.to_draw[name][0].y + self.specMan.to_draw[name][0].box[1]:
                    #self.specMan.to_draw[name][0].the_mouse_is_not_here_anymore()

    def on_mouse_press(self,x, y, button, modifiers):

        if self.actions[self.action] == 'menu':
            for name in self.buttons[self.action_menu]:
                if self.specMan.to_draw[name][0].here:
                    self.specMan.to_draw[name][0].i_am_pressed()

    def on_mouse_release(self,x, y, button, modifiers):

        if self.actions[self.action] == 'menu':
            for name in self.buttons[self.action_menu]:
                if self.specMan.to_draw[name][0].pressed:
                    self.specMan.to_draw[name][0].i_am_released()
    """

    def bite(self):

        print('pd')
        img = pyglet.image.load('item/fond.png')
        img.blit(0,0)
        self.flip()
        os.system('pause')
    """
    def draw(self):

        if self.actions[self.action] == 'pd' or self.actions[self.action] == 'menu':


            if self.actions[self.action] == 'menu':

                if self.action_menu == 0:
                    self.specMan.draw(['play_btn'])
    """
    def gameloop(self,dt):

        if self.playing:

            ### CLEAR
            #self.clear()
            a=0

        else:
            self.close()


def main():

    app = App()
    app.init()

if __name__ == '__main__':
    main()









