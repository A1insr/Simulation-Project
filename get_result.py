
import random
import base
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from tqdm import tqdm
from scipy.stats import t
# import seaborn as sns


def run_simulation(simulation_time=30 * 24):
    simulation = base.simulation(simulation_time, excel_creation=True)

    print('--------------------------------------------------------------')
    print('Metrics:\n')
    print(f"The average time in the system is: {simulation['average_time_in_system']}")
    print(f"The possibility that the emergency queue capacity is full is: {simulation['Full_Emergency_Queue_Probability']}")
    print(f"The average number of reoperations for patients with complex operations is: {simulation['average_complex_operation_reoperations']}")
    print(f"The percentage of emergency patients who are admitted immediately is: {simulation['immediately_admitted_emergency_patients_percentage']}")

    print('\nAverage productivity of different hospital departments:')
    print(f'rho_Emergency = {simulation['rho_Emergency']}')
    print(f'rho_Preoperative = {simulation['rho_Preoperative']}')
    print(f'rho_Laboratory = {simulation['rho_Laboratory']}')
    print(f'rho_Operation = {simulation['rho_Operation']}')
    print(f'rho_General_Ward = {simulation['rho_General_Ward']}')
    print(f'rho_ICU = {simulation['rho_ICU']}')
    print(f'rho_CCU = {simulation['rho_CCU']}')

    print('\nAverage queue length in different hospital departments:')
    print(f'Lq_Emergency = {simulation['Lq_Emergency']}')
    print(f'Lq_Preoperative = {simulation['Lq_Preoperative']}')
    print(f'Lq_Laboratory_Normal = {simulation['Lq_Laboratory_Normal']}')
    print(f'Lq_Laboratory_Urgent = {simulation['Lq_Laboratory_Urgent']}')
    print(f'Lq_Operation_Normal = {simulation['Lq_Operation_Normal']}')
    print(f'Lq_Operation_Urgent = {simulation['Lq_Operation_Urgent']}')
    print(f'Lq_General_Ward = {simulation['Lq_General_Ward']}')
    print(f'Lq_ICU = {simulation['Lq_ICU']}')
    print(f'Lq_CCU = {simulation['Lq_CCU']}')

    print('\nMaximum queue length in different hospital departments:')
    print(f'Max_Lq_Emergency = {simulation['Max_Lq_Emergency']}')
    print(f'Max_Lq_Preoperative = {simulation['Max_Lq_Preoperative']}')
    print(f'Max_Lq_Laboratory_Normal = {simulation['Max_Lq_Laboratory_Normal']}')
    print(f'Max_Lq_Laboratory_Urgent = {simulation['Max_Lq_Laboratory_Urgent']}')
    print(f'Max_Lq_Operation_Normal = {simulation['Max_Lq_Operation_Normal']}')
    print(f'Max_Lq_Operation_Urgent = {simulation['Max_Lq_Operation_Urgent']}')
    print(f'Max_Lq_General_Ward = {simulation['Max_Lq_General_Ward']}')
    print(f'Max_Lq_ICU = {simulation['Max_Lq_ICU']}')
    print(f'Max_Lq_CCU = {simulation['Max_Lq_CCU']}')

    print('\nAverage waiting time in queues in different hospital departments:')
    print(f'Wq_Emergency = {simulation['Wq_Emergency']}')
    print(f'Wq_Preoperative = {simulation['Wq_Preoperative']}')
    print(f'Wq_Laboratory_Normal = {simulation['Wq_Laboratory_Normal']}')
    print(f'Wq_Laboratory_Urgent = {simulation['Wq_Laboratory_Urgent']}')
    print(f'Wq_Operation_Normal = {simulation['Wq_Operation_Normal']}')
    print(f'Wq_Operation_Urgent = {simulation['Wq_Operation_Urgent']}')
    print(f'Wq_General_Ward = {simulation['Wq_General_Ward']}')
    print(f'Wq_ICU = {simulation['Wq_ICU']}')
    print(f'Wq_CCU = {simulation['Wq_CCU']}')

    print('\nMaximum waiting time in queues in different hospital departments:')
    print(f'Max_Wq_Emergency = {simulation['Max_Wq_Emergency']}')
    print(f'Max_Wq_Preoperative = {simulation['Max_Wq_Preoperative']}')
    print(f'Max_Wq_Laboratory_Normal = {simulation['Max_Wq_Laboratory_Normal']}')
    print(f'Max_Wq_Laboratory_Urgent = {simulation['Max_Wq_Laboratory_Urgent']}')
    print(f'Max_Wq_Operation_Normal = {simulation['Max_Wq_Operation_Normal']}')
    print(f'Max_Wq_Operation_Urgent = {simulation['Max_Wq_Operation_Urgent']}')
    print(f'Max_Wq_General_Ward = {simulation['Max_Wq_General_Ward']}')
    print(f'Max_Wq_ICU = {simulation['Max_Wq_ICU']}')
    print(f'Max_Wq_CCU = {simulation['Max_Wq_CCU']}')

    print('--------------------------------------------------------------')
    print('Simulation Ended!')


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


run_simulation()
# Example usage
result = replication()
