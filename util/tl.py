''' This class models a simple Tabu-List.
'''

class TabuList:
	def __init__(self, max_length, equality_rate = 0.8):
		if max_length > 0:
			self.max_length = max_length
			self._solutions = list()
			self.equality_rate = equality_rate
		else:
			raise(Exception('The length of a tabu list must be bigger than 0.'))


	@property
	def length(self):
		return len(self._solutions)


	def add(self, solution):
		if self.length >= self.max_length:
			self._solutions.remove(self._solutions[0])
		self._solutions.append(solution)


	def is_tabu(self, solution):
		for sol in self._solutions:
			equals = list()
			for i in range(len(solution)):
				equals.append(int(sol[i] == solution[i]))
			if sum(equals)/len(sol) >= self.equality_rate:
				return True
		return False