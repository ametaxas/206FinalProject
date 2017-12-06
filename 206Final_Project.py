#206Final Project
#Arielle Metaxas
import info
import requests
import json
import datetime
import re
import sqlite3
import time
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from os import path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS
#caching pattern
fname = '206Final_Project.json'
try:
	f = open(fname, 'r')
	fcontents = f.read()
	cache_diction = json.loads(fcontents)
	f.close()
except:
	cache_diction = {'IG': {}, 'TB': {}, 'IMDB' : {}, 'NYT': {}, 'OT': {}}

#Instagram 
print ('API #1: Instagram\n')
def lst_of_IG_days(): #creates a list of dictionaries for every day and timeframe of insta posts
	days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
	time_frames = ['12:00am-5:59am', '6:00am-11:59am','12:00pm-5:59pm', '6:00pm-11:59pm']
	sorted_days_and_times = [] #will append to get every day in time fram in order
	for day in days:
		for time in time_frames:
			sorted_days_and_times.append(day + ' ' + time) #each item in the list is a string containing the day and time
	x = [{'time': timestamp ,'likes': 0 , 'comments' : 0, 'count': 0} for timestamp in sorted_days_and_times] #every time has its own dic where the likes comments and count keys are all set to zero
	return (x)

def get_insta_data(): #data accumulation
	sn = input("What is the authenticating user's screenanme?: @") #needed to check whether the authenticating user is already in the cache
	if sn not in cache_diction['IG']:
		IGbase_url = 'https://api.instagram.com/v1/users/self/media/recent/?'
		IG_request = requests.get(IGbase_url, params = {'client_id': info.IGclient_id, 'access_token' : info.IGaccess_code, 'count': '20'}) #calls the api, count = 20 which is the max for an authenticating user in sandbox mode
		IG_data = json.loads(IG_request.text)['data'] #load the instagram info within the data key into the IG_data variable
		cache_diction['IG'][sn] = IG_data
		f = open(fname, 'w') #open the cache file 
		f.write(json.dumps(cache_diction, indent = 4)) #write to the cache file
		f.close() #close
	return cache_diction['IG'][sn] #returns a list of dictionaries containing info of the authenticating users 20 most recent posts

myinstadata = get_insta_data() #assigning the varibale my insta data to the info pulled from the get_insta_data function

def get_insta_times(IG_data): #data insights
	x = lst_of_IG_days() #calls the function defined earleir that gets a list of dictionaries to keep track of likes,comments, and count of each post
	time_frames = {'12:00am-5:59am': [0,1,2,3,4,5], '6:00am-11:59am' : [6,7,8,9,10,11], '12:00pm-5:59pm' : [12,13,14,15,16,17], '6:00pm-11:59pm' : [18,19,20,21,22,23]} #initializes a dictionary where the keys are the time frames and the values are a list containing the hours associated with that time frame
	for item in IG_data:
		IGpost_time = (datetime.datetime.fromtimestamp(int(item['created_time'])).strftime('%Y-%m-%d %H')) #converts the IG timestamp to a time in the format %Y-%m-%d %H
		IGpost_day = datetime.datetime.strptime(IGpost_time, '%Y-%m-%d %H').strftime('%A') #converts the post time into a post day using datetime
		IGpost_timeframe = IGpost_time.split(' ')[-1] #indexing the hour of the post
		for time_frame in time_frames:
			if int(IGpost_timeframe) in time_frames[time_frame]: #if the posted hour is within the list of hours
				IGpost_timeframe = time_frame #update the timeframe variable to accurately represent which timeframe the posting hour falls into
				break
		IGlikes = item['likes']['count'] #pulls like information from the post
		IGcomments = item['comments']['count'] #pulls comment information from the post
		akey = (IGpost_day + ' ' + IGpost_timeframe) #creats a key that reflects the day and timeframe of the post
		for dic in x:
			if dic['time'] == akey: #finds the dic in lst_of_IG_days that reflects the day/time of the post
				ind = x.index(dic)
				new_dic = dic
				new_dic['likes'] += IGlikes #adds overall likes to the time frame info
				new_dic['comments'] += IGcomments #adds overall comments to the time fram info
				new_dic['count'] += 1 #updates count by 1 to reflect an additional post in that time fram
				x[ind] = new_dic #replace the dictionary with updated information
				break
	return (x) #returns a list of dictionaries containing the sum of likes, comments, and the count of every post in the specified timefram

myinstatimes = get_insta_times(myinstadata) #will be refrenced for databse insertion

#Tumblr
print ('\n------------------------------------\n')
print ('API #2: Tumblr\n')
def lst_of_TB_days(): #similar function to lst_of_IG_Days but with different keys in the returned list of dictioinaries to reflect Tumblr data
	days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
	time_frames = ['12:00am-5:59am', '6:00am-11:59am','12:00pm-5:59pm', '6:00pm-11:59pm']
	sorted_days_and_times = [] #will append to get every day in time frame in order
	for day in days:
		for time in time_frames:
			sorted_days_and_times.append(day + ' ' + time) #each item in the list is a string containing the day and time
	x = [{'time': timestamp ,'post_type': [] , 'total_notes':0,'count': 0} for timestamp in sorted_days_and_times] #every time has its own dic with post type, total notes, and count all initalized as empty/0
	return (x)

def get_tumblr_data(): #data accumulation
	blog = input('Enter a tumblr url! example.tumblr.com: ') #can by any blog! not just authenticating users!
	if blog not in cache_diction['TB']: #if the blog isnt in the cache dictionary
		cache_diction['TB'][blog] = [] #initalize a cache dictionary key within the tumblr key to an empty list
		offset = 0 #initalize offset as 0, will be updated later to accumulate 100 posts
		while True: #will continue untill 100 posts have been reached
			TB_request = requests.get('http://api.tumblr.com/v2/blog/{}/posts?api_key={}'.format(blog, info.TBconsumer_key), params = {'offset': offset})
			TB_data = json.loads(TB_request.text)
			for item in TB_data['response']['posts']:
				cache_diction['TB'][blog].append(item) #append the list associated with the dictionary variabe of the blog name to add all the posts 
			if len(cache_diction['TB'][blog]) != 100: #if there arent 100 posts in the list
				offset += 20 #update offset to pull 20 later posts
			else:
				break
		f = open(fname, 'w') #open the cache file
		f.write(json.dumps(cache_diction, indent = 4)) #write to the cache file
		f.close() #close the cache file
	return cache_diction['TB'][blog] #returns a list of 100 post data

my_tumblr_data = get_tumblr_data()

def get_tumblr_info(lst_of_posts): #data insights
	x = lst_of_TB_days()
	time_frames = {'12:00am-5:59am': ['00','01','02','03','04','05'], '6:00am-11:59am' : ['06','07','08','09','10','11'], '12:00pm-5:59pm' : ['12','13','14','15','16','17'], '6:00pm-11:59pm' : ['18','19','20','21','22','23']} #similar to the tiemframes in the IG function, values in the list are now strings to be compatible with the format that returns from the Tumblr api call
	for item in lst_of_posts:
		TB_post_type = item['type'] #pull post type
		TB_post_time = item['date'][:-4] #pull the date of the post (format %Y-m%-%d %H:%M:%S)
		TB_post_day = datetime.datetime.strptime(TB_post_time, '%Y-%m-%d %H:%M:%S').strftime('%A') #convert the date into a day of the week
		TB_post_timeframe = re.findall('[0-9]+', TB_post_time)[3] #pull the hour from the post time
		TB_post_notes = item['note_count'] #pull the number of notes on the post
		for time_frame in time_frames:
			if TB_post_timeframe in time_frames[time_frame]: 
				TB_post_timeframe = time_frame #update timeframe to reflect timeframe instead of hour
				break
		akey = (TB_post_day + ' ' + TB_post_timeframe)
		for dic in x:
			if dic['time'] == akey: #finds the dictionary reflecting the day and time of each post
				ind = x.index(dic)
				new_dic = dic
				if TB_post_type not in new_dic['post_type']: #if the post type isnt in the list of post types for this specified time
					new_dic['post_type'].append(TB_post_type) #append the post type to the list
				new_dic['total_notes'] += TB_post_notes #add overall notes to the time frame dic key
				new_dic['count'] += 1 #add one to the count key to indicate 1 more post in the time frame
				x[ind] = new_dic #replace the old dictionary with the new dictionary
				break
	return (x) #returns a list of dictionaries containing info on the post type, overall notes, and frequency of posts in each time frame

my_tumblr_info = get_tumblr_info(my_tumblr_data)

#IMDB
print ('\n------------------------------------\n')
print ('API #3: IMDB\n')
def get_tv_data(title): #data accumulation
	if title not in cache_diction['IMDB']: #if the blog isnt in the cache dictionary 
		cache_diction['IMDB'][title] = {'Info': {}, 'Seasons': {}} #initalize a cache dictionary key within the IMDB key to a dictionary containing info and seasons
		base_url = 'http://www.omdbapi.com/'
		IMDB_response = requests.get(base_url, params = {'apikey': info.IMDBapi_key, 't':title})
		IMDB_Show_Info = json.loads(IMDB_response.text)
		totalszns = int(IMDB_Show_Info['totalSeasons']) #pulls the number of total seasons from the api, will be used to iterate through seasons
		#the info key in the title key contains Genre, Runtime, Rated, Actors, and Plot (for database insertion)
		cache_diction['IMDB'][title]['Info']['Genre'] = IMDB_Show_Info['Genre'].split(', ') 
		cache_diction['IMDB'][title]['Info']['Runtime'] = IMDB_Show_Info['Runtime']
		cache_diction['IMDB'][title]['Info']['Rated'] = IMDB_Show_Info['Rated']
		cache_diction['IMDB'][title]['Info']['Actors'] = IMDB_Show_Info['Actors']
		cache_diction['IMDB'][title]['Info']['Plot'] = IMDB_Show_Info['Plot']
		currentseason = 1
		while (totalszns - currentseason) >= 0: #while loop to go through every season of the show
		#the season key in the title key contains a dictionary of seasons where every key is the season number and every value is a list of episodes (for databse insertion and data visualization)
				IMDB_responseX = requests.get(base_url, params = {'apikey': info.IMDBapi_key, 't':title, 'Season': currentseason})
				IMDB_SeasonX = json.loads(IMDB_responseX.text)
				cache_diction['IMDB'][title]['Seasons']['Season ' + IMDB_SeasonX['Season']] = IMDB_SeasonX['Episodes'] #adds a key to the the seasons dic with a list of episdoes
				currentseason += 1 #update the current season varibale by 1
		f = open(fname, 'w') #open the cache file
		f.write(json.dumps(cache_diction, indent = 4)) #write to the cache file
		f.close() #clost the cachefile
	return cache_diction['IMDB'][title]

my_IMDB_shows = ['How I Met Your Mother', 'Game of Thrones', 'Gossip Girl', "Grey's Anatomy", 'Suits', 'Criminal Minds', 'Friends', 'Law & Order', 'Scandal', 'The Big Bang Theory', 'The Blacklist', 'Stranger Things', 'This Is Us', 'How to Get Away With Murder', 'Ray Donovan', 'Breaking Bad', 'The Office', 'Modern Family', 'The Vampire Diaries', 'Homeland', 'Saturday Night Live', 'Once Upon a Time', 'Supergirl', 'Chicago P.D.', 'The Sopranos', 'House of Cards', 'House', 'The X-Files', 'Downton Abbey', 'Mr. Robot', 'Mad Men', 'Big Little Lies', 'The Night Of']

def get_tv_info(lst_of_shows): #data insights
#acepts a list of shows
	shows = []
	for show in lst_of_shows:
		showdata = get_tv_data(show) #refrences the previous function for accessing show info and season info
		szns = showdata['Seasons']
		showinfo = showdata['Info']
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
		shows.append({'Show':show, 'Episodes': eps, 'Release_Day':release_day, 'Avg_Rating':avg_rating, 'Genre': showinfo['Genre'], 'Runtime': showinfo['Runtime'], 'Rated': showinfo['Rated'], 'Actors': showinfo['Actors'], 'Plot': showinfo['Plot']})
	return (shows)

my_show_info = get_tv_info(my_IMDB_shows)

#New York Times
print ('\n------------------------------------\n')
print ('API #4: NYT\n')
def get_nyt_data(term):
	if term not in cache_diction['NYT']:
		cache_diction['NYT'][term] = []
		page = 0
		while page != 10:
			NYT_base_url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
			NYT_request = requests.get(NYT_base_url, params = {'q': term, 'sort': 'newest', 'fl': 'web_url, headline, pub_date, document_type, word_count', 'page': page, 'api-key': info.NYT_APIkey})
			NYT_data = json.loads(NYT_request.text)
			for item in NYT_data['response']['docs']:
				cache_diction['NYT'][term].append(item)
			page += 1
			print ('{}0/100 results retrieved'.format(str(page)))
			time.sleep(1) #https://stackoverflow.com/questions/510348/how-can-i-make-a-time-delay-in-python
		f = open(fname, 'w')
		f.write(json.dumps(cache_diction, indent = 4))
		f.close()
	return cache_diction['NYT'][term]

def get_nyt_info(term):
	articles = get_nyt_data(term)
	info = {}
	for article in articles:
		post_date = article['pub_date'][:10]
		post_day = datetime.datetime.strptime(post_date, '%Y-%m-%d').strftime('%A')
		info[article['headline']['main']] = (post_day, article['document_type'], article['word_count'], article['web_url'])
	print ("Here's a list of the 100 most recent articles that contain the search term '{}':\n".format(term))
	num = 1
	for article in info:
		print (str(num) + '. ' + article)
		num += 1
	return (info)

um_nyt_info = get_nyt_info('University of Michigan')

#OpenTable
print ('\n------------------------------------\n')
print ('API #5: OpenTable\n')

def get_opentable_data():
	OTcity_url = 'https://opentable.herokuapp.com/api/cities'
	OTcity_request = requests.get (OTcity_url)
	cities = OTcity_request.text
	citylist = json.loads(cities)['cities']
	while True:
		OTcity = input('What city are you looking to eat in? ')
		if OTcity in citylist:
			break
		else:
			print ("I'm sorry, that was an invalid city :( ")
			print ("Please try again. Examples include: Austin, Chicago, New Orleans, San Francisco")
	if OTcity not in cache_diction['OT']:
		OTbase_url = 'https://opentable.herokuapp.com/api/restaurants'
		OTrequest = requests.get(OTbase_url, params = {'city':OTcity, 'per_page':'100'})
		OTdata = json.loads(OTrequest.text)['restaurants']
		cache_diction['OT'][OTcity] = OTdata
		f = open(fname, 'w')
		f.write(json.dumps(cache_diction, indent = 4))
		f.close()
	return cache_diction['OT'][OTcity]

my_opentable_data = get_opentable_data()

def get_opentable_info(lst_of_restaurants):
	restaurant_dic = {}
	for restaurant in lst_of_restaurants:
		OTfull_address = restaurant['address']+ ', ' + restaurant['city'] + ' ' + restaurant['state'] + ', ' + restaurant['postal_code']
		OTphone = '({}) {}-{}'.format(restaurant['phone'][:3], restaurant['phone'][3:6], restaurant['phone'][-5:-1])
		restaurant_dic[restaurant['name']] = {'Address': OTfull_address, 'Phone': OTphone, 'Price_Level': restaurant['price'], 'Coord': (restaurant['lat'], restaurant['lng'])}
	return restaurant_dic

my_opentable_info = get_opentable_info(my_opentable_data)

#Database creation
conn = sqlite3.connect('206Final_Project.sqlite')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Instagram')
cur.execute('CREATE TABLE Instagram (Weekday TEXT, Time_Frame TEXT, Num_Posts INTEGER, Total_Likes INTEGER, Total_Comments INTEGER, Avg_Likes INTEGER, Avg_Comments INTEGER)')

cur.execute('DROP TABLE IF EXISTS Tumblr')
cur.execute('CREATE TABLE Tumblr (Weekday TEXT, Time_Frame TEXT, Num_Posts TEXT, Post_Types TEXT, Total_Notes INTEGER, Avg_Notes INTEGER)')

cur.execute('DROP TABLE IF EXISTS IMDB')
cur.execute('CREATE TABLE IMDB (Title TEXT, Episode_Count INT, Release_Day TEXT, Rating TEXT, Genre TEXT, Runtime TEXT, Rated TEXT, Actors TEXT, Plot TEXT)')

cur.execute('DROP TABLE IF EXISTS NYT')
cur.execute('CREATE TABLE NYT (Headline TEXT, Post_Day TEXT, Document_Type TEXT, Word_Count TEXT, URL TEXT)')

cur.execute('DROP TABLE IF EXISTS OpenTable')
cur.execute('CREATE TABLE OpenTable (Name TEXT, Address TEXT, Phone TEXT, Price_Level INT, Coordinates TEXT)')

for day in myinstatimes:
	if day['count'] == 0:
		avgl = 0
		avgc = 0
	else:
		avgl = day['likes']/day['count']
		avgc = day['comments']/day['count']
	tup = (day['time'].split(' ')[0], day['time'].split(' ')[1], day['count'], day['likes'], day['comments'], avgl, avgc)
	cur.execute('INSERT INTO Instagram (Weekday, Time_Frame, Num_Posts, Total_Likes, Total_Comments, Avg_Likes, Avg_Comments) VALUES (?,?,?,?,?,?,?)', tup)

for day in my_tumblr_info:
	if day['count'] == 0:
		avgn = 0
	else:
		avgn = int((day['total_notes'])/(day['count']))
	tup = (day['time'].split(' ')[0], day['time'].split(' ')[1], day['count'], (', '.join(day['post_type'])), day['total_notes'], avgn)
	cur.execute('INSERT INTO Tumblr (Weekday, Time_Frame, Num_Posts, Post_Types, Total_Notes, Avg_Notes) VALUES (?,?,?,?,?,?)', tup)

for show in sorted(my_show_info, key = lambda x: x['Episodes']):
	tup = (show['Show'], show['Episodes'], show['Release_Day'], show['Avg_Rating'], ', '.join(show['Genre']), show['Runtime'], show['Rated'], show['Actors'], show['Plot'])
	cur.execute('INSERT INTO IMDB (Title, Episode_Count, Release_Day, Rating, Genre, Runtime, Rated, Actors, Plot) VALUES (?,?,?,?,?,?,?,?,?)', tup)

for article in um_nyt_info:
	tup = (article, ) + um_nyt_info[article]
	cur.execute('INSERT INTO NYT (Headline, Post_Day, Document_Type, Word_Count, URL) VALUES (?,?,?,?,?)', tup)

for rest in my_opentable_info:
	tup = (rest, my_opentable_info[rest]['Address'], my_opentable_info[rest]['Phone'], my_opentable_info[rest]['Price_Level'], str(my_opentable_info[rest]['Coord']))
	cur.execute('INSERT INTO OpenTable (Name, Address, Phone, Price_Level, Coordinates) VALUES (?,?,?,?,?)', tup)
conn.commit()

#Data Visualization
#	Tumblr and Instagram Bar Chart
plotly.tools.set_credentials_file(username='ametaxas', api_key=info.PLapi_key)
total_insta_count = sum([int(dic['count']) for dic in myinstatimes])
trace1 = go.Bar(
	x = [dic['time'] for dic in myinstatimes],
	y = [(dic['count']/total_insta_count) for dic in myinstatimes],
	text = ['{}/{} posts'.format(str(dic['count']), str(total_insta_count)) for dic in myinstatimes],
	name = 'Instagram',
	marker = dict(
		color='rgb(146,34,150)',
		line=dict(
			color='rgb(232,116,16)',
			width=2),
		)
)
total_tumblr_count = sum([int(dic['count']) for dic in my_tumblr_info])
trace2 = go.Bar(
	x = [dic['time'] for dic in my_tumblr_info],
	y = [(int(dic['count'])/total_tumblr_count) for dic in my_tumblr_info],
	text = ['{}/{} posts'.format(str(dic['count']), str(total_tumblr_count)) for dic in my_tumblr_info],
	name = 'Tumblr',
	marker = dict(
		color='rgb(40,75,104)',
		line=dict(
			color='rgb(77,79,81)',
			width=2),
		)
)
data = [trace1, trace2]
layout = go.Layout(
	autosize = False,
	width = 1000,
	height = 1000,
	hovermode = 'closest',
	margin = go.Margin(
		l=100,
		r=50,
		b=300,
		t=100,
		pad=4
	),
	title = 'Instagram and Tumblr activity',
	xaxis=dict(
		title='Time of Day',
		titlefont=dict(
			size=16,
			color='rgb(107,107,107)'
		),
		tickfont = dict(
			size=14,
			color='rgb(107,107,107)'
		)
	),
	yaxis=dict(
		title='Percentage of Posts',
		titlefont=dict(
			size=16,
			color='rgb(107,107,107)'
		),
		tickfont = dict(
			size=14,
			color='rgb(107,107,107)'
		),
		tickformat='%'
	),
	legend=dict(
		x=0,
		y=1.0,
		bgcolor='rgba(255,255,255,0)',
		bordercolor='rgba(255,255,255,0)'
	),
	barmode = 'group',
	bargap = 0.0,
	bargroupgap=0.0,
)
fig = go.Figure(data=data, layout=layout)
py.iplot(fig, filename='IG_TB_bar')
#		NYT Wordcloud
d = path.dirname(__file__)
text = (' ').join(um_nyt_info)
um_mask = np.array(Image.open(path.join(d, 'm.png')))
image_colors = ImageColorGenerator(um_mask)
stopwords = set(STOPWORDS)
stopwords.add('Dies')
wc = WordCloud(mask= um_mask, stopwords=stopwords).generate(text)
plt.imshow(wc.recolor(color_func=image_colors), interpolation='bilinear')
plt.axis('off')
plt.figure()
wc.to_file(path.join(d, 'um.png'))
#		IMDB Scatterplot
genre_colors = {'Comedy': 'rgb(255,240,79)', 'Adventure': 'rgb(24,165,38)', 'Drama': 'rgb(113,27,163)', 'Crime': 'rgb(204,132,0)', 'Action': 'rgb(255,79,79)'}
trace = go.Scatter(
	x = [show['Episodes'] for show in my_show_info],
	y = [show['Avg_Rating'] for show in my_show_info],
	legendgroup = [show['Genre'][0] for show in my_show_info],
	mode = 'markers',
	text = [show['Show'] for show in my_show_info],
	name = [show['Genre'][0] for show in my_show_info],
	marker = dict(
		size = 20,
		color = [genre_colors[(show['Genre'][0])] for show in my_show_info],
		line = dict(
			width = 1,
			color = 'rgb(0,0,0)')
		)
)
data = [trace]
layout = dict(
	title = 'Episode Count vs. Rating',
	yaxis = dict(title = 'Rating'),
	xaxis = dict(title = 'Episode Count')
)
fig = dict(data = data, layout = layout)
py.iplot(fig, filename = 'IMDB_Scatter')