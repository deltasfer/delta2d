import os,pyglet

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))+'\\' # fopatouché

def couper(nom,size=(32,32)):


    img = pyglet.image.load(CURRENT_PATH+nom)
    size = img.height//size[1], img.width//size[0]
    textures = pyglet.image.ImageGrid(img, *size)

    i=0
    for txt in textures:
        txt.save(CURRENT_PATH+nom.split('.')[0]+'_'+str(i)+'.'+nom.split('.')[1])
        i+=1
