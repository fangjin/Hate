import json
from unidecode import unidecode
import string
import nltk
import datetime
import sqlite3 as lite
import os
import sys
# format: http://dev.datasift.com/docs/getting-started/data/twitter

def	twitTimeToDBTime(time):
	TIME_FORMAT = "%a, %d %b %Y %H:%M:%S +0000"
	if time:
		createdAt = datetime.datetime.strptime(time,TIME_FORMAT)
		createdAt = createdAt.strftime("%Y-%m-%d %H:%M:%S")
	else:
		createdAt = time
	return createdAt


def twitTimeToDBTime1(t):
    TIME_FORMAT = "%a, %d %b %Y %H:%M:%S +0000"
    createdAt = datetime.datetime.strptime(t,TIME_FORMAT)
    return createdAt.strftime("%Y-%m-%d %H:%M:%S")



def	read_twitter(hateCode, filepath, database): 
	start_time = datetime.datetime.now()  
	with open(filepath) as f:
		con = lite.connect(database)
		for line in f:
			try:
				tweet  = json.loads(line)	
				city = country =  pop = admin1 = admin2 = admin3 = geo_id = ""
				username= author_id= content= ""
				uLang = tLang= ""
				sentiment =klot_value= 0
				mention_ids = []
				text = text_id = reply_to_user_id = user_id = location = time_zone = user_screen_name = ""
				user_status= user_followers= user_friends = 0
				created_at = re_created_at = 0
				hashtags = []
				user_description =lang=""				
				re_text_id= re_user_id= re_screen_name= re_time_zone= re_location= re_lang =re_country= re_place_name="-1"
				latitude = longitude = 0
				re_latitude= re_longitude=-1
				
 
				#embersGeocode
				if tweet.has_key('embersGeoCode'):
					city = tweet['embersGeoCode']['city']
					country = tweet['embersGeoCode']['country']
					latitude = tweet['embersGeoCode']['latitude']
					longitude = tweet['embersGeoCode']['longitude']
					pop = tweet['embersGeoCode']['pop']
					admin1 = tweet['embersGeoCode']['admin1']
					admin2 = tweet['embersGeoCode']['admin2']
					admin3 = tweet['embersGeoCode']['admin3']
					geo_id = tweet['embersGeoCode']['id']

				#interaction
				if tweet.has_key('interaction'):
					if tweet['interaction'].has_key('author'):
						if tweet['interaction']['author'].has_key('username'):
							username = tweet['interaction']['author']['username']
							author_id = tweet['interaction']['author']['id']
					if tweet['interaction'].has_key('content'):
						content = tweet['interaction']['content']

				#language
				if tweet.has_key("language"):
					if tweet["language"].has_key("tag"):
						tLang = tweet["language"]["tag"]

				#salience
				if tweet.has_key("salience"):
					if tweet["salience"].has_key("content"):
						sentiment = tweet["salience"]["content"]["sentiment"]
				# klout
				if tweet.has_key("klout"):
					klot_value = tweet["klout"]["score"]

				
				# twitter				
				if tweet.has_key('twitter'):
					if tweet['twitter'].has_key('text'):
						text = tweet['twitter']['text']
					if tweet['twitter'].has_key('id'):
						text_id = tweet['twitter']['id']
					if tweet['twitter'].has_key('created_at'):
						created_at = twitTimeToDBTime1(tweet['twitter']['created_at'])
						#print created_at

					if tweet['twitter'].has_key('in_reply_to_user_id'):
						reply_to_user_id = tweet['twitter']['in_reply_to_user_id']
						
					if tweet['twitter'].has_key('mention_ids'):
						for m in tweet['twitter']['mention_ids']:
							mention_ids.append(m)
							

					# original post, no retweet
					if tweet['twitter'].has_key('user'):					
						if tweet['twitter']['user'].has_key('time_zone'):
							time_zone = tweet['twitter']['user']['time_zone']
						if tweet['twitter']['user'].has_key('location'):
							location = tweet['twitter']['user']['location']						
						if tweet['twitter']['user'].has_key('friends_count'):
							user_friends = tweet['twitter']['user']['friends_count']
						if tweet['twitter']['user'].has_key('lang'):
							ulang = tweet['twitter']['user']['lang']	       
						if tweet['twitter']['user'].has_key('id'):
							user_id  = tweet['twitter']['user']['id']
						if tweet['twitter']['user'].has_key('screen_name'):
							user_screen_name  = tweet['twitter']['user']['screen_name']


					#retweet means the current person
					if tweet['twitter'].has_key('retweet'):
						if tweet['twitter']['retweet'].has_key('text'):
							text  = tweet['twitter']['retweet']['text']
						if tweet['twitter']['retweet'].has_key('id'):
							text_id = tweet['twitter']['retweet']['id']
						if tweet['twitter']['retweet'].has_key('created_at'):
							created_at = twitTimeToDBTime1(tweet['twitter']['retweet']['created_at'])
							#created_at = tweet['twitter']['retweet']['created_at']
							#print "created_at ",created_at
						if tweet['twitter']['retweet'].has_key('hashtags'):
							for h in tweet['twitter']['retweet']['hashtags']:
								hashtags.append(h)			  
					

						if tweet['twitter']['retweet'].has_key('user'):	
							if tweet['twitter']['retweet']['user'].has_key('description'):
								user_description = tweet['twitter']['retweet']['user']['description']
							if tweet['twitter']['retweet']['user'].has_key('statuses_count'):
								user_status = tweet['twitter']['retweet']['user']['statuses_count']
							if tweet['twitter']['retweet']['user'].has_key('followers_count'):
								user_followers = tweet['twitter']['retweet']['user']['followers_count']
							if tweet['twitter']['retweet']['user'].has_key('friends_count'):
								user_friends = tweet['twitter']['retweet']['user']['friends_count']
							if tweet['twitter']['retweet']['user'].has_key('lang'):
								ulang = tweet['twitter']['retweet']['user']['lang']				
							if tweet['twitter']['retweet']['user'].has_key('id'):
								user_id  = tweet['twitter']['retweet']['user']['id']
							if tweet['twitter']['retweet']['user'].has_key('time_zone'):
								time_zone = tweet['twitter']['retweet']['user']['time_zone']
							if tweet['twitter']['retweet']['user'].has_key('location'):
								location  = tweet['twitter']['retweet']['user']['location']
					

			    		#retweeted means the source person
					if tweet['twitter'].has_key('retweeted'):
						if tweet['twitter']['retweeted'].has_key('id'):
							re_text_id = tweet['twitter']['retweeted']['id']
						if tweet['twitter']['retweeted'].has_key('created_at'):
							re_created_at = twitTimeToDBTime1(tweet['twitter']['retweeted']['created_at'])
							#re_created_at = tweet['twitter']['retweeted']['created_at']
							#print "re_created_at ", re_created_at
						if tweet['twitter']['retweeted'].has_key('user'):
					    		re_user_id = tweet['twitter']['retweeted']['user']['id']
							re_screen_name = tweet['twitter']['retweeted']['user']['screen_name']
							re_time_zone = tweet['twitter']['retweeted']['user']['time_zone']
							re_location = tweet['twitter']['retweeted']['user']['location']
							re_lang = tweet['twitter']['retweeted']['user']['lang']
						if tweet['twitter']['retweeted'].has_key('geo'):
					    		re_latitude = tweet['twitter']['retweeted']['geo']['latitude']
							re_longitude = tweet['twitter']['retweeted']['geo']['longitude']
						if tweet['twitter']['retweeted'].has_key('place'):
							re_country = tweet['twitter']['retweeted']['place']['country']
							re_place_name = tweet['twitter']['retweeted']['place']['full_name']					   
		
   	
				hateData = [hateCode, city, country, float(latitude), float(longitude), pop, admin1, admin2, admin3, geo_id, username, author_id, content, uLang, tLang, int(sentiment), int(klot_value), text, text_id, reply_to_user_id, str(mention_ids), user_id, location, time_zone, user_screen_name, created_at, str(hashtags), int(user_friends), int(user_followers), int(user_status), user_description, re_text_id, re_created_at, re_user_id, re_screen_name, re_time_zone, re_location, re_lang, re_country, re_place_name, float(re_latitude), float(re_longitude)]

				with con:			
				        cur=con.cursor()			
				        cur.execute("INSERT INTO t_hate( hateCode, city, country, latitude, longitude, pop, admin1, admin2, admin3, geo_id, username, author_id, content, uLang, tLang, sentiment, klot_value, text, text_id, reply_to_user_id, mention_ids, user_id, location, time_zone, user_screen_name, created_at, hashtags, user_friends, user_followers, user_status, user_description, re_text_id, re_created_at, re_user_id, re_screen_name, re_time_zone, re_location, re_lang, re_country, re_place_name, re_latitude, re_longitude ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", hateData)
	      
			except:
				print "first ", sys.exc_info()
				continue



for _file in os.listdir("/home/jf/Documents/hate/mexico_soccer/matched_tweets"):
	try:		
		read_twitter("soccer","/home/jf/Documents/hate/mexico_soccer/matched_tweets/"+_file,"/home/jf/Documents/hate/mexico_soccer/hate.db")
	except:
		print sys.exc_info()
		print _file, "  file read error"
		continue



