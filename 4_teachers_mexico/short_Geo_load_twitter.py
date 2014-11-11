import json
from unidecode import unidecode
import string
import nltk
import datetime
import sqlite3 as lite
import os
import sys
# format: http://dev.datasift.com/docs/getting-started/data/twitter


def twitTimeToDBTime1(t):
    TIME_FORMAT = "%a, %d %b %Y %H:%M:%S +0000"
    createdAt = datetime.datetime.strptime(t,TIME_FORMAT)
    return createdAt.strftime("%Y-%m-%d %H:%M:%S")



def	read_twitter(filepath, database): 
	start_time = datetime.datetime.now()  
	with open(filepath) as f, open("./new_mention.txt", "a") as new:
		con = lite.connect(database)
		for line in f:
			try:
				tweet  = json.loads(line)				
				user_id = re_target = re_source_id = "" 
				created_at = 0
				mention_ids = []
				
				# twitter				
				if tweet.has_key('twitter'):
					if tweet['twitter'].has_key('created_at'):
						created_at = twitTimeToDBTime1(tweet['twitter']['created_at'])
					# original post, no retweet
					if tweet['twitter'].has_key('user'):	       
						if tweet['twitter']['user'].has_key('id'):
							user_id  = tweet['twitter']['user']['id']
					if tweet['twitter'].has_key('mention_ids'):
						for m in tweet['twitter']['mention_ids']:
							mention_ids.append(m)

					if mention_ids:
						for target in mention_ids:
							record = str(user_id) +"," + str(target) +"," + "1"
		      					new.write("%s" % record)
							new.write("\n")

					#retweeted means the source person
					if tweet['twitter'].has_key('retweeted'):						
						if tweet['twitter']['retweeted'].has_key('user'):
					    		re_source_id = tweet['twitter']['retweeted']['user']['id']

					#retweet means the current person
					if tweet['twitter'].has_key('retweet'):
						if tweet['twitter']['retweet'].has_key('created_at'):
							created_at = twitTimeToDBTime1(tweet['twitter']['retweet']['created_at'])
						if tweet['twitter']['retweet'].has_key('user'):						
							if tweet['twitter']['retweet']['user'].has_key('id'):
								re_target  = tweet['twitter']['retweet']['user']['id']
					if re_target and re_source_id:
						record = str(re_source_id) +"," + str(re_target) +"," + "1"
		      				new.write("%s" % record)
						new.write("\n")

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

def	count_fre():
	my_dic = {}
	with open("./new_mention.txt", "r") as raw:
		for line in raw:
			try:
				line = line.strip().split(",")
				source = line[0]
				target = line[1]
				weight = line[2]
				if source not in my_dic:
					my_dic[source] = {}
					my_dic[source][target] = int(weight)
				else:
					if target not in my_dic[source]:
						my_dic[source][target] = int(weight)
					else:
						my_dic[source][target] = my_dic[source][target]+1

			except:
				print "second ", sys.exc_info()
				continue
	
	with open("./fre_new_mention.json", "w") as outfile:
  		json.dump(my_dic, outfile)



def	write_file():
	my_dic = json.load(open('./fre_new_mention.json'))
	with open("./fre_new_mention.txt","w") as f:
		for s in my_dic:
			for t in my_dic[s]:
				edge = [s, t, my_dic[s][t] ]
				onerecord = s + "," + t + "," + str(my_dic[s][t])
				f.write("%s" % onerecord)
				f.write("\n")
				
	

def	write_db():
	conn = lite.connect("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db")
	my_dic = json.load(open('./fre_new_mention.json'))	
	for s in my_dic:
		for t in my_dic[s]:
			edge = [s, t, my_dic[s][t] ]
			with conn:			
				cur=conn.cursor()
				sql = "INSERT INTO pure_mention(source, target, weight) VALUES(?,?,?)"
				cur.execute(sql, edge )
						
				
def	main():
	#insert()
	write_db()


if __name__ == "__main__":
	main()





