







import pyglet

class SprButton(pyglet.text.Label):

    def __init__(self):

        super(SprButton,self).__init__()


class LabelButton(pyglet.text.Label):

    def __init__(self,fonction,box,text,font,font_size,x,y,param=None,color=(0,0,0,255),nobig=True):

        super(LabelButton,self).__init__(text,font_name=font,font_size=font_size,x=x,y=y,color=(0,0,0,255),anchor_y='center',anchor_x= 'center')

        self.fonction = fonction
        self.standard_size = font_size
        self.standard_col = color
        self.box = box

        self.nobig = nobig
        self.here = False
        self.pressed = False
        self.param = param

    def activate(self):
        #print(self.fonction,self.param)
        if self.param == None:
            self.fonction()
        elif type(self.param) == type([]) or type(self.param) == type((0,1)):
            self.fonction(*self.param)
        else:
            self.fonction(self.param)

    def i_am_pressed(self):
        self.font_size = int(self.standard_size*(3/4))
        self.pressed = True
        self.here = True

    def i_am_released(self):
        self.color = self.standard_col
        self.font_size = self.standard_size

        self.here = False
        self.pressed = False
        self.activate()

    def the_mouse_is_here(self):
        if not self.here:
            if not self.nobig:
                self.font_size = int(self.standard_size*1.5)
            self.color = (50, 175, 225,255)
            self.here = True

    def the_mouse_is_not_here_anymore(self):
        if self.here:
            if not self.nobig:
                self.font_size = self.standard_size
            self.color = self.standard_col
            self.here = False

    def get_box(self):
        w,h = self.box
        return self.x-w,self.y-h,w*2,h*2

class WritingBar(pyglet.text.Label):

    def __init__(self,fct,box,text,font,font_size,x,y,color=(100,100,100,255)):

        super(WritingBar,self).__init__(text,font_name=font,font_size=font_size,x=x,y=y,color=color,anchor_y='center',anchor_x= 'center')

        self.fonction = fct

        self.initial_text = text

        self.standard_col = color
        self.box = box

        self.selected = False
        self.validated = False

        self.writing_color = (50,50,50,255)
        self.initial_color = (100,100,100,255)
        self.yes_color = (0,255,0,255)
        self.no_color = (255,0,0,255)

    def i_am_selected(self):

        if self.text == self.initial_text:
            self.text = ''

        self.color = self.writing_color
        self.selected = True
        self.validated = False

    def add_letter(self,res):

        self.text+=res

    def del_letter(self):
        self.text = self.text[:-1]

    def he_tried_to_validate_XO(self):

        if self.text != '':
            if self.fonction(self.text):
                self.color = self.yes_color
                self.validated = True
            else:
                self.color = self.no_color
                self.validated = False
        else:
            self.text = self.initial_text
            self.color = self.initial_color
            self.validated = False

        self.selected = False

    def put_to_zero(self):
        self.text = self.initial_text
        self.color = self.initial_color
        self.validated = False
        self.selected = False



