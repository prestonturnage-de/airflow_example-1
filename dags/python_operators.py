"""
Description:
	An example airflow DAG to demonstrate:
		* Using python operators in airflow
		* Using ML (namely clustering) to anonimize data optained through API calls

Author: Ryan Whitney
"""

import os
import pendulum

from airflow.decorators import dag, task


@task.virtualenv(requirements=['requests'])
def get_pokemons(limit=1):
	'''
	Hits the pokemon api for a list of pokemon, organized in 20-mon chunks

	Parameters
	---------
	limit : int
		the limit on the number of pokemon to fetch

	Returns
	---------
	[dict]
		a list of dicts in the following format:
			{
				'name': <str>
				'url': <str>
			}
	'''
	import requests
	import time

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


@task.virtualenv(requirements=['requests'])
def get_pokemon_weights(mons):
	'''
	Adds a weight field to the list of pokemon dicts obtained in the previous step.

	Parameters
	----------
	[dict]
		a list of dicts in the following format:
			{
				'name': <str>
				'url': <str>
			}

	Returns
	----------
	[dict]
		a list of dicts in the following format:
			{
				'name': <str>
				'url': <str>
				'weight': int
			}
	'''
	import requests
	import time

	output = []
	for i in mons:
		print('getting:',i['name'])
		output.append(i | {
			'weight': requests.get(i['url']).json()['weight']
			})
		time.sleep(.1)
	return output


@task.virtualenv(requirements=['scikit-learn', 'numpy'])
def cluster_pokemon_weights(mons):
	'''
	Uses the clustering function from scikit-learn to sort the weight information
	into bins.

	Parameters
	---------
	[dict]
		a list of dicts in the following format:
			{
				'name': <str>
				'url': <str>
				'weight': int
			}

	Returns
	---------
	{
		'clusterdata': {},
		'pokemondata':
			[dict]
				a list of dicts in the following format:
					{
						'name': <str>
						'url': <str>
						'weight': int
					}
	}
	'''
	from sklearn.cluster import KMeans
	import numpy as np

	# get the weights array
	weightsarr = np.array([i['weight'] for i in mons]).reshape(-1, 1)
	# perform the clustering algorithm
	kmeans = KMeans(n_clusters=3, random_state=0, n_init="auto").fit(weightsarr)

	outp = []

	# append the cluster information to the data that was passed in
	# throw in the error factor for good measure.
	for i,j in enumerate(mons):
		outp.append(j | {
			'parent_cluster': kmeans.labels_[i],
			'parent_centroid': kmeans.cluster_centers_[kmeans.labels_[i]][0],
			'deviation_factor': abs(kmeans.cluster_centers_[kmeans.labels_[i]][0] - j['weight'])/kmeans.cluster_centers_[kmeans.labels_[i]][0]
		})

	# restructure the output json to add the clustering metadata
	labels = list(kmeans.labels_)
	# get the list of centroids
	centroids = [i[0] for i in kmeans.cluster_centers_.reshape(-1,1)]
	# create a dict containing the centroids and the size of their respective clusters
	histogram = {centroids[i]: labels.count(i) for i in set(labels)}
	outp = {
		'clusterdata': {
			'n_clusters': len(kmeans.cluster_centers_),
			# 'centroids': {i: histogram[i] for i in centroids}
			'centroids': histogram
		},
		'pokemondata': outp
	}
	return outp


@task.virtualenv
def metrics_pokemon_weights(mons):
	'''
	Calculate the metrics and print the results of the previous functions.

	Parameters
	----------
	{
		'clusterdata': {},
		'pokemondata':
			[dict]
				a list of dicts in the following format:
					{
						'name': <str>
						'url': <str>
						'weight': int
					}
	}

	Returns
	--------
	None
	'''
	import statistics
	import json
	import tabulate

	divider = '-'*100

	# print the raw data being fed into the metrics function
	print(divider)
	print('raw data:')
	print(tabulate.tabulate(mons['pokemondata'], headers='keys'))

	# do some statistics
	weightsarr = [i['weight'] for i in mons['pokemondata']]
	outp = {
		'max': max(weightsarr),
		'min': min(weightsarr),
		'mean': statistics.mean(weightsarr),
		'median': statistics.median(weightsarr),
		'stdev:': statistics.stdev(weightsarr)
	}

	# print the information regarding the cluster centroids
	print(divider)
	print('clusters detail (centroids and sizes):')
	print(json.dumps(mons['clusterdata'], indent=4))
	print(divider)
	print('weight statistics:')
	print(json.dumps(outp, indent=4))
	print(divider)
	print('anonymized information:')
	outp2 = []
	for i,j in enumerate(mons['pokemondata']):
		outp2.append({
			'index': i, 'name': j['name'], 'parent cluster': j['parent_centroid']
		})
	print(tabulate.tabulate(outp2, headers='keys'))


@dag(
		dag_id='clustering_deidentification',
		schedule=None,
		catchup=False,
		tags=["example"],
)
def mainfunc():
	'''
	Define the DAG
	'''
	# get the list of pokemon names and urls for querying their details.
	mons = get_pokemons(100)
	# Hit the endpoints from the previous result to get their weights.
	monsdetail = get_pokemon_weights(mons)
	# Perform clustering. We could use a much simpler algorithm for this but this is mostly
	# for demonstration purposes. 
	monsclustered = cluster_pokemon_weights(monsdetail)
	# compute the metrics and print the results.
	metrics_pokemon_weights(monsclustered)

# You have to call the DAG function in order to register it with airflow. Let's do that here.
mainfunc()