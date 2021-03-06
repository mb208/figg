import logging

"""
Functions to compute distance matrices
"""

def workspace(orders, labels, is_circular):
	"Defines the workspace"

	ref_order = []
	ref_matrix = []
	first_seen = []

	# Initialize the reference order with that of the first genome and delete it from the list 
	ref_order = orders[0] 
	del orders[0]
	first_seen = [labels[0]]*len(ref_order)
	if ( is_circular ):
		del first_seen[-1]
	
	# Initialize the reference matrix
	num_genes = len(set(ref_order))
	index_list = [ref_order.index(i) for i in ref_order]
	ref_matrix = [[0]*num_genes for i in range(num_genes)]
	for i in range(len(index_list) - 1):
		if "-" in ref_order[i + 1]:
			ref_matrix[index_list[i]][index_list[i + 1]] = -1
		else:
			ref_matrix[index_list[i]][index_list[i + 1]] = 1

	# Extend the reference order and matrix by looking for new genes in all other input genomes
	for i in range(1, len(set(labels))):
		for j in orders[i - 1]: 
			a = j not in ref_order
			b = j.replace('-','') not in ref_order
			if a & b:
				ref_order.append(j)
				ref_matrix.append([0]*len(ref_matrix))
				first_seen.append(labels[i])
				for x in range(len(ref_matrix)):
					ref_matrix[x] += [0]
	ref_order.pop(ref_order[1:].index(ref_order[0]) + 1)

	return ref_order, ref_matrix, first_seen


def adj_matrix(order, ref_order):
	"Computes the adjacency matrix for a given genome"

	num_genes = len(set(ref_order))
	matrix = [[0]*num_genes for i in range(num_genes)]
	index_list = [ref_order.index(i) if i in ref_order else ref_order.index(i.replace('-', '')) for i in order]
	for i in range(len(index_list) - 1):
		if "-" in list(order[i + 1]):
			matrix[index_list[i]][index_list[i + 1]] = -1
		else:
			matrix[index_list[i]][index_list[i + 1]] = 1 

	return matrix


def adj_matrix_set(ref_matrix, ref_order, gene_orders):
	"Computes the set of all adjacency matrices" 

	num_genomes = len(gene_orders) + 1

	# Initialize the set of adjacency matrices and append the reference 
	matrix_set = []
	matrix_set.append(ref_matrix) 

	# Append the matrices for all other genomes 
	[matrix_set.append(adj_matrix(gene_orders[i], ref_order)) for i in range(len(gene_orders))]

	return matrix_set 


def AD(matrix_1, matrix_2):
	"Counts the differences between two adjacency matrices (AD)"

	diff = 0 
	for i in range(len(matrix_1)):
		for j in range(len(matrix_2)):
			if ( matrix_1[i][j] != matrix_2[i][j] ):
				diff += 1

	return diff


def dist_matrix(adj_matrices):
	"Computes the uncorrected distance matrix (matrix of AD)" 

	num_genomes = len(adj_matrices)
	matrix = [[0]*num_genomes for i in range(num_genomes)]
	for i in range(num_genomes):
		for j in range(i):
			matrix[i][j] = AD(adj_matrices[i], adj_matrices[j])
			
	return matrix 


def freq_matrix_pos(adj_matrices):
	"Computes the positive frequency matrix"

	num_genes = len(adj_matrices[0])
	matrix = [[0]*num_genes for i in range(num_genes)]
	for i in range(len(matrix)):
		for j in range(len(matrix)):
			matrix[i][j] = round(sum([1 for x in range(len(adj_matrices)) if adj_matrices[x][i][j] == 1]) / float(len(adj_matrices)), 4)
	
	return matrix


def freq_matrix_neg(adj_matrices):
	"Computes the negative frequency matrix"

	num_genes = len(adj_matrices[0])
	matrix = [[0]*num_genes for i in range(num_genes)]
	for i in range(len(matrix)):
		for j in range(len(matrix)):
			matrix[i][j] = round(sum([1 for x in range(len(adj_matrices)) if adj_matrices[x][i][j] == -1]) / float(len(adj_matrices)), 4)
	
	return matrix


def ADc(matrix_1, matrix_2, positive_freqs, negative_freqs):
	"Similar to AD() but uses frequencies to correct the observed differences"

	diff = 0 
	for i in range(len(matrix_1)):
		for j in range(len(matrix_1)):
			if ( matrix_1[i][j] != matrix_2[i][j] ):
				if ( matrix_1[i][j] > 0 & matrix_2[i][j] > 0 ):
					diff += (1 - positive_freqs[i][j])
				else:
					diff += (1 - negative_freqs[i][j])
	
	return diff


def dist_matrix_corrected(adj_matrices, pos_freqs, neg_freqs):
	"Computes the corrected distance matrix (matrix of ADc)"

	num_genomes = len(adj_matrices)
	matrix = [[0]*num_genomes for i in range(num_genomes)]
	for i in range(num_genomes):
		for j in range(i):
			matrix[i][j] = ADc(adj_matrices[i],adj_matrices[j], pos_freqs, neg_freqs)
			
	return matrix   
