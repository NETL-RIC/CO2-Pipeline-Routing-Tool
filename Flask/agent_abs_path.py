""" This version of agent.py uses absolute path imports so it can work from the 
Flask/backendml/grid directory, to work with ben's original code.

The normal agent.py uses relative imports because it will be ran as a module from the
Flask directory
"""

import os.path
import sys

import numpy as np
from pathlib import Path
import torch
import torch.nn as nn
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
import gymnasium as gym

import grid_world as _
from grid_world.envs.grid_world_env_v6 import GridWorldEnv_v6
from resnet.models import ResNet


# from PIL import Image
# from time import time
# from skimage.transform import resize, rescale 
# import os
# import matplotlib.pyplot as plt

def ml_least_cost_path():
    """ Single function to perform all route-creating code, returns route as list object
    """
    ml_warpper = MLWrapper()
    start = (254, 560)
    dest = (267, 538)

    res = ml_warpper.route(start, dest)

    route = res['route']
    return route

def fix_pathing(input_path):
    """ Converts relative paths to absolute paths

    Joins absolute location of script itself with provided path.
    Will only work if input_path is a relative path to absolute script location
    """
    return os.path.join(os.path.realpath(os.path.dirname(__file__)), os.path.normpath(input_path))
    
def nomrmalize(arr, high=1, low=0):
    norm = (high-low)*(arr - arr.min())/(arr.max() - arr.min()) + low
    return norm
class CostSurface:
    """
    A class for manipulating cost surfaces in both coordinates systems
    """

    def __init__(self):
        self.obs_size = 112
        self.local_regional_ratio = 6/3
        self.local_national_ratio = 6
        self.pad_width = 136

    def load_rasters(self, raster_dir):
        """
        Loads processed rasters arrays.

        This method should only be used to load arrays which have
        alreasd
        """
        if raster_dir is None:
            self.path = Path(fix_pathing('./cost_surfaces/10km_112nat_336reg_672loc/'))

        else:
            # raster_dir = Path(os.path.abspath(os.path.join('./grid/', raster_dir)))
            raster_dir = Path(fix_pathing(raster_dir))

        self.national = np.load(raster_dir.joinpath('national.npy'))
        self.regional = np.load(raster_dir.joinpath('regional.npy'))
        self.local = np.load(raster_dir.joinpath('local.npy'))
        self.no_go = np.load(raster_dir.joinpath('no_go.npy'))

    def __process_raster(self, path):

        raise NotImplementedError('This functionality should not be used at the time')
        self.path = Path(path)

    def to_game_coordiantes(self, y_coor, x_coor):

        # Remove clipped portions
        y_coor -= 75
        x_coor -= 350

        # Add the padding
        y_coor += self.pad_width
        x_coor += self.pad_width

        return y_coor, x_coor

    
    def from_game_coordiantes(self, y_coor, x_coor):
        
        # Remove the padding
        y_coor -= self.pad_width
        x_coor -= self.pad_width

        # Add the clipped portions
        y_coor += 75
        x_coor += 350

        return y_coor, x_coor


class PPOAgent:
    """
    A class to represent trained RL agents.
    """

    def load_model(self, model_path):
        if model_path is None:
            #model_path = fix_pathing('./trained_model/model.pt')
            model_path = ('./trained_model/model_scripted.pt')
        self.model = torch.load(model_path)
    
    def _start_env(self, cost_surface, start, target, rgb_array=False):
        """
        Start a gym environment

        Arguments:
            cost_surface (CostSurface) : The cost surface manager class
            start (tuple) : The start location of the agent (y-coor, x-coor)
            target (tuple) : The target location (y-coor, x-coor)
        """
        self.env_config = {
            'env': 'grid_world/GridWorld-v6', # Custom gym env version
            'size': 112, # Observation image size (112x112)
            'max_distance': None, # Max distance agent can start from target
            'start': start, # The agent start location
            'target': target, # The target location
            'distance_goal': 10, # Proximity of agent to target required for episode termination
            'obs_radius': 5, # Radius of circle on obs to represent agent/target
            'render_mode': None, # For viewing the agent in real time or playback
            'national': cost_surface.national, # National raster (112x112)
            'regional': cost_surface.regional, # Regional raster (336x336)
            'local': cost_surface.local, # Local raster (672x672)
            'no_go': cost_surface.no_go, # The no-go raster
            'max_steps': 1000 # maximum number of agent steps in an episode
            }
        
        if rgb_array:
            self.env_config['render_mode'] = 'rgb_array'

        self.env = gym.make(self.env_config['env'], env_config=self.env_config)
    
    def route(self, cost_surface, start, target, return_images=False):

        observation_images = []
        org_coor = []
        terminated = False
        truncated = False

        self._start_env(cost_surface, start, target, rgb_array=return_images)
        observation, info = self.env.reset()
        org_coor.append(cost_surface.from_game_coordiantes(*info['agent'][-1]))

        if return_images:
            observation_images.append(self.env.render())

        while not terminated and not truncated:

            with torch.no_grad():
                results = self.model(
                    input_dict={'obs': torch.from_numpy(np.expand_dims(observation, axis=0)), 'is_training':False},
                    state=[torch.tensor(0)],   # dummy value
                    seq_lens=torch.tensor(0),  # dummy value
                )

            action = results[0].argmax().item()
            observation, reward, terminated, truncated, info = self.env.step(action)
            org_coor.append(cost_surface.from_game_coordiantes(*info['agent'][-1]))

            # tensor = transformer(observation).unsqueeze(0)

            if return_images:
                observation_images.append(self.env.render())


        self.env.close()
        # fps=480
        # duration = 1000/fps # duration in ms
        # imageio.mimsave('/home/ben/gym/grid/gifs/ppo-0280.gif', observation_images, duration=duration)

        if return_images:
            return observation_images
        
        return {'route': org_coor, 'images':observation_images}


class MLWrapper:

    def __init__(self, raster_dir='./cost_surfaces/10km_112nat_336reg_672loc/', model_path='./trained_model/model.pt'):
        raster_dir = fix_pathing(raster_dir)
        model_path = fix_pathing(model_path)
        self.cost_surface = CostSurface()
        self.cost_surface.load_rasters(raster_dir)
        self.agent = PPOAgent()
        self.agent.load_model(model_path)


    def route(self, start, target):
        game_start = self.cost_surface.to_game_coordiantes(*start)
        game_target = self.cost_surface.to_game_coordiantes(*target)
        results = self.agent.route(
            self.cost_surface,
            game_start,
            game_target
        )

        return results




class CustomTorchModel(TorchModelV2, nn.Module):
    
    def __init__(self, obs_space, action_space, num_outputs, model_config, name):
        super(CustomTorchModel, self).__init__(obs_space, action_space, num_outputs, model_config, name)
        nn.Module.__init__(self)

        self.encoder = ResNet(in_channels=9, num_blocks=3)
        self.policy_fc = nn.Linear(in_features=256, out_features=action_space.n)
        self.value_fc = nn.Linear(in_features=256, out_features=1)
    
    def forward(self, input_dict, state, seq_lens):
        # is_training = input_dict.is_training
        observation = input_dict['obs']

        assert isinstance(observation, torch.Tensor)
        # assert observation.shape[]
        # tensor = torch.tensor(observation).to(torch.float)
        # tensor = torch.tensor(observation, dtype=torch.float)
        # tensor = torch.moveaxis(observation, -1, 1)
        encoded_obs = self.encoder(observation)
        logits = self.policy_fc(encoded_obs)
        self.state_value = self.value_fc(encoded_obs)

        return logits, []
    
    def value_function(self):
        return self.state_value.squeeze(-1)