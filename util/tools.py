''' This file contains some functionalities to support the development
of the TS'''

from .topology import Topology, MultiSourcedTopology
from random import randint, random
import copy, pandapower as pp

# Defining contants for the functions

# The value for the max probability for the probability vector
MAX_PROB = 0.7


def create_topology(pp_net):
	top = Topology()
	# Creating vertices (buses)
	for bus in pp_net.bus['name']:
		top.add_vertex(bus)
	# Creating edges (lines)
	lines = list()
	for from_bus in pp_net.line['from_bus']:
		lines.append([pp_net.bus['name'][from_bus], ''])
	for i, to_bus in enumerate(pp_net.line['to_bus'], start = 0):
		lines[i][1] = pp_net.bus['name'][to_bus]
	for i, state in enumerate(pp_net.switch['closed'], start = 0):
		top.add_edge(lines[i][0], lines[i][1], state)
	return top


def create_multisourced_topology(pp_net):
	top = MultiSourcedTopology()
	# Creating vertices (buses)
	for bus in pp_net.bus['name']:
		top.add_vertex(bus)
	# Creating edges (lines)
	lines = list()
	for from_bus in pp_net.line['from_bus']:
		lines.append([pp_net.bus['name'][from_bus], ''])
	for i, to_bus in enumerate(pp_net.line['to_bus'], start = 0):
		lines[i][1] = pp_net.bus['name'][to_bus]
	for i, state in enumerate(pp_net.switch['closed'], start = 0):
		top.add_edge(lines[i][0], lines[i][1], state)
	return top


def make_switch_operations(solution, pp_net):
	''' Sets the switch states of 'solution' in the 'pp_net'

	Parameters
	----------
	solution : list
		The solution to be applied in the 'pp_net'.
	pp_net : pandapower.auxiliary.pandapowerNet
		The pandapower net where the switch states should be applied.
	'''

	for i, value in enumerate(solution, start=0):
		pp_net.switch['closed'][i] = bool(value)


def swap(index_a, index_b, line_vector):
	lv = line_vector.copy()
	lv[index_a], lv[index_b] = lv[index_b], lv[index_a]
	return lv


def objective_function(topology, root):
	return len(topology.conex_vertices(root))


def best_of(solutions, topology, source):
	if solutions != []:
		sol = solutions.copy()
		best = sol.pop(0)
		top = copy.deepcopy(topology)
		top.set_edge_states(best)
		value = objective_function(top, source)
		for s in sol:
			top.set_edge_states(s)
			v = objective_function(top, source)
			if v > value:
				best = s
				value = v
	else:
		raise(Exception('The solutions list is empty.'))
	return best
	

def get_used_indexes(line_vector):
	used = list()
	for i, item in enumerate(line_vector, start=0):
		if item == 1:
			used.append(i)
	return used


def get_unused_indexes(line_vector):
	unused = list()
	for i, item in enumerate(line_vector, start=0):
		if item == 0:
			unused.append(i)
	return unused


def swap_1_0(line_vector):
	used = get_used_indexes(line_vector)
	unused = get_unused_indexes(line_vector)
	if used != [] and unused != []:
		a = used[randint(0, len(used)-1)]
		b = unused[randint(0, len(unused)-1)]
	else:
		return line_vector
		
	return swap(a, b, line_vector)


def set_value(line_vector, indexes, value):
	if value not in [0, 1]:
		raise(Exception('Invalid value to set in a solution'))
	for index in indexes:
		line_vector[index] = value
	return line_vector


def set_faults(topology, fault_points):
	for fault in fault_points:
		topology.deactivate_edge(fault)
	return topology


''' Returns the indexes of the bridge lines between the source and
the first fork '''
def bridge_lines(topology, root):
	bridges = list()
	adjacent = topology.get_adjacent(root)
	while len(adjacent) == 1:
		bridges.append(topology.get_edge_index(root, adjacent[0]))
		predecessor = root
		root = adjacent[0]
		adjacent = list()
		for adj in topology.get_adjacent(root):
			if adj != predecessor:
				adjacent.append(adj)
	return bridges


def get_lines_probability(topology, source):
	probabilities = list()
	heights, _ = topology.breadth_first_search(source)
	tree_h = topology.height(source)
	for i in range(len(topology.get_edge_states())):
		va, vb, state = topology.get_edge(i)
		ha = heights[topology.get_vertex_index(va)][1]
		hb = heights[topology.get_vertex_index(vb)][1]
		p = MAX_PROB if max(ha, hb)/tree_h > MAX_PROB else max(ha, hb)/tree_h
		probabilities.append(p)
	return probabilities


def draw(probability = 0.5):
	return random() < probability


def next_binary(binary):
	''' Returns the binary next to the provided 'binary'

	The provide 'binary' must be reversed against the natural sense of reading.
	This function updates the provided 'binary' to the next number and return
	None.

	Parameters
	----------
	binary : list
		A list representing a binary number
	
	Returns
	-------
	list
		A list representing the binary next to the provided 'binary'
	'''

	if binary != []:
		i = 0
		while binary[i] == 1:
			binary[i] = 0
			i += 1
			if i == len(binary):
				binary.append(1)
				return
		binary[i] = 1
	else:
		binary.append(0)


def value_of_solution(solution, net):
	''' Returns the value of the solution in the objective function

	This function has the same role that 'tools.objective_function' function,
	but this function doesn't depends on 'Topology' objects.

	Parameters
	----------
	solution : list
		A solution to be verified in the objective function.
	net : pandapower.auxiliary.pandapowerNet
		The pandapower net representing the network model.
	
	Returns
	-------
	int
		The value of provided 'solution' in the objective function.
	'''

	make_switch_operations(solution, net)
	return len(net.bus) - len(list(pp.topology.unsupplied_buses(net)))


def format_solution(solution, net):
	''' Returns a 'solution' with the same length than 'net.switch'

	Parameters
	----------
	solution : list
		The solution to be formated.
	net : pandapower.auxiliary.pandapowerNet
		The pandapower net representing the network model.
	
	Returns
	-------
	list
		The formated solution according the 'net.switch' length.
	'''

	sol = solution.copy()
	if len(sol) < len(net.switch):
		return sol + [0 for _ in range(len(sol), len(net.switch))]
	else:
		return sol