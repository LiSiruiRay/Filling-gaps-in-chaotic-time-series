# Author: ray
# Date: 5/8/24

import unittest

from data_generator.data_generator import demo_data_generator
from gap_filling_pipline.gap_filler import GapFiller


class MyTestCaseGapFiller(unittest.TestCase):
    def test_reconstruct_timeseries(self):
        gp = GapFiller()
        ts = demo_data_generator()
        gp.ts = ts
        gp.t = 10
        gp.m = 3
        gp.reconstruct_timeseries()
        print(gp.reconstructed_vectors)

if __name__ == '__main__':
    unittest.main()
