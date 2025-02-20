import base
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib as mpl
from tqdm import tqdm
from scipy.stats import t
from openpyxl import Workbook
from openpyxl.styles import Font


original_param = {
    'Preoperative Capacity': 25,
    'Emergency Capacity': 10,
    'Emergency Queue Capacity': 10,
    'Laboratory Capacity': 3,
    'Operation Capacity': 50,
    'General Ward Capacity': 40,
    'ICU Capacity': 10,
    'CCU Capacity': 5,
    'Normal Arrival Exp Param': 1,
    'Urgent Arrival Exp Param': 4,
    'Normal Laboratory Param': 1,
    'Urgent Laboratory Param': (10 / 60),
    'After Laboratory Uni a Param': (28 / 60),
    'After Laboratory Uni b Param': (32 / 60),
    'Normal Operation Param': 48,
    'Urgent Operation trgl LB Param': (5 / 60),
    'Urgent Operation trgl M Param': (75 / 60),
    'Urgent Operation trgl UB Param': (100 / 60),
    'Simple Operation Mean': 30.22,
    'Simple Operation SD': 4.96,
    'Medium Operation Mean': 74.54,
    'Medium Operation SD': 9.53,
    'Complex Operation Mean': 242.03,
    'Complex Operation SD': 63.27,
    'Care Unit Exp Param': (1 / 25),
    'End of Service Exp Param': (1 / 50)
}


def run_simulation(simulation_time, param, excel_creation=False):
    """
    Runs a simulation based on the provided parameters and outputs key performance metrics for the warm-up period.

    Args:
        simulation_time (int): The total duration of the simulation in hours.
        param (dict): A dictionary containing the parameters for the system simulation.
        excel_creation (bool, optional): If set to True, an Excel file will be created with the simulation results.
                                          Default is False (no Excel file creation).

    Returns:
        dict: A dictionary containing the simulation results with key metrics, including:
            - 'Lq_Preoperative_Warm_Period': The length of the preoperative queue during the warm-up period.
            - 'Wq_Preoperative_Warm_Period': The waiting time for the preoperative queue during the warm-up period.
            - 'Finished_Patients': The total number of patients that have finished the process during the simulation.

    Outputs:
        - Prints key performance metrics for the warm-up period, including:
            1. `Lq_Preoperative_Warm_Period`
            2. `Wq_Preoperative_Warm_Period`
            3. `Finished_Patients`
        - Optionally generates an Excel file containing the simulation results if `excel_creation` is set to True.
    """

    simulation = base.simulation(simulation_time, param, excel_creation)['Results']

    print(f"Lq_Preoperative_Warm_Period = {simulation['Lq_Preoperative_Warm_Period']}")
    print(f"Wq_Preoperative_Warm_Period = {simulation['Wq_Preoperative_Warm_Period']}")
    print(f"Finished_Patients = {simulation['Finished_Patients']}")


def warm_up_replication(simulation_time, r, param):
    """
    Runs multiple replications of a simulation to analyze warm-up periods and computes statistical summaries.

    Args:
        simulation_time (int): The total simulation duration in hours.
        r (int): The number of replications to run.
        param (dict): A dictionary of parameters used for the simulation.

    Returns:
        pd.DataFrame: A DataFrame where:
            - Rows correspond to different performance metrics ('Lq_Preoperative_Warm_Period',
              'Wq_Preoperative_Warm_Period', 'Finished_Patients').
            - Columns correspond to individual replications and statistical summaries:
                - 'mean': The average value across replications.
                - 'std': The standard deviation across replications.
                - 'R': The number of replications used.

    Process:
        - Runs the simulation `r` times, collecting data on:
            - Preoperative queue length during the warm-up period ('Lq_Preoperative_Warm_Period').
            - Preoperative waiting time during the warm-up period ('Wq_Preoperative_Warm_Period').
            - Number of patients who finished their process ('Finished_Patients').
        - Stores results in a dictionary and converts it into a Pandas DataFrame.
        - Computes the mean and standard deviation for each metric.
    """

    # Initialize results dictionary
    list_of_result = None

    for i in tqdm(range(r)):
        # Run the simulation
        result = base.simulation(simulation_time, param)['Results']

        # On the first iteration, initialize structures
        if i == 0:
            list_of_result = {key: [0] * r for key in ['Lq_Preoperative_Warm_Period',
                                                       'Wq_Preoperative_Warm_Period', 'Finished_Patients']}

        # Store the result for the current replication
        for key in ['Lq_Preoperative_Warm_Period', 'Wq_Preoperative_Warm_Period', 'Finished_Patients']:
            list_of_result[key][i] = result[key]

    # Create a DataFrame where rows correspond to metrics and columns to replications
    results = pd.DataFrame(list_of_result).transpose()
    results.columns = [f"Replication{j + 1}" for j in range(r)]

    # Calculate point estimate (mean) and confidence intervals for each metric
    means = results.mean(axis=1)  # Point estimate
    stds = results.std(axis=1)  # Standard deviation
    results['mean'] = means
    results['std'] = stds
    results['R'] = r

    return results


def estimate_warm_up_metrics(first_system, second_system, alpha):
    estimate_table = first_system[['mean', 'std', 'R']].merge(second_system[['mean', 'std', 'R']],
                                                              how='inner', left_index=True, right_index=True)
    estimate_table.columns = ['Y_bar_1', 'S_1', 'R_1', 'Y_bar_2', 'S_2', 'R_2']

    # Standard Error (SE) calculation (fixed)
    estimate_table['se'] = np.sqrt(((estimate_table['S_1'] ** 2) / estimate_table['R_1']) +
                                   ((estimate_table['S_2'] ** 2) / estimate_table['R_2']))

    # Compute v (fixed)
    estimate_table['v'] = (
        (
            (estimate_table['S_1'] ** 2) / estimate_table['R_1'] +
            (estimate_table['S_2'] ** 2) / estimate_table['R_2']
        ) ** 2
    ) / (
        ((estimate_table['S_1'] ** 2) / estimate_table['R_1']) ** 2 / (estimate_table['R_1'] - 1) +
        ((estimate_table['S_2'] ** 2) / estimate_table['R_2']) ** 2 / (estimate_table['R_2'] - 1)
    )

    # Compute Point Estimate
    estimate_table['Point Estimate'] = estimate_table['Y_bar_1'] - estimate_table['Y_bar_2']

    # Compute t_alpha row-wise
    estimate_table['t_alpha'] = estimate_table['v'].apply(lambda v: t.ppf(1 - alpha / 2, df=v))

    # Compute confidence interval half-width
    estimate_table['ci_half_width'] = estimate_table['t_alpha'] * estimate_table['se']

    # Compute Confidence Interval correctly
    estimate_table['Confidence Interval'] = estimate_table.apply(
        lambda row: f"[{round(row['Point Estimate'] - row['ci_half_width'], 3)}, {round(row['Point Estimate'] + row['ci_half_width'], 3)}]",
        axis=1
    )

    # Select final columns
    result = estimate_table[['Point Estimate', 'Confidence Interval']]

    # Save to Excel with formatting
    filename = 'systems_comparison_table.xlsx'
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        result.to_excel(writer, sheet_name='Comparison', index=True)

        workbook = writer.book
        worksheet = workbook.active
        font = Font(name='Times New Roman', size=12)

        # Apply font and adjust column widths dynamically
        for col in worksheet.columns:
            max_length = 0
            col_letter = col[0].column_letter  # Get column letter (e.g., A, B, C)

            for cell in col:
                cell.font = font
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass

            # Set column width based on max content length (with padding)
            worksheet.column_dimensions[col_letter].width = max_length + 2

        workbook.save(filename)

    print(f"Results saved to {filename}.")
    return result


def calculate_aggregate_queue_waiting_time(start_time, end_time, patients_data):

    patient_number = 0
    cumulative_waiting_time = 0
    # print('hey')
    # print(patients_data)
    for patient in patients_data:
        if 'Time Preoperative Service Begins' in patients_data[patient]:
            # if the customer has arrived in this time-frame ...
            if start_time <= patients_data[patient]['Arrival Time'] < end_time:
                # if the customer starts getting service in this time-frame...
                if patients_data[patient]['Time Preoperative Service Begins'] < end_time:
                    cumulative_waiting_time += patients_data[patient]['Time Preoperative Service Begins'] - \
                                               patients_data[patient]['Arrival Time']
                    patient_number += 1

                # else if the customer will start getting service after this time-frame...
                else:
                    cumulative_waiting_time += end_time - \
                                               patients_data[patient]['Arrival Time']
                    patient_number += 1

            elif patients_data[patient]['Arrival Time'] < start_time and \
                    patients_data[patient]['Time Preoperative Service Begins'] > end_time:
                cumulative_waiting_time += end_time - start_time
                patient_number += 1

            elif patients_data[patient]['Arrival Time'] > end_time:
                break

    if patient_number == 0:
        return 0

    return cumulative_waiting_time / patient_number


def calculate_aggregate_queue_length(start_time, end_time, preoperative_queue_data):

    cumulative_queue_length = 0

    t_1 = start_time
    for time in preoperative_queue_data:
        if start_time <= time < end_time:
            cumulative_queue_length += (time - t_1) * preoperative_queue_data[time]
            t_1 = time
        elif time > end_time:
            break

    return cumulative_queue_length / (end_time - start_time)
    

def calculate_number_of_finishing_patients(start_time, end_time, patients_data):

    number_of_finishing_patients = 0

    for patient in patients_data:
        if 'Time Service Ends' in patients_data[patient]:
            if start_time < patients_data[patient]['Time Service Ends'] <= end_time:
                number_of_finishing_patients += 1
            elif patients_data[patient]['Time Service Ends'] > end_time:
                break

    return number_of_finishing_patients
    

def simulate_and_plot(original_param, param_updates, simulation_config, system_name):
    """
    Simulates a system with user-defined parameters, aggregates key performance metrics over multiple replications,
    and visualizes the results in a series of plots.

    Args:
        original_param (dict): A dictionary containing the base parameters for the system simulation.
        param_updates (dict): A dictionary of parameter updates to modify the original_param.
        simulation_config (dict): A dictionary containing simulation configuration, including:
            - 'num_of_replications' (int): The number of replications to run.
            - 'num_of_days' (int): The total number of simulation days.
            - 'frame_length' (int): The length of each frame in hours.
            - 'window_size' (int): The window size for calculating the moving average.
            - 'tick_spacing' (int): The tick spacing for the x-axis in the plots.
        system_name (str): The name of the system to use for the plot title and saved file name.

    Returns:
        None: The function generates and displays plots, and saves the figure as a PNG file.

    Generates:
        - Three plots showing:
            1. Aggregate preoperative queue length over time.
            2. Aggregate waiting time over time.
            3. Number of finishing patients over time.
        Each plot includes both the raw average and a moving average for trend visualization.
        The plots are saved as a PNG file named 'Warm-up analysis - {system_name}.png'.

    Notes:
        - The simulation assumes that the 'base.simulation' function is available for generating simulation data.
        - The function uses the Matplotlib library for plotting and includes customized font settings.
        - The results of each replication are aggregated, and a moving average is applied to smooth the data.
    """

    # Update original_param with user-defined changes
    original_param.update(param_updates)

    # Extract simulation configurations
    num_of_replications = simulation_config.get('num_of_replications', 10)
    num_of_days = simulation_config.get('num_of_days', 500)
    frame_length = simulation_config.get('frame_length', 18)
    window_size = simulation_config.get('window_size', 10)
    tick_spacing = simulation_config.get('tick_spacing', 50)

    # Set font and font size
    mpl.rc('font', family='Times New Roman')
    mpl.rc('font', size=12)

    # Create an empty figure with two subplots
    fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(8, 6))

    # Data structures to save outputs
    waiting_time_frame_aggregate = {}
    preoperative_frame_queue_length = {}
    finishing_patients_frame_count = {}  

    def moving_average(input_list, m):
        output_list = []
        n = len(input_list)
        for i in range(n):
            output_list.append(sum(input_list[max(i - m // 2, 2 * i - n + 1, 0):min(i + m // 2 + 1, 2 * i + 1, n)]) / (
                    min(i + m // 2, 2 * i, n - 1) - max(i - m // 2, 2 * i - n + 1, 0) + 1))
        return output_list

    simulation_time = num_of_days * 24
    num_of_frames = simulation_time // frame_length - 2
    x = [i for i in range(1, num_of_frames + 1)]

    for replication in tqdm(range(1, num_of_replications + 1), desc="Simulating Replications"):
        simulation_data = base.simulation(simulation_time, original_param)
        patients_data = simulation_data['Patients']
        preoperative_queue_data = simulation_data['preoperative_queue_tracker']

        waiting_time_frame_aggregate[replication] = []
        preoperative_frame_queue_length[replication] = []
        finishing_patients_frame_count[replication] = []

        for time in range(0, num_of_frames * frame_length, frame_length):
            waiting_time_frame_aggregate[replication].append(
                calculate_aggregate_queue_waiting_time(time, time + frame_length, patients_data))
            preoperative_frame_queue_length[replication].append(
                calculate_aggregate_queue_length(time, time + frame_length, preoperative_queue_data))
            finishing_patients_frame_count[replication].append(
                calculate_number_of_finishing_patients(time, time + frame_length, patients_data))
                

    waiting_time_replication_average = []
    preoperative_queue_length_replication_average = []
    finishing_patients_replication_average = []

    for i in range(num_of_frames):
        avg_wait_time = sum(
            waiting_time_frame_aggregate[rep][i] for rep in range(1, num_of_replications + 1)) / num_of_replications
        avg_queue_length = sum(
            preoperative_frame_queue_length[rep][i] for rep in range(1, num_of_replications + 1)) / num_of_replications
        avg_finishing_count = sum(
            finishing_patients_frame_count[rep][i] for rep in range(1, num_of_replications + 1)) / num_of_replications
        waiting_time_replication_average.append(avg_wait_time)
        preoperative_queue_length_replication_average.append(avg_queue_length)
        finishing_patients_replication_average.append(avg_finishing_count)

    waiting_time_moving_replication_average = moving_average(waiting_time_replication_average, window_size)
    preoperative_queue_length_moving_replication_average = moving_average(preoperative_queue_length_replication_average,
                                                                          window_size)
    finishing_patients_moving_replication_average = moving_average(finishing_patients_replication_average, window_size)

    fig, ax = plt.subplots(3, 1, figsize=(10, 8))
    fig.suptitle(f'Warm-up analysis over {num_of_replications} replications', fontsize=14, fontweight='bold')

    fig.subplots_adjust(hspace=0.4)

    colors = ['blue', 'orange']

    ax[0].plot(x, preoperative_queue_length_replication_average, colors[0], alpha=0.2, linewidth=3,
               label="Average across replications")
    ax[0].plot(x, preoperative_queue_length_moving_replication_average, colors[1], linestyle='dashed',
               label=f'Moving average (m = {window_size})')
    ax[0].set_title('Aggregate Preoperative Queue Length', fontsize=12)
    ax[0].set_xlabel('Frame No.', fontsize=10)
    ax[0].set_ylabel('Queue Length', fontsize=10)
    ax[0].legend(loc='upper right', fontsize=9, frameon=False)
    ax[0].xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    ax[0].grid(True, linestyle='--', alpha=0.5)

    ax[1].plot(x, waiting_time_replication_average, colors[0], alpha=0.2, linewidth=3, label="Average across replications")
    ax[1].plot(x, waiting_time_moving_replication_average, colors[1], linestyle='dashed',
               label=f'Moving average (m = {window_size})')
    ax[1].set_title('Aggregate Waiting Time', fontsize=12)
    ax[1].set_xlabel('Frame No.', fontsize=10)
    ax[1].set_ylabel('Waiting Time', fontsize=10)
    ax[1].legend(loc='upper right', fontsize=9, frameon=False)
    ax[1].xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    ax[1].grid(True, linestyle='--', alpha=0.5)

    ax[2].plot(x, finishing_patients_replication_average, colors[0], alpha=0.2, linewidth=3, label="Average across replications")
    ax[2].plot(x, finishing_patients_moving_replication_average, colors[1], linestyle='dashed',
               label=f'Moving average (m = {window_size})')
    ax[2].set_title('Number of Finishing Patients', fontsize=12)
    ax[2].set_xlabel('Frame No.', fontsize=10)
    ax[2].set_ylabel('Patients', fontsize=10)
    ax[2].legend(loc='upper right', fontsize=9, frameon=False)
    ax[2].xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    ax[2].grid(True, linestyle='--', alpha=0.5)

    # Save each plot as a separate file
    file_name = f'Warm-up analysis - {system_name}.svg'
    plt.savefig(file_name, format="svg", bbox_inches="tight")
    print(f"Saved plot as {file_name}")
    plt.show()
    plt.close()  # Close the figure to free memory


param_updates_1 = {
    'Preoperative Capacity': 25,
    'General Ward Capacity': 55,
    'CCU Capacity': 10,
    'Normal Operation Param': 24,
    'End of Service Exp Param': (1 / 40)
}

param_updates_2 = {
    'Preoperative Capacity': 32,
    'General Ward Capacity': 60,
    'CCU Capacity': 10,
    'Normal Operation Param': 30,
    'End of Service Exp Param': (1 / 45)
}

simulation_config = {
    'num_of_replications': 25,
    'num_of_days': 900,
    'frame_length': 18,
    'window_size': 10,
    'tick_spacing': 50
}

# Diagram of the 2 systems introduced for warm-up analysis
simulate_and_plot(original_param, param_updates_1, simulation_config, '1st System')
simulate_and_plot(original_param, param_updates_2, simulation_config, '2nd System')

# Running the system over the long term to obtain metrics
system1_param = original_param
system1_param.update(param_updates_1)
simulation_time_1 = ((300 * simulation_config['frame_length']) * 11)
R1 = 10

system2_param = original_param
system2_param.update(param_updates_2)
simulation_time_2 = ((300 * simulation_config['frame_length']) * 11)
R2 = 10

print('---------------------------------------------')
print('Warm Period Metrics For 1st System:')
run_simulation(simulation_time_1, system1_param)

print('\n---------------------------------------------')
print('Warm Period Metrics For 2nd System:')
run_simulation(simulation_time_2, system2_param)

warm_up_results1 = warm_up_replication(simulation_time_1, R1, system1_param)
warm_up_results2 = warm_up_replication(simulation_time_2, R2, system2_param)
print('\n---------------------------------------------')
print('Point Estimate & Confidence Interval For These Metrics:')
estimate_warm_up_metrics(warm_up_results1, warm_up_results2, 0.05)
