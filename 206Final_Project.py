#206Final Project
#Arielle Metaxas

#caching pattern
fname = ''
try:
	f = open(fname, 'r')
	fcontents = f.read()
	cache_diction = json.dumps(fcontents)
	f.close()
except:
	cache_diction = {}