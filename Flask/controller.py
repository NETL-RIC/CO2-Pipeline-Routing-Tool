import sys

import fiona

from rout import leastCostPath
from agent import ml_least_cost_path
# from backendml.grid import agent


class PipelineController():
    """ Passes line data between processing modules and the api module
    """
    def __init__(self, x,y):
        self.start = x
        self.end = y

    def ml_run(self):
        """Machine-learning informed routing logic
        """
        return ml_least_cost_path(self.start, self.end)

    def run(self):
        """Old routing logic - not machine learning
        """
        leastCostPath(self.start[0], self.start[1], self.end[0], self.end[1], 'ras_071323_4alpha.tif', 'result.tif')
        print('done')

