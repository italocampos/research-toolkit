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

    # > Defines the bridge lines of the model
    bridges = [0, 9]
    #bridges = [0]

    # > Defines the network model used in the search
    net = models.network16bus()

    # > Creating the topology correspondent to the model
    top = tools.create_multisourced_topology(net) # for 10-bus and 16-bus
    #top = tools.create_topology(net) # for 33-bus and 119-bus

    # > Creating abstract lines (for multi-sourced models)
    # top.add_abstract_edge('bus0', 'bus1') # for 10-bus
    top.add_abstract_edge('bus0', 'bus1') # for 16-bus
    top.add_abstract_edge('bus1', 'bus2') # for 16-bus

    # > Defining the source for graph searches
    source = 'bus1'

    # > Defining the initial solution
    solution = [1]

    # > Defining the failed lines
    failed_lines = [4]

    # > The list with the optimal solutions found
    optimal_solutions = list()

    # > The value of the best solution(s) found
    # >> Passing the evaluated solution to the topology
    top.set_edge_states(tools.format_solution(solution, net))
    # >> Getting the value of the solution in the objective function
    best_value = tools.objective_function(top, source)

    # A variable to help the calculation of the progress of the search
    max_solution = tools.binary_to_decimal([1 for _ in net.switch.values])


    # MAIN LOOP ---------------------------------------------------------------
    while len(solution) <= len(net.switch):
        # > Gets the formated solution
        sol = tools.format_solution(solution, net)
        # > Passing the evaluated solution to the topology
        top.set_edge_states(sol)

        # > Checks if the solution matches the bridge and the failed lines
        if tools.bridges_closed(sol, bridges) and tools.failed_lines_opened(sol, failed_lines):
            # > Gets the value of the solution of this iteration
            sol_value = tools.objective_function(top, source)
            # > If a new best solution is found, set it as new best solution
            if sol_value > best_value:
                # > Testing the feasibility of the solution
                if (top.cycles(source) == []) and tools.validate_voltages(sol, net) and tools.validate_current(sol, net):
                    print(color.green('A new best solution was found!', 'bold'))
                    optimal_solutions.clear()
                    optimal_solutions.append(sol.copy())
                    best_value = sol_value
            elif sol_value == best_value:
                # > Testing the feasibility of the solution
                if (top.cycles(source) == []) and tools.validate_voltages(sol, net) and tools.validate_current(sol, net):
                    #print(color.blue('An other solution has the same value of the best solution. Saving it...',))
                    optimal_solutions.append(sol.copy())
        
        # > Printing the progress of the method
        sol.reverse()
        current_solution = tools.binary_to_decimal(sol)
        if current_solution % round(max_solution * 0.05) == 0:
            print(color.yellow('> Method progress: {percent}%...'.format(
                percent = round(current_solution/max_solution*100)
            )))                

        tools.next_binary(solution)
    
    return optimal_solutions


if __name__ == "__main__":
    print(run())