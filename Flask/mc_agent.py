import multiprocessing as mp
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from IPython import display

from extra_utils import resource_path

def least_cost_path_ml(start, dest):
    """Simple wrapper function to return just the list that composes the ML-generated line
    """
    wrapper = MLWrapper()
    res = wrapper.route(start, dest)
    return res[0]
    # lucy_route_cntr = res[0]
    # lucy_route = lucy_route_cntr['route']
    # return lucy_route

def normalize(arr, high=1, low=0):
    norm = (high-low)*(arr - arr.min())/(arr.max() - arr.min()) + low
    return norm

def draw_circle(img, center, radius):
    """
    Modifies the specified img in place by drawing a circle on it.
    """
    y, x = np.mgrid[:img.shape[0], :img.shape[1]]
    circle = (y-center[0])**2 + (x-center[1])**2
    img[circle < radius**2] = 1

    return img

def visualize(cost_surface, agent, target, locations=[], path=[], radius=5):
    
    # Build observation
    shape = (3, *cost_surface.shape)
    obs = np.zeros(shape, dtype=np.float32)

    # Set red channel equal to the given cost surface
    obs[0,:,:] = cost_surface.copy()

    # Set green channel to target location
    obs[1,:,:] = draw_circle(
        np.zeros((cost_surface.shape), dtype=np.float32), 
        center=target,
        radius=radius
        )
    
    # Set blue channel to agent location
    obs[2,:,:] = draw_circle(
        np.zeros((cost_surface.shape), dtype=np.float32), 
        center=agent,
        radius=radius
        )
    
    # Record path through the surface
    if path:
        all_y, all_x = zip(*path)
        obs[:, all_y, all_x] = 1

    elif locations:
        all_y, all_x = zip(*locations)
        obs[:, all_y, all_x] = 1
        
    return obs
    
def plot_path(obs, done=False):
    
    fig = plt.figure(1, figsize=(20,20))
    plt.clf()

    ax1 = fig.add_subplot(1, 1, 1) # rows, cols, pos
    ax1.set_title('Current Path')
    # ax1.set_xlabel('Iteration')
    # ax1.set_ylabel('Mean Reward')
    ax1.imshow(obs)

    if not done:
        display.display(plt.gcf())
        display.clear_output(wait=True)

    else:
        display.display(plt.gcf())


class CostSurface:
    """
    A class for manipulating cost surfaces in both coordinates systems
    """

    def __init__(self):
        self.cost = None
        self.no_go = None

    def load_rasters(self, raster_dir):
        """
        Loads processed rasters arrays.

        This method should only be used to load arrays which have already been
        preprocessed.
        """
        assert raster_dir is not None, 'Must provide raster directory'
        raster_dir = Path(raster_dir)

        self.cost = np.load(raster_dir.joinpath('cost.npy'))
        self.no_go = np.load(raster_dir.joinpath('no_go.npy'))

    def __process_raster(self, path):

        raise NotImplementedError('This functionality should not be used at the time')
        self.path = Path(path)


class Node:

    def __init__(self, location, parent, reward, path):
        self.location = location
        self.parent = parent
        self.children = []
        self.selections = 0
        self.reward = reward # Reward for the parent node selecting this node
        self.value = 0       # Expected discounted returns when in this state
        self.path = path
        self.action_to_direction = {
            0: np.array([-1, 0]),  # Up
            1: np.array([-1, 1]),  # Up/Right
            2: np.array([0, 1]),   # Right
            3: np.array([1, 1]),   # Down/Right
            4: np.array([1, 0]),   # Down
            5: np.array([1, -1]),  # Down/Left
            6: np.array([0, -1]),  # Left
            7: np.array([-1, -1]), # Up/Left
        }

    def calculate_eucldian_reward(self, new_location, target_location):

        ay = new_location[0]
        ax = new_location[1]
        py = self.location[0]
        px = self.location[1]
        ty = target_location[0]
        tx = target_location[1]

        # Calculate distance to target
        distance_to_target = np.sqrt((ax-tx)**2 + (ay-ty)**2)
        previous_distance = np.sqrt((px-tx)**2 + (py-ty)**2)

        # subtract constant to prevent postive rewards, otherwise agent wants to
        # keep moving to keep gaining rewards
        euclidean_reward = previous_distance - distance_to_target - 1.42

        return euclidean_reward

    def select(self, c=np.sqrt(2)):
        """
        Select child node to investigate using UCB
        """
        high_score = -np.inf
        selected_child = None
        for child in self.children:
            ucb = child.reward + child.value + c*np.sqrt(np.log(self.selections)/(child.selections + 0.001))

            if ucb > high_score:
                high_score = ucb
                selected_child = child

        return selected_child


    def expand(self, cost_surface, target_location):
        rewards = []
        for a in self.action_to_direction.values():
            
            child_location = a + self.location
            location_hash_key = str(child_location[0]).zfill(3) \
                                + ',' + str(child_location[1]).zfill(3)

            # Do not allow path to cross with itself
            if location_hash_key in self.path:
                continue

            cost_reward = -cost_surface[child_location[0], child_location[1]]

            # Do not allow out of bounds moves
            if cost_reward == 1:
                continue

            if np.array_equal(child_location, target_location):
                reward = 100

            else:
                euclidian_reward = self.calculate_eucldian_reward(child_location, target_location)
                reward = euclidian_reward + cost_reward*2
            
            path = self.path.copy()
            path[location_hash_key] = True
            self.children.append(Node(child_location, self, reward, path))
            rewards.append(reward)
            
        self.value = np.mean(rewards)
        if not self.children:
            raise ValueError('Unable to find pipline route')
    
    def backpropagate(self, discount=0.98):
        self.parent.value += (self.value*discount - self.parent.value)/self.parent.selections
        if self.parent.parent is not None:
            self.parent.backpropagate()
            self.parent.selections += 1


class MCTree:

    def __init__(self, cost_surface, start, target):
        self.cost_surface = cost_surface
        self.target = target
        path = {str(start[0]).zfill(3) + ',' + str(start[1]).zfill(3): True}
        self.root = Node(location=start, parent=None, reward=None, path=path)

    def traverse(self, node):
        locations = [node.location.tolist()]
        for child in node.children:
            locations.extend(self.traverse(child))
        return locations   

    def prune(self, new_root):
        if isinstance(new_root, str):
            next_root_found = False
            for child in self.root.children:
                location = str(child.location[0]).zfill(3) + ',' + str(child.location[1]).zfill(3)

                if new_root == location:
                    new_root = child
                    next_root_found = True
                    break
            if not next_root_found:
                child_locations = [child.location for child in self.root.children]
                raise ValueError('Unable to find the child node at {} from following locations: {}'.format(new_root, child_locations))
            #assert next_root_found, 'Unable to find the child node at {}'.format(new_root)

        else:
            assert isinstance(new_root, Node), 'new_root must be str or Node'

        assert isinstance(new_root, Node)
        assert not np.array_equal(new_root.location, self.target), 'Root node cannot be terminal node'
        del self.root
        self.root = new_root
        self.root.parent = None

def search(root, target, num_trajectories, cost_surface, c=np.sqrt(2)):
    """
    Search a MCTree by selecting the next node, expanding leaf nodes and
    back-propagating values.
    """

    for i in range(num_trajectories):
        root.selections += 1
        current_node = root

        # Run until a leaf node is encountered
        while current_node.children:
            
            # Select new child node to investigate using UCB
            current_node = current_node.select(c=c)

            # Check if new node is terminal
            if np.array_equal(current_node.location, target):
                break
        
        if not np.array_equal(current_node.location, target):
            # Expand non-terminal nodes
            current_node.expand(cost_surface, target)
        
        if not current_node is root:
            current_node.backpropagate()
            current_node.selections += 1

    max_value = -np.inf
    most_selections = 0
    next_node = None

    for child in root.children:

        # First check for terminal node
        if np.array_equal(child.location, target):
            next_node = child
            break

        if child.selections > most_selections:
            most_selections = child.selections
            next_node = child

    return root, next_node


class MCAgent:
    def __init__(self, trajectories, num_workers=None):
        
        self.num_workers = num_workers
        if num_workers is None:
            self.num_workers = mp.cpu_count()//2
        self.trajectories = trajectories
        if num_workers > 1:
            self.c = np.linspace(0, 5, self.num_workers)
        else:
            self.c = [np.sqrt(2)]

    def route(self, cost_surface, start, target, max_steps=1000, show_viz=False):
        forest = [MCTree(cost_surface, start, target) for _ in range(self.num_workers)]
        path = [start]
        
        for _ in range(max_steps):
            args = [(tree.root, target, self.trajectories, cost_surface, c) for tree,c in zip(forest, self.c)]
            
            with Pool(self.num_workers) as pool:
                results = pool.starmap(search, args)
                votes = {}

            for (root, node), tree in zip(results, forest):
                y = str(node.location[0]).zfill(3)
                x = str(node.location[1]).zfill(3)
                key = y + ',' + x
                votes[key] = votes.get(key, 0) + 1
                tree.root = root
            
            next_location_str = max(votes, key=votes.get)
            next_location_arr = np.array([int(next_location_str.split(',')[0]), int(next_location_str.split(',')[1])])
            path.append(next_location_arr.tolist())

            if show_viz:
                obs = visualize(cost_surface, next_location_arr, target, path=path)
                plot_path(np.moveaxis(obs, 0, -1))

            if np.array_equal(next_location_arr, target):
                break

            for tree in forest:
                tree.prune(next_location_str)

        return path


class MLWrapper:

    def __init__(self, trajectories=100, num_workers=1, raster_dir=resource_path('cost_surfaces/raw_cost_10km_aea')):
        self.cost_surface = CostSurface()
        self.cost_surface.load_rasters(raster_dir)
        self.agent = MCAgent(trajectories=trajectories, num_workers=num_workers)

    def route(self, start, target, show_viz=False):
        print("In mc_agent.MLWrapper.route:") 
        print(f"start is {start}")
        print(f"target is {target}")

        surface = self.cost_surface.cost
        no_go = self.cost_surface.no_go

        if start[0]<275:
            assert target[0]<275 , 'Start location in AL but target location is not'
            region = 'al'

        else:
            assert target[0]>275 , 'Start location in US but target location is not'
            region = 'us'
        
        path = self.agent.route(
            surface,
            list(start),
            list(target),
            show_viz=show_viz
        )

        lucy_path = path

        if lucy_path:
            print("Path generated")
        else:
            print("Error with lucy_path in mc_agent")
        return lucy_path, path
