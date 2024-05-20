# Author: ray
# Date: 5/9/24
# Description: Here is a demo of how to use the program
import time

from scipy.optimize import minimize

from FunctionalJStrategies.discrete_j_1_strategy import DiscreteJ1Strategy
from MinDistanceStrategies.min_distance_bruteforce_store_all import MinDistanceBruteforceStoreAll
from VectorFieldFStrategies.vector_field_f_discrete_mid_point_strategy import VectorFieldFDiscreteMidPointStrategy
from data_generator.data_generator import demo_data_generator
from gap_filling_pipline.gap_filler import GapFiller


def main():
    # For t = 10
        # For m  = 3, it took 5 second to run on my computer.
        # For m = 8, it took 3 min to run on my computer
        # For m = 20, it took 5 min to run on my computer

    start_time = time.time()
    mds = MinDistanceBruteforceStoreAll()
    ts, time_data = demo_data_generator()
    t = 3  # the gap between each sampling
    m = 3  # sample vector dimension
    n_f = 3  # same n_f in the paper, stride time
    n_b = 5  # same n_d in the paper, stride time
    r = 2  # stride step
    fjs = DiscreteJ1Strategy()
    vffs = VectorFieldFDiscreteMidPointStrategy()
    gp = GapFiller(time_data=time_data, ts=ts, m=m, n_f=n_f, r=r, t=t, n_b=n_b,
                   mds=mds, fjs=fjs, vffs=vffs, minimize=minimize)
    gp.get_branches_forward()
    gp.get_branches_backward()
    print(f"finished branching")
    print(f"reconstruct vector length: {len(gp.reconstructed_vectors)}")
    gp.get_closest_points_layer()
    gp.get_gap_vector_and_index_list()
    print(f"finished gapping")

    print(f"gp.gap_vecto_list: {gp.gap_vector_list}")
    # print(f"gp.gap_vecto_list: {len(gp.gap_vector_list)}")
    gp.minimize_gap_vectors()
    end_time = time.time()
    # print(f"Filling gap vector: {gp.gap_vector_list}")
    # print(f"Filling gap time series: {gp.gap_vector_list[:, 0]}")
    print(f"time spent: {end_time - start_time}")


if __name__ == '__main__':
    main()
