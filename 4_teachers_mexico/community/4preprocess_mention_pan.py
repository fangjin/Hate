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


### need to train those parameters
"propagation model: Poission and Brownian"
def mixture_model():
	mu = 0.0013 - 0.5*0.0176
	sigma_square = 0.0176
	
	start_time = datetime.datetime.now()	
	result = json.load(open("./mention_lists.json"))	
	Poisson_pro = 0.00005
	loop = 100
	count_temp1 = 0
	count_temp2 = 0
	infect_list = []
	Poisson_rate = []
		
	Brown_rate = []
	huge = json.load(open("./transfer_step1.json"))
	
	for i in range(loop):
		count_temp1 = count_temp2
		for source in result["hasmention"]:
			if random.random() < Poisson_pro:
				result["hasmention"][source] = 1
				infect_list.append(source)

		for source in result["nomention"]:
			if random.random() < Poisson_pro:
				result["nomention"][source] = 1
				infect_list.append(source)
		count_temp2 = len(set(infect_list))
		Poisson_rate.append(count_temp2 - count_temp1)					


		count_temp1 = count_temp2
		for infect_id in result["hasmention"]:		
			if result["hasmention"][infect_id] == 1:		
				if infect_id in huge:		
					for neighbor in huge[infect_id]:
						mean = mu*i*15
						var = sigma_square*i*15
						if random.normalvariate(mean, var) < huge[infect_id][neighbor]["Brown_distance"]:
							if neighbor in result["hasmention"]:
								result["hasmention"][neighbor] = 1
										
							else:
								result["nomention"][neighbor] = 1
							infect_list.append(neighbor)

		count_temp2 = len(set(infect_list))
		Brown_rate.append(count_temp2 - count_temp1)


	with open("./Simulation_result.json","w") as Brownian_file:
		json.dump(result, Brownian_file)


	sum_rate = [x + y for x, y in zip(Poisson_rate, Brown_rate)] # zip: takes two equal-length collections, merges them together in pairs
	gound_truth = [4, 11, 13, 18, 5, 16, 25, 19, 25, 34, 17, 22, 21, 15, 25, 33, 18, 19, 28, 24, 20, 27, 15, 14, 8, 5, 4, 7, 3, 5, 5, 6, 1, 6, 2, 3, 2, 6, 0, 3, 0, 6, 4, 4, 2, 7, 5, 3, 2, 8, 0, 10, 6, 7, 16, 4, 11, 14, 8, 6, 5, 12, 86, 26, 10, 10, 12, 16, 9, 0, 11, 12, 10, 9, 6, 5, 7, 5, 11, 13, 7, 10, 4, 9, 6, 2, 5, 9, 5, 3, 14, 8, 5, 12, 11, 13]

	print "sum_rate= ", sum_rate

	fig = plt.figure()

	#plt.plot(Poisson_rate,'b--o', label='Poisson Propagation simulation, probability = 0.0001')
	#plt.plot(Brown_rate,'r--o', label='Brownian Propagation simulation, $\mu$=0.0013, $\sigma^2 =  0.0176$')
	#plt.plot(sum_rate,'g-^', label='Total simulated infected nodes of Bio-space')
	#plt.plot(gound_truth,'m-o', label='Truly infected nodes')

	plt.plot(Poisson_rate,'b--o', label='Poisson',linewidth=4.0)
	plt.plot(Brown_rate,'r--o', label='GBM',linewidth=4.0)
	plt.plot(sum_rate,'g-^', label='Bi-space simulation',linewidth=4.0)
	plt.plot(gound_truth,'m-o', label='Ground truth',linewidth=4.0)
	
	plt.ylabel('Infected nodes', fontsize=35)
	plt.xlabel('Infection time', fontsize=35)
	plt.xticks(fontsize = 30)
	plt.yticks([0,20,40,60,80,100], fontsize = 30)
	#plt.yticks(fontsize = 30)
	
	plt.legend( loc='upper left', numpoints = 2, prop={'size':30})


	plt.show()
		
	fig.savefig('teacher-with-community7.pdf')	

	end_time = datetime.datetime.now()
	print 	(end_time -start_time).seconds



def evaluation():	
	try:
		final_result = json.load(open("./Simulation_result.json"))
		con = lite.connect('/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db')	    
		with con, open("./evaluate_mention_new.txt","w") as f:
			cur = con.cursor()			
			for source in final_result["hasmention"]:
				if final_result["hasmention"][source] == 1:
					sql = "select source, target from t_mention where source =? " 
					cur.execute(sql, [source])
					rows = cur.fetchall()
					for r in rows:
						if str(r[1]) in final_result["hasmention"].keys():
							#if final_result["hasmention"][str(r[1])] == 1:
							#	print r[0], r[1]
							record = r[0] + "," + r[1] + "\n"
							f.write("%s" % record)
	except Exception as e:
		print "Error: %s" % e.args


def true_evaluation():	
	try:		
		con = lite.connect('/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db')	    
		with con, open("./true_evaluation_t_mention.txt","w") as f:
			cur = con.cursor()			
			
			sql = "select source, target from t_mention where created_at!='' " 
			cur.execute(sql)
			rows = cur.fetchall()
			for r in rows:			
				record = r[0] + "," + r[1] + "\n"
				f.write("%s" % record)
	except Exception as e:
		print "Error: %s" % e.args
			



def parse_args():
	ap = argparse.ArgumentParser("association")
	ap.add_argument('-f',dest="old_file",metavar="NEWS FILE", type=str, default = "./2013-09-01_mentions_graph.edges")
	#ap.add_argument('-f',dest="old_file",metavar="NEWS FILE", type=str, default = "./transfer_step2.json" ,help="The process file")
	#ap.add_argument('-f',dest="old_file",metavar="NEWS FILE", type=str, default = "./mention_lists.json" ,help="The process file")

	return ap.parse_args()
	

def main():
	#args = parse_args()
	#old_file = args.old_file
	#transfer_step1(old_file)
	#get_twolists(old_file)
	#mixture_model()
	evaluation()
	#true_evaluation()


if __name__ == "__main__":
	main()




