# -*- coding: utf-8 -*-

"""
given a sentence in L1, need to be translated into a sentence in L2

L1 generates a dependency graph, which generates possible spatial dependency graphs, SDG,
which may already be learned the corresponding graph in L2 with GED
Target SDG in L2 is the one with the minimal GED.


1. construction possible SDGs
2. similarity between words in L1
3. GED between graphs
4. learning from paired sentences
    4.1 database table of paired sentences
    4.2 language dependency graph
    4.3 construct a tree, SDG*, each node is spatial dependency graph
        types of SDGs
    4.4 find the minimal GED between nodes of SDG*, save MCS in database, with context

5. translation process
    5.1 L1 to LDG
    5.2 construct SDG* of LDG
    5.3 for each node of SDG*, map its subgraphs into the graph in the L2, based on the learned knowledge
    5.4 integrate these subgraphs into a whole, and compute the GED
    5.5 the one with the minimal GED will be linearized into the sentence
"""

