import numpy as np
import pygame
import gymnasium as gym
from gymnasium import spaces
from skimage.transform import resize


"""
This version returns local and global images to the agent.
"""

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


def generate_locations(cost_surface, start, target, rng, max_distance=9999):

    while start is None:
        shape = cost_surface.shape
        y = rng.integers(0, shape[0], 1)[0]
        x = rng.integers(0, shape[1], 1)[0]
        if cost_surface[y, x] == -1:
            continue
        if cost_surface[y, x] == 0:
            continue
        else:
            start = (y, x)
    
    while target is None:
        shape = cost_surface.shape
        y = rng.integers(
            max(0, start[0]-max_distance), 
            min(shape[0], start[0] + max_distance),
            1
        )
        y = y[0]

        x = rng.integers(
            max(0, start[1]-max_distance), 
            min(shape[1], start[1] + max_distance),
            1
        )
        x = x[0]


        if cost_surface[y, x] == -1:
            continue
        if cost_surface[y, x] == 0:
            continue
        else:
            target = (y, x)

    return start, target

def draw_circle(img, center, radius):
    """
    Modifies the specified img in place by drawing a circle on it.
    """
    y, x = np.mgrid[:img.shape[0], :img.shape[1]]
    circle = (y-center[0])**2 + (x-center[1])**2
    img[circle < radius**2] = 255

    return img


class GridWorldEnv_v5(gym.Env):
    """
    Args:
        cost_surface (str | numpy.ndarry): The padded cost curface as array or file path
        size (int): Final width and height of an observation across all resolutions (national, regional and local)
        render_mode (str): How the environment should be rendered, None, human or rgb_array
        start (tuple): Array line coordinates of agent start location; based upon cost surface dimensions
        target (tuple): Array line coordinates of target location; based upon cost surface dimensions
        max_distance (int): Furthest possible starting position of agent to goal in either dimension
        distance_goal (int): How close (in pixels) the agent must be to the target to terminate episode
        obs_radius (int): Radius of circle drawn on observations to represent agent and target
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 5}

    def __init__(
            self, 
            cost_surface, 
            size=224, 
            render_mode=None, 
            start=None, 
            target=None, 
            max_distance=9999,
            distance_goal=10,
            obs_radius=10
            ):
        
        self.rng = None

        if isinstance(cost_surface, str):
            self.cost_surface = np.load(cost_surface)
        elif isinstance(cost_surface, np.ndarray):
            self.cost_surface = cost_surface

        if cost_surface.shape[0] != cost_surface.shape[1]:
            raise Warning('The first and second dimension of the cost surface does not match')
        
        self.info = {
            'agent': [],
            'target': []
        }
        self.size = size
        self.window_size = 500
        self.start = start
        self.target = target
        self.max_distance = max_distance
        self.distance_goal = distance_goal
        self.obs_radius = obs_radius

        resolution = 5
        self.national_resolution = size/self.cost_surface.shape[0]
        self.regional_resolution = size*resolution/self.cost_surface.shape[0]
        self.local_resolution = 1

        if start is not None and cost_surface[start[0], start[1]] == 0:
            raise ValueError('start location must be inside continental US')
        
        if target is not None and cost_surface[target[0], target[1]] == 0:
            raise ValueError('target location must be inside continental US')
        
        # Save original surface for no go area and out of bounds area
        self.no_go = self.cost_surface.copy()

        # Set no go areas to high value
        self.cost_surface[self.cost_surface==-1] = 255

        self.national_cost = resize(self.cost_surface, (self.size, self.size))
        self.national_cost = self.national_cost.astype(np.uint8)

        self.regional_cost = resize(
            self.cost_surface, (self.size*resolution, self.size*resolution)
            )
        self.regional = self.regional_cost.astype(np.uint8)

        # Determines the observation shapes required for gym env meta data
        self.obs_shape = (3, self.size, self.size)
        
        # Determines PyGame window size for human viewing
        wy = self.obs_shape[1]
        wx = self.obs_shape[2]*3
        wr = wx/wy

        if wr > 1:
            # window size x,y
            self.window_shape = (int(self.window_size*wr), self.window_size)

        else:
            self.window_shape = (self.window_size, int(self.window_size*(1/wr)))

        # National regional and local observations are images of the same shape
        self.observation_space = spaces.Dict(
            {
                'national': spaces.Box(low=0, high=255, shape=self.obs_shape, dtype=np.uint8),
                'regional': spaces.Box(low=0, high=255, shape=self.obs_shape, dtype=np.uint8),
                'local': spaces.Box(low=0, high=255, shape=self.obs_shape, dtype=np.uint8),
            }
        )

        # We have 8 actions, corresponding to "right", "up", "left", "down", etc.
        self.action_space = spaces.Discrete(8)

        """
        The following dictionary maps abstract actions from `self.action_space` to
        the direction we will walk in if that action is taken.
        I.e. 0 corresponds to "right", 1 to "up" etc.
        """
        self._action_to_direction = {
            0: np.array([-1, 0]),  # Up
            1: np.array([-1, 1]),  # Up/Right
            2: np.array([0, 1]),   # Right
            3: np.array([1, 1]),   # Down/Right
            4: np.array([1, 0]),   # Down
            5: np.array([1, -1]),  # Down/Left
            6: np.array([0, -1]),  # Left
            7: np.array([-1, -1]), # Up/Left
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

    
    def _get_local_obs(self, cost_surface, resolution):

        # Handle even and odd sized national/regional observations
        xo = 0
        yo = 0

        if self.obs_shape[1]%2 == 1:
            yo = 1

        if self.obs_shape[2]%2 == 1:
            xo = 1

        # Find where to slice cost surface for regional observation
        y_size = self.obs_shape[1]
        ys = int(self._agent_location[0]*resolution) - (y_size//2)
        ye = int(self._agent_location[0]*resolution) + (y_size//2) + yo

        x_size = self.obs_shape[2]
        xs = int(self._agent_location[1]*resolution) - (x_size//2)
        xe = int(self._agent_location[1]*resolution) + (x_size//2) + xo

        # print(ys, ye)
        # print(xs, xe)

        # Determine where to draw agent and target location on regional obs
        target_center = (
            self._target_location[0]*resolution - ys, 
            self._target_location[1]*resolution - xs
            )
        
        agent_center = (
            self._agent_location[0]*resolution - ys, 
            self._agent_location[1]*resolution - xs
            )
        
        # Build local observation
        obs = np.zeros(self.obs_shape, dtype=np.uint8)

        # Set red channel equal to slice of the given cost surface
        obs[0,:,:] = cost_surface[ys:ye, xs:xe].copy()

        # Set green channel to target location
        obs[1,:,:] = draw_circle(
            np.zeros((self.size, self.size)), 
            center=target_center,
            radius=self.obs_radius
            )
        
        # Set blue channel to agent location
        obs[2,:,:] = draw_circle(
            np.zeros((self.size, self.size)), 
            center=agent_center,
            radius=self.obs_radius
            )
        
        return obs


    def _get_obs(self):
        """
        Get observation from the environment.

        This is not mandatory and can also be defined in the environment's step
        and reset member methods.
        """
        
        # Build national observation
        self.national_obs = np.zeros(self.obs_shape, dtype=np.uint8)
        agent_center = (self._agent_location*self.national_resolution).astype(int)
        target_center = (self._target_location*self.national_resolution).astype(int)
        # print(center)
        # print('agent location {}'.format(self._agent_location))
        # print('national center {}'.format(center))
        # print('Agent Location {}'.format(self._agent_location))
        # print('Scale Factor {}'.format(self.scale_factor))
        # print('Center {}'.format(center))

        # Set red channel equal to cost surface
        self.national_obs[0,:,:] = self.national_cost.copy()

        # Set green channel to agent location
        self.national_obs[1,:,:] = draw_circle(
            np.zeros((self.size, self.size)), 
            center=target_center,
            radius=self.obs_radius
            )

        # Set blue channel to agent location
        self.national_obs[2,:,:] = draw_circle(
            np.zeros((self.size, self.size)), 
            center=agent_center,
            radius=self.obs_radius
            )
        
        # Save the observations as instance attributes for rendering
        self.regional_obs = self._get_local_obs(self.regional_cost, self.regional_resolution)
        self.local_obs = self._get_local_obs(self.cost_surface, self.local_resolution)

        observation = {
            'national': self.national_obs,
            'regional': self.regional_obs,
            'local': self.local_obs
        }

        return observation
    
    def _get_info(self):
        """
        Return auxillary information about the environment, in this case the
        manhattan distance of the agent from the goal.
        """

        self.info['agent'].append(self._agent_location.tolist())
        self.info['target'].append(self._target_location.tolist())

        return self.info

    def reset(self, seed=None, start_target_seed=None, options=None):
        """
        Reset the environment to initial state.
        
        This must return an observation and auxillary information about the 
        game.
        """

        # Uses the same rng each time the env is reset, so will give same series
        # of env
        # if self.rng is None:
        #     self.rng = np.random.default_rng(seed=seed)

        # Uses a new rng each time so state is always the same if one is passed
        rng = np.random.default_rng(seed=start_target_seed)

        self.ep_start, self.ep_target = generate_locations(
            self.no_go,
            self.start,
            self.target,
            rng,
            self.max_distance
            )
        
        self._agent_location = np.array(self.ep_start)
        self._target_location = np.array(self.ep_target)

        # print(self._agent_location.shape)
        # print(self._target_location.shape)
        
        # self.img = self.cost_surface.copy()
        # self.img = draw_circle(self.img, center=self.start, radius=50)

        # Define the agent and target coordinates from arrays
        # self._agent_location = np.array(np.where(self.start > 0)).flatten()
        # self._target_location = np.array(np.where(self.target > 0)).flatten()

        ay = self.ep_start[0]
        ax = self.ep_start[1]
        ty = self.ep_target[0]
        tx = self.ep_target[1]

        self._initial_distance_target = np.sqrt((ax-tx)**2 + (ay-ty)**2)

        # Define the current location of the agent as starting location
        # self.current = self.start.copy().astype(np.int8)

        # Generate a RGB image for rendering
        # self.img = generate_rgb(self.grid, self.target)

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
        new_location = self._agent_location + direction

        # Check if agent out of bounds
        if self.cost_surface[new_location[0], new_location[1]] == 0:
            out_bounds_reward = -1

        else:
            out_bounds_reward = 0
            self._agent_location += direction

        previous_location = self._agent_location
        # We use `np.clip` to make sure we don't leave the grid
        # self._agent_location = np.clip(
        #     self._agent_location + direction, 0, np.array(self.shape) - 1
        # )

        previous_location = self._agent_location

        ay = self._agent_location[0]
        ax = self._agent_location[1]
        py = previous_location[0]
        px = previous_location[1]
        ty = self._target_location[0]
        tx = self._target_location[1]

        distance_to_target = np.sqrt((ax-tx)**2 + (ay-ty)**2)
        previous_distance = np.sqrt((px-tx)**2 + (py-ty)**2)

        if distance_to_target < previous_distance:
            euclidean_reward = 1
        elif distance_to_target == previous_distance:
            euclidean_reward = 0
        else:
            euclidean_reward = -1

        # self.current = np.zeros(self.grid.shape, dtype=np.int8)
        # self.current[ay, ax] = 1

        # An episode is done if the agent has reached the target
        terminated = np.array_equal(self._agent_location, self._target_location)
        terminated = distance_to_target <= self.distance_goal

        if terminated:
            reward = 100

        else:
            # euclidean_reward = -(distance_to_target/self._initial_distance_target)
            cost_reward = -self.cost_surface[ay, ax]*(2/255)
            movement_reward = -1
            reward = euclidean_reward + cost_reward + movement_reward #+ out_bounds_reward

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

        # if self.render_mode == "human":

        raw_image = np.concatenate(
            (self.national_obs, self.regional_obs, self.local_obs), axis=2
            )
        
        rgb_array = np.moveaxis(raw_image, 0, -1)

        human_mode_array = np.transpose(rgb_array, axes=(1,0,2))

        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(self.window_shape)

        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        if self.render_mode == "human":

            # Create surface to display images
            # canvas = pygame.Surface(self.window_shape)

            # Create a surface from an array (image)
            surface = pygame.surfarray.make_surface(human_mode_array)

            # Scale the surface/image
            surface = pygame.transform.scale(surface, self.window_shape)  # Scaled a bit.

            # Place the surface array (image) on the blank surface (canvas)
            # canvas.blit(surface, (0, 0))

            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(surface, surface.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])

        # In this version we always need to return the image array regardless of 
        # render mode since the image is used as an observation
        return rgb_array
    
    def close(self):
        """
        Close any open resources

        This method is not required for a gym environment but in this case it is
        good to close the pygame window if 
        """
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
