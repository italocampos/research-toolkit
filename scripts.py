'''
Analyzing module
----------------

This module validates and analyzes the results of TS.

@author: @italocampos

Dependencies
    This module depends on the module 'evaluation' in
    'smash/analysis-tools/evaluation.py'. To refer this file, see the
    repository in https://gitlab.com/italocampos/smash-py
'''

import evaluation as ev, color, util

default_topologies = {
    '10-bus': [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0],
    '16-bus': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    '33-bus': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
    '119-bus': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
}

def evaluate_solutions(results):
    ''' Evaluates the solutions returned by TS

    Parameters
    ----------
    results : list
        A list with the results of the TS. This list is a list of dicts under
        the following form:
        {
            'time': float, # The time wasted in the search
            'best': list # The best solution found in the search,
            'total_i': int, # The number of the final iteration 
            'i_best': int, # The iteration where the best solution was found
            'fault': list, # The list with the faulted lines
            'i_local': int, # The parameter of the max local search
            'itm': int, # The parameter of the max iteration to reset the TS
            'max_i': int, # The parameter of the max iteration set in the TS
        }
    
    Raises
    ------
    Exception
        In case the solution don't match any supported network model
    '''

    for i, res in enumerate(results):
        print(color.blue('\nSEARCH #%d ------------' % (i + 1)))
        validation = ev.validate(res['best'])
        if validation:
            if len(res['best']) == len(default_topologies['10-bus']):
                default = default_topologies['10-bus'].copy()
            elif len(res['best']) == len(default_topologies['16-bus']):
                default = default_topologies['16-bus'].copy()
            elif len(res['best']) == len(default_topologies['33-bus']):
                default = default_topologies['33-bus'].copy()
            elif len(res['best']) == len(default_topologies['119-bus']):
                default = default_topologies['119-bus'].copy()
            else:
                raise(Exception('No such model to this solution.'))
            
            faulted = default.copy()
            for f in res['fault']:
                faulted[f] = 0

            value = ev.value(res['best'])

            zeros = list()
            for j, element in enumerate(default):
                if element == 0:
                    zeros.append(j)
            
            ones = list()
            for j, element in enumerate(default):
                if element == 1:
                    ones.append(j)
            
            opened_switches = list()
            for j, element in enumerate(res['best']):
                if element == 0 and j not in zeros:
                    opened_switches.append(j)
            
            closed_switches = list()
            for j, element in enumerate(res['best']):
                if element == 1 and j not in ones:
                    closed_switches.append(j)
            
            print(color.green('VALIDATION: %s' % validation, 'b'))
            print('VALUE:', value)
            print('NAB:', len(ev.unsupplied_buses(faulted)))
            print('NRB:', value - (ev.value(default) - len(ev.unsupplied_buses(faulted))))
            print('OPENED SW:', opened_switches)
            print('CLOSED SW:', closed_switches)
            print('TIME:', res['time'])
        else:
            print(color.red('VALIDATION: %s' % validation, 'b'))


def select_best(results):
    ''' Selects and returns the best solution among the 'results'

    Parameters
    ----------
    results : list
        A list with the results of the TS. This list is a list of dicts under
        the following form:
        {
            'time': float, # The time wasted in the search
            'best': list # The best solution found in the search,
            'total_i': int, # The number of the final iteration 
            'i_best': int, # The iteration where the best solution was found
            'fault': list, # The list with the faulted lines
            'i_local': int, # The parameter of the max local search
            'itm': int, # The parameter of the max iteration to reset the TS
            'max_i': int, # The parameter of the max iteration set in the TS
        }

    Returns
    -------
    tuple
        A pair (a, b) with a being the index of the best solution, and b being
        the value of this solution.

    Raises
    ------
    Exception
        In case the solution don't match any supported network model
    '''

    res = results.copy()
    initial = res.pop(0)
    top.set_edge_states(initial['best'])
    value = objective_function(top, source)
    index = 0
    for i, r in enumerate(res, start=1):
        top.set_edge_states(r['best'])
        v = objective_function(top, source)
        if v > value:
            value = v
            index = i
    return index, value


def show_all_values(results):
    ''' Show the values of all the solutions in 'results'

    Parameters
    ----------
    results : list
        A list with the results of the TS. This list is a list of dicts under
        the following form:
        {
            'time': float, # The time wasted in the search
            'best': list # The best solution found in the search,
            'total_i': int, # The number of the final iteration 
            'i_best': int, # The iteration where the best solution was found
            'fault': list, # The list with the faulted lines
            'i_local': int, # The parameter of the max local search
            'itm': int, # The parameter of the max iteration to reset the TS
            'max_i': int, # The parameter of the max iteration set in the TS
        }
    '''
    for i, r in enumerate(results):
        top.set_edge_states(r['best'])
        print('Solution: %d; value: %d' % (i, objective_function(top, source)))