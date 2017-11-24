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
	cache_diction = {'IG': {}, 'IMBD' : {}}

def lst_of_days():
	days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
	time_frames = ['12:00am-5:59am', '6:00am-11:59am','12:00pm-5:59pm', '6:00pm-11:59pm']
	sorted_days_and_times = []
	for day in days:
		for time in time_frames:
			sorted_days_and_times.append(day + ' ' + time)
	x = [{'time': timestamp ,'likes': 0 , 'comments' : 0, 'count': 0} for timestamp in sorted_days_and_times]
	return (x)

#Instagram
def get_insta_data():
	sn = input("What is the authenticating user's screenanme?: @")
	if sn not in cache_diction['IG']:
		IGbase_url = 'https://api.instagram.com/v1/users/self/media/recent/?'
		IG_request = requests.get(IGbase_url, params = {'client_id': info.IGclient_id, 'access_token' : info.IGaccess_code, 'count': '20'})
		IG_data = json.loads(IG_request.text)['data']
		cache_diction['IG'][sn] = IG_data
		f = open(fname, 'w')
		f.write(json.dumps(cache_diction, indent = 4))
		f.close()
	return cache_diction['IG'][sn]

myinstadata = get_insta_data()

def get_insta_times(IG_data):
	x = lst_of_days()
	time_frames = {'12:00am-5:59am': [0,1,2,3,4,5], '6:00am-11:59am' : [6,7,8,9,10,11], '12:00pm-5:59pm' : [12,13,14,15,16,17], '6:00pm-11:59pm' : [18,19,20,21,22,23]}
	for item in IG_data:
		IGpost_time = (datetime.datetime.fromtimestamp(int(item['created_time'])).strftime('%Y-%m-%d %H'))
		IGpost_day = datetime.datetime.strptime(IGpost_time, '%Y-%m-%d %H').strftime('%A')
		IGpost_timeframe = IGpost_time.split(' ')[-1] #indexing the hour of the post
		for time_frame in time_frames:
			if int(IGpost_timeframe) in time_frames[time_frame]: #if the posted hour is within the list of hours
				IGpost_timeframe = time_frame #update the timeframe variable to accurately represent which timeframe the posting hour falls into
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
	return (x)

myinstatimes = get_insta_times(myinstadata)

#IMBD
def get_tv_data(title):
	if title not in cache_diction['IMBD']:
		cache_diction['IMBD'][title] = {}
		base_url = 'http://www.omdbapi.com/'
		IMBD_response = requests.get(base_url, params = {'apikey': info.IMBDapi_key, 't':title, 'Season': '1'})
		IMBD_Season1 = json.loads(IMBD_response.text)
		cache_diction['IMBD'][title]['Season 1'] = IMBD_Season1['Episodes']
		if int(IMBD_Season1['totalSeasons']) > 1:
			currentseason = 2
			while (int(IMBD_Season1['totalSeasons']) - currentseason) >= 0:
				IMBD_response1 = requests.get(base_url, params = {'apikey': info.IMBDapi_key, 't':title, 'Season': currentseason})
				IMBD_SeasonX = json.loads(IMBD_response1.text)
				cache_diction['IMBD'][title]['Season ' + IMBD_SeasonX['Season']] = IMBD_SeasonX['Episodes']
				currentseason += 1
		f = open(fname, 'w')
		f.write(json.dumps(cache_diction, indent = 4))
		f.close()
	return cache_diction['IMBD'][title]

lst_of_shows = ['How I Met Your Mother, Game of Thrones, Blackish, Gossip Girl, Greys Anatomy']


# #Database creation
conn = sqlite3.connect('206Final_Project.sqlite')
cur = conn.cursor()

#alexa

cur.execute('DROP TABLE IF EXISTS Instagram')
cur.execute('CREATE TABLE Instagram (Weekday TEXT, Time_Frame TEXT, Num_Posts INTEGER, Total_Likes INTEGER, Total_Comments INTEGER, Avg_Likes INTEGER, Avg_Comments INTEGER)')

cur.execute('DROP TABLE IF EXISTS IMBD')
cur.execute('CREATE TABLE IMBD (Title TEXT, Season TEXT, Episode TEXT, Release_Date TEXT, Release_Day TEXT, Rating TEXT)')

for day in myinstatimes:
	if day['count'] == 0:
		avgl = 0
		avgc = 0
	else:
		avgl = day['likes']/day['count']
		avgc = day['comments']/day['count']
	info = (day['time'].split(' ')[0], day['time'].split(' ')[1], day['count'], day['likes'], day['comments'], avgl, avgc)
	cur.execute('INSERT INTO Instagram (Weekday, Time_Frame, Num_Posts, Total_Likes, Total_Comments, Avg_Likes, Avg_Comments) VALUES (?,?,?,?,?,?,?)', info)

# count = 100
# for season in HIMYMdata:
# 	for episode in HIMYMdata[season]:
# 		if count > 0:
# 			IMBDreleaseday = datetime.datetime.strptime(episode['Released'], '%Y-%m-%d').strftime('%A')
# 			info = (episode['Title'], season.split(' ')[1], episode['Episode'], episode['Released'], IMBDreleaseday, episode['imdbRating'])
# 			cur.execute('INSERT INTO IMBD (Title, Season, Episode, Release_Date, Release_Day, Rating) VALUES (?,?,?,?,?,?)', (info))
# 			count -= 1

conn.commit()





