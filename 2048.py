 #!/usr/bin/env python
# -*- coding: utf8 -*-
import random #fonction random
points = 0
print ("----------Game Rules----------\n")
print("Il faut fusionner les cases identiques (2 et 2; 4 et 4 ect...) ")
print("z = haut, q = gauche, d = droite, s = bas")
print("Notez que ce jeu a un lien avec le cours sur le binaire en classe car il s'agit a chaque fois  de puissance de 2 ")
#----------Initialisation----------
game_box = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]] #tableau 4 lignes et 4 colonnes
position_chiffre_dans_game_box = [0,1,2,3]
position_ligne_chiffre1 = random.choice(position_chiffre_dans_game_box) #choice permet de choisir al�atoirement un element dans une liste. Ici pour choisir la ligne et la colonne ou le chiffre 2 va se mettre
position_colonne_chiffre1 = random.choice(position_chiffre_dans_game_box)
game_box[position_ligne_chiffre1][position_colonne_chiffre1] = 2# on place un 2 dans une ligne et colonne aleatoirement

position_ligne_chiffre2 = random.choice(position_chiffre_dans_game_box)
position_colonne_chiffre2 = random.choice(position_chiffre_dans_game_box)
game_box[position_ligne_chiffre2][position_colonne_chiffre2] = 2 # on place un deuxieme 2 choisi aleatoirement

#recalcule de la position du deuxieme chiffre tant que les deux chiffres sont a la meme position
while position_ligne_chiffre1 == position_ligne_chiffre2 and position_colonne_chiffre1 == position_colonne_chiffre2:
    position_ligne_chiffre2 = random.choice(position_chiffre_dans_game_box)
    position_colonne_chiffre2 = random.choice(position_chiffre_dans_game_box)
    game_box[position_ligne_chiffre2][position_colonne_chiffre2] = 2


#----------mouvement_haut----------
def up_movement(game_box):
    ligne = int(0)
    for colonne in range(0,4): #boucle sur les 4 lignes
        if game_box[ligne][colonne]!=0 or game_box[ligne+1][colonne]!=0 or game_box[ligne+2][colonne]!=0 or game_box[ligne+3][colonne]!=0: #si chiffres ligne 1 different de 0 ou chiffres ligne 2 different de 0 ...
            if game_box[ligne][colonne]==0: #si il ya un zero dans la premiere ligne
                while game_box[ligne][colonne] == 0: #boucle jusqu'a ce qu'un chiffre different de zéro apparaisse dans la premiere ligne
                    for i in range (0,3):
                        game_box[ligne+i][colonne] = game_box[ligne+i+1][colonne]
                    game_box[ligne+3][colonne] = 0


            if game_box[ligne+1][colonne]==0 and (game_box[ligne+2][colonne]!=0 or game_box[ligne+3][colonne]!=0): #si les chiffres de la deuxieme ligne sont egales a 0 et si les chiffres de la 3 eme ou 4 eme ligne different de 0
                while game_box[ligne+1][colonne]==0: #boucle sur la deuxi�me ligne si chiffre = 0
                    for i in range (1,3):
                        game_box[ligne+i][colonne] = game_box[ligne+i+1][colonne]
                    game_box[ligne+3][colonne] = 0

            if game_box[ligne+2][colonne] == 0 and game_box[ligne+3][colonne]!=0: #si chiffre de la 3 eme ligne = 0 et chiffre de la quatri�me diff�rent de 0:
                while game_box[ligne+2]==0:
                    game_box[ligne+2] = game_box[ligne+3]
                    game_box[ligne+3][colonne] = 0



def up_addition(game_box):
    ligne = int(0)
    global points
    for colonne in range(0,4):#loop sur colonnes
        if game_box[ligne][colonne]==game_box[ligne+1][colonne]: #si chiffre premi�re ligne egale chiffre deuxi�me ligne
            game_box[ligne][colonne]=game_box[ligne][colonne]+game_box[ligne+1][colonne] #ajoute 1 er et deuxieme element de la colonne + stocke en tant que 1 er element
            points += game_box[ligne][colonne] #ajoute les points si simplification

            for i in range (1,3):
                game_box[ligne+i][colonne] = game_box[ligne+i+1][colonne]
                game_box[ligne+3][colonne] = 0


        if game_box[ligne+1][colonne]==game_box[ligne+2][colonne]: #si 2 eme et 3 eme colonne sont egale
            game_box[ligne+1][colonne]=game_box[ligne+1][colonne]+game_box[ligne+2][colonne] #ajoute deuxieme et troisieme + stocke en tant que deuxieme
            points += game_box[ligne+1][colonne] #ajoute point pour simplification
            game_box[ligne+2][colonne]=game_box[ligne+3][colonne] #4 to 3 eme position
            game_box[ligne+3][colonne]=0 #4 = 0

        if game_box[ligne+2][colonne]==game_box[ligne+3][colonne]: #si 3 et 4 egale
            game_box[ligne+2][colonne]=game_box[ligne+2][colonne]+game_box[ligne+3][colonne] #ajoute 3 et et 4 eme et stocke dans 3 eme
            points += game_box[ligne+2][colonne] #ajoute des points
            game_box[ligne+3][colonne]=0 #4 eme a 0



#----------mouvement_bas----------

def down_movement(game_box):
    ligne = int(0)
    for colonne in range(0,4): #loop sur colonnes
        if game_box[ligne][colonne]!=0 or game_box[ligne+1][colonne]!=0 or game_box[ligne+2][colonne]!=0 or game_box[ligne+3][colonne]!=0: #si ligne 1 ou ligne 2 ou ligne 3 ou ligne 4 diffferent de 0
            if game_box[ligne+3][colonne]==0: #si dernier element = 0
                while game_box[ligne+3][colonne]==0: #loop si 4 eme element = 0
                    indice=3
                    for i in range (0,3):
                        game_box[ligne+indice][colonne] = game_box[ligne+indice-1][colonne]
                        indice =  indice-1
                    game_box[ligne][colonne] = 0

            if game_box[ligne+2][colonne]==0 and (game_box[ligne+1][colonne]!=0 or game_box[ligne][colonne]!=0): #si 3 eme ligne = 0 et 1 ere et 2 eme ligne different de 0
                while game_box[ligne+2][colonne]==0: #loop si 3 eme ligne = 0
                     indice=2
                     for i in range (0,2):
                        game_box[ligne+indice][colonne] = game_box[ligne+indice-1][colonne]
                        indice =  indice-1
                     game_box[ligne][colonne] = 0

            if game_box[ligne+1][colonne]==0 and game_box[ligne][colonne]!=0: #si 2 eme ligne = 0 et 1 ere ligne different 0
                while game_box[ligne+1][colonne]==0: #loop si 2 eme ligne = 0
                    game_box[ligne+1][colonne]=game_box[ligne][colonne]
                    game_box[ligne][colonne]=0



def down_addition(game_box): #après mouvement bas
    ligne=int(0)
    global points
    for colonne in range(0,4): #looping sur tableau
        if game_box[ligne+3][colonne]==game_box[ligne+2][colonne]: #si 3 et 4 eme ligne egale
            game_box[ligne+3][colonne]=game_box[ligne+3][colonne] + game_box[ligne+2][colonne] #ajoute 3 et 4 eme ligne et stocke en tant que 4 eme element
            points += game_box[ligne+3][colonne] #ajoute point

            indice=2
            for i in range (0,2):
                game_box[ligne+indice][colonne] = game_box[ligne+indice-1][colonne]
                indice =  indice-1
            game_box[ligne][colonne] = 0


        if game_box[ligne+2][colonne]==game_box[ligne+1][colonne]:
            game_box[ligne+2][colonne]=game_box[ligne+2][colonne]+game_box[ligne+1][colonne]
            points += game_box[ligne+2][colonne]
            game_box[ligne+1][colonne]=game_box[ligne][colonne]
            game_box[ligne][colonne]=0

        if game_box[ligne+1][colonne]==game_box[ligne][colonne]:
            game_box[ligne+1][colonne]=game_box[ligne+1][colonne]+game_box[ligne][colonne]
            points += game_box[ligne+1][colonne]
            game_box[ligne][colonne]=0


#----------mouvement_gauche----------

def left_movement(game_box):
    colonne=int(0)
    for ligne in range(0,4):

        if game_box[ligne][colonne]!=0 or game_box[ligne][colonne+1]!=0 or game_box[ligne][colonne+2]!=0 or game_box[ligne][colonne+3]!=0:
            if game_box[ligne][colonne]==0:
                while game_box[ligne][colonne]==0:

                    for i in range (0,3):
                        game_box[ligne][colonne+i] = game_box[ligne][colonne+i+1]
                    game_box[ligne][colonne+3] = 0

            if game_box[ligne][colonne+1]==0 and (game_box[ligne][colonne+2]!=0 or game_box[ligne][colonne+3]!=0):
                while game_box[ligne][colonne+1]==0:
                     for i in range (1,3):
                        game_box[ligne][colonne+i] = game_box[ligne][colonne+i+1]
                     game_box[ligne][colonne+3] = 0


            if game_box[ligne][colonne+2]==0 and (game_box[ligne][colonne+3]!=0):
                while game_box[ligne][colonne+2]==0:
                    game_box[ligne][colonne+2]=game_box[ligne][colonne+3]
                    game_box[ligne][colonne+3]=0


def left_addition(game_box):
    colonne=int(0)
    global points
    for ligne in range(0,4):
        if game_box[ligne][colonne]==game_box[ligne][colonne+1]:
            game_box[ligne][colonne]=game_box[ligne][colonne]+game_box[ligne][colonne+1]
            points += game_box[ligne][colonne]
            for i in range (1,3):
                game_box[ligne][colonne+i] = game_box[ligne][colonne+i+1]
            game_box[ligne][colonne+3] = 0


        if game_box[ligne][colonne+1]==game_box[ligne][colonne+2]:
            game_box[ligne][colonne+1]=game_box[ligne][colonne+1]+game_box[ligne][colonne+2]
            points += game_box[ligne][colonne+1]
            game_box[ligne][colonne+2]=game_box[ligne][colonne+3]
            game_box[ligne][colonne+3]=0

        if game_box[ligne][colonne+2]==game_box[ligne][colonne+3]:
            game_box[ligne][colonne+2]=game_box[ligne][colonne+2]+game_box[ligne][colonne+3]
            points += game_box[ligne][colonne+2]
            game_box[ligne][colonne+3]=0


#----------mouvement_droite----------

def right_movement(game_box):
    colonne=int(0)
    for ligne in range(0,4):
        if game_box[ligne][colonne]!=0 or game_box[ligne][colonne+1]!=0 or game_box[ligne][colonne+2]!=0 or game_box[ligne][colonne+3]!=0:
            if game_box[ligne][colonne+3]==0:
                while game_box[ligne][colonne+3]==0:
                    indice = 3
                    for i in range (0,3):
                        game_box[ligne][colonne+indice] = game_box[ligne][colonne+indice-1]
                        indice =  indice -1
                    game_box[ligne][colonne] = 0


            if game_box[ligne][colonne+2]==0 and (game_box[ligne][colonne+1]!=0 or game_box[ligne][colonne]!=0):
                while game_box[ligne][colonne+2]==0:
                    indice = 2
                    for i in range (0,2):
                        game_box[ligne][colonne+indice] = game_box[ligne][colonne+indice-1]
                        indice =  indice -1
                    game_box[ligne][colonne] = 0

            if game_box[ligne][colonne+1]==0 and game_box[ligne][colonne]!=0:
                while game_box[ligne][colonne+1]==0:
                    game_box[ligne][colonne+1]=game_box[ligne][colonne]
                    game_box[ligne][colonne]=0





def right_addition(game_box):
    colonne=int(0)
    global points
    for ligne in range(0,4):
        if game_box[ligne][colonne+3]==game_box[ligne][colonne+2]:
            game_box[ligne][colonne+3]=game_box[ligne][colonne+3] + game_box[ligne][colonne+2]
            points += game_box[ligne][colonne+3]

            indice = 2
            for i in range (0,2):
                game_box[ligne][colonne+indice] = game_box[ligne][colonne+indice-1]
                indice =  indice -1
            game_box[ligne][colonne] = 0

        if game_box[ligne][colonne+2]==game_box[ligne][colonne+1]:
            game_box[ligne][colonne+2]=game_box[ligne][colonne+2]+game_box[ligne][colonne+1]
            points += game_box[ligne][colonne+2]
            game_box[ligne][colonne+1]=game_box[ligne][colonne]
            game_box[ligne][colonne]=0

        if game_box[ligne][colonne+1]==game_box[ligne][colonne]:
            game_box[ligne][colonne+1]=game_box[ligne][colonne+1]+game_box[ligne][colonne]
            points += game_box[ligne][colonne+1]
            game_box[ligne][colonne]=0



while True:
    print ("Vos points")
    print (str(points))
    print ("\n\n")
    print (game_box[0][0],"|",game_box[0][1],"|",game_box[0][2],"|",game_box[0][3],"\n")
    print (game_box[1][0],"|",game_box[1][1],"|",game_box[1][2],"|",game_box[1][3],"\n")
    print (game_box[2][0],"|",game_box[2][1],"|",game_box[2][2],"|",game_box[2][3],"\n")
    print (game_box[3][0],"|",game_box[3][1],"|",game_box[3][2],"|",game_box[3][3],"\n")
    Liste_2_ou_4=[2,4]
    #les "evenement" avec input
    movement_choice = input("8 = haut, 4 = gauche, 6 = droite, 2 = bas")
    if movement_choice == "z":
        up_movement(game_box)
        up_addition(game_box)
    elif movement_choice == "s":
        down_movement(game_box)
        down_addition(game_box)
    elif movement_choice == "q":
        left_movement(game_box)
        left_addition(game_box)
    elif movement_choice == "d":
        right_movement(game_box)
        right_addition(game_box)
    position_0_lignes = []
    position_0_colonnes = []
    for ligne in range(0,4):
        for colonne in range(0,4):
            if game_box[ligne][colonne] == 0:
                position_0_lignes.append(ligne) #prend position des 0 dans les lignes
                position_0_colonnes.append(colonne)#prend position de 0 dans les colonnes
            if game_box[ligne][colonne] == 2048:#regarde dans tout le tableau si il y a un chiffre 2048
                print ("t'as gagne")
                break
#pour mettre aleatoirement les chiffre 2 ou 4 au fil du colonneeu
    if len(position_0_lignes) > 1: #si il y a plusieurs 0 dans les lignes
        random_index = position_0_lignes.index(random.choice(position_0_lignes))
        nombre_placer_ligne = position_0_lignes[random_index]
        nombre_placer_colonne = position_0_colonnes[random_index]
        game_box[nombre_placer_ligne][nombre_placer_colonne] = random.choice(Liste_2_ou_4) #mettre 2 ou 4 dans une ligne et colonne choisis aleatoirement parmi les places libres (les 0 du tableau)

    elif len(position_0_lignes) == 1: # si il reste qu'un 0
        nombre_placer_ligne = position_0_lignes[0]
        nombre_placer_colonne = position_0_colonnes[0]
        game_box[nombre_placer_ligne][nombre_placer_colonne] = random.choice(Liste_2_ou_4) #mettre un 2 ou un 4 dans la position du dernier 0

    else: #si plus de zero et qu'il n'y a pas simplification au prochain coup on arrete le jeu
        break

print ("Game over !! tu as  ", str(points), "points")
