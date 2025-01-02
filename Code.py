"""
Simulation of Single Channel Queue
Input Distributions:
    1- Entering population: poisson with mean = 3 people per hour
        (Inter-arrival time: Exponential with mean = 20 minutes)
    2- Service time: uniform(10, 25) minutes
No limits on queue length
People get served based on a FIFO discipline
Outputs:
    1-
    2-
    3-
System starts at an empty state

Author:
Date:
"""

import random
import math
import pandas as pd


def starting_state():
    # State variables
    state = dict()
    state['Preoperative Occupied Beds'] = 0
    state['Emergency Occupied Beds'] = 0
    state['Laboratory Occupied Beds'] = 0
    state['Operation Occupied Beds'] = 0
    state['General Ward Occupied Beds'] = 0
    state['ICU Occupied Beds'] = 0
    state['CCU Occupied Beds'] = 0
    state['Preoperative Queue'] = 0
    state['Emergency Queue'] = 0
    state['Laboratory Normal Queue'] = 0
    state['Laboratory Urgent Queue'] = 0
    state['Surgery Normal Queue'] = 0
    state['Surgery Urgent Queue'] = 0
    state['General Ward Queue'] = 0
    state['ICU Queue'] = 0
    state['CCU Queue'] = 0

    # Data: will save everything
    data = dict()
    data['Patients'] = dict()  # To track each customer, saving their arrival time, time service begins, etc.
    # data['Last Time Queue Length Changed'] = 0  # Needed to calculate area under queue length curve
    # data['Queue Patient'] = dict()  # Customer: Arrival Time, used to find first customer in queue
    #
    # # Cumulative Stats

    data['Last Time Emergency Queue Length Changed'] = 0 # Needed to caculate probability of a full emergency queue
    data['Last Time Preoperative Queue Length Changed'] = 0
    data['Last Time Laboratory Normal Queue Length Changed'] = 0
    data['Last Time Laboratory Urgent Queue Length Changed'] = 0
    data['Last Time Operation Normal Queue Length Changed'] = 0
    data['Last Time Operation Urgent Queue Length Changed'] = 0
    data['Last Time General Ward Queue Length Changed'] = 0
    data['Last Time ICU Queue Length Changed'] = 0
    data['Last Time CCU Queue Length Changed'] = 0

        
    data['Cumulative Stats'] = dict()
    data['Cumulative Stats']['Total Patients'] = 0
    data['Cumulative Stats']['Emergency Patients'] = 0
    data['Cumulative Stats']['System Waiting Time'] = 0
    data['Cumulative Stats']['Full Emergency Queue Duration'] = 0
    
    data['Cumulative Stats']['Area Under Emergency Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Preoperative Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Laboratory Normal Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Laboratory Urgent Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Operation Normal Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Operation Urgent Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under General Ward Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under ICU Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under CCU Queue Length Curve'] = 0

    data['Cumulative Stats']['Emergency Queue Waiting Time'] = 0 
    data['Cumulative Stats']['Preoperative Queue Waiting Time'] = 0
    data['Cumulative Stats']['Laboratory Normal Queue Waiting Time'] = 0
    data['Cumulative Stats']['Laboratory Urgent Queue Waiting Time'] = 0
    data['Cumulative Stats']['Operation Normal Queue Waiting Time'] = 0
    data['Cumulative Stats']['Operation Urgent Queue Waiting Time'] = 0
    data['Cumulative Stats']['General Ward Queue Waiting Time'] = 0
    data['Cumulative Stats']['ICU Queue Waiting Time'] = 0
    data['Cumulative Stats']['CCU Queue Waiting Time'] = 0

    data['Cumulative Stats']['Emergency Service Starters'] = 0
    data['Cumulative Stats']['Preoperative Service Starters'] = 0
    data['Cumulative Stats']['Laboratory Service Starters'] = 0
    data['Cumulative Stats']['Operation Service Starters'] = 0
    data['Cumulative Stats']['General Ward Service Starters'] = 0
    data['Cumulative Stats']['ICU Service Starters'] = 0
    data['Cumulative Stats']['CCU Service Starters'] = 0

    data['Cumulative Stats']['Emergency Server Busy Time'] = 0
    data['Cumulative Stats']['Preoperative Server Busy Time'] = 0
    data['Cumulative Stats']['Laboratory Server Busy Time'] = 0
    data['Cumulative Stats']['Operation Server Busy Time'] = 0
    data['Cumulative Stats']['General Ward Server Busy Time'] = 0
    data['Cumulative Stats']['ICU Server Busy Time'] = 0
    data['Cumulative Stats']['CCU Server Busy Time'] = 0

    data['Cumulative Stats']['Number of Repeated Operations For Patients With Complex Operation'] = 0

    data['Cumulative Stats']['Number of Immediately Addmited Emergency Patients'] = 0

    data['Cumulative Stats']['Patients With Complex Surgery'] = 0
    
    # Starting FEL
    future_event_list = list()
    future_event_list.append({'Event Type': 'Arrival', 'Event Time': 0, 'Patient': 'P1'})
    # fel_maker(future_event_list, 'Arrival', 0)
    return state, future_event_list, data


def exponential(lambd):
    r = random.random()
    return -(1 / lambd) * math.log(r)


def uniform(a, b):
    r = random.random()
    return a + (b - a) * r

def triangular(LB: float, M: float, UB: float) -> float:
    r = np.random.triangular(left=LB, mode=M, right=UB)
    return r


def fel_maker(future_event_list, event_type, clock, patient=None):  # Why?

    event_time = 0

    if event_type == 'Arrival':
        if data['Patients'][patient]['Patient Type'] == 'Normal':
            event_time = clock + exponential(1)
        else:
            C

    elif event_type == 'Laboratory Arrival':
        if data['Patients'][patient]['Patient Type'] == 'Normal':
            event_time = clock + 1
        else:
            event_time = clock + (10 / 60)

    elif event_type == 'Laboratory Departure':
        event_time = clock + uniform((28 / 60), (32 / 60))

    elif event_type == 'Operation Arrival':
        if data['Patients'][patient]['Patient Type'] == 'Normal':
            event_time = clock + 48
        else:
            event_time = clock + triangular((5 / 60), (75 / 60), (100 / 60))

    elif event_type == 'Operation Departure':
        if data['Patients'][patient]['Surgery Type'] == 'Simple':
            event_time = clock + (10 / 60) + random.normal(loc=(30.22 / 60), scale=(math.sqrt(4.96) / 60))
        elif data['Patients'][patient]['Surgery Type'] == 'Medium':
            event_time = clock + (10 / 60) + random.normal(loc=(74.54 / 60), scale=(math.sqrt(9.53) / 60))
        else:
            event_time = clock + (10 / 60) + random.normal(loc=(242.03 / 60), scale=(math.sqrt(63.27) / 60))

    elif event_type == 'Condition Deterioration':
        event_time = clock

    elif event_type == 'Care Unit Departure':
        event_time = clock + exponential(25)

    elif event_type == 'End of Service':
        event_time = clock + exponential(50)

    new_event = {'Event Type': event_type, 'Event Time': event_time, 'Patient': patient}
    future_event_list.append(new_event)


def arrival(future_event_list, state, clock, data, patient):
    data['Patients'][patient] = dict()
    data['Patients'][patient]['Arrival Time'] = clock  # track every move of this patient

    if random.random() >= 0.75:  # Normal Patient
        data['Patients'][patient]['Patient Type'] = 'Normal'
        if state['Preoperative Occupied Beds'] < 25:  # if there is an empty bed...
            state['Preoperative Occupied Beds'] += 1
            fel_maker(future_event_list, 'Laboratory Arrival', clock, patient)
            # data['Patients'][patient]['Time Service Begins'] = clock  # track "every move" of this patient
            # data['Cumulative Stats']['Service Starters'] += 1

        else:  # If there is no empty bed -> wait in queue
            # data['Cumulative Stats']['Area Under Queue Length Curve'] +=\
            #     state['Queue Length'] * (clock - data['Last Time Queue Length Changed'])
            state['Preoperative Queue'] += 1
            # data['Queue Customers'][customer] = clock  # add this customer to the queue
            # data['Last Time Queue Length Changed'] = clock

    else:  # Urgent Patient
        data['Patients'][patient]['Patient Type'] = 'Urgent'

    crn = random.random()
    if crn <= 0.5:  # Simple Surgery
        data['Patients'][patient]['Surgery Type'] = 'Simple'
    elif crn > 0.5 and crn <= 0.95:  # Medium Surgery
        data['Patients'][patient]['Surgery Type'] = 'Medium'
    else:  # Complex Surgery
        data['Patients'][patient]['Surgery Type'] = 'Complex'

    # Scheduling the next arrival
    # We know the current patient
    # Who will be the next patient? (Ex.: Current Patient = P1 -> Next Patient = P2)
    next_patient = 'P' + str(int(patient[1:]) + 1)
    fel_maker(future_event_list, 'Arrival', clock, next_patient)


def laboratory_arrival(future_event_list, state, clock, data, patient):
    if data['Patients'][patient]['Patient Type'] == 'Normal':  # if the patient is normal

        if state['Laboratory Occupied Beds'] < 3:  # if there is an empty bed
            state['Laboratory Occupied Beds'] += 1
            fel_maker(future_event_list, 'Laboratory Departure', clock, patient)

        else:  # if there is an empty bed -> wait in queue
            state['Laboratory Normal Queue'] += 1

    else:  # if the patient is urgent

        if state['Laboratory Occupied Beds'] < 3:  # if there is an empty bed
            state['Laboratory Occupied Beds'] += 1
            fel_maker(future_event_list, 'Laboratory Departure', clock, patient)

        else:  # if there is an empty bed -> wait in queue
            state['Laboratory Urgent Queue'] += 1


def laboratory_departure(future_event_list, state, clock, data, patient):
    fel_maker(future_event_list, 'Operation Arrival', clock, patient)

    if state['Laboratory Urgent Queue'] == 0:  # if there is no urgent patient in the queue

        if state['Laboratory Normal Queue'] == 0:  # if there is no normal patient in the queue
            state['Laboratory Occupied Beds'] -= 1

        else:  # there is at least one normal patient in the queue
            state['Laboratory Normal Queue'] -= 1
            fel_maker(future_event_list, 'Laboratory Departure', clock, patient)

    else:  # there is at least one urgent patient in the queue
        state['Laboratory Urgent Queue'] -= 0
        fel_maker(future_event_list, 'Laboratory Departure', clock, patient)


def operation_arrival(future_event_list, state, clock, data, patient):
    if data['Patients'][patient]['Patient Type'] == 'Normal':  # if the patient is normal

        if state['Operation Occupied Beds'] == 50:  # if there is no empty bed
            state['Surgery Normal Queue'] += 1

        else:  # there is an empty bed
            state['Operation Occupied Beds'] += 1
            fel_maker(future_event_list, 'Operation Departure', clock, patient)

            if state['Preoperative Queue'] == 0:  # if there is no patient in the preoperative queue
                state['Preoperative Occupied Beds'] -= 1

            else:  # there is at least one patient in the preoperative queue
                state['Preoperative Queue'] -= 1
                fel_maker(future_event_list, 'Laboratory Arrival', clock, patient)

    else:  # the patient is urgent

        if state['Operation Occupied Beds'] == 50:  # if there is no empty bed
            state['Surgery Urgent Queue'] += 1

        else:  # there is an empty bed
            state['Operation Occupied Beds'] += 1
            fel_maker(future_event_list, 'Operation Departure', clock, patient)

            if state['Emergency Queue'] == 0:  # if there is no patient in the emergency queue
                state['Emergency Occupied Beds'] -= 1

            else:  # there is at least one patient in the emergency queue
                state['Emergency Queue'] -= 1
                fel_maker(future_event_list, 'Laboratory Arrival', clock, patient)


def operation_departure(future_event_list, state, clock, data, patient):

    if data['Patients'][patient]['Surgery Type'] == 'Simple':  # if the surgery type is simple

        data['Patients'][patient]['Unit Type'] = 'General Ward'

        if state['General Ward Occupied Beds'] == 40:  # if there is no empty bed
            state['General Ward Queue'] += 1

        else:  # there is a empty bed
            state['General Ward Occupied Beds'] += 1
            fel_maker(future_event_list, 'End of Service', clock, patient)

    elif data['Patients'][patient]['Surgery Type'] == 'Medium':  # if the surgery type is medium
        crn = random.random()
        if crn <= 0.7:  # if the patient is sent to the general ward

            data['Patients'][patient]['Unit Type'] = 'General Ward'

            if state['General Ward Occupied Beds'] == 40:  # if there is no empty bed
                state['General Ward Queue'] += 1

            else:  # there is an empty bed
                state['General Ward Occupied Beds'] += 1
                fel_maker(future_event_list, 'End of Service', clock, patient)

        elif crn > 0.7 and crn <= 0.8:  # if the patient is sent to the ICU

            data['Patients'][patient]['Unit Type'] = 'ICU'

            if state['ICU Occupied Beds'] == 10:  # if there is no empty bed
                state['ICU Queue'] += 1

            else:  # there is an empty bed
                state['ICU Occupied Beds'] += 1
                fel_maker(future_event_list, 'Care Unit Departure', clock, patient)  # patient discharge from ICU or CCU

        else:  # if the patient is sent to the CCU

            data['Patients'][patient]['Unit Type'] = 'CCU'

            if state['CCU Occupied Beds'] == 5:  # if there is no empty bed
                state['CCU Queue'] += 1

            else:  # there is an empty bed
                state['CCU Occupied Beds'] += 1
                fel_maker(future_event_list, 'Care Unit Departure', clock, patient)  # patient discharge from ICU or CCU

    else:  # if the surgery type is complex

        if random.random() <= 0.1:  # if the patient dies
            data['Patients'].pop(patient, None)

        else:  # the patient doesn't die

            if random.random() <= 0.75:  # non-cardiac surgery

                data['Patients'][patient]['Unit Type'] = 'ICU'

                if state['ICU Occupied Beds'] == 10:  # if there is no empty bed
                    state['ICU Queue'] += 1

                else:  # there is an empty bed
                    state['ICU Occupied Beds'] += 1
                    fel_maker(future_event_list, 'Care Unit Departure', clock, patient)  # patient discharge from ICU or CCU

            else:  # cardiac surgery

                data['Patients'][patient]['Unit Type'] = 'CCU'

                if state['CCU Occupied Beds'] == 5:  # if there is no empty bed
                    state['CCU Queue'] += 1

                else:  # there is an empty bed
                    state['CCU Occupied Beds'] += 1
                    fel_maker(future_event_list, 'Care Unit Departure', clock, patient)  # patient discharge from ICU or CCU

    if state['Surgery Urgent Queue'] == 0:  # if there is no urgent patient in the queue

        if state['Surgery Normal Queue'] == 0:  # if there is no normal patient in the queue
            state['Operation Occupied Beds'] -= 1

        else:  # there is at least one normal patient in the queue
            state['Surgery Normal Queue'] -= 1
            fel_maker(future_event_list, 'Operation Departure', clock, patient)

    else:  # there is at least one urgent patient in the queue
        state['Surgery Urgent Queue'] -= 1
        fel_maker(future_event_list, 'Operation Departure', clock, patient)


def condition_deterioration(future_event_list, state, clock, data, patient):

    if state['Operation Occupied Beds'] == 50:  # if there is no empty bed in the operation room
        state['Surgery Urgent Queue'] += 1

    else:  # there is an empty bed
        state['Operation Occupied Beds'] += 1
        fel_maker(future_event_list, 'Operation Departure', clock, patient)

        if data['Patients'][patient]['Unit Type'] == 'ICU':  # if the unit where the patient was hospitalized is ICU

            if state['ICU Queue'] == 0:  # if there is no patient in the ICU queue
                state['ICU Occupied Beds'] -= 1

            else:  # there is at least one patient in the queue
                state['ICU Queue'] -= 1
                fel_maker(future_event_list, 'Care Unit Departure', clock, patient)

        elif data['Patients'][patient]['Unit Type'] == 'CCU':  # if the unit where the patient was hospitalized is CCU

            if state['CCU Queue'] == 0:  # if there is no patient in the CCU queue
                state['CCU Occupied Beds'] -= 1

            else:  # there is at least one patient in the queue
                state['CCU Queue'] -= 1
                fel_maker(future_event_list, 'Care Unit Departure', clock, patient)


def care_unit_departure(future_event_list, state, clock, data, patient):

    if state['General Ward Occupied Beds'] == 40:  # if there is no empty bed in the general ward
        state['General Ward Queue'] += 1

    else:  # there is an empty bed
        state['General Ward Occupied Beds'] += 1
        fel_maker(future_event_list, 'End of Service', clock, patient)

    if data['Patients'][patient]['Unit Type'] == 'ICU':  # if the unit where the patient was hospitalized is ICU

        if state['ICU Queue'] == 0:  # if there is no patient in the ICU queue
            state['ICU Occupied Beds'] -= 1

        else:  # there is at least one patient in the queue
            state['ICU Queue'] -= 1
            fel_maker(future_event_list, 'Care Unit Departure', clock, patient)

    elif data['Patients'][patient]['Unit Type'] == 'CCU':  # if the unit where the patient was hospitalized is CCU

        if state['CCU Queue'] == 0:  # if there is no patient in the CCU queue
            state['CCU Occupied Beds'] -= 1

        else:  # there is at least one patient in the queue
            state['CCU Queue'] -= 1
            fel_maker(future_event_list, 'Care Unit Departure', clock, patient)

def end_of_service(future_event_list, state, clock, data, patient):


    # # End of "service". Update Server Busy Time
    # data['Cumulative Stats']['Server Busy Time'] += clock - data['Customers'][customer]['Time Service Begins']
    # data['Customers'].pop(customer, None)
    #
    # if state['Queue Length'] == 0:
    #     state['Server Status'] = 0
    # else:
    #     # A queue and a free server
    #     # Who is going to get served first?
    #     first_customer_in_queue = min(data['Queue Customers'],
    #                                   key=data['Queue Customers'].get)  # key=lambda x: data['Queue Customers'][x]
    #     # This customer starts getting service
    #     data['Customers'][first_customer_in_queue]['Time Service Begins'] = clock
    #     # Update queue waiting time
    #     data['Cumulative Stats']['Queue Waiting Time'] += \
    #         clock - data['Customers'][first_customer_in_queue]['Arrival Time']
    #     # Queue length changes, so calculate the area under the current rectangle
    #     data['Cumulative Stats']['Area Under Queue Length Curve'] += \
    #         state['Queue Length'] * (clock - data['Last Time Queue Length Changed'])
    #     # Logic
    #     state['Queue Length'] -= 1
    #     # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
    #     data['Cumulative Stats']['Service Starters'] += 1
    #     # This customer no longer belongs to queue
    #     data['Queue Customers'].pop(first_customer_in_queue, None)
    #     # Queue length just changed. Update 'Last Time Queue Length Changed'
    #     data['Last Time Queue Length Changed'] = clock
    #     # Schedule 'End of Service' for this customer
    #     fel_maker(future_event_list, 'End of Service', clock, first_customer_in_queue)


def print_header():
    print('Event Type'.ljust(20) + '\t' + 'Time'.ljust(15) + '\t' +
          'Queue Length'.ljust(15) + '\t' + 'Server Status'.ljust(25))
    print('-------------------------------------------------------------------------------------------------')


def nice_print(current_state, current_event):
    print(str(current_event['Event Type']).ljust(20) + '\t' + str(round(current_event['Event Time'], 3)).ljust(15) +
          '\t' + str(current_state['Queue Length']).ljust(15) + '\t' + str(current_state['Server Status']).ljust(25))


def create_row(step, current_event, state, data, future_event_list):
    # This function will create a list, which will eventually become a row of the output Excel file

    sorted_fel = sorted(future_event_list, key=lambda x: x['Event Time'])

    # What should this row contain?
    # 1. Step, Clock, Event Type and Event Customer
    row = [step, current_event['Event Time'], current_event['Event Type'], current_event['Customer']]
    # 2. All state variables
    row.extend(list(state.values()))
    # 3. All Cumulative Stats
    row.extend(list(data['Cumulative Stats'].values()))

    # row = [step, current_event['Event Type'], current_event['Event Time'],
    #        state['Queue Length'], state['Server Status'], data['Cumulative Stats']['Server Busy Time'],
    #        data['Cumulative Stats']['Queue Waiting Time'],
    #        data['Cumulative Stats']['Area Under Queue Length Curve'], data['Cumulative Stats']['Service Starters']]

    # 4. All events in fel ('Event Time', 'Event Type' & 'Event Customer' for each event)
    for event in sorted_fel:
        row.append(event['Event Time'])
        row.append(event['Event Type'])
        row.append(event['Customer'])
    return row


def justify(table):
    # This function adds blanks to short rows in order to match their lengths to the maximum row length

    # Find maximum row length in the table
    row_max_len = 0
    for row in table:
        if len(row) > row_max_len:
            row_max_len = len(row)

    # For each row, add enough blanks
    for row in table:
        row.extend([""] * (row_max_len - len(row)))


def create_main_header(state, data):
    # This function creates the main part of header (returns a list)
    # A part of header which is used for future events will be created in create_excel()

    # Header consists of ...
    # 1. Step, Clock, Event Type and Event Customer
    header = ['Step', 'Clock', 'Event Type', 'Event Customer']
    # 2. Names of the state variables
    header.extend(list(state.keys()))
    # 3. Names of the cumulative stats
    header.extend(list(data['Cumulative Stats'].keys()))
    return header


def create_excel(table, header):
    # This function creates and fine-tunes the Excel output file

    # Find length of each row in the table
    row_len = len(table[0])

    # Find length of header (header does not include cells for fel at this moment)
    header_len = len(header)

    # row_len exceeds header_len by (max_fel_length * 3) (Event Type, Event Time & Customer for each event in FEL)
    # Extend the header with 'Future Event Time', 'Future Event Type', 'Future Event Customer'
    # for each event in the fel with maximum size
    i = 1
    for col in range((row_len - header_len) // 3):
        header.append('Future Event Time ' + str(i))
        header.append('Future Event Type ' + str(i))
        header.append('Future Event Customer ' + str(i))
        i += 1

    # Dealing with the output
    # First create a pandas DataFrame
    df = pd.DataFrame(table, columns=header, index=None)

    # Create a handle to work on the Excel file
    writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')

    # Write out the Excel file to the hard drive
    df.to_excel(writer, sheet_name='Single-server Queue Output', header=False, startrow=1, index=False)

    # Use the handle to get the workbook (just library syntax, can be found with a simple search)
    workbook = writer.book

    # Get the sheet you want to work on
    worksheet = writer.sheets['Single-server Queue Output']

    # Create a cell-formatter object (this will be used for the cells in the header, hence: header_formatter!)
    header_formatter = workbook.add_format()

    # Define whatever format you want
    header_formatter.set_align('center')
    header_formatter.set_align('vcenter')
    header_formatter.set_font('Times New Roman')
    header_formatter.set_bold('True')

    # Write out the column names and apply the format to the cells in the header row
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_formatter)

    # Auto-fit columns
    # Copied from https://stackoverflow.com/questions/29463274/simulate-autofit-column-in-xslxwriter
    for i, width in enumerate(get_col_widths(df)):
        worksheet.set_column(i - 1, i - 1, width)

    # Create a cell-formatter object for the body of excel file
    main_formatter = workbook.add_format()
    main_formatter.set_align('center')
    main_formatter.set_align('vcenter')
    main_formatter.set_font('Times New Roman')

    # Apply the format to the body cells
    for row in range(1, len(df) + 1):
        worksheet.set_row(row, None, main_formatter)

    # Save your edits
    writer.save()


def get_col_widths(dataframe):
    # Copied from https://stackoverflow.com/questions/29463274/simulate-autofit-column-in-xslxwriter
    # First we find the maximum length of the index column
    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]


def simulation(simulation_time):
    state, future_event_list, data = starting_state()
    clock = 0
    table = []  # a list of lists. Each inner list will be a row in the Excel output.
    step = 1  # every event counts as a step.
    future_event_list.append({'Event Type': 'End of Simulation', 'Event Time': simulation_time, 'Customer': None})
    # print_header()
    while clock < simulation_time:
        sorted_fel = sorted(future_event_list, key=lambda x: x['Event Time'])
        # print(sorted_fel)
        # print(data)
        current_event = sorted_fel[0]  # find imminent event
        clock = current_event['Event Time']  # advance time
        customer = current_event['Customer']  # find the customer of that event
        if clock < simulation_time:  # if current_event['Event Type'] != 'End of Simulation'  (Same)
            if current_event['Event Type'] == 'Arrival':
                arrival(future_event_list, state, clock, data, customer)
            elif current_event['Event Type'] == 'End of Service':
                end_of_service(future_event_list, state, clock, data, customer)
            future_event_list.remove(current_event)
        else:
            future_event_list.clear()

        # create a row in the table
        table.append(create_row(step, current_event, state, data, future_event_list))
        step += 1
        # nice_print(state, current_event)
    print('-------------------------------------------------------------------------------------------------')

    excel_main_header = create_main_header(state, data)
    justify(table)
    create_excel(table, excel_main_header)

    print('Simulation Ended!\n')
    Lq = data['Cumulative Stats']['Area Under Queue Length Curve'] / simulation_time
    Wq = data['Cumulative Stats']['Queue Waiting Time'] / data['Cumulative Stats']['Service Starters']
    rho = data['Cumulative Stats']['Server Busy Time'] / simulation_time

    print(f'Lq = {Lq}')
    print(f'Wq = {Wq}')
    print(f'rho = {rho}')

    print("\nChecking Little's Law")
    print(f'Lq = {Lq}')
    print(f'lambda * Wq = {(1 / 20) * Wq}')

    print('\nDo they match?')
    print(f'Ratio: {Lq / ((1 / 20) * Wq)}')

    if 0.9 < Lq / ((1 / 20) * Wq) < 1.1:
        print('Well... Almost!')


simulation(1000)
