import sys

import fiona

from rout import leastCostPath
from mc_agent import least_cost_path_ml
# from backendml.grid import agent


class PipelineController():
    """ Passes line data between processing modules and the api module
    """
    def __init__(self, x,y, mode):
        self.start = x
        self.dest = y
        self.mode = mode

    def ml_run(self):
        """Machine-learning informed routing logic
        """
        return least_cost_path_ml(self.start, self.dest, self.mode)

    def run(self):
        """Old routing logic - not machine learning
        """
        leastCostPath(self.start[0], self.start[1], self.end[0], self.end[1], 'ras_071323_4alpha.tif', 'result.tif')
        print('done')

