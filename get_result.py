
import random
import base
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
# from tqdm import tqdm
# import scipy.stats
# import seaborn as sns
data = base.simulation(60)

def replication(simulation_time= 30*24*60, r= 15, alpha= 0.05):
    