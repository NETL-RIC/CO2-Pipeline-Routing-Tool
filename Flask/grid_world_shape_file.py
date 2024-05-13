import numpy as np
import shapely.geometry
import shapely.wkt
import geopandas as gpd
import matplotlib.pyplot as plt


import gymnasium as gym
from gymnasium import spaces


def grid_color(x, rng):
    """
    Create random colors (weights/rewards) for the environment grid
    """
    if rng.uniform() < 0.05:
        return (1,0,0,1)
    
    if x%2 == 0:
        a = rng.normal(loc=0, scale=1)
    
    else:
        a = rng.normal(loc=1, scale=1)


    a = np.clip(a, 0, 1)
    return (1,0,0,a)

def generate_grid(y_grids, x_grids, rng):
    """
    Create a random grid world.
    """
    names = []
    polygons = []
    centroids = []
    colors = []

    for x in range(x_grids):
        for y in range(y_grids):
            # Bottom left
            sw = str(x) + ' ' + str(y)
            # Top left
            nw = str(x) + ' ' + str(y + 1)
            # Top right
            ne = str(x+1) + ' ' + str(y + 1)
            # Bottom right
            se = str(x+1) + ' ' + str(y)
            
            poly = shapely.wkt.loads('POLYGON (({}, {}, {}, {}, {}))'.format(sw, nw, ne, se, sw))
            polygons.append(poly)

            names.append(str(x) + ',' + str(y))
            centroids.append(poly.centroid)
            color = grid_color(x, rng)
            colors.append(color)
    

    grids = gpd.GeoDataFrame(
        {
            'name': names,
            'reward': colors,
            'geometry': polygons
        }
    )

    points = gpd.GeoDataFrame(
        {
            'name': names,
            'geometry': centroids
        }
    )

    start_loc = str(rng.integers(0, 3)) + ',' + str(rng.integers(0,3))
    end_loc = str(rng.integers(x_grids-3, x_grids)) + ',' + str(rng.integers(y_grids-3, y_grids))

    start = points.loc[points['name']==str(start_loc)]
    current = points.loc[points['name']==str(start_loc)]
    end = points.loc[points['name']==str(end_loc)]

    env_data = {
        'start': start,
        'current': current,
        'end': end,
        'grids': grids,
        'points': points
    }

    return env_data


class GridWorldEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, render_mode=None, size=(10,10)):
        self.size = size  # The size of the square grid
        self.window_size = 512  # The size of the PyGame window

        # Observations are dictionaries with the agent's and the target's 
        # location. Each location is encoded as an element of 
        # {0, ..., `size`}^2, i.e. MultiDiscrete([size, size]).
        self.observation_space = spaces.Box(
            low=0, 
            high=1, 
            shape=(size[0]*100, size[1]*100)
            )

        # We have 4 actions, corresponding to "right", "up", "left", "down"
        self.action_space = spaces.Discrete(4)

        """
        The following dictionary maps abstract actions from `self.action_space` to
        the direction we will walk in if that action is taken.
        I.e. 0 corresponds to "right", 1 to "up" etc.
        """
        self._action_to_direction = {
            0: np.array([1, 0]),
            1: np.array([0, 1]),
            2: np.array([-1, 0]),
            3: np.array([0, -1]),
        }

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        """
        If human-rendering is used, `self.window` will be a reference
        to the window that we draw to. `self.clock` will be a clock that is used
        to ensure that the environment is rendered at the correct framerate in
        human-mode. They will remain `None` until human-mode is used for the
        first time.
        """
        self.window = None
        self.clock = None

    def _generate_plot(self):
        fig, ax = plt.subplots(figsize=(6,6))
        ax.axis('off')
        ax.margins(0.01)
        grids = self.data['grids']
        points = self.data['points']
        current = self.data['current']
        end = self.data['end']
        
        grids.plot(ax=ax, color=grids['reward'], edgecolor='black', linewidth=2)
        current.plot(ax=ax, color='blue', markersize=40)
        end.plot(ax=ax, color='green', markersize=40)

        w,h = fig.canvas.get_width_height()
        buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        buf = buf.reshape(w, h)
        
        return buf

    def _get_obs(self):
        """
        Get observation from the environment.

        This is not mandatory and can also be defined in the environment's step
        and reset member methods.
        """

        fig = super()._generate_plot()


        return self.data
    
    def _get_info(self):
        """
        Return auxillary information about the environment, in this case the
        manhattan distance of the agent from the goal.
        """
        return 'No info yet, maybe send agent distance to goal?'
    
    def reset(self, seed=None, options=None):
        """
        Reset the environment to initial state.
        
        This must return an observation and auxillary information about the 
        game.
        """

        self.rng = np.random.default_rng(seed)
        self.data = generate_grid(*self.size, self.rng)

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info
    
    def step(self, action):
        """
        Move the environment one time step depending on agent's action.
        """
        # Map the action (element of {0,1,2,3}) to the direction we walk in
        direction = self._action_to_direction[action]
        # We use `np.clip` to make sure we don't leave the grid
        self._agent_location = np.clip(
            self._agent_location + direction, 0, self.size - 1
        )
        # An episode is done if the agent has reached the target
        terminated = np.array_equal(self._agent_location, self._target_location)
        reward = 1 if terminated else 0  # Binary sparse rewards
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, False, info
    


    def render(self):
        # if self.render_mode == "rgb_array":
        #     return self._render_frame()
        pass

    def _render_frame(self):
        pass
        # if self.window is None and self.render_mode == "human":
        #     pygame.init()
        #     pygame.display.init()
        #     self.window = pygame.display.set_mode(
        #         (self.window_size, self.window_size)
        #     )
        # if self.clock is None and self.render_mode == "human":
        #     self.clock = pygame.time.Clock()

        # canvas = pygame.Surface((self.window_size, self.window_size))
        # canvas.fill((255, 255, 255))
        # pix_square_size = (
        #     self.window_size / self.size
        # )  # The size of a single grid square in pixels

        # # First we draw the target
        # pygame.draw.rect(
        #     canvas,
        #     (255, 0, 0),
        #     pygame.Rect(
        #         pix_square_size * self._target_location,
        #         (pix_square_size, pix_square_size),
        #     ),
        # )
        # # Now we draw the agent
        # pygame.draw.circle(
        #     canvas,
        #     (0, 0, 255),
        #     (self._agent_location + 0.5) * pix_square_size,
        #     pix_square_size / 3,
        # )

        # # Finally, add some gridlines
        # for x in range(self.size + 1):
        #     pygame.draw.line(
        #         canvas,
        #         0,
        #         (0, pix_square_size * x),
        #         (self.window_size, pix_square_size * x),
        #         width=3,
        #     )
        #     pygame.draw.line(
        #         canvas,
        #         0,
        #         (pix_square_size * x, 0),
        #         (pix_square_size * x, self.window_size),
        #         width=3,
        #     )

        # if self.render_mode == "human":
        #     # The following line copies our drawings from `canvas` to the visible window
        #     self.window.blit(canvas, canvas.get_rect())
        #     pygame.event.pump()
        #     pygame.display.update()

        #     # We need to ensure that human-rendering occurs at the predefined framerate.
        #     # The following line will automatically add a delay to keep the framerate stable.
        #     self.clock.tick(self.metadata["render_fps"])
        # else:  # rgb_array
        #     return np.transpose(
        #         np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
        #     )
        
    def close(self):
        """
        Close any open resources

        This method is not required for a gym environment but in this case it is
        good to close the pygame window if 
        """
        # if self.window is not None:
        #     pygame.display.quit()
        #     pygame.quit()
        pass