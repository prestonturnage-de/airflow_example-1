# pokemon api informaiton: https://pokeapi.co/api/v2/pokemon/

import requests
import json
import time
import statistics
from sklearn.cluster import KMeans
import numpy as np

weightsarr = np.array([69, 130, 1000, 85, 190, 905, 90, 225, 855, 29, 99, 320, 32, 100, 295, 18, 300, 395, 35, 185, 20, 380, 69, 650, 60, 300, 120, 295, 70, 200, 600, 90, 195, 620, 75, 400, 99, 199, 55, 120, 75, 550, 54, 86, 186, 54, 295, 300, 125, 8, 333, 42, 320, 196, 766, 280, 320, 190, 1550, 124, 200, 540, 195, 565, 480, 195, 705, 1300, 40, 64, 155, 455, 550, 200, 1050, 3000, 300, 950, 360, 785, 200, 540, 195, 565, 480, 195, 705, 1300, 40, 64, 155, 455, 550, 200, 1050, 3000, 300, 950, 360, 785, 60, 600, 150, 392, 852, 900, 1200, 300, 300, 40, 1325, 1, 1, 405, 2100, 324, 756, 65, 600, 104, 666, 25, 1200, 65, 450, 498, 502, 655, 10, 95, 1150, 1200, 346, 350, 800, 80, 250, 150, 390, 345, 60, 600, 150, 392, 852, 900, 1200, 300, 300, 40, 1325, 1, 1, 405, 2100, 324, 756, 65, 600, 104, 666, 25, 1200, 65, 450, 498, 502, 655, 10, 95, 1150, 1200, 346, 350, 800, 80, 250, 150, 390, 345, 800, 545, 560, 406, 300, 445, 550, 884, 100, 2350, 2200, 40, 65, 290, 245, 250, 365, 75, 350, 115, 405, 590, 4600, 554, 526, 600, 33, 165, 2100, 1220, 40, 64, 158, 1005, 79, 190, 795, 95, 250, 888])

divider = '-'*100

pokemon='eevee'
endpoint = 'https://pokeapi.co/api/v2/pokemon/?offset=20&limit=20'
# print(json.dumps(requests.get('https://pokeapi.co/api/v2/pokemon/'+pokemon).json(), indent=4))
# print(json.dumps(requests.get(endpoint).json(), indent=4))
def getpokemons(limit=1):
	output = []
	increment = 20
	index = 0
	while index < limit:
		endpoint = 'https://pokeapi.co/api/v2/pokemon/?offset=' + str(index) + '&limit=' + str(index)
		print('getting:',endpoint)
		output = output + requests.get(endpoint).json()['results']
		time.sleep(.5)
		index += increment
	return output

def getpokemonweights(mons):
	output = []
	for i in mons:
		print('getting:',i['name'])
		output.append(i | {
			'weight': requests.get(i['url']).json()['weight']
			})
		time.sleep(.1)
	return output

def metricspokemonweights(monsdict):
	weightsarr = [i['weight'] for i in monsdict['pokemondata']]
	# return sum([i['weight'] for i in mons])
	return {
		'max': max(weightsarr),
		'min': min(weightsarr),
		'mean': statistics.mean(weightsarr),
		'median': statistics.median(weightsarr),
		'stdev:': statistics.stdev(weightsarr)
	}

def clusterpokemonweights(mons):
	weightsarr = np.array([i['weight'] for i in mons]).reshape(-1, 1)
	kmeans = KMeans(n_clusters=3, random_state=0, n_init="auto").fit(weightsarr)
	# print(kmeans.labels_)
	outp = []
	for i,j in enumerate(mons):
		outp.append(j | {
			'parent_cluster': kmeans.labels_[i],
			'parent_centroid': kmeans.cluster_centers_[kmeans.labels_[i]][0]
		})
	outp = {
		'clusterdata': {
			'n_clusters': len(kmeans.cluster_centers_),
			'centroids': [list(i)[0] for i in kmeans.cluster_centers_.reshape(-1, 1)]
		},
		'pokemondata': outp
	}
	return outp

def test1():
	mons = getpokemons()
	weights = getpokemonweights(mons)
	clustered = clusterpokemonweights(weights)
	print(json.dumps(mons, indent=4))
	print(json.dumps(weights, indent=4))
	print(json.dumps(metricspokemonweights(clustered), indent=4))
	# print([i['weight'] for i in weights])
	print(divider)
	print('cluster data:')
	print(clustered['clusterdata'])
	print(type(clustered['clusterdata']))
	print(json.dumps(clustered['clusterdata'], indent=4))
	print(divider)
	print('raw data:')
	for i,j in enumerate(clustered['pokemondata']):
		print(i,':',j)

def histogram(numslist):
	# labels = list(set(numslist))
	# outp = []
	# for i in labels:
	# 	outp.append([i, numslist.count(i)])
	# return outp
	return [[i, numslist.count(i)] for i in set(numslist)]

def test2():
	kmeans = KMeans(n_clusters=3, random_state=0, n_init="auto").fit(weightsarr.reshape(-1, 1))
	# print(kmeans.labels_)
	help(kmeans)
	outp = [list(i) for i in zip(weightsarr, kmeans.labels_)]
	outp.sort(key=lambda x: x[0])
	# print(outp)
	for i,j in enumerate(outp):
		print(i,':',j)
	print('centers:',kmeans.cluster_centers_)
	print(divider)
	print(histogram(list(kmeans.labels_)))


if __name__ == '__main__':
	# test1()
	test2()

