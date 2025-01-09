
import random
import base
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from tqdm import tqdm
from scipy.stats import t
# import seaborn as sns


def replication(simulation_time=30 * 24, r=15, alpha=0.05):
    # Initialize results dictionary
    list_of_result = None

    for i in tqdm(range(r)):
        # Run the simulation
        result = base.simulation(simulation_time)

        # On the first iteration, initialize structures
        if i == 0:
            list_of_result = {key: [0] * r for key in result.keys()}

        # Store the result for the current replication
        for key in result.keys():
            list_of_result[key][i] = result[key]

    # Create a DataFrame where rows correspond to metrics and columns to replications
    results = pd.DataFrame(list_of_result).transpose()
    results.columns = [f"Replication{j + 1}" for j in range(r)]

    # Calculate point estimate (mean) and confidence intervals for each metric
    means = results.mean(axis=1)  # Point estimate
    stds = results.std(axis=1)  # Standard deviation
    n = r  # Number of replications
    t_alpha = t.ppf(1 - alpha / 2, df=n - 1)  # Critical value from t-distribution
    ci_half_width = t_alpha * stds / (n ** 0.5)  # Half-width of the confidence interval

    # Add the point estimate and CI to the DataFrame
    results['Point Estimate'] = means
    results['Confidence Interval'] = [
        f"[{round(mean - ci, 4)}, {round(mean + ci, 4)}]"
        for mean, ci in zip(means, ci_half_width)
    ]

    return results

# Example usage
dd = replication(r=20)
# print(dd)