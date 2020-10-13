



import random,os,ctypes,time
from ctypes import windll, Structure, c_long, byref
from math import *
#from win32gui import GetWindowRect, GetForegroundWindow, GetWindowText


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

## partie SCREEN

def get_screen_size():
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


## partie random

def choice(thg):

    if type(thg) == type({}):
        return choice(list(thg.keys()))
        #print(thg.keys())
    else:
        return random.choice(thg)

def randmultint(n,a,b=None): #returns n differents numbers between a and b-1

    if b == None:
        return randmultint(n,0,a-1)
    else:
        t = []
        while len(t) < n:
            new = random.randint(a,b-1)
            while new in t:
                new = random.randint(a,b-1)
            t.append(new)
        return t


def get_key_from_value(d,v,s=[]): # v valeur seule, d dic ou tab

    if type(d) == type({}):
        for key,val in d.items():
            if type(val) != type({}) and type(val) != type([]):
                if v == val:
                    return s+[key]
            else:
                ns = get_key_from_value(val,v,s+[key])
                if ns != None:
                    return ns

    elif type(d) == type([]):
        for key in range(len(d)):
            val = d[key]
            if type(val) != type({}) and type(val) != type([]):
                #print(val)
                if v == val:
                    return s+[key]
            else:
                ns = get_key_from_value(val,v,s+[key])
                if ns != None:
                    return ns

    return None

def getMousePos():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return pt.x,pt.y

def module(x,y):
    return sqrt(x**2+y**2)

def int_rd(dec):
    if dec < int(dec)+0.5:
        return int(dec)
    else:
        return ceil(dec)

def sign(n):
    if n==0:
        return 0
    else:
        return n//abs(n)

def rangef(a,b,d=1):

    res = []
    if b > a:
        while b>a:
            res.append(a)
            a+=d
    else:
        while abs(b-a)>0:
            res.append(a)
            a+=d

    return res

ids = 1112

def get_id(key):

    global ids

    id = ''+key
    id+=str(ids)
    ids+=1
    return id

def mycopy(thg):

    if type(thg) == type([]):

        res = []

        for i in thg:
            res.append(mycopy(i))

        return res

    else:

        return thg

def truncate(f, n=3):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

### PARTIE AUTO-SAUVEGARDE

def save_files(bigpath,path = ['/.','/src'],save_path = '/autosav/'):

    autosav = ''

    for chem in path:
        #print('path',bigpath+chem,':',os.listdir(bigpath+chem))
        try:
            for file in os.listdir(bigpath+chem):
                if file[-3:] == '.py':
                    autosav += '\n\n\n _newfile_ :' + bigpath+chem+'/'+file + '\n\n\n'
                    with open(bigpath+chem+'/'+file,'r') as f:
                        autosav += f.read()
        except :
            jsghd=0
            #print('no path',bigpath+chem,':',os.listdir(bigpath+chem))

    version = ['alpha',10001]

    try:
        with open(bigpath+save_path+'version','r') as f:
            tab = f.read().split('_')
            version = [tab[0],int(tab[1])*10000+int(tab[2])]
        version[1]+=1
        with open(bigpath+save_path+'version','w') as f:
            f.write(version[0]+'_'+str(version[1])[0]+'_'+str(version[1])[-4:])
    except:
        os.makedirs(bigpath+save_path)
        with open(bigpath+save_path+'version','w') as f:
            f.write(version[0]+'_'+str(version[1])[0]+'_'+str(version[1])[-4:])

    with open(bigpath+save_path+'saved_'+version[0]+'_'+str(version[1])[0]+'_'+str(version[1])[-4:]+'.savd','w') as f:
        f.write(autosav)

    print('files saved, version',version[0]+'_'+str(version[1])[0]+'_'+str(version[1])[-4:])

def recup_files(path2):

    currentpath = path2.split('\\')[-1]
    currentpath = currentpath.split('/')[-1]
    currentpath = path2[:(len(path2)-len(currentpath))]

    all =[]
    with open(path2,'r') as f:
        all = f.readlines()

    files = {}
    titles = [0]
    file = []
    for line in all:
        if '_newfile_ :' in line and line[-4:] == '.py\n':
            name = line[len('_newfile_ '):]
            names = name.split('\\')
            names2 = []

            for nam in names:
                for naam in nam.split('/'):
                    names2.append(naam)
                    name = ('/').join(names2[-2:])

            files[titles[-1]] = file
            titles.append(name[:-1])
            file = []
        else:
            file.append(line)

    files[titles[-1]] = file

    for name in files:
        print(name)
        if name != 0:
            try:
                with open(currentpath+name,'w') as f:
                    for line in files[name]:
                        f.write(line)
            except :
                file = name.split('/')[0]
                os.makedirs(currentpath+file)
                with open(currentpath+name,'w') as f:
                    for line in files[name]:
                        f.write(line)

def get_version(bigpath,save_path = '/autosav/'):
    version = ['alpha',10001]

    try:
        with open(bigpath+save_path+'version','r') as f:
            tab = f.read().split('_')
            version = [tab[0],int(tab[1])*10000+int(tab[2])]
    except:
        a=0
    return version[0]+'_'+str(version[1])[0]+'_'+str(version[1])[-4:]

def compt(bigpath,path = ['/.','/src']):

    long = 0

    for chem in path:
        try:
            for file in os.listdir(bigpath+chem):
                if file[-3:] == '.py':
                    with open(bigpath+chem+'/'+file,'r') as f:
                        long += len(f.readlines())
        except :
            jsghd=0
            #print('no path',bigpath+chem,':',os.listdir(bigpath+chem))

    return long
