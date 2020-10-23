'''
Tabu Search Module
------------------

This file implements the Tabu Search to the modeled problem in the
research.

@author: Italo Campos

Functions
---------
- run : The function that runs the Tabu Search.
'''

from util import tools, models, TabuList
import time, color, pandapower as pp


def run(loops = 10):
	''' Runs the Tabu Search

	Parameters
	----------
	loops : int, optional
		The number of loops that the Tabu Search should execute. Default is 10.
	
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
		'i_local': int, # The amout of loops of the local search
		'itm': int, # The loops for reset the search with ITM
		'max_i': # The max loops for stop the search
		}
	'''

	results = list()
		
	for step in range(loops):

		print(color.yellow('\n\nLOOP #%d ---------------------------------------------' % (step + 1), 'bold'))

		# Extra variables
		elapsed_time = 0
		

		# DEFINING GLOBAL VARIABLES AND PARAMETERS --------------

		# For single-sourced models, use the lines of code below:
		# -------------------------------------------------------
		# Getting the test model
		#net = models.network33bus()

		# Getting the power source name (it works only for one-sourced nets)
		#source = net.bus['name'][int(net.ext_grid['bus'])]

		# Getting the initial topology
		#top = tools.create_topology(net)
		# Getting the indexes of the bridge lines between the source (bus0) and
		# the first fork
		#bridges = tools.bridge_lines(top, source)

		# For multiple-sourced models, use the lines of code below:
		# ---------------------------------------------------------
		net = models.network16bus()

		# Defines the power source name
		source = 'bus1'

		# Creating a multi-sourced topology
		top = tools.create_multisourced_topology(net)

		# Adding the abstract edges to the topology
		top.add_abstract_edge('bus0', 'bus1')
		top.add_abstract_edge('bus1', 'bus2')

		# Defining manually the bridge lines according to the model
		bridges = [0, 4, 9]
		# ---------------------------------------------------------

		# The variable that controls the loop
		stop = False

		# Creating the tabu-list
		tabu = TabuList(max_length = int(0.2 * len(net.line))) #int(20% of the number of lines)

		# Getting the probability vector for the initial state of the net
		prob_vector = tools.get_lines_probability(top, source)

		# Defining the fault points
		fault = [4]
		#fault = [top.get_edge_index('bus2', 'bus3')]
		#fault = [top.get_edge_index('bus5', 'bus6')]
		#fault = [top.get_edge_index('bus3', 'bus4'), top.get_edge_index('bus26', 'bus27'), top.get_edge_index('bus9', 'bus10')]
		#fault = [top.get_edge_index('bus18', 'bus19'), top.get_edge_index('bus10', 'bus11')]
		#fault = [top.get_edge_index('bus4', 'bus5'), top.get_edge_index('bus8', 'bus9'), top.get_edge_index('bus20', 'bus21'), top.get_edge_index('bus15', 'bus16')]

		# Applying the fault points
		tools.set_faults(top, fault)

		# Limit for voltage variation
		#v_variation = 0.18
		v_variation = 0.05

		# Limit for current variation
		i_variation = 0.05

		# Best solution (starting with the initial solution)
		best = top.get_edge_states()

		# Number of solutions generated per iteration
		n_solutions = int(0.2 * len(net.line))

		# Iteration number (starting with 0)
		iteration = 1

		# The IT memory
		memory = [0 for _ in range(len(net.line))]

		# Stores the last iteration that improve the best solution
		improved = iteration

		# Limiar of frequence that determines if a component will stay in the
		# solution after the reset of the search by the ITM
		frequence = 0.6

		# A flag that indicates if the search was restarted once
		reset = False

		# The number of max iterations before reset the search with IT memory
		max_reset = 25

		# Maximum limit of iterations without improvement of the best solution
		# found (termination criteria)
		max_i = 50

		# Maximum iterations to local search
		max_local = 10
		# -------------------------------------------------------

		# MAIN LOOP ---------------------------------------------
		print('Starting loop...')
		print('Initial solution:', top.get_edge_states())
		# Stores the initial time
		begin = time.time()

		while not stop:

			# List of generated neighbors (solutions)
			neighbors = list()

			# The iteration-selected solution
			selected = top.get_edge_states()

			# Neighborhood generation ---------------------------
			print(color.blue('Iteration #%d' % iteration))
			print('Generating neighbors...')
			# Making `n_solutions` neihgbors
			for k in range(n_solutions):
				print('  Generating neighbor %d/%d' % (k+1, n_solutions))
				# Generating the neighbor components
				sol = list()
				for i in range(len(net.line)):
					c = selected[i]
					if c == 1:
						if tools.draw(prob_vector[i]):
							c = 0
					else:
						if tools.draw(0.5):
							c = 1
					# Making solution
					sol.append(c)
				
				# Local search
				#print('  Performing local search...')
				local_search = [sol] + [tools.swap_1_0(sol.copy()) for _ in range(max_local)]
				
				# Activating the bridge lines and removing fault points
				for i in range(len(local_search)):
					local_search[i] = tools.set_value(local_search[i], bridges, 1)
					local_search[i] = tools.set_value(local_search[i], fault, 0)
				
				#print('  Removing cycles...')
				# Removing cycles
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
						print(color.red('  ### Power flow not converged. Ignoring the solution.'))
						continue

				# Getting the best of local search
				if valid_solutions != []:
					neighbors.append(tools.best_of(valid_solutions, top, source))
			# ---------------------------------------------------

			# Neighbor selection --------------------------------
			print('Selecting the neighbor...')
			if neighbors != []:
				best_of_iteration = tools.best_of(neighbors, top, source)
				while len(neighbors) != 0:
					selected = tools.best_of(neighbors, top, source)
					neighbors.remove(selected)
					if tabu.is_tabu(selected):
						print('  TABU: This solution is in tabu list. Applying aspiration criteria...')
						# Aspiration criteria
						if not tools.draw(0.3):
							print('  Result: REFUSED')
							continue
						print('  Result: ACCEPTED')
						if len(neighbors) == 0:
							print('  All solutions is in tabu list. Selecting the best found.')
							selected = best_of_iteration.copy()
							tabu.add(best_of_iteration)
							top.set_edge_states(best_of_iteration)
							break
					tabu.add(selected.copy())
					top.set_edge_states(selected)
					print('  Solution selected.')
					break
			else:
				# Case no valid solutions were generated, select the same
				# previous iteration solution
				top.set_edge_states(selected)
			
			# Comparing the selected solution with the best solution found
			#print('  Comparing the selected solution with the best solution found...')
			if best != []:
				sel = tools.best_of([selected, best], top, source)
				if sel != best:
					print(color.green('IMPROVEMENT: Improving solution at iteration %d.' % iteration, 'bold'))
					best = sel.copy()
					improved = iteration
			else:
				best = selected.copy()
			# ---------------------------------------------------

			# Intermediate-term memory --------------------------
			print('Saving the solution in the intermediate-term memory...')
			for i in range(len(selected)):
				memory[i] += selected[i]
			if not reset and iteration - improved >= max_reset:
				print(color.yellow('RESETING SEARCH -------------------'))
				print('Reseting the search with intermediate-term memory.')
				reset = True
				mcc = list()
				for value in memory:
					if value/iteration > frequence:
						mcc.append(1)
					else:
						mcc.append(0)
				# Activating the bridge lines and removing fault points
				mcc = tools.set_value(mcc, bridges, 1)
				mcc = tools.set_value(mcc, fault, 0)
				print('Most common components:', mcc)
				selected = mcc.copy()
				top.set_edge_states(selected)
			# ---------------------------------------------------

			# Checking termination criteria ---------------------
			#print('Selected:', selected)
			#print('Best:', best)
			iteration += 1
			if iteration - improved > max_i:
				stop = True
				elapsed_time = time.time() - begin
				print(color.yellow('Elapsed time: %f s' % elapsed_time))
				print(color.yellow('Best solution found: %s' % best, 'bold'))
			# ---------------------------------------------------

		# -------------------------------------------------------
		results.append({
			'time': elapsed_time,
			'best': best,
			'total_i': iteration,
			'i_best': improved,
			'fault': [(top.get_edge(e)[0], top.get_edge(e)[1]) for e in fault],
			'i_local': max_local,
			'itm': max_reset,
			'max_i': max_i,
			})

	return results


if __name__ == '__main__':
	print(run())