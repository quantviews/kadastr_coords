import unittest
from shapely.geometry import mapping
from coords import calculate_centroid_and_coords

class TestCalculateCentroidAndCoords(unittest.TestCase):

    def test_valid_multipolygon(self):
        geometry = {
            "type": "MultiPolygon",
            "coordinates": [
                [[(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]],
                [[(2, 2), (2, 3), (3, 3), (3, 2), (2, 2)]]
            ]
        }
        result = calculate_centroid_and_coords(geometry)
        self.assertIn("centroid", result)
        self.assertIn("coordinates", result)
        self.assertEqual(len(result["coordinates"]), 2)

    def test_empty_multipolygon(self):
        geometry = {
            "type": "MultiPolygon",
            "coordinates": []
        }
        result = calculate_centroid_and_coords(geometry)
        self.assertEqual(result, "The multipolygon is empty or invalid.")

    def test_invalid_geometry(self):
        geometry = {
            "type": "Polygon",
            "coordinates": [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]
        }
        with self.assertRaises(ValueError):
            calculate_centroid_and_coords(geometry)

if __name__ == '__main__':
    unittest.main()