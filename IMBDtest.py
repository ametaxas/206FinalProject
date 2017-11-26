IMBDapi_key = 'f2a81789'
cache_diction = {'IMBD':{}}
def get_tv_data(title):
	if title not in cache_diction['IMBD']:
		cache_diction['IMBD'][title] = {}
		base_url = 'http://www.omdbapi.com/'
		IMBD_response = requests.get(base_url, params = {'apikey': info.IMBDapi_key, 't':title)
		IMBD_data = json.loads(IMBD_response.text)
		cache_diction['IMBD'][title]['Season 1'] = IMBD_Season1['Episodes']
		# if int(IMBD_Season1['totalSeasons']) > 1:
		# 	currentseason = 2
		# 	while (int(IMBD_Season1['totalSeasons']) - currentseason) >= 0:
		# 		IMBD_response1 = requests.get(base_url, params = {'apikey': info.IMBDapi_key, 't':title, 'Season': currentseason})
		# 		IMBD_SeasonX = json.loads(IMBD_response1.text)
		# 		cache_diction['IMBD'][title]['Season ' + IMBD_SeasonX['Season']] = IMBD_SeasonX['Episodes']
		# 		currentseason += 1
		f = open(fname, 'w')
		f.write(json.dumps(cache_diction, indent = 4))
		f.close()
	return cache_diction['IMBD'][title]

lst_of_shows = ['How I Met Your Mother, Game of Thrones, Blackish, Gossip Girl, Greys Anatomy']
