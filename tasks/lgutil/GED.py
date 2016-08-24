
"""
One method is to use what is called Eigenvector Similarity.
Basically, you calculate the Laplacian eigenvalues for the
adjacency matrices of each of the graphs. For each graph,
find the smallest k such that the sum of the k largest
eigenvalues constitutes at least 90% of the sum of all
of the eigenvalues. If the values of k are different between
the two graphs, then use the smaller one. The similarity
metric is then the sum of the squared differences between
the largest k eigenvalues between the graphs. This will
produce a similarity metric in the range [0, ∞), where
values closer to zero are more similar.
"""

import networkx as nx

def select_k(spectrum, minimum_energy = 0.9):
    running_total = 0.0
    total = sum(spectrum)
    if total == 0.0:
        return len(spectrum)
    for i in range(len(spectrum)):
        running_total += spectrum[i]
        if running_total / total >= minimum_energy:
            return i + 1
    return len(spectrum)

laplacian1 = nx.spectrum.laplacian_spectrum(graph1)
laplacian2 = nx.spectrum.laplacian_spectrum(graph2)

k1 = select_k(laplacian1)
k2 = select_k(laplacian2)
k = min(k1, k2)

similarity = sum((laplacian1[:k] - laplacian2[:k])**2)

