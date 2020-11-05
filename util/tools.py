''' This file contains some functionalities to support the development
of the TS'''

from .topology import Topology, MultiSourcedTopology
from random import randint, random
import copy, pandapower as pp

# Defining contants for the functions

# The value for the max probability for the probability vector
MAX_PROB = 0.7


def create_topology(pp_net):
    ''' Creates a topology for a model

    The topology created is a graph that implements some graph functions (like
    cycles detection, conectivity, searches, and more).

    Parameters
    ----------
    pp_net : pandapower.auxiliary.pandapowerNet
        The pandapower net from which the topology will be generated.
    
    Returns
    -------
    Topology
        The 'Topology' object for the provided 'net'.
    '''

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
    ''' Creates a topology for multi-sourced models

    The topology created is a topology with support to abstract edges. This
    aproach is used to avoid cyclic tipologies to multi-sourced models.

    Parameters
    ----------
    pp_net : pandapower.auxiliary.pandapowerNet
        The pandapower net from which the topology will be generated.
    '''

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
    ''' Swaps the values of two indexes in the provided 'line_vector'

    Parameters
    ----------
    index_a : int
        The first index to be swapped.
    index_b : int
        The second index to be swapped.
    line_vector : list
        The list where the values of 'index_a' and 'index_b' will be swapped.
    
    Returns
    -------
    list
        The swapped list.
    '''

    lv = line_vector.copy()
    lv[index_a], lv[index_b] = lv[index_b], lv[index_a]
    return lv


def objective_function(topology, root):
    ''' Returns the value of the 'topology' in the objective function

    The objective function is defined as:
        Max(x) = x1 + x2 + ... + xi,
        where xi are the buses recovered by in the topology.
    
    Parameters
    ----------
    topology : .tolopogy.Topology
        The topology object with the solution to be evaluated.
    root : str
        The name of the root vertex in 'topology'.
    
    Returns
    -------
    int
        The value of the provided 'topology' in the objective function.
    '''
    
    return len(topology.connected_vertices(root))


def best_of(solutions, topology, source):
    ''' Returns the best solution among 'solutions'

    Parameters
    ----------
    solutions : list
        The list of solutions to be compared among them.
    topology : .tolopogy.Topology
        The topology object corresponding the itens of 'solutions'.
    root : str
        The name of the root vertex in 'topology'.
    
    Returns
    -------
    list
        The best solution among 'solutions'.
    '''

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


def bridges_closed(solution, bridges):
    ''' Checks if the 'solution' has the 'bridge' lines all closed

    Parameters
    ----------
    solution : list
        The solution to be checked.
    bridges : list
        A list with the indexes of the bridge lines (must be less than
        len(solution)).
    
    Returns
    -------
    bool
        The bool that indicates if all the 'bridge' lines has the value '1' in
        'solution'.
    
    Raises
    ------
    Exception
        In case of len(briges) > len(solution)
    '''

    if len(bridges) <= len(solution):
        for bridge in bridges:
            if solution[bridge] != 1:
                return False
        return True
    else:
        raise(Exception("len(bridges) must be less than len(solution)"))


def failed_lines_opened(solution, failed_lines):
    ''' Checks if the 'solution' has the 'failed_lines' all opened

    Parameters
    ----------
    solution : list
        The solution to be checked.
    failed_lines : list
        A list with the indexes of the faulted lines (must be less than
        len(solution)).
    
    Returns
    -------
    bool
        The bool that indicates if all the 'bridge' lines has the value '1' in
        'solution'.

    Raises
    ------
    Exception
        In case of len(failed_lines) > len(solution)
    '''

    if len(failed_lines) <= len(solution):
        for line in failed_lines:
            if solution[line] != 0:
                return False
        return True
    else:
        raise(Exception("len(failed_lines) must be less than len(solution)"))


def validate_voltages(solution, net):
    ''' Validates a solution against the voltage constraints

    Parameters
    ----------
    solution : list
        The solution to be validated.
    net : pandapower.auxiliary.pandapowerNet
        The pandapower net representing the network model.
    
    Returns
    -------
    bool
        The bool that indicates if the 'solution' is valid or not.
    '''

    if len(solution) == 11:
        v_variation = 0.05
    elif len(solution) == 16:
        v_variation = 0.05
    elif len(solution) == 37:
        v_variation = 0.18
    elif len(solution) == 132:
        v_variation = 0.15
    else:
        raise Exception('Solution not supported.')

    make_switch_operations(solution, net)
    try:
        pp.runpp(net)
        for voltage in net.res_bus['vm_pu']:
            if abs(1 - voltage) > v_variation: # out of the voltage constraints
                return False
    except(pp.powerflow.LoadflowNotConverged):
        print('  ### Power flow not converged. Ignoring the solution.')
        return False
    return True


def validate_current(solution, net):
    ''' Validates a solution against the current constraints

    Parameters
    ----------
    solution : list
        The solution to be validated.
    net : pandapower.auxiliary.pandapowerNet
        The pandapower net representing the network model.
    
    Returns
    -------
    bool
        The bool that indicates if the 'solution' is valid or not.
    '''

    # Defining the current varition
    i_variation = 0.00
    
    make_switch_operations(solution, net)
    try:
        pp.runpp(net)
        for current in net.res_line['loading_percent']:
            if current > 100 * (1 + i_variation): # out of the current constraints
                return False
    except(pp.powerflow.LoadflowNotConverged):
        print('  ### Power flow not converged. Ignoring the solution.')
        return False
    return True


def binary_to_decimal(binary):
    ''' Converts a binary (under list format) to decimal

    Parameters
    ----------
    binary : list
        The binary number to be converted.
    
    Returns
    -------
    int
        The decimal correspondent to 'binary'.
    '''

    decimal = 0
    hold = 0
    i = 0
    exp = len(binary) - 1
    while i < len(binary):
        x = int(binary[i])
        quot= 2**exp
        hold = x*quot
        i += 1
        exp -= 1
        decimal = decimal + hold
    return decimal