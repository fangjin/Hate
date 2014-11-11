import json
from unidecode import unidecode
import datetime, time
import argparse
import codecs
from disco.core import Job, result_iterator
import disco

__author__ = 'Rachel Jin'
__email__ = 'jfang8@cs.vt.edu'
	
def	twitTimeToDBTime(t):
	TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
	createdAt = datetime.datetime.strptime(t,TIME_FORMAT) # datetime.datetime(2013, 4, 23, 6, 41, 42)
	return createdAt.strftime("%Y-%m-%d %H:%M:%S") # 2013-04-23 06:41:42

	
def	composite(t):
	current_day = t.split()[0]
	all_time = time.strptime(t, '%Y-%m-%d %H:%M:%S')	
	hour = all_time[3]
	minute = all_time[4]
	if minute % 2:
		minute = minute - 1
	final_time = current_day + ':' + str(hour) + ':' + str(minute)
	return final_time


def	read_twitter(in_file):
	with codecs.open(in_file, encoding='utf8', mode='r') as f:
		for line in f:
			tweet  = json.loads(line)
			try:	
				post_time = tweet["date"]
				post_time = twitTimeToDBTime(post_time)		
				post_key = composite(post_time)

				if tweet.has_key('twitter'):
					if tweet['twitter'].has_key('hashtags'):
						hashtag = tweet['twitter']['hashtags']
						for h in hashtag:
							print '%s\t %s' %(post_key+"***"+h,1)
							#yield (post_key, h), 1
				else:
					if tweet['twitter'].has_key('retweet'):
						if tweet['twitter']['retweet'].has_key('hashtags'):
							hashtag  = tweet['twitter']['retweet']['hashtags']
							for h in hashtag:
								print '%s\t %s' %(post_key+"***"+h,1)
								#yield (post_key, h), 1	
					
			except:
				print sys.exc_info()
				continue



def	reduce(iter, params):
	from disco.util import kvgroup
	for word, counts in kvgroup(sorted(iter)):
		yield word, sum(counts)
   

def	parse_args():
	ap = argparse.ArgumentParser("filter")
	ap.add_argument('-f',dest="news_file",metavar="NEWS FILE", type=str,help="The process file")
	return ap.parse_args()
    
    
def	main():
	args = parse_args()
	news_file = args.news_file
	job = Job().run(
                    input=news_file,
                    map_reader=disco.worker.classic.func.chain_reader,
                    map=read_twitter,
                    reduce=reduce)
	with open("output_result",'w') as out:
		for word, count in result_iterator(job.wait(show=False)):
			out.write(word + "\t" + str(count))


if __name__ == "__main__":
	main()


#http://disco.readthedocs.org/en/latest/start/install.html
"""
st = '2010-12-31 23:59:59'
	>>> tt = time.strptime(st, '%Y-%m-%d %H:%M:%S')
	>>> print tt
	time.struct_time(tm_year=2010, tm_mon=12, tm_mday=31, tm_hour=23, tm_min=59, tm_sec=59,
	print tt[4]
"""





