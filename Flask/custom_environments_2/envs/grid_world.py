import numpy as np
# import shapely.geometry
# import shapely.wkt
# import geopandas as gpd
# import matplotlib.pyplot as plt
import pygame


import gymnasium as gym
from gymnasium import spaces


def generate_grid(shape, grid_rng, start_target_rng):

    num_x = shape[1]
    num_y = shape[0]

    y, x = np.indices(shape)
    grid = np.clip(
        grid_rng.normal(loc=0, scale=1, size=shape) + x%2,
        a_min = 0,
        a_max = 1
        )
    
    start = np.zeros((shape), dtype=np.int8)
    sy, sx = start_target_rng.integers(0, num_y), start_target_rng.integers(0, num_x)
    start[sy, sx] = 1

    end = np.zeros((shape), dtype=np.int8)
    ey, ex = start_target_rng.integers(0, num_y), start_target_rng.integers(0, num_x)
    end[ey, ex] = 1

    while np.array_equal(start, end):
        end = np.zeros((shape), dtype=np.int8)
        ey, ex = start_target_rng.integers(0, num_y), start_target_rng.integers(0, num_x)
        end[ey, ex] = 1

    grid[ey, ex] = 0

    return grid.astype(np.float32), start, end

def generate_rgb(grid, end):

    y, x = grid.shape
    a = grid.reshape((y, x, 1))
    rgb = np.full((y, x, 3), [1, 0, 0], dtype=float)*a + (1-a)
    # rgb[start.astype(bool)] = [0,0,1]
    rgb[end.astype(bool)] = [0,1,0]
    rgb *= 255

    return rgb.astype(int)

def concat_observation(state_dictionary):
    arrays = [arr for arr in state_dictionary.values()]
    return np.concatenate(arrays, axis=0)


class GridWorldEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 5}

    def __init__(self, render_mode=None, shape=(10,10)):
        self.shape = shape  # The size of the square grid
        num_grids = shape[0]*shape[1]
        self.rng = None
        # self.window_size = 512  # The size of the PyGame window

        # Observations are dictionaries with the agent's and the target's 
        # location. Each location is encoded as an element of 
        # {0, ..., `size`}^2, i.e. MultiDiscrete([size, size]).
        # self.observation_space = spaces.Box(
        #     low=0, 
        #     high=1, 
        #     shape=(size[0]*size[1],)
        #     )

        # self.observation_space = spaces.Dict(
        #     {
        #         'grid': spaces.Box(low=0, high=1, shape=(num_grids,), dtype=np.float32),
        #         'agent': spaces.Box(low=0, high=1, shape=(num_grids,), dtype=np.int8),
        #         'target': spaces.Box(low=0, high=1, shape=(num_grids,), dtype=np.int8)
        #     }
        # )

        self.observation_space = spaces.Box(low=0, high=1, shape=(num_grids*3,), dtype=np.float32)

        # We have 4 actions, corresponding to "right", "up", "left", "down"
        self.action_space = spaces.Discrete(4)

        """
        The following dictionary maps abstract actions from `self.action_space` to
        the direction we will walk in if that action is taken.
        I.e. 0 corresponds to "right", 1 to "up" etc.
        """
        self._action_to_direction = {
            0: np.array([1, 0]), # Down
            1: np.array([0, 1]), # Right
            2: np.array([-1, 0]), # Left
            3: np.array([0, -1]), # Up
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

    # def _generate_plot(self):
    #     fig, ax = plt.subplots(figsize=(6,6))
    #     ax.axis('off')
    #     ax.margins(0.01)
    #     grids = self.data['grids']
    #     points = self.data['points']
    #     current = self.data['current']
    #     end = self.data['end']
        
    #     grids.plot(ax=ax, color=grids['reward'], edgecolor='black', linewidth=2)
    #     current.plot(ax=ax, color='blue', markersize=40)
    #     end.plot(ax=ax, color='green', markersize=40)

    #     w,h = fig.canvas.get_width_height()
    #     buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    #     buf = buf.reshape(w, h)
        
    #     return buf

    def _get_obs(self):
        """
        Get observation from the environment.

        This is not mandatory and can also be defined in the environment's step
        and reset member methods.
        """
        observation = {
            'grid': self.grid.flatten(),
            'agent': self.current.flatten(),
            'target': self.target.flatten()
        }
        return concat_observation(observation)
    
    def _get_info(self):
        """
        Return auxillary information about the environment, in this case the
        manhattan distance of the agent from the goal.
        """
        info = {
            'target': self._target_location,
            'agent': self._agent_location
        }

        return info

    def reset(self, seed=None, grid_seed=None, start_target_seed=None, options=None):
        """
        Reset the environment to initial state.
        
        This must return an observation and auxillary information about the 
        game.
        """

        # Uses the same rng each time the env is reset, so will give same series
        # of env
        # if self.rng is None:
        #     self.rng = np.random.default_rng(seed=seed)

        # Uses a new rng each time so state is always the same
        self.grid_rng = np.random.default_rng(seed=grid_seed)
        self.start_target_rng = np.random.default_rng(seed=start_target_seed)
            
        # Generate random grid
        self.grid, self.start, self.target = generate_grid(
            self.shape, 
            grid_rng=self.grid_rng,
            start_target_rng=self.start_target_rng
            )

        # Define the agent and target coordinates from arrays
        self._agent_location = np.array(np.where(self.start > 0)).flatten()
        self._target_location = np.array(np.where(self.target > 0)).flatten()

        ay = self._agent_location[0]
        ax = self._agent_location[1]
        ty = self._target_location[0]
        tx = self._target_location[1]

        self._initial_distance_target = np.sqrt((ax-tx)**2 + (ay-ty)**2)


        # Define the current location of the agent as starting location
        self.current = self.start.copy().astype(np.int8)

        # Generate a RGB image for rendering
        self.img = generate_rgb(self.grid, self.target)

        # Get observation for agent
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

        if np.any(self._agent_location + direction > np.array(self.shape)-1):
            out_bounds_reward = -10
        else:
            out_bounds_reward = 0

        # We use `np.clip` to make sure we don't leave the grid
        self._agent_location = np.clip(
            self._agent_location + direction, 0, np.array(self.shape) - 1
        )

        ay = self._agent_location[0]
        ax = self._agent_location[1]
        ty = self._target_location[0]
        tx = self._target_location[1]

        distance_to_target = np.sqrt((ax-tx)**2 + (ay-ty)**2)

        self.current = np.zeros(self.grid.shape, dtype=np.int8)
        self.current[ay, ax] = 1

        # An episode is done if the agent has reached the target
        terminated = np.array_equal(self._agent_location, self._target_location)

        if terminated:
            reward = 100

        else:
            euclidean_reward = -(distance_to_target/self._initial_distance_target)
            cost_reward = -self.grid[ay, ax]
            movement_reward = -1
            reward = euclidean_reward + cost_reward + movement_reward + out_bounds_reward

        # reward = 1 if terminated else 0  # Binary sparse rewards
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, False, info
    


    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()


    def _render_frame(self):

        self.display_img = np.transpose(self.img, axes=(1,0,2))
        wx = self.display_img.shape[0]
        wy = self.display_img.shape[1]
        wr = wx/wy

        if wr > 1:
            self.window_size = (int(500*wr), 500) # window size x,y
            self.pix_grid_size = self.window_size[1]/wy

        else:
            self.window_size = (500, int(500*(1/wr)))
            self.pix_grid_size = self.window_size[0]/wx
        

        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(self.window_size)


        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface(self.window_size)
        surface = pygame.surfarray.make_surface(self.display_img)
        surface = pygame.transform.scale(surface, self.window_size)  # Scaled a bit.

        canvas.blit(surface, (0, 0))

        center = (self._agent_location[::-1] + 0.5)*self.pix_grid_size
        radius = self.pix_grid_size / 3


        pygame.draw.circle(
                surface=canvas,
                color=(0, 0, 255),
                center=center,
                radius=radius, 
            )
        # clock.tick(60)

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

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])

        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )
        
    def close(self):
        """
        Close any open resources

        This method is not required for a gym environment but in this case it is
        good to close the pygame window if 
        """
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
