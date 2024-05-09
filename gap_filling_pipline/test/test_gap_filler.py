# Author: ray
# Date: 5/8/24

import unittest

from FunctionalJStrategies.discrete_j_1_strategy import DiscreteJ1Strategy
from MinDistanceStrategies.min_distance_bruteforce_store_all import MinDistanceBruteforceStoreAll
from VectorFieldFStrategies.vector_field_f_discrete_mid_point_strategy import VectorFieldFDiscreteMidPointStrategy
from data_generator.data_generator import demo_data_generator
from gap_filling_pipline.gap_filler import GapFiller
from scipy.optimize import minimize


class MyTestCaseGapFiller(unittest.TestCase):
    def test_reconstruct_timeseries(self):
        # gp = GapFiller()
        # ts = demo_data_generator()
        # gp.ts = ts
        # gp.t = 10
        # gp.m = 3
        # gp.reconstruct_timeseries()
        # print(gp.reconstructed_vectors)
        pass

    def test_calc_last_valid_closest_neighbor_index(self):
        # mds = MinDistanceBruteforceStoreAll()
        # gp = GapFiller()
        # ts = demo_data_generator()
        # gp.ts = ts
        # gp.t = 10
        # gp.m = 3
        # gp.mds = mds
        # gp.reconstruct_timeseries()
        # gp.get_breaking_points()
        # gp.calc_last_valid_closest_neighbor_index()
        # self.assertEqual(gp.last_valid_closest_neighbor_index, 185)
        # print(mds.dis_matrix[gp.last_valid_v_index])
        # """
        # 18.08056936 16.49282081 15.7939515  14.55868094 11.34621452  3.43052589
        # 11.79431908  6.01438878 12.73234273 20.94818707 24.86383871 29.75267702
        # 36.01171858 37.21026881 30.59424624 25.00563872 23.83610122 26.26390284 ...
        # """
        pass

    def test_branching(self):
        mds = MinDistanceBruteforceStoreAll()
        ts, time_data = demo_data_generator()
        t = 10
        m = 3
        n_f = 5
        n_b = 5
        r = 2
        gp = GapFiller(ts=ts, m=m, n_f=n_f, r=r, t=t, n_b=n_b, mds=mds, fjs=None, vffs=None)
        gp.get_branches_backward()
        print(f"back_branches_df: {gp.backward_branches_df}, back_branches_df_reverse: {gp.back_branches_df_reverse}")

    def test_get_gap_list(self):
        mds = MinDistanceBruteforceStoreAll()
        ts, time_data = demo_data_generator()
        t = 10
        m = 3
        n_f = 5
        n_b = 5
        r = 2
        gp = GapFiller(time_data=time_data, ts=ts, m=m, n_f=n_f, r=r, t=t, n_b=n_b, mds=mds, fjs=None, vffs=None)
        gp.get_branches_forward()
        gp.get_branches_backward()
        gp.get_closest_points_layer()
        print(gp.get_gap_vector_index_list())
        correct_result = [185, 186, 187, 387, 388, 389, 390, 391, 392, 393]
        self.assertEqual(gp.get_gap_vector_index_list(), correct_result)

    def test_pipeline(self):
        mds = MinDistanceBruteforceStoreAll()
        ts, time_data = demo_data_generator()
        t = 10
        m = 3
        n_f = 5
        n_b = 5
        r = 2
        fjs = DiscreteJ1Strategy()
        vffs = VectorFieldFDiscreteMidPointStrategy()
        gp = GapFiller(time_data=time_data, ts=ts, m=m, n_f=n_f, r=r, t=t, n_b=n_b,
                       mds=mds, fjs=fjs, vffs=vffs, minimize=minimize)
        gp.get_branches_forward()
        gp.get_branches_backward()
        gp.get_closest_points_layer()
        gp.get_gap_vector_and_index_list()
        gp.minimize_gap_vectors()
        print(gp.optimized_gap_vector)
        print(len(gp.optimized_gap_vector))




if __name__ == '__main__':
    unittest.main()
