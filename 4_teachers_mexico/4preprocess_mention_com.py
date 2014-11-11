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


"transfer to json file"
def transfer_step1(class_file):
	result = {}	
	with open(class_file) as f, open("./transfer_step1-1.json","w") as output_file:		
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

	with open("./mention_lists1.json","w") as output_file:
		json.dump(result, output_file)


# story 1, mu=0.0098, sigma_square=0.0141
# story 4, mu=0.0013, sigma_square=0.0176
# story 6, mu=0.0111, sigma_square=0.0175
# story 7, mu=0.0099, sigma_square=0.0143

##         mu                         sigmaSquare
#0         0.00987241838926387        0.0146715124062799
#1         0.0137839934866855         0.0222640335827928
#2         0.00856190375810401        0.0125049989731591
#3         0.00267847216709107        0.00134058386750654
#4         0.00593457664336078        0.00661784045851451
#5         0.00514690526198996        0.00521069339128078
#6         0.00839664482779614        0.0119794680151281

"propagation model: Poission and Brownian"
def mixture_model():
	mu = 0.002678 - 0.5*0.00134
	sigma_square = 0.00134
	
	start_time = datetime.datetime.now()	
	result = json.load(open("./mention_lists1.json"))	
	Poisson_pro = 0.0001
	loop = 240
	count_temp1 = 0
	count_temp2 = 0
	infect_list = []
	Poisson_rate = []
		
	Brown_rate = []
	huge = json.load(open("./transfer_step1-1.json"))
	
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
						mean = mu*i*60
						var = sigma_square*i*60
						if random.normalvariate(mean, var) < huge[infect_id][neighbor]["Brown_distance"]:
							if neighbor in result["hasmention"]:
								result["hasmention"][neighbor] = 1
										
							else:
								result["nomention"][neighbor] = 1
							infect_list.append(neighbor)

		count_temp2 = len(set(infect_list))
		Brown_rate.append(count_temp2 - count_temp1)

	sum_rate = [x + y for x, y in zip(Poisson_rate, Brown_rate)]
	gound_truth = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 150, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 44, 105, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]



	fig = plt.figure()
	plt.legend(loc=2,prop={'size':28})

	#plt.plot(Poisson_rate,'b--o', label='Poisson Propagation simulation, probability = 0.0001')
	#plt.plot(sum_rate,'g-^', label='Total simulated infected nodes of Bio-space')
	plt.plot(gound_truth,'m-o', label='Truly infected nodes')
	
	plt.ylabel('Infected nodes')
	plt.xlabel('Infection time')
	plt.legend( loc='upper right', numpoints = 1 )
	plt.show()
		
	fig.savefig('community3.pdf')

	#with open("./Brownian_result.json","w") as Brownian_file:
	#	json.dump(result, Brownian_file)

	end_time = datetime.datetime.now()
	print 	(end_time -start_time).seconds



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
	mixture_model()


if __name__ == "__main__":
	main()




