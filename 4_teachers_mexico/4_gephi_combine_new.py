#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from unidecode import unidecode
import sqlite3 as lite
import networkx as nx
import argparse
import datetime
from datetime import datetime
import matplotlib.pyplot as plt
import os
import sys

def twitTimeToDBTime1(t):
    TIME_FORMAT = "%a, %d %b %Y %H:%M:%S +0000"
    createdAt = datetime.datetime.strptime(t,TIME_FORMAT)
    return createdAt.strftime("%Y-%m-%d %H:%M:%S")



def	insert_mention(mention_day, mention_file):
	conn = lite.connect("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db")
	with open(mention_file, "r") as men:
		for line in men:
			tmp = line.strip().split()
			edge = [ tmp[0], tmp[1], int(tmp[2]), mention_day]
			with conn:			
			        cur=conn.cursor()
				sql = "INSERT INTO t_mention(source, target, weight, mention_day) VALUES(?,?,?,?)"
				cur.execute(sql, edge )


def	insert_community():
	conn = lite.connect("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db")
	with open("teacher_pure_gephi_nodes.csv", "r") as men:
		for line in men:
			tmp = line.strip().split(",",1)
			edge = [tmp[1], tmp[0] ]
			with conn:			
			        cur=conn.cursor()
				sql = "UPDATE pure_mention SET community = '{}' WHERE source='{}' or target='{}' ".format(tmp[1],tmp[0],tmp[0])
				cur.execute(sql)




def	insert_community1():
	conn = lite.connect("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db")
	with open("4_teacher_pure_major_community_degree.csv", "r") as men:
		for line in men:
			tmp = line.strip().split(",",2)
			edge = [tmp[1], tmp[2], tmp[0] ]
			with conn:			
			        cur=conn.cursor()
				sql = "UPDATE pure_mention SET community1 = '{}', degree='{}' WHERE source='{}' or target='{}' ".format(tmp[1], tmp[2], tmp[0], tmp[0])
				cur.execute(sql)


def	insert_community_full():
	conn = lite.connect("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db")
	with open("full_mention_gephi_nodes_community.csv", "r") as men:
		for line in men:
			tmp = line.strip().split(",",1)
			with conn:			
			        cur=conn.cursor()
				sql = "UPDATE t_mention SET community = '{}' WHERE source='{}' or target='{}' ".format(tmp[1],tmp[0],tmp[0])
				cur.execute(sql)

	

def	read_twitter(filepath, database): 
	start_time = datetime.datetime.now()  
	with open(filepath) as f:
		con = lite.connect(database)
		for line in f:
			try:
				tweet  = json.loads(line)				
				user_id = ""
				created_at = 0				
				# twitter				
				if tweet.has_key('twitter'):
					if tweet['twitter'].has_key('created_at'):
						created_at = twitTimeToDBTime1(tweet['twitter']['created_at'])
					# original post, no retweet
					if tweet['twitter'].has_key('user'):	       
						if tweet['twitter']['user'].has_key('id'):
							user_id  = tweet['twitter']['user']['id']
					#retweet means the current person
					if tweet['twitter'].has_key('retweet'):
						if tweet['twitter']['retweet'].has_key('created_at'):
							created_at = twitTimeToDBTime1(tweet['twitter']['retweet']['created_at'])
						if tweet['twitter']['retweet'].has_key('user'):						
							if tweet['twitter']['retweet']['user'].has_key('id'):
								user_id  = tweet['twitter']['retweet']['user']['id']   	
				hateData = [created_at, user_id]
				with con:			
				        cur=con.cursor()
					sql = "UPDATE pure_mention SET target_time = '{}' where target = '{}' ".format(hateData[0], hateData[1])
					#sql = "UPDATE pure_mention SET created_at = '{}' where source = '{}' ".format(hateData[0], hateData[1])
					cur.execute(sql)	      
			except:
				print "first ", sys.exc_info()
				continue


def	execute():
	for _file in os.listdir("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/tweets"):
		try:		
			read_twitter("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/tweets/"+_file,"/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db")
		except:
			print sys.exc_info()
			print _file, "  file read error"
			continue



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



def	select_big_community():
	G=nx.Graph()
	conn = lite.connect("/home/jf/Documents/hate/hate_db/yosoy_test.db")
	with open("./yosoy_infected.csv","w") as f:
		with conn:
			cur=conn.cursor()
			cur.execute("select source, created_at, target, target_time, community from t_mention where community='435' ")
			lines = cur.fetchall()
			for r in lines:
				if r[1] != "":
					record = str(r[0]) + "," + str(r[4]) + ",Yes\n"
				elif r[1] == "":
					record = str(r[0]) + "," + str(r[4]) + ",No\n"
				elif r[3] != "":
					record = str(r[2]) + "," + str(r[4]) + ",Yes\n"
				elif r[3] == "":
					record = str(r[2]) + "," + str(r[4]) + ",No\n"
				f.write('%s' % record )
	

def	got_time_diff():
	conn = lite.connect("/home/jf/Documents/hate/hate_db/yosoy_test.db")
	with open("./yosoy_time_diff2.txt","w") as f:
		with conn:
			cur=conn.cursor()
			sql = "select created_at, target_time, weight from t_mention where created_at!='' and target_time!='' "	
			cur.execute(sql)
			lines = cur.fetchall()
			for r in lines:
				created_at = datetime.strptime(r[0],"%Y-%m-%d %H:%M:%S")
				target_time = datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S")
				delta = created_at - target_time
				record = str(delta.seconds/60 +1) + "," + str(r[2]) 
				f.write("%s" % record )
				f.write("\n")
	



def	mention_distance():
	conn = lite.connect("/home/jf/Documents/hate/hate_db/yosoy_test.db")
	my_dic = {}
	with conn:
		cur=conn.cursor()
		sql = "select source, target from t_mention"	
		cur.execute(sql)
		lines = cur.fetchall()
		for r in lines:
			source = r[0]
			target = r[1]
			my_dic[source] = target

		for key in my_dic:
			if my_dic[key] in my_dic:
				if my_dic[my_dic[key]] == key:
					print key, my_dic[key]	
				
					sql1 = "select source, target, weight, created_at, target_time from t_mention where (source=? and target=?) or (source=? and target=?) "	
					cur.execute(sql1, (key, my_dic[key], my_dic[key], key) )
					result = cur.fetchall()
					for re in result:
						print re[0], re[1], re[2], re[3], re[4]



def	get_pure_mention():
	conn = lite.connect("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db")
	with open("./4teacher_community_0.txt", "w") as men:
		with conn:		
			cur = conn.cursor()
			sql = "select source, target from pure_mention where community1 = 0"
			#sql = "select source, target from pure_mention where community=222 or community=363 or community=307 or community=403 or community=170 or community=435 or community=318 "	
			cur.execute(sql)
			lines = cur.fetchall()
		
			for r in lines:
				record = r[0] + "," + r[1] + "\n"
				men.write("%s" % record)



def	got_community_time_diff(community):
	conn = lite.connect("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db")
	with open("./teacher_community8070_diff.txt","w") as f:
		with conn:
			cur=conn.cursor()
			sql = "select created_at, target_time, weight from t_mention where created_at!='' and target_time!='' and community='{}' ".format(community)	
			cur.execute(sql)
			lines = cur.fetchall()
			for r in lines:
				created_at = datetime.strptime(r[0],"%Y-%m-%d %H:%M:%S")
				target_time = datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S")
				delta = created_at - target_time
				record = str(delta.seconds/60 +1) + "," + str(r[2]) 
				f.write("%s" % record )
				f.write("\n")


# train the community paramters mu and sigma
# step 1
def	get_both_infected_com(community):
	conn = lite.connect("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db")
	with open("./all_4_infection"+community, "w") as f:
		with conn:
			cur=conn.cursor()
			sql = "select source, target, weight, created_at, target_time from t_mention where target_time !='' and created_at!='' and community='{}' ".format(community)	
			cur.execute(sql)
			result = cur.fetchall()
			for r in result:
				record = r[0] + "|" + r[1] + "|" +str(r[2]) + "|" + str(r[3]) + "|" + str(r[4])
				f.write("%s" % record)
				f.write("\n")


def	get_both_infected():
	conn = lite.connect("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db")
	with open("./all_4_infection_rest", "w") as f:
		with conn:
			cur=conn.cursor()
			sql = "select source, target, weight, created_at, target_time from t_mention where target_time !='' and created_at!=''  and community!='8070' and community!='989' "	
			cur.execute(sql)
			result = cur.fetchall()
			for r in result:
				record = r[0] + "|" + r[1] + "|" +str(r[2]) + "|" + str(r[3]) + "|" + str(r[4])
				f.write("%s" % record)
				f.write("\n")

# step 2
def	get_time():
	conn = lite.connect("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db")
	with open("./all_4_infection_rest", "r") as men, open("./all_4_time_diff_rest","w") as f:
		for line in men:
			tmp = line.strip().split("|")
			created_at = 0
			target_time = 0
			if tmp[3]:			
				created_at = datetime.strptime(tmp[3],"%Y-%m-%d %H:%M:%S")
			if tmp[4]:
				target_time = datetime.strptime(tmp[4], "%Y-%m-%d %H:%M:%S")
			delta = created_at - target_time
			 
			with conn:
				cur=conn.cursor()
				sql = "select weight from pure_mention where source=? and target=? "	
				cur.execute(sql, (tmp[1], tmp[0]) )
				result = cur.fetchall()
				weight2 = 0

				for re in result:
					weight2 = weight2 + int(re[0])

			record = tmp[2] + "," + str(weight2) + "," + str(delta.seconds/60 )
			#print record
			f.write("%s" % record)
			f.write("\n")

				

def	main():
	#ap = argparse.ArgumentParser()
	#ap.add_argument("--graph", type=str, help="graph file")	
	#arg = ap.parse_args()
	#result = get_graph(arg.graph)
	#nx.write_gexf(result, "mention_sample.gexf")
	#insert_mention("2013-09-02", "/home/jf/Documents/hate/Hate_story/4_teachers_mexico/mentions_network/2013-09-02_mentions_graph.edges")
	
	#insert_community1()
	#execute()
	#select_big_community()
	#complete_mention()
	#got_time_diff()
	#mention_distance()
	#get_pure_mention()
	#insert_community_full()

	comm_list = [ "989", "8070"]
	get_both_infected()
	get_time( )



if __name__ == "__main__":
    main()

# python gephi.py --graph /home/jf/Documents/hate/Gephi/mention_sample.txt
#python gephi.py --graph /home/jf/Documents/hate/mention_network/hot-women/women_mention_network_notime.txt
#python gephi.py --graph /home/jf/Documents/hate/mention_network/Google/Google_mention_network_notime.txt
# python gephi.py --graph /home/jf/Documents/hate/mention_network/girl/girl_mention_network_notime.txt
# python gephi.py --graph /home/jf/Documents/hate/Gay_mention_network_notime.txt

"""
def	select_big_community():
	G=nx.Graph()
	conn = lite.connect("/home/jf/Documents/hate/hate_db/yosoy_test.db")
	with conn:
		cur=conn.cursor()
		cur.execute("select source, target from t_mention where community='435' ")
		lines = cur.fetchall()
		for r in lines:
			print str(r[0]), str(r[1])
			#G.add_nodes_from(str(r[0]), str(r[1]) )
			G.add_edge(str(r[0]), str(r[1]), weight="1")
	nx.write_gexf(G, "community435_graph.gexf")
"""
