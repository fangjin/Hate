# -*- coding: utf-8 -*-
import sqlite3 as lite
import json
import sys
from unidecode import unidecode
from datetime import datetime
import datetime
import argparse
import os
import math
import random
import matplotlib.pyplot as plt
import pylab
import networkx as nx


"transfer to json file"
def transfer_step1(class_file):
	result = {}	
	with open(class_file) as f, open("./transfer_step1.json","w") as output_file:		
		for line in f:
			line = line.strip() 
			try:
				source = line.split(" ")[0]
				target = line.split(" ")[1]
				count = line.split(" ")[2]
				if source != target and int(source)>100 and int(target)>100:
					if source not in result:
						result[source] = {}
					result[source][target] = {"fre":0, "Brown_distance":0 }
					result[source][target]["fre"] = int(count)
					result[source][target]["Brown_distance"] = 1+ 1.0/float(count)				
			except:
				print sys.exc_info()
				continue
		json.dump(result, output_file)



def diff(a, b):
        b = set(b)
        return [x for x in a if x not in b]


"transfer to two lists"
"hasmention are nodes who mention other people, are source nodes "
"nomention are nodes who did not mention other people, are target nodes"
def get_twolists(class_file):
	source_list = []
	target_list = []
	result = {"hasmention":{}, "nomention":{}}	
	with open(class_file) as f:	
		for line in f:
			line = line.strip() 
			source = line.split(" ")[0]
			target = line.split(" ")[1]

			if source != target and int(source)>100 and int(target)>100:
				source_list.append(source)
				target_list.append(target)
				if source not in result["hasmention"]:
					result["hasmention"][source] = 0
		for k in diff(target_list, source_list):
			result["nomention"][k] = 0

	with open("./mention_lists.json","w") as output_file:
		json.dump(result, output_file)


# story 1, mu=0.0098, sigma_square=0.0141
# story 4, mu=0.0013, sigma_square=0.0176
# story 6, mu=0.0111, sigma_square=0.0175
# story 7, mu=0.0099, sigma_square=0.0143


def useLargeSize(axis,marker_lines = None, fontsize = 'xx-large',fontproperties=None):
	axis.xaxis.get_label().set_size(fontsize)
	axis.yaxis.get_label().set_size(fontsize)
	for label in axis.xaxis.get_ticklabels():
		label.set_fontsize(18)
	for label in axis.yaxis.get_ticklabels():
		label.set_fontsize(18)



# mu = 0.0277      sigmaSquare = 0.0495
### need to train those parameters
"propagation model: Poission and Brownian"
def mixture_model():
	
	#mu = 0.0013 - 0.5*0.0176
	#sigma_square = 0.0176
	mu = 0.0277 - 0.5*0.0495
	sigma_square = 0.0495		
	start_time = datetime.datetime.now()	
	result = json.load(open("./mention_lists.json")) #result = {"nomention": {"358378445": 0,...}, "hasmention":{"143658559": 0, ...} }
 	Poisson_pro = 0.00005
	loop = 100
	count_temp1 = 0
	count_temp2 = 0
	infect_list = []
	Poisson_rate = []		
	Brown_rate = []
	huge = json.load(open("./transfer_step1.json")) # huge = {"211401376": {"86649040": {"Brown_distance": 2.0, "fre": 1}}, "562559441": {"486722762": {"Brown_distance": 2.0, "fre": 1}}, ...}
	for i in range(loop):
		count_temp1 = count_temp2 # at begining of a new loop, update count_temp1
		for source in result["hasmention"]:
			if random.random() < Poisson_pro:
				result["hasmention"][source] = 1
				infect_list.append(source)

		for source in result["nomention"]:
			if random.random() < Poisson_pro:
				result["nomention"][source] = 1
				infect_list.append(source)
		count_temp2 = len(set(infect_list))
		Poisson_rate.append(count_temp2 - count_temp1)	# now, count_temp2 is the pure nodes get infected by Poisson propagation				


		count_temp1 = count_temp2
		for infect_id in result["hasmention"]:		
			if result["hasmention"][infect_id] == 1: # the source nodes was infected in the Poisson propagation		
				if infect_id in huge:		 # check if the node in the mention network as source
					for neighbor in huge[infect_id]: # check this source node's neighbor
						mean = mu * i * 15
						var = sigma_square*i*15
						if random.normalvariate(mean, var) < huge[infect_id][neighbor]["Brown_distance"]: # judge by Brown_distance
							if neighbor in result["hasmention"]:
								result["hasmention"][neighbor] = 1
										
							else:
								result["nomention"][neighbor] = 1
							infect_list.append(neighbor) # infect_list is based on the previoius poisson propagation

		count_temp2 = len(set(infect_list)) # now, count_temp2 is the pure nodes get infected by Brown druing this loop
		Brown_rate.append(count_temp2 - count_temp1)


	with open("./Simulation_result.json","w") as Brownian_file:
		json.dump(result, Brownian_file)


	sum_rate = [x + y for x, y in zip(Poisson_rate, Brown_rate)] # zip: takes two equal-length collections, merges them together in pairs
	gound_truth = [4, 11, 13, 18, 5, 16, 25, 19, 25, 34, 17, 22, 21, 15, 25, 33, 18, 19, 28, 24, 20, 27, 15, 14, 8, 5, 4, 7, 3, 5, 5, 6, 1, 6, 2, 3, 2, 6, 0, 3, 0, 6, 4, 4, 2, 7, 5, 3, 2, 8, 0, 10, 6, 7, 16, 4, 11, 14, 8, 6, 5, 12, 86, 26, 10, 10, 12, 16, 9, 0, 11, 12, 10, 9, 6, 5, 7, 5, 11, 13, 7, 10, 4, 9, 6, 2, 5, 9, 5, 3, 14, 8, 5, 12, 11, 13]

	#sum_rate=  [2, 2, 10, 6, 6, 8, 2, 6, 9, 6, 14, 9, 18, 12, 11, 6, 4, 7, 18, 19, 14, 10, 14, 24, 17, 29, 33, 63, 82, 58, 40, 38, 41, 46, 48, 16, 15, 18, 9, 12, 8, 7, 5, 6, 5, 8, 7, 12, 6, 7, 10, 10, 9, 10, 12, 6, 19, 16, 13, 5, 10, 6, 1, 7, 4, 11, 7, 9, 10, 16, 6, 9, 10, 5, 4, 3, 2, 3, 18, 7, 11, 7, 5, 6, 7, 4, 6, 17, 7, 11, 7, 12, 6, 7, 3, 13, 19, 24, 18, 14]

	#sum_rate=  [11, 17, 10, 10, 18, 17, 20, 12, 32, 23, 9, 17, 12, 16, 21, 16, 14, 15, 28, 16, 10, 18, 30, 37, 55, 85, 62, 41, 48, 42, 19, 21, 20, 27, 22, 16, 5, 3, 5, 4, 8, 6, 7, 11, 2, 6, 5, 8, 7, 8, 7, 15, 11, 10, 8, 12, 13, 11, 19, 14, 3, 7, 2, 11, 11, 16, 8, 7, 3, 6, 3, 13, 5, 11, 6, 9, 18, 5, 10, 4, 6, 8, 4, 5, 5, 5, 11, 5, 8, 3, 6, 8, 5, 7, 6, 10, 6, 11, 2, 3]

	print "sum_rate= ", sum_rate
	print "without, the accuracy is ", 1- abs(sum(sum_rate) - sum(gound_truth))*1.00/sum(gound_truth)
	with open("./dots_result", "a") as text_file:
		text_file.write("without, the accuracy is: %s \n" % str(1- abs(sum(sum_rate) - sum(gound_truth))*1.00/sum(gound_truth)) )

	

	fig = plt.figure()

	#plt.plot(Poisson_rate,'b--o', label='Poisson Propagation simulation, probability = 0.0001')
	#plt.plot(Brown_rate,'r--o', label='Brownian Propagation simulation, $\mu$=0.0013, $\sigma^2 =  0.0176$')
	#plt.plot(sum_rate,'g-^', label='Total simulated infected nodes of Bio-space')
	#plt.plot(gound_truth,'m-o', label='Truly infected nodes')

	plt.plot(Poisson_rate,'b--o', label='Poisson',linewidth=6.0)
	plt.plot(Brown_rate,'r--o', label='GBM',linewidth=6.0)
	plt.plot(sum_rate,'g-^', label='Bispace simulation',linewidth=6.0)
	plt.plot(gound_truth,'m-o', label='Ground truth',linewidth=6.0)
	
	plt.ylabel('Infected nodes', fontsize=35)
	plt.xlabel('Time (15 minutes)', fontsize=35)
	plt.xticks(fontsize = 30)
	plt.yticks([0,20,40,60,80,100], fontsize = 30)
	#plt.yticks(fontsize = 30)
	
	plt.legend( loc='upper left', numpoints = 2, prop={'size':30})


	plt.show()
		
	fig.savefig('without-teacher-community-lastTry2.pdf')	

	end_time = datetime.datetime.now()
	print 	(end_time -start_time).seconds


"""
sqlite> select count(1) from pure_mention where community1=7; # community = 435
68
sqlite> select count(1) from pure_mention where community1=6; # community = 363
971
sqlite> select count(1) from pure_mention where community1=5; # community = 403, 363
252
sqlite> select count(1) from pure_mention where community1=4; # community = 363
160
sqlite> select count(1) from pure_mention where community1=3; # community = 170
150
sqlite> select count(1) from pure_mention where community1=2; # community = 403, 318
197
sqlite> select count(1) from pure_mention where community1=1; # community = 307, 222
449
sqlite> select count(1) from pure_mention where community1=0; # community = 222
1776
"""


# I am trying to transfer 2013-09-01_mentions_graph.edges to gephi format, and split community based on the full mention network
# then simulate the GBM community according to the full mention network community.
# using gephi, we get the top communities: 
# select community, count(community) from t_mention group by community order by count(community);
# 3737|11868 13.4%
# 8070|8659 9.02%
# 16122|5910 7.22%
# 9687|3183 4.05%
# 989|3410 4.02%
# 2127|3440 3.87%
# 8094|1298 1.47% 
# 2313|1107
# 657|390
	
	

# question: pure_mention is different with classfile, hasmention and nomention
"transfer to two lists"
"hasmention are nodes who mention other people, are source nodes "
"nomention are nodes who did not mention other people, are target nodes"
def get_twolists_commu(class_file):
	con = lite.connect('/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db')		
	source_list = []
	target_list = []
	count = 0
	result = {"hasmention":{}, "nomention":{}}	
	with con, open(class_file) as f:
		cur = con.cursor()	
		for line in f:
			line = line.strip() 
			source = line.split(" ")[0]
			target = line.split(" ")[1]

			if source != target and int(source)>100 and int(target)>100:
				source_list.append(source)
				target_list.append(target)
				sql = "select community from t_mention where source=?"
				cur.execute(sql, [source])
				row = cur.fetchone()

				if source not in result["hasmention"]:
					result["hasmention"][source]={"status":0}
					result["hasmention"][source]["commu"] = row[0]  # get from database
					count = count+1 # only 306 source nodes has commu1
					
		for k in diff(target_list, source_list):
			result["nomention"][k] = 0
	print "count ", count

	with open("./mention_lists_commu.json","w") as output_file: 
		json.dump(result, output_file)


# mention_lists_commu.json
# result = {"nomention": {"358378445": 0, ...}, "hasmention":{"103913734": {"status": 0, "commu": 2}, "42768210": {"status": 0, "commu": 8070}, ...} } 
# "nomention" is target node, "hasmention" is source node



######################### need to train community parameters now 
# all_4_time_diff_all :   mu = 0.0277      sigmaSquare = 0.0495
# all_4_time_diff989:     mu = 0.0129      sigmaSquare = 0.0198
# all_4_time_diff8070:    mu = 0.0266      sigmaSquare = 0.0475
# rest:                   mu = 0.1055      sigmSquare = 0.2034

# result is dynamic changing, since the propagation is changing during the loop
# huge is static, only denote the neighbor relationship
# we have two propagation simulation method, one is Poisson, the other is Brown.
def community_mixture():
	commu_dic = {"8070":{"mu": 0.0266-0.5*0.0475 , "sigma_square": 0.0475}, "989":{"mu":0.0129-0.5*0.0198 , "sigma_square":0.0198 }, "all":{"mu": 0.0277-0.5*0.0495, "sigma_square": 0.0495}, "rest":{"mu": 0.1055-0.5*0.2034, "sigma_square": 0.2034} }
	# result dictionary should add "community1" option, so the "infect_id" will know which "community1" it belongs to
	result = json.load(open("./mention_lists_commu.json"))
	
	com = "all"						
	Poisson_pro = 0.00005
	loop = 100
	count_temp1 = 0
	count_temp2 = 0
	infect_list = []
	Poisson_rate = [] # Poisson_rate: Store infected nodes number during each loop, by Poission process.		
	Brown_rate = [] # Brown_rate: store infected nodes number during each loop, by Brown process. 

	huge = json.load(open("./transfer_step1.json")) # huge = {"211401376": {"86649040": {"Brown_distance": 2.0, "fre": 1}}, "562559441": {"486722762": {"Brown_distance": 2.0, "fre": 1}}, ...}
	for i in range(loop):
		count_temp1 = count_temp2
		for source in result["hasmention"]:
			if random.random() < Poisson_pro: # question: why hasmention need to < poisson_pro?
				result["hasmention"][source]["status"] = 1
				infect_list.append(source) # infection nodes got by Poission distribution ?
		for source in result["nomention"]:
			if random.random() < Poisson_pro:
				result["nomention"][source] = 1
				infect_list.append(source)
		count_temp2 = len(set(infect_list))
		Poisson_rate.append(count_temp2 - count_temp1)

		count_temp1 = count_temp2
		for infect_id in result["hasmention"]:
			if result["hasmention"][infect_id]["status"] == 1:
				if infect_id in huge:
					com = result["hasmention"][infect_id]["commu"]
					for neighbor in huge[infect_id]:			
						if com != "8070" and com !="989":
							com = "rest"
						mean = i * 15 * commu_dic[com]["mu"]
						var = i * 15 * commu_dic[com]["sigma_square"]

						if random.normalvariate(mean, var) < huge[infect_id][neighbor]["Brown_distance"]:
							if neighbor in result["hasmention"]:
								result["hasmention"][neighbor]["status"] = 1
										
							else:
								result["nomention"][neighbor] = 1
							infect_list.append(neighbor)
		count_temp2 = len(set(infect_list)) # now, count_temp2 is the pure nodes get infected by Brown druing this loop
		Brown_rate.append(count_temp2 - count_temp1)	
	
	with open("./Simulation_result_community.json","w") as Brownian_file:
		json.dump(result, Brownian_file)


	sum_rate = [x + y for x, y in zip(Poisson_rate, Brown_rate)] # zip: takes two equal-length collections, merges them together in pairs
	gound_truth = [4, 11, 13, 18, 5, 16, 25, 19, 25, 34, 17, 22, 21, 15, 25, 33, 18, 19, 28, 24, 20, 27, 15, 14, 8, 5, 4, 7, 3, 5, 5, 6, 1, 6, 2, 3, 2, 6, 0, 3, 0, 6, 4, 4, 2, 7, 5, 3, 2, 8, 0, 10, 6, 7, 16, 4, 11, 14, 8, 6, 5, 12, 86, 26, 10, 10, 12, 16, 9, 0, 11, 12, 10, 9, 6, 5, 7, 5, 11, 13, 7, 10, 4, 9, 6, 2, 5, 9, 5, 3, 14, 8, 5, 12, 11, 13]

	print "sum_rate= ", sum_rate
	print "community, the accuracy is ", 1- abs(sum(sum_rate) - sum(gound_truth))*1.00/sum(gound_truth)

	with open("./dots_result", "a") as text_file:
		text_file.write("community, the accuracy is: %s \n" % str(1- abs(sum(sum_rate) - sum(gound_truth))*1.00/sum(gound_truth)) )

	fig = plt.figure()

	#plt.plot(Poisson_rate,'b--o', label='Poisson Propagation simulation, probability = 0.0001')
	#plt.plot(Brown_rate,'r--o', label='Brownian Propagation simulation, $\mu$=0.0013, $\sigma^2 =  0.0176$')
	#plt.plot(sum_rate,'g-^', label='Total simulated infected nodes of Bio-space')
	#plt.plot(gound_truth,'m-o', label='Truly infected nodes')

	plt.plot(Poisson_rate,'b--o', label='Poisson',linewidth=6.0)
	plt.plot(Brown_rate,'r--o', label='GBM',linewidth=6.0)
	plt.plot(sum_rate,'g-^', label='Bispace simulation',linewidth=6.0)
	plt.plot(gound_truth,'m-o', label='Ground truth',linewidth=6.0)
	
	plt.ylabel('Infected nodes', fontsize=35)
	plt.xlabel('Time (15 minutes)', fontsize=35)
	plt.xticks(fontsize = 30)
	plt.yticks([0,20,40,60,80,100], fontsize = 30)
	#plt.yticks(fontsize = 30)
	
	plt.legend( loc='upper left', numpoints = 2, prop={'size':30})
	plt.show()		
	fig.savefig('teacher-with-community-lastTry2.pdf')


		

 

def evaluation():	
	try:
		final_result = json.load(open("./Simulation_result_community.json"))
		con = lite.connect('/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db')	    
		with con, open("./evaluate_mention_community_final.txt","w") as f:
			cur = con.cursor()			
			for source in final_result["hasmention"]:
				if final_result["hasmention"][source]["status"] == 1:
					sql = "select source, target from t_mention where source =? " 
					cur.execute(sql, [source])
					rows = cur.fetchall()
					for r in rows:
						#if str(r[1]) in final_result["hasmention"].keys():
							#if final_result["hasmention"][str(r[1])] == 1:
							#	print r[0], r[1]
							record = r[0] + "," + r[1] + "\n"
							f.write("%s" % record)
	except Exception as e:
		print "Error: %s" % e.args


def strict_evaluation():		
	try:
		final_result = json.load(open("./Simulation_result_community.json"))
		con = lite.connect('/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db')
		temp_list = []	    
		with con, open("./evaluate_mention_community_final.txt","a") as f:
			cur = con.cursor()			
			for source in final_result["hasmention"]:
				if final_result["hasmention"][source]["status"] == 1:
					temp_list.append(source)
			for sid in temp_list:
				sql1 = "select source, target from t_mention where source =? " 
				cur.execute(sql1, [sid])
				rows = cur.fetchall()
				for r in rows:
					if str(r[1]) in temp_list:
						record = r[0] + "," + r[1] + "\n"
						f.write("%s" % record)

				sql2 = "select source, target from t_mention where target =? " 
				cur.execute(sql2, [sid])
				rows = cur.fetchall()
				for r in rows:
					if str(r[0]) in temp_list:
						record = r[0] + "," + r[1] + "\n"
						f.write("%s" % record)

	except Exception as e:
		print "Error: %s" % e.args


def more_evaluation():	
	try:
		final_result = json.load(open("./Simulation_result_community.json"))
		con = lite.connect('/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db')	    
		with con, open("./evaluate_mention_more.txt","w") as f:
			cur = con.cursor()			
			for source in final_result["hasmention"]:
				if final_result["hasmention"][source]["status"] == 1:
					sql = "select source, target from t_mention where source =? " 
					cur.execute(sql, [source])
					rows = cur.fetchall()
					for r in rows:						
						record = r[0] + "," + r[1] + "\n"
						f.write("%s" % record)
	except Exception as e:
		print "Error: %s" % e.args



def remove_duplicate():
	with open("evaluate_mention_community_final_640.txt") as ori, open("duplicate","a") as du, open("pure_evaluation","a") as pu:
		for line in ori:
			try:
				flag = 0
				line = line.strip()
				a = line.split(",")[0]
				b = line.split(",")[1]
				for line1 in ori:
					try:
						line1 = line1.strip()
						c = line1.split(",")[0]
						d = line1.split(",")[1]					
						if b == c and a == d:
							print line1
							#du.write("%s \n" % line1)
							#flag = 1
					except:
						continue
				#if flag==0:
				#	pu.write("%s \n" % line)

			except Exception as e:
				print "Error: %s" % e.args
				continue


def true_evaluation():	
	try:		
		con = lite.connect('/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db')	    
		with con, open("./true_evaluation_t_mention_1715.txt","w") as f:
			cur = con.cursor()			
			
			sql = "select source, target from t_mention where created_at!='' " 
			cur.execute(sql)
			rows = cur.fetchall()
			for r in rows:			
				record = r[0] + "," + r[1] + "\n"
				f.write("%s" % record)
	except Exception as e:
		print "Error: %s" % e.args
			


def get_mention_gephi(class_file):
	G=nx.Graph()
	with open(class_file, "r") as f:
		for line in f:
			tmp = line.strip().split(",")
			try:
				G.add_nodes_from( [str(tmp[0]), str(tmp[1].split()[0]) ]  )
				G.add_edge(str(tmp[0]), str(tmp[1].split()[0]), weight = "1" )
			except:	
				print tmp[1].split(" ", 0)
				continue
	return G
		


def parse_args():
	ap = argparse.ArgumentParser("association")
	#ap.add_argument('-f',dest="old_file",metavar="NEWS FILE", type=str, default = "./2013-09-01_mentions_graph.edges")
	ap.add_argument('-f',dest="old_file",metavar="NEWS FILE", type=str, default = "./1000.txt")
	#ap.add_argument('-f',dest="old_file",metavar="NEWS FILE", type=str, default = "./mention_lists.json" ,help="The process file")
	return ap.parse_args()
	

def main():
	args = parse_args()
	old_file = args.old_file
	#more_evaluation()
	#true_evaluation()
	#transfer_step1(old_file)
	#get_twolists(old_file)
	mixture_model()
	#evaluation()
	#strict_evaluation()
	#remove_duplicate()
	#true_evaluation()
	#get_twolists_commu(old_file)

	#community_mixture()	
	#result = get_mention_gephi(old_file)
	#nx.write_gexf(result, "./911nodes.gexf")


if __name__ == "__main__":
	main()




