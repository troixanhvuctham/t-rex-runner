# coding: utf8

from master import *
import numpy as np
import random as rd


# ----------------------- DESCRIPTIONS ----------------------- #

# Variables d'entrée normalisées entre 0 et 1
# max_cactus_size : 75
# max_speed : 13
# max_distance : 600
# Variable  de sortie : HAUT pour > 0.6
#                       BAS  pour < 0.4

# STRUCTURE DU RN :      3   --   3   --   1
#
#              distance.╭─╮ ____ ╭─╮
#                       ╰─╯ ╲  ╱ ╰─╯ ╲
#                taille.╭─╮ _╲╱_ ╭─╮ _╲_ ╭─╮.sortie
#                       ╰─╯  ╱╲  ╰─╯  ╱  ╰─╯
#               vitesse.╭─╮ ╱__╲ ╭─╮ ╱
#                       ╰─╯      ╰─╯
#

# STOCKAGE DES DONNEES:
# On garde seulement les poids et le seuil de chaque perceptron.
# Le suil est compté comme poids associé à une entrée "-1"
# On a donc 1 RN = 16 'poids' (12 poids et 4 seuils)

# Ici le RN est simple, et on n'a pas besoin de calculer plusieurs
# sorties d'un seul coup. On ne fait dc pas de classe matricielle,
# en mode flemmard.

# liste :
# [W.e1→c1, W.e2→c1, W.e3→c1, S.c1,
#  W.e1→c2, W.e2→c2, W.e3→c2, S.c2,
#  W.e1→c3, W.e2→c3, W.e3→c3, S.c3,
#  W.c1→s1, W.c2→s1, W.c3→s1, S.s1]
#
# syntaxe :
# W.e1→c3 = poids de la connexion entrée 1 à couche cachée 3
# S.c2    = seuil d'activation du neurone 2 de la C.C.
# ----------------------- ------------ ----------------------- #



# ---------------------- NN COMPUTATION ---------------------- #


# A decaler ASAP dans master.py
def crouch():
    pg.press('down')


# fonction de transfert (en tanh)
def f(z):
    return np.tanh(z)


def compute(reseau, speed, dist, size):
    in_cc = []
    for i in range (3):
        in_cc += [reseau[4*i:4*i+4]]
    out_cc = []
    for i in range(3):
        cc = in_cc[i]
        out_cc += [f(speed*cc[0] + dist*cc[1] + size*cc[2] - cc[3])]
    in_s = reseau[12:16]
    out_s = f(sum([(in_s[i]*out_cc[i]) for i in range(3)]) - in_s[3])
    if out_s > 0.55:
        jump()
    if out_s < 0.45:
        crouch()


# Variables globales
mutate_prob = 0.1
max_score = 0
gen_max_score = 0
ind_no = 1
gen_no = 1


# ------------------------ GENERATION ------------------------ #


# Paramètres entre -1 et 1
def randIndiv():
    global gen_no
    return [2*rd.random() - 1 for i in range(16)] + [str(gen_no)]


def randGen(gen_size):
    return [randIndiv() for i in range(gen_size)]


# ------------------------ EVALUATION ------------------------ #


def evalIndiv(indiv):
    time.sleep(0.3)
    k = indiv[0]
    m = indiv[1]
    time.sleep(0.5)  # Avoids missing evals
    jump()  # Starts the game
    speed, obs_dist, obs_size, passed, score, crashed = getVars()
    print(chr(27) + "[2J")
    print('\n')
    print('        ╔══════════════════════════════════════╗ ')
    print('        ║T-Rex:        GENETIC AI          v2.0║ ')
    print('       ╔╩══════════════════════════════════════╩╗')
    print('       ║  EVALUATING NEURAL NETWORK...          ║')
    print('       ║                                        ║')
    print('       ║  GEN n°'+ str(gen_no).rjust(2) +'/20          MAX_SCORE: '+ str(max_score).ljust(4) +'  ║')
    print('       ║  IND n°'+ str(ind_no).rjust(2) +'/20      GEN_MAX_SCORE: '+ str(gen_max_score).ljust(4) +'  ║')
    print('       ║  ID: ' + indiv[-1].ljust(34) + '║')
    print('       ║                                        ║')
    print('       ╚╦══════════════════════════════════════╦╝')
    while not crashed:
        speed, obs_dist, obs_size, passed, score, crashed = getVars()
        compute(indiv, speed, obs_dist, obs_size)
        dispStr = ""
        dispStr += '        ║ SCORE: ' + str(score).rjust(4)
        dispStr += '   SPEED: ' + (str(speed) + "0000")[:5]
        dispStr += '   JMP:' + str(passed).rjust(3) + " ║"
        write(dispStr + '\r')
    return score


def evalGen(generation):
    global gen_max_score, max_score, ind_no
    eval_tab = []
    ind_no = 0
    gen_max_score = 0
    for indiv in generation:
        ind_no += 1
        score = evalIndiv(indiv)
        max_score = max(score, max_score)
        gen_max_score = max(score, gen_max_score)
        eval_tab += [score]
    return eval_tab


# ----------------------- REPRODUCTION ----------------------- #
# -                     - ET MUTATIONS -                     - #


def mutate(indiv):
    global gen_no
    if rd.random() < mutate_prob:
        indiv[rd.randint(0,16)] *= (0.5 + rd.random())
        indiv[-1] += ('.' + str(gen_no) + 'm')
    return indiv


# Crossover simple de la forme #-a-a-a-a-a-B-B-B-#
def crossover(indiv1, indiv2):
    global gen_no
    pos = rd.randint(1, 15)
    ordre = rd.randint(1,2)
    if ordre == 1:
        return indiv1[:pos] + indiv2[pos:-1] + [str(gen_no)+'('+indiv1[-1]+'+'+indiv2[-1]+')']
    else:
        return indiv2[:pos] + indiv1[pos:-1] + [str(gen_no)+'('+indiv2[-1]+'+'+indiv1[-1]+')']


# ------------------------ EVOLUTION! ------------------------ #


def nextGen(generation):
    global gen_no
    eval_tab = evalGen(generation)
    # affichage des scores de la génération
    str_tab = [""] + [str(i).ljust(4) for i in eval_tab]
    print(chr(27) + "[2J")
    print('        ╔══════════════════════════════════════╗ ')
    print('        ║T-Rex:        GENETIC AI          v2.0║ ')
    print('       ╔╩══════════════════════════════════════╩╗')
    print('       ║             GENERATION n°'+ str(gen_no).ljust(2) +'            ║')
    print('       ║ 1 : '+ str_tab[1] +'  6 : '+ str_tab[6] + '  11: '+ str_tab[11] +'  16: '+ str_tab[16] +' ║')
    print('       ║ 2 : '+ str_tab[2] +'  7 : '+ str_tab[7] + '  12: '+ str_tab[12] +'  17: '+ str_tab[17] +' ║')
    print('       ║ 3 : '+ str_tab[3] +'  8 : '+ str_tab[8] + '  13: '+ str_tab[13] +'  18: '+ str_tab[18] +' ║')
    print('       ║ 4 : '+ str_tab[4] +'  9 : '+ str_tab[9] + '  14: '+ str_tab[14] +'  19: '+ str_tab[19] +' ║')
    print('       ║ 5 : '+ str_tab[5] +'  10: '+ str_tab[10] +'  15: '+ str_tab[15] +'  20: '+ str_tab[20] +' ║')
    print('       ╚╦══════════════════════════════════════╦╝')
    time.sleep(5)
    # os.system('scrot genetic/tab_gen_'+ str(gen_no) +'.png')
    # Choix des 4 parents
    eval_tab = [(i - 40)**2 for i in eval_tab]  # On accentue les meilleurs
    eval_tab_norm = [float(i)/sum(eval_tab) for i in eval_tab]
    parents_id = []
    while len(parents_id) != 5:
        i = np.random.choice(range(20), 1, p=eval_tab_norm)[0]
        if not  i in parents_id:
            parents_id += [i]
    parents = [generation[i] for i in parents_id]
    # Construction de la génération suivante
        #  1-5 : Parents
        #  5-15: Tous les c-o possibles
        # 16-20: Aléas
    gen_no += 1
    # Ajout des parents
    nextGeneration = parents[:]
    # Ajout des c-o
    for i in range(5):
        for j in range(i+1, 5):
            nextGeneration += [crossover(parents[i], parents[j])]
    # Mutation parents et c-o
    nextGeneration = [mutate(i) for i in nextGeneration]
    # Ajout des rd
    for i in range(5):
        nextGeneration += [randIndiv()]
    return nextGeneration


def EVOLUTION(gen_number = 50):
    global max_score
    driver.get(url)
    gen = randGen(20)
    for i in range(gen_number):
        gen = nextGen(gen)
    return max_score


EVOLUTION()
