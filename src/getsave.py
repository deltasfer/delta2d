"""""
programme sauvegarde de fichiers sources
"""""

# va de pair avec getback v3

version = 3

import os

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

def get_version(bigpath,save_path = '/autosav/'):
    version = ['alpha',10001]

    try:
        with open(bigpath+save_path+'version','r') as f:
            tab = f.read().split('_')
            version = [tab[0],int(tab[1])*10000+int(tab[2])]
    except:
        a=0
    return version[0]+'_'+str(version[1])[0]+'_'+str(version[1])[-4:]
