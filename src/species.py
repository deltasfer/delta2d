





dic = {} ## dic regroupant des caractéristiques de chaque espèce (skin seq etc) afin que ça soa pratik qoa



## LOUTRE

if True:

    names = ['Louli','Croquette','Luisante','Marcel','Mamadou','Poisson','Lebleu','Rosetou','Cracante'
        ,'Dodue','Mimi','Moumou','Toumoumou','Limonade','Mimosa','Merlin','Timon','Timéo','Juice','Grenadine','Melon','Legend','IM THE LOUTRE MASTER']

    skin = { 'up':17,
        'right':20,
        'down':23,
        'left':26}

    skills = ['none','normal','walking','swimming']

    dic2 = { 'skin_seq':skin,
            'life':20,
            'names':names,
            'speed':20,
            'skills':skills,
            'size':(32,32)
            }

dic['loutre'] = dic2




## HUMAIN

if True:

    namesg = ['John']*25+['Gabriel','Raphaël','Léo','Louis','Lucas','Adam','Arthur','Jules','Hugo'
    ,'Maël','Liam','Ethan','Paul','Nathan','Gabin','Sacha','Noah','Tom','Mohamed','Aaron'
    ,'Théo','Noé','Victor','Martin','Mathis','Timéo','Nolan','Enzo','Éden','Axel','Antoine','Léon'
    ,'Marius','Robin','Valentin','Clément','Baptiste','Tiago','Rayan','Samuel','Amir','Augustin','Naël'
    ,'Maxime','Maxence','Gaspard','Eliott','Alexandre','Isaac','Mathéo','Yanis','Évan','Simon','Malo','Nino','Marceau','Kylian','Thomas'
    ,'Ibrahim','Imran','Ayden','Lenny','Camille','Lyam','Kaïs','Oscar','Naïm','Sohan','Côme','Milo','Noa','Ilyes','Noam','Diego','Ismaël'
    ,'Léandre','Soan','Mathys','Alexis','Lorenzo','Esteban','Owen','Youssef','Ilyan','William','Adrien','Ayoub','Jean','David','Ali','Adem'
    ,'Wassim','Logan','Sandro','Pablo','Antonin','Joseph','Benjamin','Noham','Kenzo']

    namesf = ['Emma','Jade','Louise','Alice','Chloé','Lina','Léa','Rose','Anna','Mila','Inès','Ambre','Julia','Mia','Léna','Manon','Juliette','Lou','Camille'
    ,'Zoé','Lola','Agathe','Jeanne','Lucie','Éva','Nina','Sarah','Romane','Inaya','Charlotte','Léonie','Romy','Adèle','Iris','Louna','Sofia','Margaux','Luna','Olivia'
    ,'Clémence','Victoria','Léana','Clara','Éléna','Victoire','Aya','Margot','Nour','Giulia','Charlie','Capucine','Mya','Mathilde','Lana','Anaïs','Lilou','Alicia','Théa'
    ,'Gabrielle','Lya','Yasmine','Maëlys','Assia','Apolline','Élise','Alix','Emy','Lise','Elsa','Lily','Lyana','Lisa','Noémie','Marie','Roxane','Lyna','Héloïse','Candice','Valentine'
    ,'Zélie','Maya','Soline','Maria','Célia','Maëlle','Emmy','Éléna','Faustine','Salomé','Lila','Louane','Alya','Thaïs','Constance','Laura','Mélina','Livia','Amelia','Océane','Sara']

    skin = { 'up':1,
        'right':4,
        'down':7,
        'left':10}

    skills = ['none','normal','walking']

    dic2 = {'skin_seq':skin,
            'life':100,
            'names':namesg+namesf,
            'speed':30,
            'skills':skills,
            'size':(32,32)
            }

dic['human'] = dic2






