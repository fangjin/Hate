#!/usr/bin/python
# -*- coding: utf-8 -*-

import networkx as nx
import argparse
import matplotlib.pyplot as plt


def	get_graph(graph_file):
	G=nx.Graph()
	with open(graph_file, "r") as rg:
		for line in rg:
			tmp = line.strip().split("\t",1)
			if len(tmp) > 1:
				G.add_nodes_from([str(tmp[0]), str(tmp[1])])
				G.add_edge(str(tmp[0]), str(tmp[1]))
	nx.draw(G,node_color = 'yellow')
	#nx.draw_circular(G)
	#nx.draw_random(G)
	plt.show()
	# magenta, cyan
	return G


def	main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--graph", type=str, help="graph file")
	arg = ap.parse_args()
	result = get_graph(arg.graph)
	cliques = [clique for clique in nx.find_cliques(result) if len(clique)>2]
	print cliques


if __name__ == "__main__":
    main()

#python color_clique.py --graph /home/jf/Documents/hate/hot-women/women_mention_network_notime.txt
#python color_clique.py --graph /home/jf/Documents/hate/Google/Google_mention_network_notime.txt
# python color_clique.py --graph /home/jf/Documents/hate/girl/girl_mention_network_notime400.txt
#  python color_clique.py --graph /home/jf/Documents/hate/Gay/gay-sample300.txt
