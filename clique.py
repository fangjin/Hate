#!/usr/bin/python
# -*- coding: utf-8 -*-
import networkx as nx
import argparse
import matplotlib.pyplot as plt
import numpy as np
import random

def	get_graph(graph_file):
	G=nx.Graph()
	nodelist = []
	with open(graph_file, "r") as rg:
		for line in rg:
			tmp = line.strip().split("\t",1)
			if len(tmp) > 1:
				nodelist.append(str(tmp[0]))
				nodelist.append(str(tmp[1]))
				G.add_nodes_from([str(tmp[0]), str(tmp[1])])
				G.add_edge(str(tmp[0]), str(tmp[1]), weight="1")
	nx.draw(G,node_color = 'blue')
	pure_list = list(set(nodelist))
	#plt.show()
	return G, pure_list

	
def	get_matrix(graph_file):
	result, pure_list = get_graph(graph_file)
	#cliques = [clique for clique in nx.find_cliques(result) if len(clique)>2]
	matrix = nx.to_numpy_matrix(result, nodelist=pure_list)
	np.savetxt('Gay-matrix.txt', matrix, fmt='%i', delimiter=' ')
	#brownian_list = [-1]*matrix.shape[0]
		

		

def	main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--graph", type=str, help="graph file")
	#ap.add_argument("--matrix", type=str,help="matrix file")
	arg = ap.parse_args()
	#get_matrix(arg.graph)
	get_graph(arg.graph)


if __name__ == "__main__":
    main()

# python clique.py --graph /home/jf/Documents/hate/hot-women/women_mention_network_notime.txt
# python clique.py --graph /home/jf/Documents/hate/Google/Google_mention_network_notime.txt
# python clique.py --graph /home/jf/Documents/hate/girl/girl_mention_network_notime.txt
#  python clique.py --graph /home/jf/Documents/hate/Gay/Gay_mention_network_notime.txt
