#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3 as lite
import networkx as nx
import argparse
import matplotlib.pyplot as plt

def	get_graph(graph_file):
	G=nx.Graph()
	with open(graph_file, "r") as rg:
		for line in rg:
			tmp = line.strip().split(" ",2)
			if len(tmp) > 1:
				G.add_nodes_from([str(tmp[0]), str(tmp[1])])
				G.add_edge(str(tmp[0]), str(tmp[1]), weight=int(tmp[2]) )
	#nx.draw(G,node_color = 'blue')
	#plt.show()
	return G


def	insert_mention():
	conn = lite.connect("/home/jf/Documents/hate/Gephi/test.db")
	with open("/home/jf/Documents/hate/Gephi/test.edges", "r") as men:
		for line in men:
			tmp = line.strip().split(" ",2)
			edge = ["test", tmp[0], tmp[1], int(tmp[2])]
			with conn:			
			        cur=conn.cursor()			
			        cur.execute("INSERT INTO t_mention(hateCode, source, target, weight) VALUES(?,?,?,?)", edge)


def	insert_community():
	conn = lite.connect("/home/jf/Documents/hate/Gephi/test.db")
	with open("/home/jf/Documents/hate/Gephi/test_graph.csv", "r") as men:
		for line in men:
			tmp = line.strip().split(",",1)
			edge = [tmp[1], tmp[0] ]
			with conn:			
			        cur=conn.cursor()
				sql = "UPDATE t_mention SET community = '{}' WHERE source='{}' ".format(tmp[1],tmp[0])
				cur.execute(sql)
			
			     

"the mention_file is combined with community label already"
def	get_diamter(combined_file, community):
	G=nx.Graph()
	degree_list = []
	with open(combined_file, "r") as rg:
		for line in rg:
			tmp = line.strip().split(" ",2)
			if len(tmp) > 1 and int(tmp[3]) == community:
				G.add_nodes_from([str(tmp[0]), str(tmp[1])])
				G.add_edge(str(tmp[0]), str(tmp[1]), weight=int(tmp[2]) )
	degree_list = list(G.degree([0,1]).values())
	diameter = diameter(G, e=None)
	

def	main():
	#ap = argparse.ArgumentParser()
	#ap.add_argument("--graph", type=str, help="graph file")	
	#arg = ap.parse_args()
	#result = get_graph(arg.graph)
	#nx.write_gexf(result, "mention_sample.gexf")
	#insert_mention()
	insert_community()
	



if __name__ == "__main__":
    main()

# python gephi.py --graph /home/jf/Documents/hate/Gephi/mention_sample.txt
#python gephi.py --graph /home/jf/Documents/hate/mention_network/hot-women/women_mention_network_notime.txt
#python gephi.py --graph /home/jf/Documents/hate/mention_network/Google/Google_mention_network_notime.txt
# python gephi.py --graph /home/jf/Documents/hate/mention_network/girl/girl_mention_network_notime.txt
# python gephi.py --graph /home/jf/Documents/hate/Gay_mention_network_notime.txt
