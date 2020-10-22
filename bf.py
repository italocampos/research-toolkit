'''
Brute Force Module
------------------

This file implements the Brute Force algorithm to the modeled problem in the
research.

@author: Italo Campos

Functions
---------
- run : The function that runs the Brute Force algorithm.
'''

from util import tools, models
import color, pandapower as pp


def run():
    ''' Runs the Tabu Search

    Returns
    -------
    list
        A list with dicts containing the results and the parameters for each
        step of the loop. The dicts has the following form:
        {'time': float, # The time elapsed
        'best': list, # The best solution found
        'total_i': int, # The total iterations
        'i_best': int, # The iteration of the best solution
        'fault': list, # The list with the fault points
        'i_local': int, # The amout of loops of the lcal search
        'itm': int, # The loops for reset the search with ITM
        'max_i': # The max loops for stop the search
        }
    '''

    # Defines the bridge lines of the model
    bridges = [0, 1]

    # Defines the network model used in the search
    net = models.network10bus()

    # Defining the initial solution
    solution = [1]

    # The list with the optimal solutions found
    optimal_solutions = list()

    # The first best solution found
    best = solution.copy()

    # MAIN LOOP ---------------------------------------------------------------
    while len(solution) <= len(net.switch):
        # If the solution has the brige lines opened, then it is null
        pass

        # =====
        # Removing cycles
        '''
        for i in range(len(local_search)):
            top.set_edge_states(local_search[i])
            for cycle in top.cycles(source, search = 'bfs'):
                #print(color.magenta('    The topology has cycles. Fixing it...'))
                top.deactivate_edge(top.get_edge_index(cycle[0], cycle[1]))
                # Update the solution removing its cycles
                local_search[i] = top.get_edge_states()
        
        #print('  Running the power flow...')
        valid_solutions = list()
        for solution in local_search:
            # Setting the solution in the network switching
            top.set_edge_states(solution)
            tools.make_switch_operations(top.get_edge_states(), net)
            try:
                # Running powerflow
                pp.runpp(net)

                # Checking voltage constraints
                for index, voltage in enumerate(net.res_bus['vm_pu'], start=0):
                    if abs(1 - voltage) > v_variation: # out of the voltage constraints
                        #print(color.magenta('    Bus out of voltage contraints. Fixing it...'))
                        bus = top.get_vertex_name(index)
                        for adjacent in top.get_adjacent(bus):
                            top.deactivate_edge(top.get_edge_index(bus, adjacent))
                
                # Passing the topology alterations to the network
                tools.make_switch_operations(top.get_edge_states(), net)

                # Running the power flow again
                pp.runpp(net)
                
                # Checking current constraints
                for index, current in enumerate(net.res_line['loading_percent'], start=0):
                    if current > 100 * (1 + i_variation): # out of the current constraints
                        #print(color.magenta('    Line out of current limits. Fixing it...'))
                        top.deactivate_edge(index)

                # Saving the generated solution in the valid solution list
                valid_solutions.append(top.get_edge_states())

            except(pp.powerflow.LoadflowNotConverged):
                print(color.red('  ### ERROR: Power flow not converged. Ignoring the solution.'))
                continue
        '''
        # =====