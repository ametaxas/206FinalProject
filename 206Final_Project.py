#206Final Project
#Arielle Metaxas
import info
import requests
import json
#caching pattern
fname = '206Final_Project.json'
try:
	f = open(fname, 'r')
	fcontents = f.read()
	cache_diction = json.loads(fcontents)
	f.close()
except:
	cache_diction = {'IG': {} }

#Instagram
def get_insta():
	IGclient_id = info.IGclient_id
	IGclient_secret = info.IGclient_secret
	IGaccess_code = info.IGaccess_code
	IGbase_url = 'https://api.instagram.com/v1/users/self/media/recent/?'
	IG_request = requests.get(IGbase_url, params = {'client_id': IGclient_id, 'access_token' : IGaccess_code, 'count' : 20})
	IG_data = json.loads(IG_request.text)['data']
	sn = IG_data[0]['user']['full_name']
	if sn not in cache_diction['IG']:
		cache_diction['IG'][sn] = []
		for inst in range(4):
			for item in IG_data:
				post_time = item['created_time']
				likes = item['likes']['count']
				comments = item['comments']['count']
				tup = (post_time, likes, comments)
				(cache_diction['IG'][sn]).append(tup)
			IG_maxid = (IG_data[-1]['id'])
			print (IG_maxid)
			IG_request = requests.get(IGbase_url, params = {'client_id': IGclient_id, 'access_token' : IGaccess_code, 'count' : 20, 'max_id': IG_maxid})
			IG_data = json.loads(IG_request.text)['data']
	f = open(fname, 'w')
	f.write(json.dumps(cache_diction, indent = 4))
	f.close()
	return cache_diction['IG'][sn]
x = get_insta()
# a = cache_diction['IG']['Posts']['Arielle Metaxas']
# print (len(a))
# for item in a:
# 	post_time = item['created_time']
# 	likes = item['likes']['count']
# 	comments = item['comments']['count']
# 	info = (post_time, likes, comments)
# 	cache_diction['IG']['Info'].append(info)
# print (cache_diction['IG']['Info'])