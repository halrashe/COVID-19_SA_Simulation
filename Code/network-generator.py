import numpy as np
import pandas as pd
import seaborn as sns
import random
import time
import matplotlib.pyplot as plt
from scipy import stats
from random import randint
import matplotlib
randn = np.random.randn
from itertools import count
import networkx as nx
import math
import collections
#-----------------------------------------------------------

# global variables

g = nx.Graph()
similarity_matrix = [[]]
N = 0 #total number of nodes+

#-----------------------------------------------------------

def assign_citizenship_and_area(sizes, cnt1, cnt2, cnt3, p):

    global g
    cnt=0
    #choices = ('Riyadh', 'Mecca', 'Jeddah', 'Taif', 'Almadinah', 'Alquassim', 'Eastern region', 'Aseer', 'Tabuk', 'Hail', 'Northern region', 'Jazan', 'Najran', 'Albaha', 'Aljouf')
    choices = ('Riyadh', 'Mecca', 'Jeddah', 'Taif', 'Almadinah', 'Alquassim', 'Eastern region', 'Aseer', 'Tabuk', 'Hail', 'Northern region', 'Jazan', 'Najran', 'Albaha', 'Aljouf')

    for counter,i in enumerate(sizes):
        area = np.random.choice(choices, p=p)
        for j in range(i):
            if counter < cnt1:
               g.node[cnt]['citizenship'] = 'saudi'
               g.node[cnt]['area'] = area
            elif counter >= cnt1 and counter < cnt1+cnt2:
               g.node[cnt]['citizenship'] = 'non saudi'
               g.node[cnt]['area'] = area
            else:
               g.node[cnt]['citizenship'] = 'single'
               g.node[cnt]['area'] = area
            cnt=cnt+1

#-----------------------------------------------------------
   
def assign_family_id(sizes):

    global g
    cnt=0

    nx.set_node_attributes(g, '', name='family_id')
    nx.set_node_attributes(g, 'not assigned', name='citizenship')
    for counter,i in enumerate(sizes):
        for j in range(i):
            g.node[cnt]['family_id'] = str(counter)
            cnt=cnt+1

#-----------------------------------------------------------

def assign_genders():

    nx.set_node_attributes(g, '', name='gender')
    
    for n in g.nodes():
        if g.node[n]['citizenship'] == 'saudi':
              g.node[n]['gender'] = np.random.choice(('F','M'), p=[.5,.5])
           
        elif g.node[n]['citizenship'] == 'non saudi':
             if g.node[n]['area'] == 'Mecca':
                g.node[n]['gender'] = np.random.choice(('F','M'), p=[.6,.4])
             if g.node[n]['area'] == 'Eastern region':
                g.node[n]['gender'] = np.random.choice(('F','M'), p=[.45,.55])
             else:
                g.node[n]['gender'] = np.random.choice(('F','M'), p=[.5,.5])
                
        else:
           g.node[n]['gender'] = np.random.choice(('F','M'), p=[.5,.5])  
         
#-----------------------------------------------------------

def assign_ages(psf, psm, pnsf, pnsm, ps):

    global g
    nx.set_node_attributes(g, -1, name='age')
    choices = ('0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+')
    
    for n in g.nodes():
        if g.node[n]['citizenship'] == 'saudi' and g.node[n]['gender'] == 'F':
           g.node[n]['age'] = np.random.choice(choices, p=psf)
           
        elif g.node[n]['citizenship'] == 'saudi' and g.node[n]['gender'] == 'M':
           g.node[n]['age'] = np.random.choice(choices, p=psm)

        elif g.node[n]['citizenship'] == 'non saudi' and g.node[n]['gender'] == 'F':
           g.node[n]['age'] = np.random.choice(choices, p=pnsf)

        elif g.node[n]['citizenship'] == 'non saudi' and g.node[n]['gender'] == 'M':
           g.node[n]['age'] = np.random.choice(choices, p=pnsm)

        else:
           g.node[n]['age'] = np.random.choice(choices, p=ps)
 
#-----------------------------------------------------------

def list_sizes(p, avg):

    sizes=[]
    global N
    while p > 0:
        num = random.randrange(avg-2, avg+3, 1)
        sizes.append(num)
        p = p - num
        N = N + num

    return sizes    
        
#-----------------------------------------------------------

def list_sizes_for_singles(p, avg):

    sizes=[]
    global N
    while p > 0:
        num = random.randrange(avg-5, avg+5, 1)
        sizes.append(num)
        p = p - num
        N = N + num

    return sizes    
        
#-----------------------------------------------------------

def set_probabilities(sizes):

    prob = np.zeros((len(sizes), len(sizes)))

    for i in range(len(sizes)):
         prob[i][i] = 1.0

    return prob

#-----------------------------------------------------------

def compute_node_similarity(i,j):

    global g
    v1=[]
    v2=[]


    if g.node[i]['area']!=g.node[j]['area']:
       v1.append(0)
       v2.append(0)
    else:
       v1.append(0)
       v2.append(1)

    if g.node[i]['citizenship']!=g.node[j]['citizenship']:
       v1.append(0)
       v2.append(0)
    else:
       v1.append(0)
       v2.append(1)
       

    if g.node[i]['gender']!=g.node[j]['gender']:
       v1.append(0)
       v2.append(0)
    else:
       v1.append(0)
       v2.append(1)

    if g.node[i]['age']!=g.node[j]['age']:
       v1.append(0)
       v2.append(0)
    else:
       v1.append(0)
       v2.append(1)

    sim = math.sqrt(.7*((v1[0]-v2[0])**2) + .1*((v1[1]-v2[1])**2) + .1*((v1[2]-v2[2])**2) + .1*((v1[3]-v2[3])**2)) #+ .1*((v1[3]-v2[3])**2))

    return round(sim, 3)
    
#-----------------------------------------------------------

def connect_clusters(p1,p2, p3):

   # We use two types of edges. For 1 --> edge type is random (random contact)
   #                            For 2 --> edge type is social (social contact)

   # first propability: propability that a node will be connected to a single node in the same area
   # second propability: propability that a node will be connected to a single node in a different area
   # third propability: propability that a node will be connected to a similar node


    global g
    global similarity_matrix
    links_similarity = 0
    links_random = 0
    links_random_single=0

    start_time = time.time()

    single_nodes = set(n for n,d in g.nodes(data=True) if d['citizenship']=='single')
    non_single_nodes = set(n for n,d in g.nodes(data=True) if d['citizenship']=='saudi' or d['citizenship']=='non saudi')
    print 'done 1'

    #non_edges = nx.non_edges(g)
    #print 'done 2, num of non edges = ', len(non_edges)

   
    for i in g.nodes():
        print 'processing node ', i
        for j in filter(lambda x:x>i, g.nodes()):
            #print i,j
            similarity = compute_node_similarity(i,j)
            similarity_matrix[i][j] = similarity
            similarity_matrix[j][i] = similarity

            if j not in g.neighbors(i):
               #connect nodes based on similarity 
               if similarity >= .7 and g.node[i]['citizenship'] != g.node[j]['citizenship'] and g.node[i]['citizenship'] != 'single':
                  if random.uniform(0,1) < p3:
                     g.add_edge(i,j)
                     g.edges[i, j]['type'] = 'social'
                     links_similarity=links_similarity+1

               #connect everyone to single nodes in the same area
               elif g.node[i]['citizenship'] == 'single':
                  if g.node[i]['area'] == g.node[j]['area']:
                     if random.uniform(0,1) < p2:
                        g.add_edge(i,j)
                        g.edges[i, j]['type'] = 'random'
                        links_random_single=links_random_single+1      
                     
               #connect nodes completely at random
               else:
                  if random.uniform(0,1) < p1:
                     g.add_edge(i,j)
                     g.edges[i, j]['type'] = 'random'
                     links_random = links_random+1
                     
                     
                        

    print 'time: ', time.time() - start_time
    print '# of similarity links = ', links_similarity
    print '# of random links with singles = ', links_random_single
    print '# of random links = ', links_random         

#-----------------------------------------------------------

def remove_edges(p1, p2, p3):

    # first probability: deleting a familial edge
    # second probability: deleting a social edge
    # third probability: deleting a random edge = sum of probabilities of connectinf clusters

    global g
    removed_links=0
    removed_links_familial=0
    removed_links_social=0
    removed_links_random=0 

    edges = list(g.edges)
    
    for e in g.edges().keys():
        if g.edges[e]['type'] == 'familial':
           if random.uniform(0,1) < p1:
              g.remove_edge(*e)
              removed_links_familial=removed_links_familial+1
              
        elif g.edges[e]['type'] == 'social':
           if random.uniform(0,1) < p2:
              g.remove_edge(*e)
              removed_links_social=removed_links_social+1     

        else:
           if random.uniform(0,1) < p3:
              g.remove_edge(*e)
              removed_links_random = removed_links_random+1
               

    print '# of familial removed links = ', removed_links_familial
    print '# of social removed links = ', removed_links_social
    print '# of random removed links = ', removed_links_random


    return removed_links

#-----------------------------------------------------------

def print_details(c1,c2,c3):

    global g

    print 'Total num of nodes: ', len(g)
    print 'Total num of clusters: ', c1+c2+c3
    print 'Num of Saudi clusters: ', c1
    print 'Num of Non Saudi clusters: ', c2
    print 'Num of single clusters: ', c3
    print 'Num of Female: ', sum(1 for n,d in g.nodes(data=True) if d['gender']=='F')
    print 'Num of Male: ', sum(1 for n,d in g.nodes(data=True) if d['gender']=='M')
    print '----------------------------------------------------------\n'

#=============================================
   
def main():

    global g
    global similarity_matrix
    
    # assign model parameters
    # The percent of Saudis = 62%
    # The percent of Non Saudis = 38% - This will be distributed among families and singles.
    # We assume that singles live in community homes with other singles
    
    p1 = 6200 #620 #num of citizens
    p2 = 1900 #190 #num of residents
    p3 = 1900 #190 #num of singles
    avg1 = 5 #average citizens family size
    avg2 = 4 #average residents family size 
    avg3 = 40 #average of singles and couples

    sizes = list_sizes(p1, avg1)
    num_of_saudi_clusters = len(sizes)
    sizes = sizes + list_sizes(p2, avg2)
    num_of_non_saudi_clusters = len(sizes) - num_of_saudi_clusters
    sizes = sizes + list_sizes_for_singles(p3, avg3)
    num_of_non_single_clusters = len(sizes) - num_of_saudi_clusters - num_of_non_saudi_clusters
    probs = set_probabilities(sizes) 

    #create a graph with family clusters and assign ids
    g = nx.stochastic_block_model(sizes, probs, seed=0)
    print 'Done creating initial graph'

    #print 'len g ', len(g)
    similarity_matrix = np.zeros((len(g), len(g)))

    assign_family_id(sizes)
    print 'Done assigning family IDs'

    # probability distributions of people over the 15 areas
    p=[.25,.08, .14, .03,.07,.04,.15,.07,.03,.02,.01,.05,.02,.02,.02]
    assign_citizenship_and_area(sizes, num_of_saudi_clusters, num_of_non_saudi_clusters, num_of_non_single_clusters,p)
    print 'Done assigning citizenships and areas'


    # probability distributions of genders among saudis, non saudis, and singles
    assign_genders()
    print 'Done assigning genders'


    # probability distributions of age groups among saudis and non saudis based on gender
    # last list the prob distribution of the single nodes
    pSF= [0.210,0.181,0.192,0.162,0.115,0.073,0.039,0.019,0.009]
    pSM= [0.210,0.180,0.196,0.159,0.116,0.075,0.038,0.017,0.009]
    pNSF=[0.162,0.133,0.170,0.259,0.204,0.044,0.020,0.006,0.002]
    pNSM=[0.078,0.065,0.123,0.285,0.278,0.128,0.035,0.006,0.002]
    ps=  [0.078,0.065,0.123,0.285,0.278,0.128,0.035,0.006,0.002] #XXX needs accurate values
    assign_ages(pSF, pSM, pNSF, pNSM, ps)
    print 'Done assigning ages'

    nx.set_edge_attributes(g, 'familial', 'type')
    num_of_familial_edges = nx.number_of_edges(g)
    # add node connections based on node similarity with randomness

    # first parameter: propability of random connectivity
    # second parameter: propability that a node will be connected to a single node in the same area
    # third parameter: propability that a node will be connected to a similar node

    connect_clusters(.01, .15, .25)
    #connect_clusters(.0005, .1, .3)
    print 'Done connecting clusters'

    # first probability: deleting a familial edge
    # second probability: deleting a social edge
    # third probability: deleting a random edge = sum of probabilities of connecting clusters

    removed_links = remove_edges(.0001, .005, .001)

    nx.write_pajek(g,"contact-network.net")
   
    heat_map_similarity()
    heat_map_adjacency_matrix()
    
#=============================================

if __name__ == "__main__":
   print 'Start'
   main()
   print 'Done!'

