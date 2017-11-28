#206Final Project
#Arielle Metaxas
import info
import requests
import json
import datetime
import re
import sqlite3

#caching pattern
fname = '206Final_Project.json'
try:
	f = open(fname, 'r')
	fcontents = f.read()
	cache_diction = json.loads(fcontents)
	f.close()
except:
	cache_diction = {'IG': {}, 'IMDB' : {}, 'TB': {}}

def lst_of_IG_days():
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
	x = lst_of_IG_days()
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

#IMDB
def get_tv_data(title):
	if title not in cache_diction['IMDB']:
		cache_diction['IMDB'][title] = {}
		base_url = 'http://www.omdbapi.com/'
		IMDB_response = requests.get(base_url, params = {'apikey': info.IMDBapi_key, 't':title, 'season': '1'})
		IMDB_Season1 = json.loads(IMDB_response.text)
		cache_diction['IMDB'][title]['Season 1'] = IMDB_Season1['Episodes']
		if int(IMDB_Season1['totalSeasons']) > 1:
			currentseason = 2
			while (int(IMDB_Season1['totalSeasons']) - currentseason) >= 0:
				IMDB_responseX = requests.get(base_url, params = {'apikey': info.IMDBapi_key, 't':title, 'Season': currentseason})
				IMDB_SeasonX = json.loads(IMDB_responseX.text)
				cache_diction['IMDB'][title]['Season ' + IMDB_SeasonX['Season']] = IMDB_SeasonX['Episodes']
				currentseason += 1
		f = open(fname, 'w')
		f.write(json.dumps(cache_diction, indent = 4))
		f.close()
	return cache_diction['IMDB'][title]

my_IMDB_shows = ['How I Met Your Mother', 'Game of Thrones', 'Gossip Girl', "Grey's Anatomy", 'Suits', 'Criminal Minds', 'Friends', 'Law & Order', 'Scandal', 'The Big Bang Theory', 'NCIS', 'The Blacklist', 'Stranger Things', 'This Is Us', 'How to Get Away With Murder', 'Ray Donovan', 'Breaking Bad', 'The Office', 'Modern Family', 'The Vampire Diaries', 'Homeland', 'Saturday Night Live']

def get_tv_info(lst_of_shows):
	shows = {}
	for show in lst_of_shows:
		szns = get_tv_data(show)
		eps = 0
		total_rating = 0
		NA = 0
		release_date = szns['Season 1'][0]['Released']
		release_day = datetime.datetime.strptime(release_date, '%Y-%m-%d').strftime('%A')
		for season in szns:
			for episode in szns[season]:
				eps += 1
				if episode['imdbRating'] != 'N/A':
					total_rating += float(episode['imdbRating'])
				else:
					NA += 1
		avg_rating = round(total_rating/(eps - NA), 1)
		print ('{} was released on {}, {} and now has {} episodes'.format(show, release_day, release_date, eps))
		print ('The average IMDB rating of all {} episodes is {}/10.0 \n'.format(show, avg_rating))
		shows[show] = (eps, release_day, avg_rating)
	return (shows)

my_show_info = get_tv_info(my_IMDB_shows)

#Tumblr
def lst_of_TB_days():
	days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
	time_frames = ['12:00am-5:59am', '6:00am-11:59am','12:00pm-5:59pm', '6:00pm-11:59pm']
	sorted_days_and_times = []
	for day in days:
		for time in time_frames:
			sorted_days_and_times.append(day + ' ' + time)
	x = [{'time': timestamp ,'post_type': [] , 'count': 0} for timestamp in sorted_days_and_times]
	return (x)

def get_tumblr_data():
	blog = input('Enter a tumblr domain name!: ')
	if blog not in cache_diction['TB']:
		cache_diction['TB'][blog] = []
		offset = 0
		while True:
			TB_request = requests.get('http://api.tumblr.com/v2/blog/{}/posts?api_key={}'.format(blog, info.TBconsumer_key), params = {'offset': offset})
			TB_data = json.loads(TB_request.text)
			for item in TB_data['response']['posts']:
				cache_diction['TB'][blog].append(item)
			if len(cache_diction['TB'][blog]) != 100:
				offset += 20
			else:
				break
		f = open(fname, 'w')
		f.write(json.dumps(cache_diction))
		f.close()
	return cache_diction['TB'][blog]

my_tumblr_data = get_tumblr_data()

def get_tumblr_info(lst_of_posts):
	x = lst_of_TB_days()
	time_frames = {'12:00am-5:59am': ['00','01','02','03','04','05'], '6:00am-11:59am' : ['06','07','08','09','10','11'], '12:00pm-5:59pm' : ['12','13','14','15','16','17'], '6:00pm-11:59pm' : ['18','19','20','21','22','23']}
	for item in lst_of_posts:
		TB_post_type = item['type']
		TB_post_time = item['date'][:-4]
		TB_post_day = datetime.datetime.strptime(TB_post_time, '%Y-%m-%d %H:%M:%S').strftime('%A')
		TB_post_timeframe = re.findall('[0-9]+', TB_post_time)[3]
		print (TB_post_timeframe)
		for time_frame in time_frames:
			if TB_post_timeframe in time_frames[time_frame]:
				print ('here')
				TB_post_timeframe = time_frame
				break
		akey = (TB_post_day + ' ' + TB_post_timeframe)
		print (akey)
		for dic in x:
			if dic['time'] == akey:
				ind = x.index(dic)
				new_dic = dic
				if TB_post_type not in new_dic['post_type']:
					new_dic['post_type'].append(TB_post_type)
				new_dic['count'] += 1
				x[ind] = new_dic
				break
	return (x)

my_tumblr_info = get_tumblr_info(my_tumblr_data)
#Alexa
# #Database creation
conn = sqlite3.connect('206Final_Project.sqlite')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Instagram')
cur.execute('CREATE TABLE Instagram (Weekday TEXT, Time_Frame TEXT, Num_Posts INTEGER, Total_Likes INTEGER, Total_Comments INTEGER, Avg_Likes INTEGER, Avg_Comments INTEGER)')

cur.execute('DROP TABLE IF EXISTS IMDB')
cur.execute('CREATE TABLE IMDB (Title TEXT, Episode_Count INT, Release_Day TEXT, Rating TEXT)')

cur.execute('DROP TABLE IF EXISTS Tumblr')
cur.execute('CREATE TABLE Tumblr (Weekday TEXT, Time_Frame TEXT, Post_Types TEXT, Count TEXT)')

for day in myinstatimes:
	if day['count'] == 0:
		avgl = 0
		avgc = 0
	else:
		avgl = day['likes']/day['count']
		avgc = day['comments']/day['count']
	info = (day['time'].split(' ')[0], day['time'].split(' ')[1], day['count'], day['likes'], day['comments'], avgl, avgc)
	cur.execute('INSERT INTO Instagram (Weekday, Time_Frame, Num_Posts, Total_Likes, Total_Comments, Avg_Likes, Avg_Comments) VALUES (?,?,?,?,?,?,?)', info)

for show in sorted(my_show_info, key = lambda x: my_show_info[x][2]):
	tup = my_show_info[show]
	info = (show, tup[0], tup[1], tup[2])
	cur.execute('INSERT INTO IMDB (Title, Episode_Count, Release_Day, Rating) VALUES (?,?,?,?)', (info))

for day in my_tumblr_info:
	tup = (day['time'].split(' ')[0], day['time'].split(' ')[1], (', '.join(day['post_type'])), day['count'])
	cur.execute('INSERT INTO Tumblr (Weekday, Time_Frame, Post_Types, Count) VALUES (?,?,?,?)', tup)

conn.commit()





