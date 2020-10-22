''' This file models a graph that uses some properties
in the vertices. This class hinerits from the Graph 
class, available on https://github.com/italocampos/graphs/blob/python/adjacency_matrix/graph.py
'''

from graph import Graph

class Topology(Graph):
	def __init__(self):
		super().__init__(list(), list())
		self._edges = list()
		''' The edges are in the form [a, b, c], where `a` and `b`
		the vertices of the edge and `c` is a boolean value that
		indicates whether the edge is used or not '''


	def add_edge(self, vertex_a, vertex_b, used = True):
		if used:
			super().add_edge(vertex_a, vertex_b)
		self._edges.append([vertex_a, vertex_b, used])


	def get_edge(self, index):
		if self._is_valid_index(index):
			return self._edges[index]


	def get_edge_index(self, vertex_a, vertex_b):
		index = 0
		for line in self._edges:
			va, vb, _ = line
			edge = [(va, vb), (vb, va)]
			if (vertex_a, vertex_b) in edge:
				return index
			index += 1


	def is_used(self, edge_index):
		return self.get_edge(edge_index)[2]


	def get_edge_states(self):
		return [int(b[2]) for b in self._edges]


	def set_edge_states(self, vector):
		if len(vector) != len(self._edges):
			raise(Exception('The given vector has a different size against the number of edges.'))
		for i, value in enumerate(vector, start=0):
			if value == 1:
				self.activate_edge(i)
			else:
				self.deactivate_edge(i)


	def set_state_of_edge(self, edge, state):
		if self._is_valid_index(edge):
			self._edges[edge] = state


	def get_state_of_edge(self, edge):
		return self.get_edge(edge)[2]
	

	def activate_edge(self, index):
		if self._is_valid_index(index):
			va, vb, _ = self.get_edge(index)
			self._edges[index][2] = True
			super().add_edge(va, vb)
	

	def deactivate_edge(self, index):
		if self._is_valid_index(index):
			va, vb, _ = self.get_edge(index)
			self._edges[index][2] = False
			self.remove_edge(va, vb)


	def num_of_used_edges(self):
		return self._edges.count(1)

	
	def _is_valid_index(self, index):
		if 0 <= index < len(self._edges):
			return True
		raise(ValueError('There is no an edge related to the given index.'))



class MultiSourcedTopology(Topology):
	''' This class is a derivation of Topology class in order to support multi-
	sourced models in the Tabu Search.

	This class is meant to link the multiple sources with abstract lines and
	choose only one among them to be a Topology 'source'. This mechanism makes
	possible the topology perform the Tabu Search without change too many code.

	Properties
	----------
	abstract_edges : list
		A list with the index of the abstract lines. See the stringdoc of the
		method 'add_abstract_edge()' to more info.
	'''

	def __init__(self):
		super().__init__()
		self.abstract_edges = list()
	

	def add_abstract_edge(self, vertex_a, vertex_b):
		''' Adds an abstract edge to the topology.

		An abstract edge is an edge that only exists in the topology, not in
		the original network model. These edges are used to link multiple
		sources of the model in only one vertex and perform the graph
		operations as the model had a single source. The abstract lines MUST
		be instantiated after all the normal edges of the topology.

		Parameters
		----------
		vertex_a : str
			The name of one of the vertices of the edge.
		vertex_b : str
			The name of the other vertex of the edge.
		'''

		self.add_edge(vertex_a, vertex_b, used = True)
		self.abstract_edges.append(self.get_edge_index(vertex_a, vertex_b))
	
	
	def get_edge_states(self):
		''' Return the states of the edges in [1, 0, 1,...] form, excluding the
		abstract edges.

		Returns
		-------
		list
			The binary vector with the state of the edges exclugind the
			positions of the abstract edges.
		'''

		edges = super().get_edge_states()
		states = list()
		for i in range(len(edges)):
			if not i in self.abstract_edges:
				states.append(edges[i])
		return states
	

	def set_edge_states(self, vector):
		''' Put the states of the switches described in the provided vector in
		each edge of the topology, except in the abstract lines, which are ever
		actives.

		Parameters
		----------
		vector : list
			The vector of binaries indicating the states of the edges in the
			topology.
		'''

		super().set_edge_states(vector + [1 for _ in self.abstract_edges])