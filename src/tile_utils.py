





import math

## definitions de fonctions et classes utiles pour le tilemapping

### VARIABLES

SIZE_TERRAIN = 4,4
SIZE_BIOM = 32,32
SIZE_TILE = 32,32

DEPTH_BIOM = 3

Y_DEP = (SIZE_BIOM[1]-1)*SIZE_TILE[1]
Y_DEP_BIOM = (SIZE_TERRAIN[1]-1)*SIZE_BIOM[1]*SIZE_TILE[1]

def set_var(ter,biom,tile=(32,32)):

    global SIZE_TERRAIN,SIZE_BIOM,SIZE_TILE,Y_DEP,Y_DEP_BIOM

    SIZE_TERRAIN = ter[0],ter[1]
    SIZE_BIOM = biom[0],biom[1]
    SIZE_TILE = tile[0],tile[1]

    Y_DEP = (SIZE_BIOM[1]-1)*SIZE_TILE[1]
    Y_DEP_BIOM = (SIZE_TERRAIN[1]-1)*SIZE_BIOM[1]*SIZE_TILE[1]


### CLASSES

class XY_Pos():

    def __init__(self,x=0,y=0):
        self.x = x
        self.y = y

    def xy(self):
        return self.x,self.y

    def __repr__(self):
        return "XY_Pos : x= %s, y= %s" % (self.x, self.y)
    def __str__(self):
        return "XY_Pos : x= %s, y= %s" % (self.x, self.y)

class BCX_Pos():

    def __init__(self,b=(0,0),c=(0,0),p=(0,0),l=0):

        #if b==(0,0) and c==(0,0) and p==(0,0):
        #print('connar')
        self.x = [b[0],c[0],p[0]]
        self.y = [b[1],c[1],p[1]]
        self.l = l
        #print(self)

    def bcx(self):
        return (self.x[0],self.y[0]),(self.x[1],self.y[1]),(self.x[2],self.y[2])

    def ijxy(self):
        return self.x[0],self.y[0],self.x[1],self.y[1]

    def lvl(self):
        return self.l

    def __repr__(self):
        return "BCX_Pos : x= %s, y= %s, l= %s" % (self.x, self.y,self.l)
    def __str__(self):
        return "BCX_Pos : x= %s, y= %s, l= %s" % (self.x, self.y,self.l)
    """def __sub__(self,pos):

        pos = pos.bcx()
        self.x[0]-= pos[0][0]
        self.x[1]-= pos[1][0]
        self.x[2]-= pos[2][0]
        self.x[0]-= pos[0][1]
        self.x[1]-= pos[1][1]
        self.x[2]-= pos[2][1]
        return BCX_Vec(*self.bcx())"""

class XY_Vec():

    def __init__(self,x=0,y=0):
        self.x = x
        self.y = y

    def xy(self):
        return self.x,self.y

    def __repr__(self):
        return "XY_Vec : x= %s, y= %s" % (self.x, self.y)
    def __str__(self):
        return "XY_Vec : x= %s, y= %s" % (self.x, self.y)

class BCX_Vec():

    def __init__(self,b=(0,0),c=(0,0),p=(0,0)):

        #if b==(0,0) and c==(0,0) and p==(0,0):
        #print('connar')
        self.x = [b[0],c[0],p[0]]
        self.y = [b[1],c[1],p[1]]
        #print(self)

    def bcx(self):
        return (self.x[0],self.y[0]),(self.x[1],self.y[1]),(self.x[2],self.y[2])

    def ijxy(self):
        return self.x[0],self.y[0],self.x[1],self.y[1]

    def __repr__(self):
        return "BCX_Vec : x= %s, y= %s" % (self.x, self.y)
    def __str__(self):
        return "BCX_Vec : x= %s, y= %s" % (self.x, self.y)

class XY_Size():

    def __init__(self,w=0,h=0):
        self.w = w
        self.h = h

    def xy(self):
        return self.w,self.h

    def __repr__(self):
        return "XY_Size : w= %s, h= %s" % (self.w, self.h)
    def __str__(self):
        return "XY_Size : w= %s, h= %s" % (self.w, self.h)

class BCX_Size():

    def __init__(self,b=(0,0),c=(0,0),p=(0,0)):
        self.w = [b[0],c[0],p[0]]
        self.h = [b[1],c[1],p[1]]

    def bcx(self):
        return (self.w[0],self.h[0]),(self.w[1],self.h[1]),(self.w[2],self.h[2])

    def ijxy(self):
        return self.w[0],self.h[0],self.w[1],self.h[1]

    def __repr__(self):
        return "BCX_Size : w= %s, h= %s" % (self.w, self.h)
    def __str__(self):
        return "BCX_Size : w= %s, h= %s" % (self.w, self.h)

class XY_Box():

    def __init__(self,x,y,w,h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def pos(self):
        return self.x,self.y
    def size(self):
        return self.w,self.h

    def Pos(self):
        return XY_Pos(self.x,self.y)
    def Size(self):
        return XY_Size(self.w,self.h)

    def __repr__(self):
        return "XY_Box : x= %s, y= %s, w= %s, h= %s" % (self.x, self.y,self.w, self.h)
    def __str__(self):
        return "XY_Box : x= %s, y= %s, w= %s, h= %s" % (self.x, self.y,self.w, self.h)

class BCX_Box():

    def __init__(self,b1=[0,0],c1=[0,0],p1=[0,0],l=0,b2=[0,0],c2=[0,0],p2=[0,0]):
        self.x = [b1[0],c1[0],p1[0]]
        self.y = [b1[1],c1[1],p1[1]]
        self.w = [b2[0],c2[0],p2[0]]
        self.h = [b2[1],c2[1],p2[1]]
        self.l = l

    def pos(self):
        return (self.x[0],self.y[0]),(self.x[1],self.y[1]),(self.x[2],self.y[2]),self.l
    def size(self):
        return (self.w[0],self.h[0]),(self.w[1],self.h[1]),(self.w[2],self.h[2])

    def Pos(self):
        return BCX_Pos((self.x[0],self.y[0]),(self.x[1],self.y[1]),(self.x[2],self.y[2]),self.l)
    def Size(self):
        return BCX_Size((self.w[0],self.h[0]),(self.w[1],self.h[1]),(self.w[2],self.h[2]))


    def __repr__(self):
        return "BCX_Box : x= %s, y= %s, l=%s, w= %s, h= %s" % (self.x, self.y,self.l,self.w, self.h)
    def __str__(self):
        return "BCX_Box : x= %s, y= %s, l=%s, w= %s, h= %s" % (self.x, self.y,self.l,self.w, self.h)


### CAMERAS

class Cam():

    def __init__(self,name,center=XY_Vec(),speed=1,scale=1):

        self.name = name
        self.center = XY_Vec(center.x,center.y)
        self.speed = speed #inversé, plus c'est petit, plus la camera bouge rapidement et de manière saccadée. privilegier 6 ou 8

        self.pos = XY_Vec(center.x,center.y)
        self.obj = XY_Vec(center.x,center.y)

    def update(self):

        #vec = xy_add(self.obj,self.pos)

        dx = - self.pos.x + self.obj.x
        dy = - self.pos.y + self.obj.y

        if abs(dx/self.speed) > 1:
            dx = dx//self.speed
        if abs(dy/self.speed) > 1:
            dy = dy//self.speed

        self.pos.x += dx
        self.pos.y += dy
        #self.pos = xy_add(self.pos,vec)

    def move(self,xy_vec):

        #print(self.pos)
        self.pos = xy_add(self.pos,xy_vec,-1)
        #print(self.pos)

    def xy(self):
        return self.center.x-self.pos.x,self.center.y-self.pos.y

CAMERA = Cam('cam')
ADMIN_CAM = Cam('admin')

def get_cam(xy_pos,speed):
    return Cam(CAMERA.name,xy_pos,speed),Cam(ADMIN_CAM.name)

def set_cam(cam,admin):
    global CAMERA,ADMIN_CAM
    CAMERA = cam
    ADMIN_CAM = admin


### FUNCTIONS

# useful

def module_XY(xy_vec):

    return math.sqrt( (xy_vec.x)**2 + (xy_vec.y)**2 )

def biom_in_terrain(b):
    if (b[0]>=0 and b[0]<SIZE_TERRAIN[0]) and (b[1]>=0 and b[1]<SIZE_TERRAIN[1]):
        return True
    else:
        #print(b,'not in terrain !')
        return False

def get_pos_map_biom(b,scr_size):
    i,j = b
    return (i*SIZE_TILE[0] + scr_size[0]//2 - (SIZE_TERRAIN[0]*SIZE_TILE[0])//2,-(j+1)*SIZE_TILE[0] + scr_size[1]//2 + (SIZE_TERRAIN[1]*SIZE_TILE[0])//2)

# conversions

def from_bcx_to_pxx(b,c):

    i,j = b
    x,y = c
    posx = ADMIN_CAM.center.x-ADMIN_CAM.pos.x + CAMERA.center.x-CAMERA.pos.x +SIZE_TILE[0]*x + i*SIZE_BIOM[0]*SIZE_TILE[0]
    posy = ADMIN_CAM.center.x-ADMIN_CAM.pos.y + CAMERA.center.y-CAMERA.pos.y +Y_DEP - SIZE_TILE[0]*y + Y_DEP_BIOM - j*SIZE_BIOM[1]*SIZE_TILE[0]

    return posx,posy

def from_pxpos_to_realpos(pxpos,admin=True):

    #print(CAMERA.xy().x + pxpos.x)
    x_on_scr = CAMERA.xy()[0] + pxpos.x
    y_on_scr = CAMERA.xy()[1] + pxpos.y

    if admin:
        x_on_scr += ADMIN_CAM.pos.x
        y_on_scr += ADMIN_CAM.pos.y

    return XY_Pos(x_on_scr,y_on_scr)

def from_real_to_pxpos(realpos,admin=True):

    pxx = -CAMERA.xy()[0] + realpos.x
    pxy = -CAMERA.xy()[1] + realpos.y

    if admin:
        pxx -= ADMIN_CAM.pos.x
        pxy -= ADMIN_CAM.pos.y

    return XY_Pos(pxx,pxy)


def from_xy_to_bcx(xy_thg,l=0):

    if type(xy_thg) == XY_Pos:

        bx = xy_thg.x//(SIZE_BIOM[0]*SIZE_TILE[0])
        cx = (xy_thg.x%(SIZE_BIOM[0]*SIZE_TILE[0]))//SIZE_TILE[0]
        px = (xy_thg.x%(SIZE_BIOM[0]*SIZE_TILE[0]))%SIZE_TILE[0]

        y = xy_thg.y - Y_DEP - Y_DEP_BIOM
        py = (y%(SIZE_BIOM[1]*SIZE_TILE[1]))%(SIZE_TILE[1])

        y = - xy_thg.y + Y_DEP + Y_DEP_BIOM + py

        by = y//(SIZE_BIOM[1]*SIZE_TILE[1])
        cy = (y%(SIZE_BIOM[1]*SIZE_TILE[1]))//(SIZE_TILE[1])

        return BCX_Pos((bx,by),(cx,cy),(px,py),l)

    elif type(xy_thg) == XY_Vec:

        bx = xy_thg.x//(SIZE_BIOM[0]*SIZE_TILE[0])
        cx = (xy_thg.x%(SIZE_BIOM[0]*SIZE_TILE[0]))//SIZE_TILE[0]
        px = (xy_thg.x%(SIZE_BIOM[0]*SIZE_TILE[0]))%SIZE_TILE[0]

        by = xy_thg.y//(SIZE_BIOM[1]*SIZE_TILE[1])
        cy = (xy_thg.y%(SIZE_BIOM[1]*SIZE_TILE[1]))//SIZE_TILE[1]
        py = (xy_thg.y%(SIZE_BIOM[1]*SIZE_TILE[1]))%SIZE_TILE[1]

        return BCX_Vec((bx,by),(cx,cy),(px,py))

    elif type(xy_thg) == XY_Size:

        bw = xy_thg.w//(SIZE_BIOM[0]*SIZE_TILE[0])
        cw = (xy_thg.w%(SIZE_BIOM[0]*SIZE_TILE[0]))//SIZE_TILE[0]
        pw = (xy_thg.w%(SIZE_BIOM[0]*SIZE_TILE[0]))%SIZE_TILE[0]

        bh = xy_thg.h//(SIZE_BIOM[1]*SIZE_TILE[1])
        ch = (xy_thg.h%(SIZE_BIOM[1]*SIZE_TILE[1]))//SIZE_TILE[1]
        ph = (xy_thg.h%(SIZE_BIOM[1]*SIZE_TILE[1]))%SIZE_TILE[1]

        return BCX_Pos((bw,bh),(cw,ch),(pw,ph))

    elif type(bcx_thg) == XY_Box:

        pos = from_xy_to_bcx(XY_Pos(bcx_thg.x,bcx_thg.y))
        size = from_xy_to_bcx(XY_Size(bcx_thg.w,bcx_thg.h))

        return BCX_Box(*pos.bcx(),l,*size.bcx())

def from_bcx_to_xy(bcx_thg):

    if type(bcx_thg) == BCX_Pos:

        px = SIZE_TILE[0]*SIZE_BIOM[0]*bcx_thg.x[0] + SIZE_TILE[0]*bcx_thg.x[1] + bcx_thg.x[2]
        py = Y_DEP + Y_DEP_BIOM - SIZE_TILE[1]*SIZE_BIOM[1]*bcx_thg.y[0] - SIZE_TILE[1]*bcx_thg.y[1] + bcx_thg.y[2]

        return XY_Pos(px,py)

    elif type(bcx_thg) == BCX_Vec:

        px = SIZE_TILE[0]*SIZE_BIOM[0]*bcx_thg.x[0] + SIZE_TILE[0]*bcx_thg.x[1] + bcx_thg.x[2]
        py = SIZE_TILE[1]*SIZE_BIOM[1]*bcx_thg.y[0] + SIZE_TILE[1]*bcx_thg.y[1] + bcx_thg.y[2]

        return XY_Vec(px,py)

    elif type(bcx_thg) == BCX_Size:

        wx = SIZE_TILE[0]*SIZE_BIOM[0]*bcx_thg.w[0] + SIZE_TILE[0]*bcx_thg.w[1] + bcx_thg.w[2]
        wy = SIZE_TILE[1]*SIZE_BIOM[1]*bcx_thg.h[0] + SIZE_TILE[1]*bcx_thg.h[1] + bcx_thg.h[2]

        return XY_Size(wx,wy)

    elif type(bcx_thg) == BCX_Box:

        x,y = from_bcx_to_xy(BCX_Pos((bcx_thg.x[0],bcx_thg.y[0]),(bcx_thg.x[1],bcx_thg.y[1]),(bcx_thg.x[2],bcx_thg.y[2]))).xy()
        w,h = from_bcx_to_xy(BCX_Size((bcx_thg.w[0],bcx_thg.h[0]),(bcx_thg.w[1],bcx_thg.h[1]),(bcx_thg.w[2],bcx_thg.h[2]))).xy()

        return XY_Box(x,y,w,h)


# additions

def bcx_add(bcx_thg,bcx_vec):

    l = bcx_thg.l
    xy_thg = from_bcx_to_xy(bcx_thg)
    xy_vec = from_bcx_to_xy(bcx_vec)
    return from_xy_to_bcx(xy_add(xy_thg,xy_vec),l)

def xy_add(xy_thg,xy_vec, k=1):

    xy_thg.x = xy_thg.x +k*xy_vec.x
    xy_thg.y = xy_thg.y +k*xy_vec.y

    return xy_thg


# algo collisions

def algo_colli_BCX(init_bcx_box,bcx_vec,colli_bcx_box):

    init_xy_box = from_bcx_to_xy(init_bcx_box)
    xy_vec = from_bcx_to_xy(bcx_vec)
    colli_xy_box = from_bcx_to_xy(colli_bcx_box)
    return algo_colli_XY(init_xy_box,xy_vec,colli_xy_box)

def algo_colli_XY(init_xy_box,xy_vec,colli_xy_box):

    box1 = XY_Box(init_xy_box.x,init_xy_box.y,init_xy_box.w,init_xy_box.h)
    box1.x += xy_vec.x
    box1.y += xy_vec.y
    return colli_AABB_XY(box1,colli_xy_box)

def colli_AABB_XY(box1,box2): #EST-CE QUE CA COLLISIONNE BIEN PAS ?

    if ((box2.x >= box1.x + box1.w) or (box2.x + box2.w <= box1.x) or (box2.y >= box1.y + box1.h) or (box2.y + box2.h <= box1.y)):
        return True # retourne un okaaayyyy c'est bon ca collisionne PAS
    else:
        return False # aoutch ca collisionne

def colli_ABP_XY(box,pt): #EST-CE QUE LE POINT EST BIEN DANS LA BOX ?

    if type(pt) == XY_Pos:
        if (pt.x >= box.x) and (pt.x < box.x + box.w) and (pt.y >= box.y) and (pt.y < box.y + box.h):
            return True # okaaayyyy t'es bien dans la boite mon pti
        else:
            return False # retourne un ouai bah non t pas dedans
    else:
        if (pt[0] >= box.x) and (pt[0] < box.x + box.w) and (pt[1] >= box.y) and (pt[1] < box.y + box.h):
            return True # okaaayyyy t'es bien dans la boite mon pti
        else:
            return False # retourne un ouai bah non t pas dedans

def colli_ABP(box,pt):
    x,y,w,h = box
    if (pt[0] >= x) and (pt[0] < x + w) and (pt[1] >= y) and (pt[1] < y + h):
        return True # okaaayyyy t'es bien dans la boite mon pti
    else:
        return False # retourne un ouai bah non t pas dedans

def colli_ABP_mult(boxes,pt):
    ## retourne None si le point est dans aucune boite
    ## retourne la premiere box des boites concernées sinon

    goodx = []
    goody = []

    ## Premier niveau -> on vérifie si on est pas à gauche de toutes les box
    for i in range(len(boxes)):
        if pt[0] >= boxes[i][0]:
            goodx.append(i)
    if goodx == []:
        return None # retourne un ouai bah t'es dans rien mon pote

    ## 2e niveau -> on vérifie si on est pas en dessous des box qui sont bien
    for i in goodx:
        if pt[1] >= boxes[i][1]:
            goody.append(i)
    if goody == []:
        return None # retourne un ouai bah t'es dans rien mon pote

    ## 3e niveau -> on vérifie si on est pas à droite des box qui sont bien
    goodx = []
    for i in goody:
        if pt[0] < boxes[i][0] + boxes[i][2]:
            goodx.append(i)
    if goodx == []:
        return None # retourne un ouai bah t'es dans rien mon pote

    ## 4e niveau -> on vérifie si on est pas en haut des box qui sont bien
    goody = []
    for i in goodx:
        if pt[1] < boxes[i][1] + boxes[i][3]:
            goody.append(i)
    if goody == []:
        return None # retourne un ouai bah t'es dans rien mon pote

    return goody[0]



