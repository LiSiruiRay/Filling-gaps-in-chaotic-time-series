# Author: ray
# Date: 5/8/24

import unittest

from tools.utils import tree_to_layers


class MyTestCaseTree2Layer(unittest.TestCase):
    def test_tree_to_layers(self):
        test_tree = {
            9: {90},
            90: {91},
            91: {92},
            92: {93, 920},
            93: {94},
            94: {95},
            95: {96},
            96: {97},
            97: {98},
            98: {99},
            99: {100},
            920: {921},
            921: {922},
            922: {923, 95},
            923: {924},
            924: {925},
            925: {926},
            926: {927},
        }
        max_layer = 11
        layer = tree_to_layers(test_tree, queue=[(9, 0)], max_layer=max_layer)
        print(layer)
        print(len(layer))


if __name__ == '__main__':
    unittest.main()
