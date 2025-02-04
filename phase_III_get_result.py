import base
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib as mpl
from tqdm import tqdm


# Initialize parameters
num_of_replications = 3
num_of_days = 500
frame_length = 18
window_size = 10
tick_spacing = 50

original_param = {
    'Preoperative Capacity': 30,
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
    'Normal Operation Param': 24,
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


# Set font and font size
mpl.rc('font', family='Times New Roman')
mpl.rc('font', size=12)

# Create an empty figure with two subplots
fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(8, 6))

# Set up a data structure to save required outputs in each replication
waiting_time_frame_aggregate = dict()  # keys are replications
preoperative_frame_queue_length = dict() # keys are replications 

# Function to calculate moving average of a list over a sliding window of length m.
def moving_average(input_list, m):
    output_list = []
    n = len(input_list)
    for i in range(n):
        output_list.append(sum(input_list[max(i - m // 2, 2 * i - n + 1, 0):min(i + m // 2 + 1, 2 * i + 1, n)]) / (
                min(i + m // 2, 2 * i, n - 1) - max(i - m // 2, 2 * i - n + 1, 0) + 1))
    return output_list


def calculate_aggregate_queue_waiting_time(start_time, end_time, patients_data):

    cumulative_waiting_time = 0

    for patient in patients_data:
        if 'Time Preoperative Service Begins' in patients_data[patient]:
            # if the customer has arrived in this time-frame ...
            if start_time <= patients_data[patient]['Arrival Time'] < end_time:
                # if the customer starts getting service in this time-frame...
                if patients_data[patient]['Time Preoperative Service Begins'] < end_time:
                    cumulative_waiting_time += patients_data[patient]['Time Preoperative Service Begins'] - \
                                               patients_data[patient]['Arrival Time']
                # else if the customer will start getting service after this time-frame...
                else:
                    cumulative_waiting_time += end_time - \
                                               patients_data[patient]['Arrival Time']

            elif patients_data[patient]['Arrival Time'] > end_time:
                break

            # if the customer has arrived before the beginning of this time-frame
            # but starts getting service during this time-frame...
            else:
                if start_time < patients_data[patient]['Time Preoperative Service Begins'] < end_time:
                    cumulative_waiting_time += patients_data[patient]['Time Preoperative Service Begins'] - \
                                               start_time

                elif patients_data[patient]['Time Preoperative Service Begins'] > end_time:
                    cumulative_waiting_time += end_time - start_time

    return cumulative_waiting_time

def calculate_aggregate_queue_length(start_time, end_time, preoperative_queue_data):
    cumulative_queue_length = 0
    for time in preoperative_queue_data:
        if start_time <= time < end_time:
           cumulative_queue_length += (time - start_time) * preoperative_queue_data[time]
        elif time > end_time:
            break
    return cumulative_queue_length / (end_time - start_time)
    
simulation_time = num_of_days * 24
# Just use the frames with full information (drop last 2 frames)
num_of_frames = simulation_time // frame_length - 2
x = [i for i in range(1, num_of_frames + 1)]

for replication in tqdm(range(1, num_of_replications + 1), desc="Simulating Replications"):

    simulation_data = base.simulation(num_of_days * 24, original_param)
    # print(simulation_data)
    patients_data = simulation_data['Patients']
    preoperative_queue_data = simulation_data['preoperative_queue_tracker']

    waiting_time_frame_aggregate[replication] = []
    preoperative_frame_queue_length[replication] = []

    # do calculations frame by frame
    for time in range(0, num_of_frames * frame_length, frame_length):

        waiting_time_frame_aggregate[replication].append(
            calculate_aggregate_queue_waiting_time(time, time + frame_length, patients_data))
        preoperative_frame_queue_length[replication].append(
            calculate_aggregate_queue_length(time, time + frame_length, preoperative_queue_data))


waiting_time_replication_average = []
preoperative_queue_length_replication_average = []


for i in range(num_of_frames):
    average_waiting_time = 0
    average_preoperative_queue_length = 0

    for replication in range(1, num_of_replications + 1):
        average_waiting_time += waiting_time_frame_aggregate[replication][i] * (1 / num_of_replications)
        average_preoperative_queue_length += preoperative_frame_queue_length[replication][i] * (1 / num_of_replications)
         
    waiting_time_replication_average.append(average_waiting_time)
    preoperative_queue_length_replication_average.append(average_preoperative_queue_length)
    

waiting_time_moving_replication_average = moving_average(waiting_time_replication_average, window_size)
preoperative_queue_length_moving_replication_average = moving_average(preoperative_queue_length_replication_average, window_size)

fig.suptitle(f'Warm-up analysis over {num_of_replications} replications')


ax[0].plot(x, preoperative_queue_length_replication_average, 'r', linewidth=5, label="Average across replications")
ax[0].plot(x, preoperative_queue_length_moving_replication_average, 'k', label=f'Moving average (m = {window_size})')
ax[0].set_title('Aggregate Preoperative Queue Length')
ax[0].set_xlabel('Frame No.')
ax[0].set_ylabel('Aggregate Preoperative Queue Length')
ax[0].xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
ax[0].legend()

ax[1].plot(x, waiting_time_replication_average, 'r', linewidth=5, label="Average across replications")
ax[1].plot(x, waiting_time_moving_replication_average, 'k', label=f'Moving average (m = {window_size})')
ax[1].set_title('Aggregate Waiting Time')
ax[1].set_xlabel('Frame No.')
ax[1].set_ylabel('Aggregate Waiting Time')
ax[1].xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
ax[1].legend()

fig.tight_layout()
fig.show()
fig.savefig('Single server queue - Warm-up analysis - Time-Frame Approach')
