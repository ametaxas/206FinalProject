#206Final Project
#Arielle Metaxas
import info
import requests
import json
import datetime
import sqlite3
#caching pattern
fname = '206Final_Project.json'
try:
	f = open(fname, 'r')
	fcontents = f.read()
	cache_diction = json.loads(fcontents)
	f.close()
except:
	cache_diction = {'IG': {} }

def search_lst(term, l):
	a = [dic for dic in l if term in dic]
	if len(a) > 0 :
		return a[0]
	else:
		return None
#Instagram
def get_insta_posts():
	IGclient_id = info.IGclient_id
	IGclient_secret = info.IGclient_secret
	IGaccess_code = info.IGaccess_code
	IGbase_url = 'https://api.instagram.com/v1/users/self/media/recent/?'
	IG_request = requests.get(IGbase_url, params = {'client_id': IGclient_id, 'access_token' : IGaccess_code, 'count': '20'})
	IG_data = json.loads(IG_request.text)['data']
	sn = IG_data[0]['user']['full_name']
	if sn not in cache_diction['IG']:
		days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
		time_frames = ['12:00am-5:59am', '6:00am-11:59am','12:00pm-5:59pm', '6:00pm-11:59pm']
		sorted_days_and_times = []
		for day in days:
			for time in time_frames:
				sorted_days_and_times.append(day + ' ' + time)
		x = [{'time': timestamp ,'likes': 0 , 'comments' : 0, 'count': 0} for timestamp in sorted_days_and_times]
		for item in IG_data:
			IGpost_time = (datetime.datetime.fromtimestamp(int(item['created_time'])).strftime('%Y-%m-%d %H'))
			IGpost_day = datetime.datetime.strptime(IGpost_time, '%Y-%m-%d %H').strftime('%A')
			IGpost_timeframe = IGpost_time.split(' ')[-1]
			time_frames = {'12:00am-5:59am': [0,1,2,3,4,5], '6:00am-11:59am' : [6,7,8,9,10,11], '12:00pm-5:59pm' : [12,13,14,15,16,17], '6:00pm-11:59pm' : [18,19,20,21,22,23]}
			for time_range in time_frames:
				if int(IGpost_timeframe) in time_frames[time_range]:
					IGpost_timeframe = time_range
					break
			IGlikes = item['likes']['count']
			IGcomments = item['comments']['count']
			akey = (IGpost_day + ' ' + IGpost_timeframe)
			for dic in x:
				if dic['time'] == akey:
					ind = x.index(dic)
					new_dic = dic
					new_dic['likes'] += IGlikes
					new_dic['comments'] += IGcomments
					new_dic['count'] += 1
					x[ind] = new_dic
					break
		cache_diction['IG'][sn]= x
		f = open(fname, 'w')
		f.write(json.dumps(cache_diction, indent = 4))
		f.close()
	return cache_diction['IG'][sn]
a = get_insta_posts()

# #Database creation
conn = sqlite3.connect('206Final_Project.sqlite')
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS Instagram')
cur.execute('CREATE TABLE Instagram (Weekday TEXT, Time_Frame TEXT, Num_Posts INTEGER, Total_Likes INTEGER, Total_Comments INTEGER, Avg_Likes INTEGER, Avg_Comments INTEGER)')
instagram_data = {}
for day in a:
	weekday = day['time'].split(' ')[0]
	time = day['time'].split(' ')[1]
	if day['count'] == 0:
		likes = 0
		comments = 0
		count = 0
		avgl = 0
		avgc = 0
	else:
		likes = day['likes']
		comments = day['comments']
		count = day['count']
		avgl = likes/count
		avgc = comments/count
	info = (weekday, time, count, likes, comments, avgl, avgc)
	cur.execute('INSERT INTO Instagram (Weekday, Time_Frame, Num_Posts, Total_Likes, Total_Comments, Avg_Likes, Avg_Comments) VALUES (?,?,?,?,?,?,?)', info)
conn.commit()





