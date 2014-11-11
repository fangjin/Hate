#!/usr/bin/env python
from datetime import datetime 
import sqlite3 as lite

# select source, target, weight,created_at, target_time from t_mention where created_at!='' and target_time !='';
# write the selection result in diff.txt

def	get_both_infected():
	conn = lite.connect("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db")
	with open("./new_2500_diff.txt", "w") as f:
		with conn:
			cur=conn.cursor()
			sql = "select source, target, weight, created_at, target_time from pure_mention where target_time !='' and created_at!='' "	
			cur.execute(sql )
			result = cur.fetchall()
			for r in result:
				record = r[0] + "|" + r[1] + "|" +str(r[2]) + "|" + str(r[3]) + "|" + str(r[4])
				f.write("%s" % record)
				f.write("\n")




def	get_time():
	conn = lite.connect("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/4teacher.db")
	with open("/home/jf/Documents/hate/Hate_story/4_teachers_mexico/experiment/new_2500_diff.txt", "r") as men, open("./2500_time_diff.txt","w") as f:
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
	get_time()
	#get_both_infected()



if __name__ == "__main__":
	    main()
