

from src import tile_utils as tut

"""
tout d'abord on défini les positions/sizes relatives, ne
prenant pas en compte la taille de l'ecran
"""


## GENERAL

_a = 1,1
_100x,_100y = 1/19.2 , 1/10.8 # donne 100 pixel par 100 pixel pour du fullhd = 1920x1080
_10x,_10y = 1/192 , 1/108
_1x,_1y = 1/1920 , 1/1080

## POSITIONS

POS_LOADING_bar = 1/2-1/4,1/8

POS_HUD_health_bar = 32*_1x , 32*_1y
POS_HUD_inventory_bar = POS_HUD_health_bar[0] , 18*_10y
POS_HUD_inventory_big = POS_HUD_health_bar[0] , 18*_10y + _100y
POS_HUD_inventory_bar_cursor = POS_HUD_inventory_bar[0] + 19*_1x , POS_HUD_inventory_bar[1] + _10y
POS_HUD_inventory_big_cursor = POS_HUD_inventory_big[0] + 19*_1x , POS_HUD_inventory_big[1] + _10y


## SIZES

SIZ_LOADING_bar = (1/2-POS_LOADING_bar[0])*2,32*_1y

SIZ_HUD_inventory_bar = 502*_1x , 6*_10y
SIZ_HUD_inventory_big = 502*_1x , 5*_100y
SIZ_HUD_inventory_selection = 50*_1x, 50*_1y

"""
maintenant qu'on a defini toutes les positions et tailles relatives,
on les utilise pour créer les BOX, POS,SIZ absolues dont on a besoin dans le programme général,
prenant donc en compte la taille de l'ecran
"""

SIZE_SCREEN = 1920,1080 # default

def box_apply_scr(pos,size):

    return tut.XY_Box(pos[0]*SIZE_SCREEN[0],pos[1]*SIZE_SCREEN[1],size[0]*SIZE_SCREEN[0],size[1]*SIZE_SCREEN[1])

def apply_scr(thg):

    return thg[0]*SIZE_SCREEN[0],thg[1]*SIZE_SCREEN[1]


def update():

    g,b,p,s = {},{},{},{} #boxes , positions, sizes


    ### GENERAL

    g['ax'],g['ay'] = apply_scr(_a)
    g['1x'],g['1y'] = apply_scr((_1x,_1y))
    g['10x'],g['10y'] = apply_scr((_10x,_10y))
    g['100x'],g['100y'] = apply_scr((_100x,_100y))

    ### POSITIONS

    p['loading_bar'] = apply_scr(POS_LOADING_bar)

    p['hud_healthbar'] = apply_scr(POS_HUD_health_bar)
    p['hud_inventory_cursor_bar'] = apply_scr(POS_HUD_inventory_bar_cursor)
    p['hud_inventory_cursor_big'] = apply_scr(POS_HUD_inventory_big_cursor)

    ### BOXES

    s['loading_bar'] = apply_scr(SIZ_LOADING_bar)

    s['hud_inventory_selection'] = apply_scr(SIZ_HUD_inventory_selection)


    #inventaire
    b['hud_inventory'] = [box_apply_scr(POS_HUD_inventory_bar,SIZ_HUD_inventory_bar),
                box_apply_scr(POS_HUD_inventory_big,SIZ_HUD_inventory_big)]

    return g,b,p,s

### BOXES (on utilise les pos et les sizes précedentes)

GEN,BOX,POS,SIZ = update()

def set_size_screen(size):
    global SIZE_SCREEN,GEN,BOX,POS,SIZ
    if size != SIZE_SCREEN:
        SIZE_SCREEN = size
        GEN,BOX,POS,SIZ = update()



