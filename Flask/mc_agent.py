import multiprocessing as mp
from multiprocessing import Pool
from pathlib import Path

import rasterio
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from IPython import display

from extra_utils import resource_path

def least_cost_path_ml(start, dest, mode):
    """
    Simple wrapper function to return just the list that composes the 
    ML-generated line.

    Args:
        start (tuple): The starting location.
        dest (tuple): The destination location.
        mode (str): The mode of the MLWrapper.

    Returns:
        list: The list that composes the ML-generated line.
    """
    # error checking .tifs
    try:
        wrapper = MLWrapper(mode=mode)
    except FileNotFoundError as e:
        print(e.args)

    # Get route and only return the optimized path
    res = wrapper.route(start, dest)
    return res[0]

def normalize(arr, high=1, low=0):
    """
    Normalizes the input array to a specified range.

    Args:
        arr (np.ndarray): The input array to normalize.
        high (float): The maximum value of the output array.
        low (float): The minimum value of the output array.

    Returns:
        np.ndarray: The normalized array. If all values in the input array are the same,
            returns an array of the same shape filled with the average of high and low.
    """
    # Check if all values are the same
    if arr.max() == arr.min():
        return np.full_like(arr, (high + low) / 2)
    
    # Normalize the array
    norm = (high-low)*(arr - arr.min())/(arr.max() - arr.min()) + low
    return norm

def exponential(x, degree):
    """
    Applies an exponential transformation to the input array.

    Args:
        x (np.ndarray): The input array to transform.
        degree (float): The exponent to raise the input array to.

    Returns:
        np.ndarray: The transformed array.
    """
    return x**degree

def draw_circle(img, center, radius):
    """
    Modifies the specified img in place by drawing a circle on it.

    Args:
        img (np.ndarray): The image to modify.
        center (tuple): The center of the circle.
        radius (int): The radius of the circle.

    Returns:
        np.ndarray: The modified image.
    """
    y, x = np.mgrid[:img.shape[0], :img.shape[1]]
    circle = (y-center[0])**2 + (x-center[1])**2
    img[circle < radius**2] = 1

    return img

def visualize(cost_surface, agent, target, locations=[], path=[], radius=5):
    """
    Visualizes the cost surface, agent location, target location, and path.

    Args:
        cost_surface (np.ndarray): The cost surface raster.
        agent (tuple): The agent's current location.
        target (tuple): The target location.
        locations (list): The locations to visualize.
        path (list): The path to visualize.
        radius (int): The radius of the circle in pixels.

    Returns:
        np.ndarray: The visualized image.
    """
    
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
    """
    Plots the real-time path through the cost surface when using Jupyter
    notebook cells.

    Args:
        obs (np.ndarray): The observation array.
        done (bool): Whether the path is done.
    """
    
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

def get_contiguous_area(bool_raster, min_size):
    """
    Get the contiguous areas of AL and US using connected component analysis.

    Args:
        bool_raster (np.ndarray): The boolean raster to analyze.
        min_size (int): The minimum number of connected pixels in order to be
            considered a contiguous portion of US or AL.

    Returns:
        tuple: A tuple containing the contiguous areas and the output array.
    """
    assert bool_raster.dtype == np.uint8, 'Array must have numpy.uint8 data type'
    contiguous = np.zeros(bool_raster.shape)
    number_components, output, stats, _ = cv.connectedComponentsWithStats(bool_raster, connectivity=4)

    labels = []
    for i in range(1, number_components):
        size = stats[i, -1]
        if size > min_size:
            # Labels start at value of 1
            labels.append(i)
    
    for value in labels:
        contiguous[output==value] = 1

    return contiguous, output

def find_transitions(arr):
    """
    Finds the indices where an array transitions from one value to another.

    This function can be used to determine where to crop an input raster that
    is not of the expected dimensions. Usually when this occurs the outside area
    is 0 (non valid areas) and the raster begins where the values transition to
    -1.

    Args:
        arr (np.ndarray): The input array.

    Returns:
        tuple: A tuple containing the indices of the top left corner and bottom
            right corner.
    """
    diff = np.diff(arr)
    transition_indices = np.where(diff != 0)
    y1, y2 = transition_indices[0][0], transition_indices[0][-1]
    x1, x2 = transition_indices[1][0], transition_indices[1][-1]
    return (y1+1, x1+1), (y2+1, x2+1)

class CostSurface:
    """
    A class for manipulating cost surfaces in both coordinate systems.
    
    This class handles the processing and manipulation of geographic cost 
    surfaces used for pipeline routing. It can load pre-processed rasters or 
    process raw raster files to generate normalized cost surfaces and no-go 
    areas.
    
    Attributes:
        cost (np.ndarray): The processed cost surface raster where values range
            from 0 (lowest cost) to 1 (highest cost/no-go areas).
        no_go (np.ndarray): Boolean array where True indicates areas that should
            not be traversed (out of bounds or otherwise prohibited).
    """

    def __init__(self):
        """
        Initialize the CostSurface object.
        """
        
        self.cost = None
        self.no_go = None

    def load_rasters(self, raster_dir):
        """
        Loads processed raster arrays from disk.

        This method should only be used to load arrays which have already been
        preprocessed and saved as numpy arrays.

        Args:
            raster_dir (str or Path): Directory containing the preprocessed 
                raster files. Must contain 'cost.npy' and 'no_go.npy' files.

        Raises:
            AssertionError: If raster_dir is None.
            FileNotFoundError: If the required files are not found.
        """

        assert raster_dir is not None, 'Must provide raster directory'
        raster_dir = Path(raster_dir)

        self.cost = np.load(raster_dir.joinpath('cost.npy'))
        self.no_go = np.load(raster_dir.joinpath('no_go.npy'))

    def process_raster(self, path, degree=2, no_go_cost=None, visualize=False):
        """
        Process a raw raster file into a normalized cost surface and no-go areas.

        This method performs several operations on the input raster:
        1. Crops the raster to its valid area
        2. Identifies and marks no-go areas (values < 0, non-contiguous areas)
        3. Applies user-specified exponential weighting to emphasize high-cost 
            areas
        4. Normalizes the values to 0-1 range
        5. Sets no-go areas to maximum cost or specified cost

        Args:
            path (str or Path): Path to the raw raster file to process.
            degree (float, optional): Exponent used to increase weighting of high 
                cost areas. Defaults to 2.
            no_go_cost (float, optional): Cost value to assign to no-go areas. 
                If None, uses 1 (maximum cost). Defaults to None.
            visualize (bool, optional): If True, displays visualizations of the 
                processing steps. Defaults to False.

        Raises:
            AssertionError: If the raw raster file does not exist.
        """

        path = Path(path)
        assert path.exists(), f'The raw raster file path does not exist at path ${path}'

        ds = rasterio.open(path)
        arr = ds.read(1)

        # Make a copy of the raw raster array to modify
        raster = arr.copy()

        # Set all values less than -1 to -1 to represent out of bounds/no-go
        raster[raster<-1]=-1

        # Check if the raster needs cropping by checking if corner is valid data
        if raster[0,0] != -1.0:
            # Find boundaries of valid data area
            (y1, x1), (y2, x2) = find_transitions(raster)
            raster = raster[y1:y2, x1:x2]

        else:
            (y1, x1), (y2, x2) = (0, 0), (-1, -1)

        # Reset invalid values to -1 (no-go)
        raster[raster==np.inf] = -1
        raster[raster==-np.inf] = -1
        
        # Special handling for visualization - set negative values to -inf for better display
        if arr.min() < -1 and visualize:
            arr[arr<-1] = -np.inf

        # Binary raster where 1=land (valid), 0=water/out-of-bounds (invalid)
        check_bounds = raster.copy()
        check_bounds[check_bounds>=0] = 1.0
        check_bounds[check_bounds<0] = 0.0

        # Use connected component analysis to identify islands not connected to mainland
        contiguous, _ = get_contiguous_area(check_bounds.astype(np.uint8), min_size=1000)

        # Set isolated areas to no-go
        raster[contiguous==0] = -1

        # Create boolean mask for no-go areas (True where value < 0)
        no_go = raster.copy()
        no_go[no_go>=0] = 1
        no_go[no_go<0] = 0
        no_go = np.invert(no_go.astype(bool))

        # Temporarily set no-go areas to 0 for normalization
        # (This ensures they don't affect the min/max value calculations)
        raster[raster==-1] = 0

        # Apply exponential weighting to emphasize high-cost areas
        raster = exponential(raster, degree)

        # Normalize all valid areas to 0-1 range
        raster = normalize(raster)

        # Reset no-go areas to maximum cost or user-specified value
        if no_go_cost is None:
            raster[no_go] = 1  # Set to max cost
        else:
            raster[no_go] = no_go_cost
        

        self.cost = raster
        self.no_go = no_go

        if visualize:
            fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(15,12))
            ax[0,0].imshow(arr[y1:y2, x1:x2], cmap='gray')
            ax[0,0].set_title('Original\n{}'.format(arr.shape))

            ax[0,1].imshow(contiguous, cmap='gray')
            ax[0,1].set_title('Contiguous\n{}'.format(contiguous.shape))

            ax[1,0].imshow(raster, cmap='gray')
            ax[1,0].set_title('Normalized\n{} - {}'.format(raster.shape, raster.dtype))

            ax[1,1].imshow(no_go, cmap='gray')
            ax[1,1].set_title('No Go\n{} - {}'.format(no_go.shape, no_go.dtype))

            plt.show()


class Node:
    """
    Node class for the Monte Carlo Tree Search algorithm.
    
    Each node represents a possible location in the pipeline route. Nodes form a 
    tree structure with parent-child relationships, allowing for backtracking and
    exploration of different possible routes.
    
    Attributes:
        location (np.ndarray): The (y, x) coordinates of this node on the cost surface.
        parent (Node): The parent node in the tree (None for root).
        children (list): List of child nodes.
        selections (int): Number of times this node has been selected during search.
        reward (float): The immediate reward received for selecting this node.
        value (float): The expected discounted returns from this state.
        path (dict): Dictionary of visited locations using hash keys.
        distance_factor (float): Weight for the euclidean distance component of rewards.
        is_no_go (bool): Flag indicating whether this node is marked as no-go.
        action_to_direction (dict): Mapping from action indices to direction vectors.
    """

    def __init__(self, location, parent, reward, path, distance_factor=1.0):
        """
        Initialize a Node object.
        
        Args:
            location (np.ndarray): The (y, x) coordinates of this node.
            parent (Node): The parent node (None for root).
            reward (float): The immediate reward for selecting this node.
            path (dict): Dictionary of locations already visited in this path.
            distance_factor (float, optional): Weight for euclidean distance in reward 
                calculation. Defaults to 1.0.
        """
        self.location = location
        self.parent = parent
        self.children = []
        self.selections = 0
        self.reward = reward # Reward for the parent node selecting this node
        self.value = 0       # Expected discounted returns when in this state
        self.path = path
        self.distance_factor=distance_factor
        self.is_no_go = False  # New flag to mark nodes as no-go
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

    def mark_as_no_go(self):
        """
        Mark this node as no-go to prevent revisiting.
        
        This is used when a node is determined to be a dead end or otherwise
        unsuitable for inclusion in the optimal path.
        """
        self.is_no_go = True

    def calculate_euclidean_reward(self, new_location, target_location):
        """
        Calculate the euclidean reward component for a potential new location.
        
        The reward is based on how much closer the new location is to the target
        compared to the current location. A small constant is subtracted to 
        prevent purely distance-based movement.
        
        Args:
            new_location (np.ndarray): The potential new location to evaluate.
            target_location (np.ndarray): The target destination location.
            
        Returns:
            float: The calculated euclidean reward component.
        """

        ay = new_location[0]
        ax = new_location[1]
        py = self.location[0]
        px = self.location[1]
        ty = target_location[0]
        tx = target_location[1]

        # Calculate distance to target
        distance_to_target = np.sqrt((ax-tx)**2 + (ay-ty)**2)
        previous_distance = np.sqrt((px-tx)**2 + (py-ty)**2)

        # Subtract constant 1.42 to penalize lateral movement that doesn't make sufficient progress toward target
        # This encourages more direct paths and discourages wandering behavior
        euclidean_reward = self.distance_factor*(previous_distance - distance_to_target - 1.42)

        return euclidean_reward

    def select(self, c=np.sqrt(2)):
        """
        Select a child node to investigate using Upper Confidence Bound (UCB).
        
        This implements the UCB formula for balancing exploration and exploitation:
        UCB = reward + value + c * sqrt(ln(parent_visits) / (child_visits + ε))
        
        Args:
            c (float, optional): Exploration parameter. Higher values encourage
                more exploration. Defaults to sqrt(2).
                
        Returns:
            Node or None: The selected child node with highest UCB score, or None
                if no valid children exist.
        """
        high_score = -np.inf
        selected_child = None
        for child in self.children:
            # Skip nodes marked as no-go (dead ends)
            if child.is_no_go:
                continue
                
            # UCB formula: balances exploitation (first terms) and exploration (last term)
            ucb = child.reward + child.value + c*np.sqrt(np.log(self.selections)/(child.selections + 0.001))

            if ucb > high_score:
                high_score = ucb
                selected_child = child

        return selected_child

    def expand(self, cost_surface, target_location):
        """
        Expand the current node by generating all valid child nodes.
        
        This method creates child nodes for all possible actions from the current
        location, checking for validity (not in path, not out of bounds, etc.).
        
        Args:
            cost_surface (np.ndarray): The cost surface to use for cost rewards.
            target_location (np.ndarray): The target destination.
            
        Returns:
            self: Returns the node itself after expansion.
        """
        rewards = []
        for a in self.action_to_direction.values():
            child_location = a + self.location
            location_hash_key = str(child_location[0]).zfill(3) \
                                + ',' + str(child_location[1]).zfill(3)

            # Do not allow path to cross with itself
            if location_hash_key in self.path:
                continue

            cost_reward = -cost_surface[child_location[0], child_location[1]]

            # Do not allow out of bounds moves or moves into no-go areas
            if cost_reward == 1:
                continue

            if np.array_equal(child_location, target_location):
                reward = 100
            else:
                euclidean_reward = self.calculate_euclidean_reward(child_location, target_location)
                reward = euclidean_reward + cost_reward*2
            
            path = self.path.copy()
            path[location_hash_key] = True
            child = Node(child_location, self, reward, path, self.distance_factor)
            self.children.append(child)
            rewards.append(reward)
            
        self.value = np.mean(rewards)
    
    def backpropagate(self, discount=0.98):
        """
        Backpropagate values up the tree to update parent nodes.
        
        This recursively updates the value estimates of parent nodes based on 
        the discounted value of this node.
        
        Args:
            discount (float, optional): Discount factor for future values.
                Defaults to 0.98.
        """
        self.parent.value += (self.value*discount - self.parent.value)/self.parent.selections
        if self.parent.parent is not None:
            self.parent.backpropagate()
            self.parent.selections += 1

    # def rollout(self, num_moves=100):
    #     for move in num_moves:



class MCTree:
    """
    Monte Carlo Tree Search implementation for pipeline routing.
    
    This class represents a search tree where each node corresponds to a location on the 
    cost surface. The tree is used to find the optimal path from a starting location to a 
    target location by exploring the state space using Monte Carlo Tree Search principles.
    
    Attributes:
        cost_surface (np.ndarray): The cost surface used for calculating move costs.
        target (np.ndarray): The target destination coordinates.
        distance_factor (float): Weight factor for distance in reward calculations.
        root (Node): The root node of the tree representing the starting location.
    """

    def __init__(self, cost_surface, start, target, distance_factor=1.0):
        """
        Initialize a Monte Carlo Tree.
        
        Args:
            cost_surface (np.ndarray): The cost surface used for calculating move costs.
            start (np.ndarray): The starting location coordinates.
            target (np.ndarray): The target destination coordinates.
            distance_factor (float, optional): Weight for euclidean distance in reward 
                calculation. Defaults to 1.0.
        """
        self.cost_surface = cost_surface
        self.target = target
        self.distance_factor = distance_factor
        path = {str(start[0]).zfill(3) + ',' + str(start[1]).zfill(3): True}
        self.root = Node(location=start, parent=None, reward=None, path=path, distance_factor=distance_factor)

    def traverse(self, node):
        """
        Traverse the tree starting from the given node and return all locations.
        
        This method recursively collects all locations in the subtree rooted at 
        the specified node.
        
        Args:
            node (Node): The node to start traversal from.
            
        Returns:
            list: A list of all location coordinates in the subtree.
        """
        # Traverse the tree and return the path
        locations = [node.location.tolist()]
        for child in node.children:
            locations.extend(self.traverse(child))
        return locations   

    def select_root(self, new_root):
        """
        Select a new root node without deleting parent connections.
        
        This method allows for re-rooting the tree at a different node, which is useful
        when committing to a particular path segment during search.
        
        Args:
            new_root (str or Node): Either a string representation of the location
                (format: "y,x" with 3-digit zero padding) or a Node object to become
                the new root.
                
        Raises:
            ValueError: If the specified node cannot be found or if trying to set
                the root to the target node.
            AssertionError: If new_root is not a string or Node, or if it equals the target.
        """
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

        else:
            assert isinstance(new_root, Node), 'new_root must be str or Node'

        assert isinstance(new_root, Node)
        assert not np.array_equal(new_root.location, self.target), 'Root node cannot be terminal node'
        self.root = new_root  # Simply update the root pointer without deleting anything

def search(root, target, num_trajectories, cost_surface, c=np.sqrt(2)):
    """
    Perform Monte Carlo Tree Search from a given root node.
    
    This function implements the core MCTS algorithm, consisting of:
    1. Selection: Traverse the tree from root to leaf following UCB policy
    2. Expansion: When a leaf node is reached, expand by creating child nodes
    3. Backpropagation: Update node values based on the search results
    
    The search continues until a specified number of trajectories are explored or
    a terminal state (target) is reached. Nodes that lead to dead ends are marked
    as no-go to avoid revisiting them.
    
    Args:
        root (Node): The root node to start the search from.
        target (np.ndarray): The target destination coordinates.
        num_trajectories (int): The number of search trajectories to perform.
        cost_surface (np.ndarray): The cost surface for calculating move costs.
        c (float, optional): Exploration parameter for UCB formula. Defaults to sqrt(2).
        
    Returns:
        tuple: A tuple containing (root_node, next_node) where next_node is the best
            child to move to, or (None, None) if no valid path exists.
    """

    for _ in range(num_trajectories):

        # Track visits to root for UCB calculations
        root.selections += 1
        current_node = root
        backtracked = False

        # MCTS Selection phase: traverse tree until reaching a leaf node
        while current_node.children:
            
            # Select new child node to investigate using Upper Confidence Bound (UCB)
            selected_child = current_node.select(c=c)

            # Dead end detection - if all children are no-go, mark current node as no-go too
            if selected_child is None:
                
                # Flag to indicate that the current node has been backtracked
                backtracked = True
                
                # Set the current node as no-go
                current_node.mark_as_no_go()

                # Backtrack to parent node
                current_node = current_node.parent

                # If no parent, raise error - no possible route exists
                if current_node is None:
                    raise ValueError('Unable to find pipeline route')

                continue

            else:
                current_node = selected_child

            # Check if we've reached the target
            if np.array_equal(current_node.location, target):
                break
        
        # MCTS Expansion phase: expand non-terminal leaf nodes
        if not np.array_equal(current_node.location, target) and not backtracked:
            
            # Create child nodes for all valid moves from current position
            current_node.expand(cost_surface, target)
            
            # Check if expansion produced valid children, otherwise mark as dead end
            if not current_node.children:

                # Flag to indicate that the current node has been backtracked
                backtracked = True

                # Mark current node as no-go
                current_node.mark_as_no_go()

                # Backtrack to parent node
                current_node = current_node.parent
                    
        # MCTS Backpropagation phase: update value estimates up the tree
        if not current_node is root and not backtracked:
            current_node.backpropagate()
            current_node.selections += 1

        # Check if the root node has any valid children left
        if not [child for child in root.children if not child.is_no_go]:
            return None, None

    # After all trajectories, select the best child based on selection count
    max_value = -np.inf
    most_selections = 0
    next_node = None

    # Find the child with the most selections (most promising move)
    for child in root.children:
        if child.is_no_go:
            continue

        # If target is directly reachable, select it immediately
        if np.array_equal(child.location, target):
            next_node = child
            break

        if child.selections > most_selections:
            most_selections = child.selections
            next_node = child

    # All children are no-go
    if next_node is None and root.children:
        return None, None
        
    return root, next_node


class MCAgent:
    """
    Agent that utilizes multiple Monte Carlo Tree Search instances to find an optimal path.
    
    This class implements a pipeline routing agent that uses multiple parallel MCTS
    instances (a "forest" of search trees) to explore the state space efficiently.
    Each tree can use different exploration parameters to diversify the search.
    The trees vote on the next best move, providing a more robust routing solution.
    
    Attributes:
        num_workers (int): Number of parallel MCTS instances to run.
        distance_factor (float): Weight factor for distance in reward calculations.
        trajectories (int): Number of search trajectories for each tree.
        c (list): List of exploration parameters, one for each worker.
    """
    def __init__(self, trajectories, num_workers=None, distance_factor=1.0):
        """
        Initialize a Monte Carlo Agent.
        
        Args:
            trajectories (int): Number of search trajectories for each MCTS instance.
            num_workers (int, optional): Number of parallel MCTS instances to run.
                If None, uses half the available CPU cores. Defaults to None.
            distance_factor (float, optional): Weight for euclidean distance in reward
                calculation. Defaults to 1.0.
        """
        
        self.num_workers = num_workers
        self.distance_factor = distance_factor
        if num_workers is None:
            self.num_workers = mp.cpu_count()//2
        self.trajectories = trajectories
        if num_workers > 1:
            self.c = np.linspace(0, 5, self.num_workers)
        else:
            self.c = [np.sqrt(2)]

    def route(self, cost_surface, start, target, max_steps=1000, show_viz=False):
        """
        Find an optimal route from start to target on the cost surface.
        
        This method uses multiple parallel MCTS instances to determine the best
        path. At each step, all trees vote on the next location to move to.
        The search continues until the target is reached or max_steps is exceeded.
        
        Args:
            cost_surface (np.ndarray): The cost surface for calculating move costs.
            start (list): The starting location coordinates [y, x].
            target (list): The target destination coordinates [y, x].
            max_steps (int, optional): Maximum number of steps to take. Defaults to 1000.
            show_viz (bool, optional): Whether to visualize the search progress.
                Defaults to False.
                
        Returns:
            list: A list of coordinates representing the optimal path from start to target.
        """
        # Create multiple search trees ("forest") for parallel exploration with the same parameters
        forest = [
            MCTree(cost_surface, start, target, distance_factor=self.distance_factor) for _ in range(self.num_workers)
            ]
        path = [start]
        
        for _ in range(max_steps):
            # Prepare arguments for parallel search across all trees, each with different exploration parameter c
            args = [(tree.root, target, self.trajectories, cost_surface, c) for tree,c in zip(forest, self.c)]
            
            # Execute MCTS search in parallel using multiprocessing
            with Pool(self.num_workers) as pool:
                results = pool.starmap(search, args)
                votes = {}

            
            valid_root = True

            # Collect votes from each tree for the next best location to move to
            for (root, node), tree in zip(results, forest):

                # Determine if the root is invalid (all children are no-go)
                if root is None or node is None:
                    valid_root = False
                    break

                # Format the node location as a string key for voting
                y = str(node.location[0]).zfill(3)
                x = str(node.location[1]).zfill(3)
                key = y + ',' + x
                votes[key] = votes.get(key, 0) + 1
                tree.root = root

            if not valid_root:
                # If no valid path forward, implement backtracking mechanism
                for tree in forest:
                    # Set root node of all trees to no-go
                    tree.root.mark_as_no_go()
                    # Select the parent node as the new root
                    tree.root = tree.root.parent

                # Remove last entry from path (the invalid root)
                path.pop()
                continue
            
            # Select the location with the most votes as the next step
            next_location_str = max(votes, key=votes.get)
            next_location_arr = np.array([int(next_location_str.split(',')[0]), int(next_location_str.split(',')[1])])
            path.append(next_location_arr.tolist())

            if show_viz:
                obs = visualize(cost_surface, next_location_arr, target, path=path)
                plot_path(np.moveaxis(obs, 0, -1))

            # Check if we've reached the target
            if np.array_equal(next_location_arr, target):
                break

            # Update all trees to have the same new root node at the chosen location
            for tree in forest:
                tree.select_root(next_location_str)  # Use select_root instead of prune

        return path


class MLWrapper:
    """
    High-level wrapper for Monte Carlo Tree Search pipeline routing.
    
    This class serves as the main interface for using the Monte Carlo Tree Search 
    algorithm for pipeline routing. It handles cost surface preparation and provides
    a simple API for routing between points. The class supports different routing modes
    (standard routing and rail-based routing) with pre-configured parameters optimal 
    for each mode.
    
    Attributes:
        cost_surface (CostSurface): The cost surface used for routing.
        agent (MCAgent): The Monte Carlo agent that performs the actual routing.
    """

    def __init__(
            self, 
            mode,
            trajectories=100, 
            num_workers=1, 
            cost_degree=2,
            distance_factor=1.0
            ):
        """
        Initialize the ML routing wrapper.
        
        Args:
            mode (str): Routing mode to use. Must be either 'route' (standard routing)
                or 'rail' (rail-based routing).
            trajectories (int, optional): Number of search trajectories for the agent.
                Defaults to 100.
            num_workers (int, optional): Number of parallel MCTS instances to run.
                Defaults to 1.
            cost_degree (float, optional): Exponent used to emphasize high-cost areas 
                in the cost surface. Defaults to 2.
            distance_factor (float, optional): Weight for euclidean distance in reward
                calculation. Defaults to 1.0.
                
        Raises:
            KeyError: If an invalid mode is specified.
            FileNotFoundError: If required cost surface files are not found.
        """
        self.cost_surface = CostSurface()
        # self.cost_surface.load_rasters(raster_dir)

        if (mode == 'route'):
            raster_path=resource_path('cost_surfaces/raw_cost_10km_aea/cost_10km_aea.tif')
            cost_degree = 2
            distance_factor = 0.2
            print("Route Mode")

        elif (mode == 'rail'):
            raster_path=resource_path('cost_surfaces/10km_RAIL/cost_10km_aea_RAIL_ready.tif')    
            cost_degree = 1
            distance_factor = 0.5
            print("Rail Mode")

        else:
            raise KeyError("Neither normal nor rail mode selected")

        # Use degree to increase the weighting of high cost areas
        self.cost_surface.process_raster(raster_path, degree=cost_degree)
        self.agent = MCAgent(trajectories=trajectories, num_workers=num_workers, distance_factor=distance_factor)

    def route(self, start, target, show_viz=False):
        """
        Find an optimal route from start to target location.
        
        This method checks that start and target points are in the same region 
        (either both in Alabama or both in the rest of the US) and then uses the 
        Monte Carlo agent to find the best path between them.
        
        Args:
            start (tuple): Starting location coordinates (y, x).
            target (tuple): Target location coordinates (y, x).
            show_viz (bool, optional): Whether to visualize the routing process.
                Defaults to False.
                
        Returns:
            tuple: A tuple containing (optimized_path, raw_path) where:
                - optimized_path: The final calculated route.
                - raw_path: The raw path data for debugging.
                
        Raises:
            AssertionError: If start and target are not in the same region.
        """

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
