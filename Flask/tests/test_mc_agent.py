import sys
sys.path.append("../Flask") # set working directory to parent folder so imports work

import unittest
import numpy as np
from unittest.mock import patch, MagicMock
from mc_agent import Node, MCTree, MCAgent, MLWrapper, CostSurface, normalize, exponential, draw_circle
from pathlib import Path

class TestMCAgent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a simple cost surface for testing
        self.cost_surface = np.zeros((10, 10))
        self.cost_surface[5:7, 5:7] = 1  # Create a high-cost area in the middle
        self.start = np.array([0, 0])
        self.target = np.array([9, 9])
        
    def test_normalize(self):
        """Test the normalize function."""
        arr = np.array([1, 2, 3, 4, 5])
        normalized = normalize(arr)
        self.assertEqual(normalized.min(), 0)
        self.assertEqual(normalized.max(), 1)
        
    def test_exponential(self):
        """Test the exponential function."""
        arr = np.array([1, 2, 3])
        result = exponential(arr, 2)
        expected = np.array([1, 4, 9])
        np.testing.assert_array_equal(result, expected)
        
    def test_draw_circle(self):
        """Test the draw_circle function."""
        img = np.zeros((10, 10))
        center = (5, 5)
        radius = 2
        result = draw_circle(img, center, radius)
        # Check if circle is drawn (should have some 1s)
        self.assertTrue(np.any(result == 1))
        # Check if circle is within bounds
        self.assertTrue(np.all(result[0:2, :] == 0))  # Top rows should be empty
        self.assertTrue(np.all(result[-2:, :] == 0))  # Bottom rows should be empty
        
    def test_node_initialization(self):
        """Test Node initialization and basic properties."""
        location = np.array([1, 1])
        parent = None
        reward = 1.0
        path = {"001,001": True}
        node = Node(location, parent, reward, path)
        
        self.assertTrue(np.array_equal(node.location, location))
        self.assertIsNone(node.parent)
        self.assertEqual(node.reward, reward)
        self.assertEqual(node.path, path)
        self.assertEqual(node.selections, 0)
        self.assertEqual(node.value, 0)
        
    def test_node_calculate_euclidean_reward(self):
        """Test the calculate_euclidean_reward method."""
        location = np.array([0, 0])
        parent = None
        reward = 0
        path = {"000,000": True}
        node = Node(location, parent, reward, path)
        
        new_location = np.array([1, 1])
        target_location = np.array([5, 5])
        reward = node.calculate_euclidean_reward(new_location, target_location)
        
        # The reward should be a float value
        self.assertIsInstance(reward, float)
        # The reward should be less than the maximum possible reward
        self.assertLess(reward, 100)
        
    def test_mctree_initialization(self):
        """Test MCTree initialization."""
        tree = MCTree(self.cost_surface, self.start, self.target)
        
        self.assertTrue(np.array_equal(tree.cost_surface, self.cost_surface))
        self.assertTrue(np.array_equal(tree.target, self.target))
        self.assertIsNotNone(tree.root)
        self.assertTrue(np.array_equal(tree.root.location, self.start))
        
    def test_mctree_traverse(self):
        """Test MCTree traverse method."""
        tree = MCTree(self.cost_surface, self.start, self.target)
        locations = tree.traverse(tree.root)
        
        self.assertIsInstance(locations, list)
        self.assertTrue(len(locations) > 0)
        self.assertTrue(np.array_equal(locations[0], self.start))
        
    def test_mcagent_initialization(self):
        """Test MCAgent initialization."""
        agent = MCAgent(trajectories=100, num_workers=2)
        
        self.assertEqual(agent.num_workers, 2)
        self.assertEqual(agent.trajectories, 100)
        self.assertEqual(len(agent.c), 2)
        
    @patch('pathlib.Path.exists', return_value=True)
    @patch('mc_agent.resource_path')
    @patch('mc_agent.rasterio.open')
    def test_mlwrapper_initialization(self, mock_rasterio, mock_resource_path, mock_exists):
        """Test MLWrapper initialization."""
        # Mock the resource path to return a valid path string
        mock_resource_path.return_value = 'dummy/path/to/raster.tif'
        
        # Mock the rasterio dataset with a transition for find_transitions
        mock_dataset = MagicMock()
        arr = np.zeros((10, 10))
        arr[0:5, :] = -1  # Top half -1, bottom half 0, creates a transition
        mock_dataset.read.return_value = arr
        mock_rasterio.return_value = mock_dataset
        
        wrapper = MLWrapper(mode='route', trajectories=100, num_workers=1)
        
        self.assertIsNotNone(wrapper.cost_surface)
        self.assertIsNotNone(wrapper.agent)
        self.assertEqual(wrapper.agent.trajectories, 100)
        
    def test_cost_surface_initialization(self):
        """Test CostSurface initialization."""
        cost_surface = CostSurface()
        
        self.assertIsNone(cost_surface.cost)
        self.assertIsNone(cost_surface.no_go)
        
    def test_invalid_mlwrapper_mode(self):
        """Test MLWrapper initialization with invalid mode."""
        with self.assertRaises(KeyError):
            MLWrapper(mode='invalid_mode')

if __name__ == '__main__':
    unittest.main() 