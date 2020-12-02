from igraph import *
from shutil import rmtree as rem
from os import path, mkdir, makedirs, getcwd, system as si
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from math import pow

class MyGraph:
    def __init__(self, filename=None):
        
        # LENDO A REDE, CASO NAO FOR PASSADO O CAMINHO DE ARQUIVO, GERA UMA REDE AKEATORIA

        originalGraph = self.dataLoader(filename, ',') if filename!= None else Graph.GRG(100, 0.3)
        if path.isdir('output'):
            rem('output')
        
        # CRIANDO FOLDERS DE SAIDA DE ARQUIVOS QUE CONTEN INFORMAÇOES DE METRICAS DA REDE
        self.output_folders('output','OrigGraph', 'plots', 'metrics')
        self.output_folders('output','Random_2L-N^2', 'plots', 'metrics')

        # Original Netork
        self.metrics_setter(originalGraph, 'OrigGraph')
        self.g = originalGraph
        self.ploting(originalGraph, 'OrigGraph', 'origGraph')

        # Random Netowork Generated From Original Netork 2L / N²
        n = originalGraph.vcount()
        p = (2*originalGraph.ecount())/(pow(n, 2))

        randomGraph2L = self.corres_network_generator(originalGraph, p)
        self.metrics_setter(randomGraph2L, 'Random_2L-N^2')
        self.ploting(randomGraph2L, 'Random_2L-N^2', 'Random_2L')
       
     
        is_small = self.is_small_world(originalGraph, randomGraph2L)
        with open('output/OrigGraph/metrics/general_info.csv', 'a') as fl:
            fl.write('Is Small World Network: '+str(is_small)+'\n')
        


    def metrics_setter(self, G, dir):
           
        # METRICS 
        lst = G.get_adjlist()
        general_info = []
        adjacency_lst = [{'key':idx, 'value':x} for idx, x in enumerate(lst)]
        clusters_coeff = [{'key':idx, 'value':round(x, 4)} if x==x else {'key':idx, 'value':0} for idx, x in enumerate(G.transitivity_local_undirected())]
        lst = G.get_adjacency()
        lst = [[x if isinstance(x, int) else 0 for x in ls] for ls in lst]
        adjacency_mtrx = [{'key':idx, 'value':x} for idx, x in enumerate(lst)]
        aux = G.shortest_paths_dijkstra()
        shortest_path_matrix = [{'key':idx, 'value':x} for idx, x in enumerate(aux)]
        lst_done = [[x if isinstance(x, int) else 0 for x in ls] for ls in aux]
        shortest_paths = [{'key':id, 'value':round(mean(x), 2)}  for id, x in enumerate(lst_done)]
        average_path_length = G.average_path_length()
        betweenness = [{'key': id, 'value': round(x, 2)} for id, x in enumerate(G.betweenness())]
        pageRank = [{'key': id, 'value': round(x, 4)} for id, x in enumerate(G.pagerank())]

        #  GENERAL INFOS

        degree = G.degree()
        general_info.append({'key':'Mean Degree',  'value':mean(degree)})
        general_info.append({'key':'Mean Cluster_Coeff',  'value':mean([x['value'] for x in clusters_coeff])})
        general_info.append({'key':'Average Path Length',  'value':average_path_length})
        general_info.append({'key':'Diamater',  'value':G.diameter()})
   

        self.exporter('output/'+dir+'/metrics/adjacency_list.csv', adjacency_lst, ':')
        self.exporter('output/'+dir+'/metrics/clusters_coeff.csv', clusters_coeff, ':')
        self.exporter('output/'+dir+'/metrics/adjacency_mtrx.csv', adjacency_mtrx, ':')
        self.exporter('output/'+dir+'/metrics/shortest_path_matrix.csv', shortest_path_matrix, ':')
        self.exporter('output/'+dir+'/metrics/general_info.csv', general_info, ':')
        self.exporter('output/'+dir+'/metrics/shortest_paths_average.csv', shortest_paths, ':')
        self.exporter('output/'+dir+'/metrics/betweenness.csv', betweenness, ':')
        self.exporter('output/'+dir+'/metrics/pageRank.csv', pageRank, ':')

     


    def exporter(self, _path, datas, separator):
        with open(_path, 'w') as fl:
            [fl.write(str(data['key'])+separator+str((data['value']))+'\n')for data in datas]



    # PLOTS 
    def ploting(self, G, dir, title):
        
        self.degree_distribution(G, dir, title)
        plt.clf()
        com = self.community_detection(G, dir, title)
        with open('output/'+dir+'/metrics/general_info.csv', 'a') as fl:
            fl.write('Modularidade: '+str(com.modularity)+'\n')
        self.plot_graph(G, dir)
    
            
        
    
    def output_folders(self, root, graph, plots, metrics):
        current = path.join(path.join(getcwd(), root), graph)
        makedirs(path.join(current, plots))
        makedirs(path.join(current, metrics))


    def dataLoader(self, fileName, delim):
        Data = np.genfromtxt(fileName, delimiter=delim)
        return Graph.TupleList(Data.tolist())
    
    def corres_network_generator(self,G, p):
        n = G.vcount()
        return Graph.Erdos_Renyi(n, p)
    
    def is_small_world(self,g, random_g):
        g_average_min_paths = []
        return (g.transitivity_avglocal_undirected() > random_g.transitivity_avglocal_undirected()) and (g.average_path_length() < random_g.average_path_length())
        
    def degree_distribution(self, G, dir, title):
        lst = G.degree()
        uniq = list(set(lst))
        cont = [lst.count(x) for x in uniq]
        cont1 = [x/G.vcount() for x in cont]
        less = min(cont)
        big = max(cont)

        lless = [id for id, x in enumerate(cont) if x==less]
        lbig = [id for id, x in enumerate(cont) if x==big]

        img =  plt.bar(uniq, cont1, width=0.80, color='b')

        for i in lless:
            img[i].set_color('r')

        for i in lbig:
            img[i].set_color('g')

        plt.xlabel('graus')
        plt.title(title)
        plt.ylabel('cont')
        plt.savefig('output/'+dir+'/plots/histgram.pdf')
    
    def community_detection(self, g, dir, title):
        dendrog = g.community_walktrap()
        community = dendrog.as_clustering()
        plot(community, "output/"+dir+"/plots/comunidades.pdf")
        return community
        si('xdg-open '+"output/"+dir+"/plots/comunidades.pdf")    
    def plot_graph(self, g, dir):
        lstd = g.degree()
        mx = max(lstd)
        mn = min(lstd)
        g.vs['label'] = [x for x in range(g.vcount())]
        g.vs['label_size'] = 8
        g.vs['color'] = 'Light Blue'
        for i in lstd:
            if i == mx:
                g.vs[lstd.index(i)]['color'] = 'green'
            elif i == mn:
                g.vs[lstd.index(i)]['color'] = 'red'
        g.vs['size'] = [x+15 for x in lstd]
        plot(g, "output/"+dir+"/plots/Grafico.pdf")
        # si('xdg-open '+"output/"+dir+"/plots/Grafico.pdf")