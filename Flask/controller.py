"""
controller
Controller class for executing the machine learning code
"""
import sys
import fiona

from .rout import leastCostPath
from .mc_agent import least_cost_path_ml

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
