#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import json
from unidecode import unidecode
import string
from Levenshtein import ratio
import nltk
import datetime
import sqlite3 as lite
import os
import re
import argparse
import ast
pattern_split = re.compile(r"\W+")

__author__ = 'Rachel Jin'
__email__ = 'jfang8@cs.vt.edu'

#python build_mention_network.py -f "./girl_mention_network_notime.txt" -sd "2013-03-22 16:29:40" -ed "2013-03-23 18:56:00" 



def	twitTimeToDBTime(time):
	TIME_FORMAT = "%a %b %d %H:%M:%S +0000 %Y"
	createdAt = datetime.datetime.strptime(time,TIME_FORMAT)
	return createdAt.strftime("%Y-%m-%d %H:%M:%S")


def	build_mention(hate_code,db_file,mention_file, start_time, end_time):
	with open(mention_file,"w") as f:	
		con = lite.connect(db_file)	
		cur=con.cursor()
		mention_list = []
		#sql = "select createdAt, userId, reply_user_id, retweet_user_id, location, time_zone, mention_id, re_created_at, sentiment, doubt from t_hate where hate_code = ? and createdAt > ? and createdAt < ? order by createdAt"
		#cur.execute(sql, (hate_code, start_time, end_time))
		sql = "select createdAt, userId, reply_user_id, retweet_user_id, location, time_zone, mention_id, re_created_at, sentiment, doubt from t_hate order by createdAt"		
		cur.execute(sql)
		rows = cur.fetchall()
		for row in rows:
			createdAt = row[0]
			userId = row[1]
			mention_list = ast.literal_eval(row[6])		
			for mid in mention_list:
				f.write(createdAt + '\t' + userId + '\t' + str(mid) + '\n')
				
	
def	parse_args():
	ap = argparse.ArgumentParser("mention_net")
	ap.add_argument('-f',dest="mention_file",metavar="mention file",type=str,nargs='?',help='the mention file')
	ap.add_argument('-c',dest="hate_code",metavar="hate code",default="girl",type=str,help='hate code')
	ap.add_argument('-sd',dest="start_time",metavar="start time", type=str,help="2013-03-22 00:00:01")
	ap.add_argument('-ed',dest="end_time",metavar="end time",type=str,help="2013-03-22 23:59:59")
	ap.add_argument('-db',dest="db_file",metavar="Database",default="/home/jf/Documents/hate/girl/girl_hate.db", type=str,help="db file")
	return ap.parse_args()



def	main():
	args = parse_args()
	mention_file = args.mention_file
	db_file = args.db_file
	hate_code = args.hate_code
	start_time = args.start_time
	end_time = args.end_time
	build_mention(hate_code,db_file,mention_file, start_time, end_time)


if __name__ == "__main__":
	main()




