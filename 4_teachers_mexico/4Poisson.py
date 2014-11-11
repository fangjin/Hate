#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from unidecode import unidecode
import sqlite3 as lite
import networkx as nx
import datetime
#from datetime import datetime
import os
import sys
import traceback
from datetime import timedelta


def twitTimeToDBTime1(t):
    TIME_FORMAT = "%a, %d %b %Y %H:%M:%S +0000"
    createdAt = datetime.datetime.strptime(t,TIME_FORMAT)
    return createdAt.strftime("%Y-%m-%d %H:%M:%S")


def	read_twitter(filepath, database): 
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
				hateData = [user_id, created_at]
				with con:			
				        cur=con.cursor()
					cur.execute("INSERT INTO t_infection(user_id, created_at) VALUES(?,?)", hateData)	      
			except:
				print "first ", sys.exc_info()
				continue



def Count_Of_Events(duration):
    teacher_list = []
    try:
        con = lite.connect('/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db')	    
        with con:
            cur = con.cursor()
	    sql = "select min(target_time), max(target_time) from pure_mention where community1=5 " 
	    #sql = "select min(created_at), max(created_at) from t_infection where mention='no' and created_at>='2013-09-01 00:00:01' and created_at<='2013-09-01 23:59:59' "
	    #sql = "select min(created_at), max(created_at) from t_mention where created_at!='' or target_time!='' "
	    cur.execute(sql)
            row = cur.fetchone()
            TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
	    minTime = datetime.strptime("2013-09-01 00:00:01",TIME_FORMAT)
	    maxTime = datetime.strptime("2013-09-10 23:59:59",TIME_FORMAT) 
            #minTime = datetime.strptime(row[0],TIME_FORMAT)
            #maxTime = datetime.strptime(row[1],TIME_FORMAT)
            
            countOfRumor ={}
            
            noOfSegments = (maxTime - minTime)/duration
            #print noOfSegments
            startTime= minTime
            endTime = minTime + timedelta(minutes=duration)

	    while (startTime< maxTime):
 	    #while endTime<=datetime.strptime("2012-06-01 23:50:41",TIME_FORMAT):
		total = 0		
                #sql = "select user_id from t_infection where mention='no' and created_at >=? and created_at<=? "
		#sql = "select user_id from t_infection where created_at >=? and created_at<=? "
		sql = "select source from pure_mention where (community1=3 and target_time >=? and target_time<=?) or (community1=3 and created_at >=? and created_at<=?) "
                cur.execute(sql,[startTime, endTime, startTime, endTime])
		#cur.execute(sql,[startTime, endTime])
                rows = cur.fetchall()
		itemKey = datetime.strftime(endTime,'%Y%m%d%H%M%S')
		for row in rows:
			total += 1 
		countOfRumor[itemKey]= total
		teacher_list.append(total)
		print "{0}	{1}".format(itemKey, total)  
		
           
                startTime = endTime
                endTime = endTime + timedelta(minutes=duration)

    except Exception as e:
            print "Error: %s" % e.args
            print traceback.format_exc()
    print teacher_list

"""
sqlite> select count(1) from pure_mention where community1=7;
68
sqlite> select count(1) from pure_mention where community1=6;
971
sqlite> select count(1) from pure_mention where community1=5;
252
sqlite> select count(1) from pure_mention where community1=4;
160
sqlite> select count(1) from pure_mention where community1=3;
150
sqlite> select count(1) from pure_mention where community1=2;
197
sqlite> select count(1) from pure_mention where community1=1;
449
sqlite> select count(1) from pure_mention where community1=0;
1776
"""

def	execute():
	for _file in os.listdir("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/tweets"):
		try:		
			read_twitter("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/tweets/"+_file,"/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db")
			print _file, "done"
		except:
			print sys.exc_info()
			print _file, "  file read error"
			continue



	#update t_infection set mention='yes' where user_id in (select target from t_mention union select source from t_mention);
def	update_db():
	try:
		con = lite.connect("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db")
		with con:
			cur = con.cursor()
			#sql = "UPDATE t_infection SET mention = 'no' where user_id not in (select target from t_mention union select source from t_mention) "
			sql = "UPDATE t_infection SET mention = 'yes' where user_id in (select target from t_mention union select source from t_mention) "
			cur.execute(sql)
			print "success"	
	except:
		print sys.exc_info()

	    

def	main():
	#execute()
	#Count_Of_Events(60)
	update_db()


if __name__ == "__main__":
    main()

