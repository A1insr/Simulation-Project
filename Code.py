"""
Hospital Simulation
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

Authors: Arman Maghsoudi & Ali Nasr
Date: Winter 2025
"""

import random
import math
import numpy as np
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
    state['Power Outage'] = 0
    state['ICU Capacity'] = 10
    state['CCU Capacity'] = 5

    # Data: will save everything
    data = dict()
    data['Patients'] = dict()  # To track each customer, saving their arrival time, time service begins, etc.
    data['Preoperative Queue Patients'] = dict()  # Patient: Arrival Time, used to find first customer in the queue
    data['Emergency Queue Patients'] = dict()
    data['Laboratory Normal Queue Patients'] = dict()
    data['Laboratory Urgent Queue Patients'] = dict()
    data['Surgery Normal Queue Patients'] = dict()
    data['Surgery Urgent Queue Patients'] = dict()
    data['General Ward Queue Patients'] = dict()
    data['ICU Queue Patients'] = dict()
    data['CCU Queue Patients'] = dict()
    data['ICU Patients'] = list()
    data['CCU Patients'] = list()

    # Needed data to find maximum waiting time in each queue
    data['Preoperative Queue Waiting Times'] = dict()
    data['Emergency Queue Waiting Times'] = dict()
    data['Laboratory Normal Queue Waiting Times'] = dict()
    data['Laboratory Urgent Queue Waiting Times'] = dict()
    data['Operation Normal Queue Waiting Times'] = dict()
    data['Operation Urgent Queue Waiting Times'] = dict()
    data['General Ward Queue Waiting Times'] = dict()
    data['ICU Queue Waiting Times'] = dict()
    data['CCU Queue Waiting Times'] = dict()

    # Needed data to find maximum queue length for each queue
    data['Preoperative Queue Lengths'] = dict()
    data['Emergency Queue Lengths'] = dict()
    data['Laboratory Normal Queue Lengths'] = dict()
    data['Laboratory Urgent Queue Lengths'] = dict()
    data['Operation Normal Queue Lengths'] = dict()
    data['Operation Urgent Queue Lengths'] = dict()
    data['General Ward Queue Lengths'] = dict()
    data['ICU Queue Lengths'] = dict()
    data['CCU Queue Lengths'] = dict()

    # Cumulative Stats
    data['Last Time Emergency Queue Length Changed'] = 0  # Needed to calculate probability of a full emergency queue
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
    data['Cumulative Stats']['Laboratory Normal Service Starters'] = 0
    data['Cumulative Stats']['Laboratory Urgent Service Starters'] = 0
    data['Cumulative Stats']['Operation Normal Service Starters'] = 0
    data['Cumulative Stats']['Operation Urgent Service Starters'] = 0
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

    data['Cumulative Stats']['Number of Immediately Admitted Emergency Patients'] = 0

    data['Cumulative Stats']['Patients With Complex Surgery'] = 0

    # Starting FEL
    future_event_list = list()
    future_event_list.append({'Event Type': 'Arrival', 'Event Time': 0, 'Patient': 'P1', 'Patient Type': 'Normal'})
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


def fel_maker(future_event_list, event_type, clock, data, patient=None):
    event_time = 0

    if event_type == 'Arrival':
        if random.random() <= 0.75:  # Normal Patient
            patient_type = 'Normal'
            event_time = clock + exponential(1)
        else:
            patient_type = 'Urgent'
            event_time = clock + exponential(1 / 4)

        new_event = {'Event Type': event_type, 'Event Time': event_time, 'Patient': patient, 'Patient Type': patient_type}
        future_event_list.append(new_event)

    elif event_type == 'Power on':
        event_time = clock + 24  # one day of power outage

        new_event = {'Event Type': event_type, 'Event Time': event_time, 'Patient': None}
        future_event_list.append(new_event)

    else:
        if event_type == 'Laboratory Arrival':
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
                event_time = clock + (10 / 60) + np.random.normal(loc=(30.22 / 60), scale=(math.sqrt(4.96) / 60))
            elif data['Patients'][patient]['Surgery Type'] == 'Medium':
                event_time = clock + (10 / 60) + np.random.normal(loc=(74.54 / 60), scale=(math.sqrt(9.53) / 60))
            else:
                event_time = clock + (10 / 60) + np.random.normal(loc=(242.03 / 60), scale=(math.sqrt(63.27) / 60))

        elif event_type == 'Condition Deterioration':
            event_time = clock

        elif event_type == 'Care Unit Departure':
            event_time = clock + exponential(25)

        elif event_type == 'End of Service':
            event_time = clock + exponential(50)

        new_event = {'Event Type': event_type, 'Event Time': event_time, 'Patient': patient}
        future_event_list.append(new_event)


def arrival(future_event_list, state, clock, data, patient, patient_type):
    # data['Patients'][patient] = dict()
    # data['Patients'][patient]['Arrival Time'] = clock  # track every move of this patient

    if patient_type == 'Normal':  # Normal Patient
        data['Patients'][patient] = dict()
        data['Patients'][patient]['Arrival Time'] = clock  # track every move of this patient
        data['Patients'][patient]['Patient Type'] = 'Normal'

        crn = random.random()
        if crn <= 0.5:  # Simple Surgery
            data['Patients'][patient]['Surgery Type'] = 'Simple'
        elif 0.5 < crn <= 0.95:  # Medium Surgery
            data['Patients'][patient]['Surgery Type'] = 'Medium'
        else:  # Complex Surgery
            data['Patients'][patient]['Surgery Type'] = 'Complex'

            # Update number of 'Patients With Complex Surgery'
            data['Cumulative Stats']['Patients With Complex Surgery'] += 1

        if state['Preoperative Occupied Beds'] < 25:  # if there is an empty bed
            state['Preoperative Occupied Beds'] += 1
            # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
            data['Cumulative Stats']['Preoperative Service Starters'] += 1
            data['Patients'][patient]['Time Preoperative Service Begins'] = clock  # track "every move" of this patient
            fel_maker(future_event_list, 'Laboratory Arrival', clock, data, patient)

        else:  # there is no empty bed -> wait in queue
            # Queue length changes, so calculate the area under the current rectangle
            data['Cumulative Stats']['Area Under Preoperative Queue Length Curve'] += \
                (clock - data['Last Time Preoperative Queue Length Changed'])*(state['Preoperative Queue'])

            state['Preoperative Queue'] += 1
            data['Preoperative Queue Patients'][patient] = clock  # add this patient to the queue
            data['Preoperative Queue Lengths'][clock] = state['Preoperative Queue'] # Save queue length

            # Queue length just changed. Update 'Last Time Queue Length Changed'
            data['Last Time Preoperative Queue Length Changed'] = clock

        next_patient = 'P' + str(int(patient[1:]) + 1)
        fel_maker(future_event_list, 'Arrival', clock, data, next_patient)

    else:  # Urgent Patient
        if random.random() >= 0.005:  # if it's single entry
            # data['Patients'][patient]['Patient Type'] = 'Urgent'

            if state['Emergency Queue'] == 10:  # if the queue is full
                pass  # patient refusal

            else:  # the queue is not full
                data['Patients'][patient] = dict()
                data['Patients'][patient]['Arrival Time'] = clock  # track every move of this patient
                data['Patients'][patient]['Patient Type'] = 'Urgent'

                # Update number of 'Emergency Patients'
                data['Cumulative Stats']['Emergency Patients'] += 1

                crn = random.random()
                if crn <= 0.5:  # Simple Surgery
                    data['Patients'][patient]['Surgery Type'] = 'Simple'
                elif 0.5 < crn <= 0.95:  # Medium Surgery
                    data['Patients'][patient]['Surgery Type'] = 'Medium'
                else:  # Complex Surgery
                    data['Patients'][patient]['Surgery Type'] = 'Complex'

                    # Update number of 'Patients With Complex Surgery'
                    data['Cumulative Stats']['Patients With Complex Surgery'] += 1

                if state['Emergency Occupied Beds'] == 10:  # if there is no empty bed
                    print(f)
                    # Queue length changes, so calculate the area under the current rectangle
                    data['Cumulative Stats']['Area Under Emergency Queue Length Curve'] += \
                        (clock - data['Last Time Emergency Queue Length Changed'])*(state['Emergency Queue'])

                    state['Emergency Queue'] += 1
                    data['Emergency Queue Patients'][patient] = clock  # add this patient to the queue
                    data['Emergency Queue Lengths'][clock] = state['Emergency Queue'] # Save queue length

                    # Queue length just changed. Update 'Last Time Queue Length Changed'
                    data['Last Time Emergency Queue Length Changed'] = clock

                else:  # there is at least one empty bed
                    state['Emergency Occupied Beds'] += 1
                    # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
                    data['Cumulative Stats']['Emergency Service Starters'] += 1
                    print('a')
                    data['Patients'][patient]['Time Emergency Service Begins'] = clock  # track "every move" of this patient

                    # Update number of 'Number of Immediately Admitted Emergency Patients'
                    data['Cumulative Stats']['Number of Immediately Admitted Emergency Patients'] += 1

                    fel_maker(future_event_list, 'Laboratory Arrival', clock, data, patient)

            next_patient = 'P' + str(int(patient[1:]) + 1)
            fel_maker(future_event_list, 'Arrival', clock, data, next_patient)

        else:  # it's group entry
            epsilon = 1e-10
            GroupNumber = random.randint(2,5)
            if (10 - state['Emergency Occupied Beds']) >= GroupNumber:  # if there are enough empty beds
                for i in range(GroupNumber):
                    data['Patients']['P' + str(int(patient[1:]) + i)] = dict()
                    data['Patients']['P' + str(int(patient[1:]) + i)]['Arrival Time'] = clock + (i * epsilon)  # track every move of this patient
                    data['Patients']['P' + str(int(patient[1:]) + i)]['Patient Type'] = 'Urgent'
                    data['Patients']['P' + str(int(patient[1:]) + i)]['Time Emergency Service Begins'] = clock + (i * epsilon) # track "every move" of this patient

                    # Update number of 'Emergency Patients'
                    data['Cumulative Stats']['Emergency Patients'] += 1

                    # Update number of 'Number of Immediately Admitted Emergency Patients'
                    data['Cumulative Stats']['Number of Immediately Admitted Emergency Patients'] += 1

                    crn = random.random()
                    if crn <= 0.5:  # Simple Surgery
                        data['Patients']['P' + str(int(patient[1:]) + i)]['Surgery Type'] = 'Simple'
                    elif 0.5 < crn <= 0.95:  # Medium Surgery
                        data['Patients']['P' + str(int(patient[1:]) + i)]['Surgery Type'] = 'Medium'
                    else:  # Complex Surgery
                        data['Patients']['P' + str(int(patient[1:]) + i)]['Surgery Type'] = 'Complex'

                        # Update number of 'Patients With Complex Surgery'
                        data['Cumulative Stats']['Patients With Complex Surgery'] += 1

                    state['Emergency Occupied Beds'] += 1
                    # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
                    data['Cumulative Stats']['Emergency Service Starters'] += 1
                    print('b')
                    # data['Patients'][patient]['Time Emergency Service Begins'] = clock  # track "every move" of this patient
                    fel_maker(future_event_list, 'Laboratory Arrival', clock + (i * epsilon), data,
                              'P' + str(int(patient[1:]) + i))

            else:  # there aren't enough empty beds
                # patient refusal
                next_patient = 'P' + str(int(patient[1:]) + GroupNumber)
                fel_maker(future_event_list, 'Arrival', clock, data, next_patient)

    # crn = random.random()
    # if crn <= 0.5:  # Simple Surgery
    #     data['Patients'][patient]['Surgery Type'] = 'Simple'
    # elif crn > 0.5 and crn <= 0.95:  # Medium Surgery
    #     data['Patients'][patient]['Surgery Type'] = 'Medium'
    # else:  # Complex Surgery
    #     data['Patients'][patient]['Surgery Type'] = 'Complex'

    # # Scheduling the next arrival
    # next_patient = 'P' + str(int(patient[1:]) + 1)
    # fel_maker(future_event_list, 'Arrival', clock, next_patient)


def laboratory_arrival(future_event_list, state, clock, data, patient):
    data['Patients'][patient]['Laboratory Arrival Time'] = clock  # track every move of this patient

    if data['Patients'][patient]['Patient Type'] == 'Normal':  # if the patient is normal

        if state['Laboratory Occupied Beds'] < 3:  # if there is an empty bed
            state['Laboratory Occupied Beds'] += 1
            # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
            data['Cumulative Stats']['Laboratory Normal Service Starters'] += 1
            data['Patients'][patient]['Time Laboratory Service Begins'] = clock  # track "every move" of this patient
            fel_maker(future_event_list, 'Laboratory Departure', clock, data, patient)

        else:  # there is no empty bed -> wait in queue
            # Queue length changes, so calculate the area under the current rectangle
            data['Cumulative Stats']['Area Under Laboratory Normal Queue Length Curve'] += \
                (clock - data['Last Time Laboratory Normal Queue Length Changed'])*(state['Laboratory Normal Queue'])

            state['Laboratory Normal Queue'] += 1
            data['Laboratory Normal Queue Patients'][patient] = clock  # add this patient to the queue
            data['Laboratory Normal Queue Lengths'][clock] = state['Laboratory Normal Queue'] # Save queue length

            # Queue length just changed. Update 'Last Time Queue Length Changed'
            data['Last Time Laboratory Normal Queue Length Changed'] = clock

    else:  # if the patient is urgent

        if state['Laboratory Occupied Beds'] < 3:  # if there is an empty bed
            state['Laboratory Occupied Beds'] += 1
            # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
            data['Cumulative Stats']['Laboratory Urgent Service Starters'] += 1
            data['Patients'][patient]['Time Laboratory Service Begins'] = clock  # track "every move" of this patient
            fel_maker(future_event_list, 'Laboratory Departure', clock, data, patient)

        else:  # if there is no empty bed -> wait in queue
            # Queue length changes, so calculate the area under the current rectangle
            data['Cumulative Stats']['Area Under Laboratory Urgent Queue Length Curve'] += \
                (clock - data['Last Time Laboratory Urgent Queue Length Changed'])*(state['Laboratory Urgent Queue'])

            state['Laboratory Urgent Queue'] += 1
            data['Laboratory Urgent Queue Patients'][patient] = clock  # add this patient to the queue
            data['Laboratory Urgent Queue Lengths'][clock] = state['Laboratory Urgent Queue'] # Save queue length

            # Queue length just changed. Update 'Last Time Queue Length Changed'
            data['Last Time Laboratory Urgent Queue Length Changed'] = clock

def laboratory_departure(future_event_list, state, clock, data, patient):
    fel_maker(future_event_list, 'Operation Arrival', clock, data, patient)

    if data['Patients'][patient]['Patient Type'] == 'Normal':  # if the patient is normal
        # End of Preoperative Service Update Server Busy Time
        data['Cumulative Stats']['Preoperative Server Busy Time'] += (clock - data['Patients'][patient]['Time Preoperative Service Begins']) \
            *(state['Preoperative Occupied Beds']/25)

    else:  # if the patient is urgent
        # End of Emergency Service Update Server Busy Time
        data['Cumulative Stats']['Emergency Server Busy Time'] += (clock - data['Patients'][patient]['Time Emergency Service Begins']) \
            *(state['Emergency Occupied Beds']/10)

    # End of Laboratory Service Update Server Busy Time
    data['Cumulative Stats']['Laboratory Server Busy Time'] += (clock - data['Patients'][patient]['Time Laboratory Service Begins']) \
        *(state['Laboratory Occupied Beds']/3)

    if state['Laboratory Urgent Queue'] == 0:  # if there is no urgent patient in the queue

        if state['Laboratory Normal Queue'] == 0:  # if there is no normal patient in the queue
            state['Laboratory Occupied Beds'] -= 1

        else:  # there is at least one normal patient in the queue
            # Queue length changes, so calculate the area under the current rectangle
            data['Cumulative Stats']['Area Under Laboratory Normal Queue Length Curve'] += \
                (clock - data['Last Time Laboratory Normal Queue Length Changed'])*(state['Laboratory Normal Queue'])

            state['Laboratory Normal Queue'] -= 1
            data['Laboratory Normal Queue Lengths'][clock] = state['Laboratory Normal Queue'] # Save queue length

            # Queue length just changed. Update 'Last Time Queue Length Changed'
            data['Last Time Laboratory Normal Queue Length Changed'] = clock

            # Who is going to get served first?
            first_patient_in_queue = min(data['Laboratory Normal Queue Patients'],
                                         key=data['Laboratory Normal Queue Patients'].get)
            data['Laboratory Normal Queue Patients'].pop(first_patient_in_queue, None)

            # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
            data['Cumulative Stats']['Laboratory Normal Service Starters'] += 1
            data['Patients'][first_patient_in_queue]['Time Laboratory Service Begins'] = clock  # track "every move" of this patient

            # Update queue waiting time
            data['Cumulative Stats']['Laboratory Normal Queue Waiting Time'] += \
                (data['Patients'][first_patient_in_queue]['Time Laboratory Service Begins'] - \
                     data['Patients'][first_patient_in_queue]['Laboratory Arrival Time'])

            # Save the waiting time
            data['Laboratory Normal Queue Waiting Times'][first_patient_in_queue] =  (data['Patients'][first_patient_in_queue]['Time Laboratory Service Begins'] - \
                data['Patients'][first_patient_in_queue]['Laboratory Arrival Time'])


            # Schedule 'End of Service' for this patient
            fel_maker(future_event_list, 'Laboratory Departure', clock, data, first_patient_in_queue)

    else:  # there is at least one urgent patient in the queue
        # Queue length changes, so calculate the area under the current rectangle
        data['Cumulative Stats']['Area Under Laboratory Urgent Queue Length Curve'] += \
            (clock - data['Last Time Laboratory Urgent Queue Length Changed'])*(state['Laboratory Urgent Queue'])

        state['Laboratory Urgent Queue'] -= 1
        data['Laboratory Urgent Queue Lengths'][clock] = state['Laboratory Urgent Queue'] # Save queue length

        # Queue length just changed. Update 'Last Time Queue Length Changed'
        data['Last Time Laboratory Urgent Queue Length Changed'] = clock

        # Who is going to get served first?
        first_patient_in_queue = min(data['Laboratory Urgent Queue Patients'],
                                     key=data['Laboratory Urgent Queue Patients'].get)
        data['Laboratory Urgent Queue Patients'].pop(first_patient_in_queue, None)

        # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
        data['Cumulative Stats']['Laboratory Urgent Service Starters'] += 1
        data['Patients'][first_patient_in_queue]['Time Laboratory Service Begins'] = clock  # track "every move" of this patient

        # Update queue waiting time
        data['Cumulative Stats']['Laboratory Urgent Queue Waiting Time'] += \
            (data['Patients'][first_patient_in_queue]['Time Laboratory Service Begins'] - \
                data['Patients'][first_patient_in_queue]['Laboratory Arrival Time'])

        # Save the waiting time
        data['Laboratory Urgent Queue Waiting Times'][first_patient_in_queue] =  (data['Patients'][first_patient_in_queue]['Time Laboratory Service Begins'] - \
            data['Patients'][first_patient_in_queue]['Laboratory Arrival Time'])

        # Schedule 'End of Service' for this patient
        fel_maker(future_event_list, 'Laboratory Departure', clock, data, first_patient_in_queue)


def operation_arrival(future_event_list, state, clock, data, patient):
    data['Patients'][patient]['Operation Arrival Time'] = clock  # track every move of this patient

    if data['Patients'][patient]['Patient Type'] == 'Normal':  # if the patient is normal

        if state['Operation Occupied Beds'] == 50:  # if there is no empty bed
            # Queue length changes, so calculate the area under the current rectangle
            data['Cumulative Stats']['Area Under Surgery Normal Queue Length Curve'] += \
                (clock - data['Last Time Surgery Normal Queue Length Changed'])*(state['Surgery Normal Queue'])

            state['Surgery Normal Queue'] += 1
            data['Surgery Normal Queue Patients'][patient] = clock  # add this patient to the queue
            data['Operation Normal Queue Lengths'][clock] = state['Surgery Normal Queue'] # Save queue length

            # Queue length just changed. Update 'Last Time Queue Length Changed'
            data['Last Time Surgery Normal Queue Length Changed'] = clock

        else:  # there is an empty bed
            state['Operation Occupied Beds'] += 1
            # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
            data['Cumulative Stats']['Operation Normal Service Starters'] += 1
            data['Patients'][patient]['Time Operation Service Begins'] = clock  # track "every move" of this patient

            fel_maker(future_event_list, 'Operation Departure', clock, data, patient)

            if state['Preoperative Queue'] == 0:  # if there is no patient in the preoperative queue
                state['Preoperative Occupied Beds'] -= 1

            else:  # there is at least one patient in the preoperative queue
                # Queue length changes, so calculate the area under the current rectangle
                data['Cumulative Stats']['Area Under Preoperative Queue Length Curve'] += \
                    (clock - data['Last Time Preoperative Queue Length Changed'])*(state['Preoperative Queue'])

                state['Preoperative Queue'] -= 1
                data['Preoperative Queue Lengths'][clock] = state['Preoperative Queue'] # Save queue length

                # Queue length just changed. Update 'Last Time Queue Length Changed'
                data['Last Time Preoperative Queue Length Changed'] = clock

                # Who is going to get served first?
                first_patient_in_queue = min(data['Preoperative Queue Patients'],
                                             key=data['Preoperative Queue Patients'].get)
                data['Preoperative Queue Patients'].pop(first_patient_in_queue, None)

                # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
                data['Cumulative Stats']['Preoperative Service Starters'] += 1
                data['Patients'][first_patient_in_queue]['Time Preoperative Service Begins'] = clock  # track "every move" of this patient

                # Update queue waiting time
                data['Cumulative Stats']['Preoperative Queue Waiting Time'] += \
                    (data['Patients'][first_patient_in_queue]['Time Preoperative Service Begins'] - \
                        data['Patients'][first_patient_in_queue]['Arrival Time'])

                # Save the waiting time
                data['Preoperative Queue Waiting Times'][first_patient_in_queue] = (data['Patients'][first_patient_in_queue]['Time Preoperative Service Begins'] - \
                    data['Patients'][first_patient_in_queue]['Arrival Time'])

                # Schedule 'End of Service' for this patient
                fel_maker(future_event_list, 'Laboratory Arrival', clock, data, first_patient_in_queue)

    else:  # the patient is urgent

        if state['Operation Occupied Beds'] == 50:  # if there is no empty bed
            # Queue length changes, so calculate the area under the current rectangle
            data['Cumulative Stats']['Area Under Surgery Urgent Queue Length Curve'] += \
                (clock - data['Last Time Surgery Urgent Queue Length Changed'])*(state['Surgery Urgent Queue'])

            state['Surgery Urgent Queue'] += 1
            data['Surgery Urgent Queue Patients'][patient] = clock  # add this patient to the queue
            data['Operation Urgent Queue Lengths'][clock] = state['Surgery Urgent Queue'] # Save queue length

            # Queue length just changed. Update 'Last Time Queue Length Changed'
            data['Last Time Surgery Urgent Queue Length Changed'] = clock


        else:  # there is an empty bed
            state['Operation Occupied Beds'] += 1
            # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
            data['Cumulative Stats']['Operation Urgent Service Starters'] += 1
            data['Patients'][patient]['Time Operation Service Begins'] = clock  # track "every move" of this patient

            fel_maker(future_event_list, 'Operation Departure', clock, data, patient)

            if state['Emergency Queue'] == 0:  # if there is no patient in the emergency queue
                state['Emergency Occupied Beds'] -= 1

            else:  # there is at least one patient in the emergency queue
                print(e)
                if state['Emergency Queue'] == 10:
                    # Queue length changes, so at this moment we can calculate the time that the queue was full
                    data['Cumulative Stats']['Full Emergency Queue Duration'] += clock - data['Last Time Emergency Queue Length Changed']

                    # Queue length changes, so calculate the area under the current rectangle
                    data['Cumulative Stats']['Area Under Emergency Queue Length Curve'] += \
                        (clock - data['Last Time Emergency Queue Length Changed'])*(state['Emergency Queue'])

                    state['Emergency Queue'] -= 1
                    data['Emergency Queue Lengths'][clock] = state['Emergency Queue'] # Save queue length

                    # Queue length just changed. Update 'Last Time Queue Length Changed'
                    data['Last Time Emergency Queue Length Changed'] = clock

                    # Who is going to get served first?
                    first_patient_in_queue = min(data['Emergency Queue Patients'],
                                                 key=data['Emergency Queue Patients'].get)
                    data['Emergency Queue Patients'].pop(first_patient_in_queue, None)

                    # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
                    data['Cumulative Stats']['Emergency Service Starters'] += 1
                    print(c)
                    data['Patients'][first_patient_in_queue]['Time Emergency Service Begins'] = clock  # track "every move" of this patient

                    # Update queue waiting time
                    data['Cumulative Stats']['Emergency Queue Waiting Time'] += \
                        (data['Patients'][first_patient_in_queue]['Time Emergency Service Begins'] - \
                             data['Patients'][first_patient_in_queue]['Arrival Time'])

                    # Save the waiting time
                    data['Emergency Queue Waiting Times'][first_patient_in_queue] = (data['Patients'][first_patient_in_queue]['Time Emergency Service Begins'] - \
                        data['Patients'][first_patient_in_queue]['Arrival Time'])

                    # Check whether the patient is admitted immidiatley or not
                    if (clock-data['Patients'][first_patient_in_queue]['Arrival Time'] == 0):
                        # Update number of 'Number of Immediately Admitted Emergency Patients'
                        data['Cumulative Stats']['Number of Immediately Admitted Emergency Patients'] += 1

                    # Schedule 'End of Service' for this patient
                    fel_maker(future_event_list, 'Laboratory Arrival', clock, data, first_patient_in_queue)

                else:
                     # Queue length changes, so calculate the area under the current rectangle
                     data['Cumulative Stats']['Area Under Emergency Queue Length Curve'] += \
                         (clock - data['Last Time Emergency Queue Length Changed'])*(state['Emergency Queue'])

                     state['Emergency Queue'] -= 1
                     data['Emergency Queue Lengths'][clock] = state['Emergency Queue'] # Save queue length

                     # Queue length just changed. Update 'Last Time Queue Length Changed'
                     data['Last Time Emergency Queue Length Changed'] = clock

                     # Who is going to get served first?
                     first_patient_in_queue = min(data['Emergency Queue Patients'],
                                                  key=data['Emergency Queue Patients'].get)
                     data['Emergency Queue Patients'].pop(first_patient_in_queue, None)

                     # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
                     data['Cumulative Stats']['Emergency Service Starters'] += 1
                     print(d)
                     data['Patients'][first_patient_in_queue]['Time Emergency Service Begins'] = clock  # track "every move" of this patient

                     # Update queue waiting time
                     data['Cumulative Stats']['Emergency Queue Waiting Time'] += \
                         (data['Patients'][first_patient_in_queue]['Time Emergency Service Begins'] - \
                              data['Patients'][first_patient_in_queue]['Arrival Time'])

                     # Save the waiting time
                     data['Emergency Queue Waiting Times'][first_patient_in_queue] = (data['Patients'][first_patient_in_queue]['Time Emergency Service Begins'] - \
                         data['Patients'][first_patient_in_queue]['Arrival Time'])

                     # Check whether the patient is admitted immidiatley or not
                     if (clock-data['Patients'][first_patient_in_queue]['Arrival Time'] == 0):
                         # Update number of 'Number of Immediately Admitted Emergency Patients'
                         data['Cumulative Stats']['Number of Immediately Admitted Emergency Patients'] += 1

                     # Schedule 'End of Service' for this patient
                     fel_maker(future_event_list, 'Laboratory Arrival', clock, data, first_patient_in_queue)


def operation_departure(future_event_list, state, clock, data, patient):
    # End of Operation Service Update Server Busy Time
    data['Cumulative Stats']['Operation Server Busy Time'] += (clock - data['Patients'][patient]['Time Operation Service Begins']) \
        *(state['Operation Occupied Beds']/50)

    if data['Patients'][patient]['Surgery Type'] == 'Simple':  # if the surgery type is simple

        data['Patients'][patient]['Unit Type'] = 'General Ward'
        data['Patients'][patient]['General Ward Arrival Time'] = clock  # track every move of this patient

        if state['General Ward Occupied Beds'] == 40:  # if there is no empty bed
            # Queue length changes, so calculate the area under the current rectangle
            data['Cumulative Stats']['Area Under General Ward Queue Length Curve'] += \
                (clock - data['Last Time General Ward Queue Length Changed'])*(state['General Ward Queue'])

            state['General Ward Queue'] += 1
            data['General Ward Queue Patients'][patient] = clock  # add this patient to the queue
            data['General Ward Queue Lengths'][clock] = state['General Ward Queue'] # Save queue length

            # Queue length just changed. Update 'Last Time Queue Length Changed'
            data['Last Time General Ward Queue Length Changed'] = clock

        else:  # there is an empty bed
            state['General Ward Occupied Beds'] += 1
            # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
            data['Cumulative Stats']['General Ward Service Starters'] += 1
            data['Patients'][patient]['Time General Ward Service Begins'] = clock  # track "every move" of this patient
            fel_maker(future_event_list, 'End of Service', clock, data, patient)

    elif data['Patients'][patient]['Surgery Type'] == 'Medium':  # if the surgery type is medium
        crn = random.random()
        if crn <= 0.7:  # if the patient is sent to the general ward

            data['Patients'][patient]['Unit Type'] = 'General Ward'
            data['Patients'][patient]['General Ward Arrival Time'] = clock  # track every move of this patient

            if state['General Ward Occupied Beds'] == 40:  # if there is no empty bed
                # Queue length changes, so calculate the area under the current rectangle
                data['Cumulative Stats']['Area Under General Ward Queue Length Curve'] += \
                    (clock - data['Last Time General Ward Queue Length Changed'])*(state['General Ward Queue'])

                state['General Ward Queue'] += 1
                data['General Ward Queue Patients'][patient] = clock  # add this patient to the queue
                data['General Ward Queue Lengths'][clock] = state['General Ward Queue'] # Save queue length

                # Queue length just changed. Update 'Last Time Queue Length Changed'
                data['Last Time General Ward Queue Length Changed'] = clock

            else:  # there is an empty bed
                state['General Ward Occupied Beds'] += 1
                # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
                data['Cumulative Stats']['General Ward Service Starters'] += 1
                data['Patients'][patient]['Time General Ward Service Begins'] = clock  # track "every move" of this patient
                fel_maker(future_event_list, 'End of Service', clock, data, patient)

        elif 0.7 < crn <= 0.8:  # if the patient is sent to the ICU

            data['Patients'][patient]['Unit Type'] = 'ICU'
            data['Patients'][patient]['ICU Arrival Time'] = clock  # track every move of this patient

            if len(data['ICU Patients']) >= state['ICU Capacity']:  # if there is no empty bed
                # Queue length changes, so calculate the area under the current rectangle
                data['Cumulative Stats']['Area Under ICU Queue Length Curve'] += \
                    (clock - data['Last Time ICU Queue Length Changed'])*(state['ICU Queue'])

                state['ICU Queue'] += 1
                data['ICU Queue Patients'][patient] = clock  # add this patient to the queue
                data['ICU Queue Lengths'][clock] = state['ICU Queue']  # Save queue length

                # Queue length just changed. Update 'Last Time Queue Length Changed'
                data['Last Time ICU Queue Length Changed'] = clock

            else:  # there is an empty bed
                state['ICU Occupied Beds'] += 1
                data['ICU Patients'].append(patient)
                # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
                data['Cumulative Stats']['ICU Service Starters'] += 1
                data['Patients'][patient]['Time ICU Service Begins'] = clock  # track "every move" of this patient
                fel_maker(future_event_list, 'Care Unit Departure', clock, data, patient)  # patient discharge from ICU or CCU

        else:  # if the patient is sent to the CCU

            data['Patients'][patient]['Unit Type'] = 'CCU'
            data['Patients'][patient]['CCU Arrival Time'] = clock  # track every move of this patient

            if len(data['CCU Patients']) >= state['CCU Capacity']:  # if there is no empty bed
                # Queue length changes, so calculate the area under the current rectangle
                data['Cumulative Stats']['Area Under CCU Queue Length Curve'] += \
                    (clock - data['Last Time CCU Queue Length Changed'])*(state['CCU Queue'])

                state['CCU Queue'] += 1
                data['CCU Queue Patients'][patient] = clock  # add this patient to the queue
                data['CCU Queue Lengths'][clock] = state['CCU Queue'] # Save queue length

                # Queue length just changed. Update 'Last Time Queue Length Changed'
                data['Last Time CCU Queue Length Changed'] = clock

            else:  # there is an empty bed
                state['CCU Occupied Beds'] += 1
                data['CCU Patients'].append(patient)
                # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
                data['Cumulative Stats']['CCU Service Starters'] += 1
                data['Patients'][patient]['Time CCU Service Begins'] = clock  # track "every move" of this patient
                fel_maker(future_event_list, 'Care Unit Departure', clock, data,
                          patient)  # patient discharge from ICU or CCU

    else:  # if the surgery type is complex

        if random.random() <= 0.1:  # if the patient dies
            data['Patients'].pop(patient, None)

        else:  # the patient doesn't die

            if random.random() <= 0.75:  # non-cardiac surgery

                data['Patients'][patient]['Unit Type'] = 'ICU'
                data['Patients'][patient]['ICU Arrival Time'] = clock  # track every move of this patient

                if len(data['ICU Patients']) >= state['ICU Capacity']:  # if there is no empty bed
                    # Queue length changes, so calculate the area under the current rectangle
                    data['Cumulative Stats']['Area Under ICU Queue Length Curve'] += \
                        (clock - data['Last Time ICU Queue Length Changed'])*(state['ICU Queue'])

                    state['ICU Queue'] += 1
                    data['ICU Queue Patients'][patient] = clock  # add this patient to the queue
                    data['ICU Queue Lengths'][clock] = state['ICU Queue'] # Save queue length

                    # Queue length just changed. Update 'Last Time Queue Length Changed'
                    data['Last Time ICU Queue Length Changed'] = clock

                else:  # there is an empty bed
                    state['ICU Occupied Beds'] += 1
                    data['ICU Patients'].append(patient)
                    # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
                    data['Cumulative Stats']['ICU Service Starters'] += 1
                    data['Patients'][patient]['Time ICU Service Begins'] = clock  # track "every move" of this patient
                    fel_maker(future_event_list, 'Care Unit Departure', clock, data,
                              patient)  # patient discharge from ICU or CCU

            else:  # cardiac surgery
                data['Patients'][patient]['Unit Type'] = 'CCU'
                data['Patients'][patient]['CCU Arrival Time'] = clock  # track every move of this patient

                if len(data['CCU Patients']) >= state['CCU Capacity']:  # if there is no empty bed
                    # Queue length changes, so calculate the area under the current rectangle
                    data['Cumulative Stats']['Area Under CCU Queue Length Curve'] += \
                        (clock - data['Last Time CCU Queue Length Changed'])*(state['CCU Queue'])

                    state['CCU Queue'] += 1
                    data['CCU Queue Patients'][patient] = clock  # add this patient to the queue
                    data['CCU Queue Lengths'][clock] = state['CCU Queue'] # Save queue length

                    # Queue length just changed. Update 'Last Time Queue Length Changed'
                    data['Last Time CCU Queue Length Changed'] = clock

                else:  # there is an empty bed
                    state['CCU Occupied Beds'] += 1
                    data['CCU Patients'].append(patient)
                    # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
                    data['Cumulative Stats']['CCU Service Starters'] += 1
                    data['Patients'][patient]['Time CCU Service Begins'] = clock  # track "every move" of this patient
                    fel_maker(future_event_list, 'Care Unit Departure', clock, data,
                              patient)  # patient discharge from ICU or CCU

    if state['Surgery Urgent Queue'] == 0:  # if there is no urgent patient in the queue

        if state['Surgery Normal Queue'] == 0:  # if there is no normal patient in the queue
            state['Operation Occupied Beds'] -= 1

        else:  # there is at least one normal patient in the queue
            # Queue length changes, so calculate the area under the current rectangle
            data['Cumulative Stats']['Area Under Surgery Normal Queue Length Curve'] += \
                (clock - data['Last Time Surgery Normal Queue Length Changed'])*(state['Surgery Normal Queue'])

            state['Surgery Normal Queue'] -= 1
            data['Operation Normal Queue Lengths'][clock] = state['Surgery Normal Queue'] # Save queue length

            # Queue length just changed. Update 'Last Time Queue Length Changed'
            data['Last Time Surgery Normal Queue Length Changed'] = clock

            # Who is going to get served first?
            first_patient_in_queue = min(data['Surgery Normal Queue Patients'],
                                         key=data['Surgery Normal Queue Patients'].get)
            data['Surgery Normal Queue Patients'].pop(first_patient_in_queue, None)

            # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
            data['Cumulative Stats']['Operation Normal Service Starters'] += 1
            data['Patients'][first_patient_in_queue]['Time Operation Service Begins'] = clock  # track "every move" of this patient

            # Update queue waiting time
            data['Cumulative Stats']['Operation Normal Queue Waiting Time'] += \
                (data['Patients'][first_patient_in_queue]['Time Operation Service Begins'] - \
                    data['Patients'][first_patient_in_queue]['Operation Arrival Time'])

            # Save the waiting time
            data['Operation Normal Queue Waiting Times'][first_patient_in_queue] = (data['Patients'][first_patient_in_queue]['Time Operation Service Begins'] - \
                data['Patients'][first_patient_in_queue]['Operation Arrival Time'])

            # Schedule 'End of Service' for this patient
            fel_maker(future_event_list, 'Operation Departure', clock, data, first_patient_in_queue)

    else:  # there is at least one urgent patient in the queue
        # Queue length changes, so calculate the area under the current rectangle
        data['Cumulative Stats']['Area Under Surgery Urgent Queue Length Curve'] += \
            (clock - data['Last Time Surgery Urgent Queue Length Changed'])*(state['Surgery Urgent Queue'])

        state['Surgery Urgent Queue'] -= 1
        data['Operation Urgent Queue Lengths'][clock] = state['Surgery Urgent Queue'] # Save queue length

        # Queue length just changed. Update 'Last Time Queue Length Changed'
        data['Last Time Surgery Urgent Queue Length Changed'] = clock

        # Who is going to get served first?
        first_patient_in_queue = min(data['Surgery Urgent Queue Patients'],
                                     key=data['Surgery Urgent Queue Patients'].get)
        data['Surgery Urgent Queue Patients'].pop(first_patient_in_queue, None)

        # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
        data['Cumulative Stats']['Operation Urgent Service Starters'] += 1
        data['Patients'][first_patient_in_queue]['Time Operation Service Begins'] = clock  # track "every move" of this patient

        # Update queue waiting time
        data['Cumulative Stats']['Operation Urgent Queue Waiting Time'] += \
            (data['Patients'][first_patient_in_queue]['Time Operation Service Begins'] - \
                data['Patients'][first_patient_in_queue]['Operation Arrival Time'])

        # Save the waiting time
        data['Operation Urgent Queue Waiting Times'][first_patient_in_queue] = (data['Patients'][first_patient_in_queue]['Time Operation Service Begins'] - \
            data['Patients'][first_patient_in_queue]['Operation Arrival Time'])


        # Schedule 'Operation Departure' for this patient
        fel_maker(future_event_list, 'Operation Departure', clock, data, first_patient_in_queue)


def care_unit_departure(future_event_list, state, clock, data, patient):

    if random.random() <= 0.001:  # if the patient's condition worsens

        # Update number of 'Number of Repeated Operations For Patients With Complex Operation'
        data['Cumulative Stats']['Number of Repeated Operations For Patients With Complex Operation'] += 1
        fel_maker(future_event_list, 'Condition Deterioration', clock, data, patient)

    else:
        data['Patients'][patient]['General Ward Arrival Time'] = clock  # track every move of this patient
        if state['General Ward Occupied Beds'] == 40:  # if there is no empty bed in the general ward

            # Queue length changes, so calculate the area under the current rectangle
            data['Cumulative Stats']['Area Under General Ward Queue Length Curve'] += \
                (clock - data['Last Time General Ward Queue Length Changed'])*(state['General Ward Queue'])

            state['General Ward Queue'] += 1
            data['General Ward Queue Patients'][patient] = clock  # add this patient to the queue
            data['General Ward Queue Lengths'][clock] = state['General Ward Queue'] # Save queue length

            # Queue length just changed. Update 'Last Time Queue Length Changed'
            data['Last Time General Ward Queue Length Changed'] = clock

        else:  # there is an empty bed
            state['General Ward Occupied Beds'] += 1
            # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
            data['Cumulative Stats']['General Ward Service Starters'] += 1
            data['Patients'][patient]['Time General Ward Service Begins'] = clock  # track "every move" of this patient
            fel_maker(future_event_list, 'End of Service', clock, data, patient)

    if data['Patients'][patient]['Unit Type'] == 'ICU':  # if the unit where the patient was hospitalized is ICU
        data['ICU Patients'].remove(patient)

        # End of ICU Service Update Server Busy Time
        data['Cumulative Stats']['ICU Server Busy Time'] += (clock - data['Patients'][patient]['Time ICU Service Begins']) \
            *(state['ICU Occupied Beds']/10)

        if state['ICU Queue'] == 0:  # if there is no patient in the ICU queue
            state['ICU Occupied Beds'] -= 1

        else:  # there is at least one patient in the queue
            # Queue length changes, so calculate the area under the current rectangle
            data['Cumulative Stats']['Area Under ICU Queue Length Curve'] += \
                (clock - data['Last Time ICU Queue Length Changed'])*(state['ICU Queue'])

            state['ICU Queue'] -= 1
            data['ICU Queue Lengths'][clock] = state['ICU Queue']  # Save queue length

            # Queue length just changed. Update 'Last Time Queue Length Changed'
            data['Last Time ICU Queue Length Changed'] = clock

            # Who is going to get served first?
            first_patient_in_queue = min(data['ICU Queue Patients'],
                                         key=data['ICU Queue Patients'].get)
            data['ICU Queue Patients'].pop(first_patient_in_queue, None)
            data['ICU Patients'].append(first_patient_in_queue)

            # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
            data['Cumulative Stats']['ICU Service Starters'] += 1
            data['Patients'][first_patient_in_queue]['Time ICU Service Begins'] = clock  # track "every move" of this patient

            # Update queue waiting time
            data['Cumulative Stats']['ICU Queue Waiting Time'] += \
                (data['Patients'][first_patient_in_queue]['Time ICU Service Begins'] - \
                    data['Patients'][first_patient_in_queue]['ICU Arrival Time'])

            # Save the waiting time
            data['ICU Queue Waiting Times'][first_patient_in_queue] = (data['Patients'][first_patient_in_queue]['Time ICU Service Begins'] - \
                data['Patients'][first_patient_in_queue]['ICU Arrival Time'])

            # Schedule 'End of Service' for this patient
            fel_maker(future_event_list, 'Care Unit Departure', clock, data, first_patient_in_queue)

    elif data['Patients'][patient]['Unit Type'] == 'CCU':  # if the unit where the patient was hospitalized is CCU
        data['CCU Patients'].remove(patient)

        # End of CCU Service Update Server Busy Time
        data['Cumulative Stats']['CCU Server Busy Time'] += (clock - data['Patients'][patient]['Time CCU Service Begins']) \
            *(state['CCU Occupied Beds']/5)

        if state['CCU Queue'] == 0:  # if there is no patient in the CCU queue
            state['CCU Occupied Beds'] -= 1

        else:  # there is at least one patient in the queue
            # Queue length changes, so calculate the area under the current rectangle
            data['Cumulative Stats']['Area Under CCU Queue Length Curve'] += \
                (clock - data['Last Time CCU Queue Length Changed'])*(state['CCU Queue'])

            state['CCU Queue'] -= 1
            data['CCU Queue Lengths'][clock] = state['CCU Queue'] # Save queue length

            # Queue length just changed. Update 'Last Time Queue Length Changed'
            data['Last Time CCU Queue Length Changed'] = clock

            # Who is going to get served first?
            first_patient_in_queue = min(data['CCU Queue Patients'],
                                         key=data['CCU Queue Patients'].get)
            data['CCU Queue Patients'].pop(first_patient_in_queue, None)
            data['CCU Patients'].append(first_patient_in_queue)

            # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
            data['Cumulative Stats']['CCU Service Starters'] += 1
            data['Patients'][first_patient_in_queue]['Time CCU Service Begins'] = clock  # track "every move" of this patient

            # Update queue waiting time
            data['Cumulative Stats']['CCU Queue Waiting Time'] += \
                (data['Patients'][first_patient_in_queue]['Time CCU Service Begins'] - \
                    data['Patients'][first_patient_in_queue]['CCU Arrival Time'])

            # Save the waiting time
            data['CCU Queue Waiting Times'][first_patient_in_queue] = (data['Patients'][first_patient_in_queue]['Time CCU Service Begins'] - \
                data['Patients'][first_patient_in_queue]['CCU Arrival Time'])

            # Schedule 'End of Service' for this patient
            fel_maker(future_event_list, 'Care Unit Departure', clock, data, first_patient_in_queue)


def condition_deterioration(future_event_list, state, clock, data, patient):
    data['Patients'][patient]['Patient Type'] = 'Urgent'  # the patient will be urgent

    data['Patients'][patient]['Operation Arrival Time'] = clock  # track every move of this patient

    if state['Operation Occupied Beds'] == 50:  # if there is no empty bed in the operation room
        # Queue length changes, so calculate the area under the current rectangle
        data['Cumulative Stats']['Area Under Surgery Urgent Queue Length Curve'] += \
            (clock - data['Last Time Surgery Urgent Queue Length Changed'])*(state['Surgery Urgent Queue'])

        state['Surgery Urgent Queue'] += 1
        data['Surgery Urgent Queue Patients'][patient] = clock  # add this patient to the queue
        data['Operation Urgent Queue Lengths'][clock] = state['Surgery Urgent Queue'] # Save queue length

        # Queue length just changed. Update 'Last Time Queue Length Changed'
        data['Last Time Surgery Urgent Queue Length Changed'] = clock


    else:  # there is an empty bed
        state['Operation Occupied Beds'] += 1
        # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
        data['Cumulative Stats']['Operation Urgent Service Starters'] += 1
        data['Patients'][patient]['Time Operation Service Begins'] = clock  # track "every move" of this patient
        fel_maker(future_event_list, 'Operation Departure', clock, data, patient)

    # if data['Patients'][patient]['Unit Type'] == 'ICU':  # if the unit where the patient was hospitalized is ICU
    #
    #     if state['ICU Queue'] == 0:  # if there is no patient in the ICU queue
    #         state['ICU Occupied Beds'] -= 1
    #
    #     else:  # there is at least one patient in the queue
    #         state['ICU Queue'] -= 1
    #
    #         # Who is going to get served first?
    #         first_patient_in_queue = min(data['ICU Queue Patients'],
    #                                      key=data['ICU Queue Patients'].get)
    #         data['ICU Queue Patients'].pop(first_patient_in_queue, None)
    #         # Schedule 'End of Service' for this patient
    #         fel_maker(future_event_list, 'Care Unit Departure', clock, first_patient_in_queue)
    #
    # elif data['Patients'][patient]['Unit Type'] == 'CCU':  # if the unit where the patient was hospitalized is CCU
    #
    #     if state['CCU Queue'] == 0:  # if there is no patient in the CCU queue
    #         state['CCU Occupied Beds'] -= 1
    #
    #     else:  # there is at least one patient in the queue
    #         state['CCU Queue'] -= 1
    #
    #         # Who is going to get served first?
    #         first_patient_in_queue = min(data['CCU Queue Patients'],
    #                                      key=data['CCU Queue Patients'].get)
    #         data['CCU Queue Patients'].pop(first_patient_in_queue, None)
    #         # Schedule 'End of Service' for this patient
    #         fel_maker(future_event_list, 'Care Unit Departure', clock, first_patient_in_queue)


def power_off(future_event_list, state, clock, data):
    state['Power Outage'] = 1
    state['ICU Capacity'] = state['ICU Capacity'] * 0.8
    state['CCU Capacity'] = state['CCU Capacity'] * 0.8
    fel_maker(future_event_list, 'Power On', clock, data)


def power_on(state):
    state['Power Outage'] = 0
    state['ICU Capacity'] = state['ICU Capacity'] * 1.25
    state['CCU Capacity'] = state['CCU Capacity'] * 1.25


def end_of_service(future_event_list, state, clock, data, patient):
    #  End of "service". Update System Waiting Time and count number of patients.
    data['Cumulative Stats']['System Waiting Time'] += clock - data['Patients'][patient]['Arrival Time']
    data['Cumulative Stats']['Total Patients'] += 1

    # End of General Ward Service Update Server Busy Time
    data['Cumulative Stats']['General Ward Server Busy Time'] += (clock - data['Patients'][patient]['Time General Ward Service Begins']) \
        *(state['General Ward Occupied Beds']/40)

    data['Patients'].pop(patient, None)

    if state['General Ward Queue'] == 0:  # if there is no patient in the queue
        state['General Ward Occupied Beds'] -= 1

    else:  # there is at least one patient in the queue
        # Queue length changes, so calculate the area under the current rectangle
        data['Cumulative Stats']['Area Under General Ward Queue Length Curve'] += \
            (clock - data['Last Time General Ward Queue Length Changed'])*(state['General Ward Queue'])

        state['General Ward Queue'] -= 1
        data['General Ward Queue Lengths'][clock] = state['General Ward Queue'] # Save queue length

        # Queue length just changed. Update 'Last Time Queue Length Changed'
        data['Last Time General Ward Queue Length Changed'] = clock

        # Who is going to get served first?
        first_patient_in_queue = min(data['General Ward Queue Patients'],
                                     key=data['General Ward Queue Patients'].get)
        data['General Ward Queue Patients'].pop(first_patient_in_queue, None)

        # Someone just started getting service. Update 'Service Starters' (Needed to calculate Wq)
        data['Cumulative Stats']['General Ward Service Starters'] += 1
        data['Patients'][first_patient_in_queue]['Time General Ward Service Begins'] = clock  # track "every move" of this patient

        # Update queue waiting time
        data['Cumulative Stats']['General Ward Queue Waiting Time'] += \
            (data['Patients'][first_patient_in_queue]['Time General Ward Service Begins'] - \
                data['Patients'][first_patient_in_queue]['General Ward Arrival Time'])

        # Save the waiting time
        data['General Ward Queue Waiting Times'][first_patient_in_queue] = (data['Patients'][first_patient_in_queue]['Time General Ward Service Begins'] - \
            data['Patients'][first_patient_in_queue]['General Ward Arrival Time'])

        # Schedule 'End of Service' for this patient
        fel_maker(future_event_list, 'End of Service', clock, data, first_patient_in_queue)


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
    # 1. Step, Clock, Event Type and Event Patient
    row = [step, current_event['Event Time'], current_event['Event Type'], current_event['Patient']]
    # 2. All state variables
    row.extend(list(state.values()))
    # 3. All Cumulative Stats
    row.extend(list(data['Cumulative Stats'].values()))
    # 4. All events in fel ('Event Time', 'Event Type' & 'Event Customer' for each event)
    for event in sorted_fel:
        row.append(event['Event Time'])
        row.append(event['Event Type'])
        row.append(event['Patient'])
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
    # 1. Step, Clock, Event Type and Event Patient
    header = ['Step', 'Clock', 'Event Type', 'Event Patient']
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
    # Extend the header with 'Future Event Time', 'Future Event Type', 'Future Event Patient'
    # for each event in the fel with maximum size
    i = 1
    for col in range((row_len - header_len) // 3):
        header.append('Future Event Time ' + str(i))
        header.append('Future Event Type ' + str(i))
        header.append('Future Event Patient ' + str(i))
        i += 1

    # Dealing with the output
    # First create a pandas DataFrame
    df = pd.DataFrame(table, columns=header, index=None)

    # Create a handle to work on the Excel file
    writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')

    # Write out the Excel file to the hard drive
    df.to_excel(writer, sheet_name='Initial State Output', header=False, startrow=1, index=False)

    # Use the handle to get the workbook (just library syntax, can be found with a simple search)
    workbook = writer.book

    # Get the sheet you want to work on
    worksheet = writer.sheets['Initial State Output']

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

    # Create a cell-formatter object for the body of Excel file
    main_formatter = workbook.add_format()
    main_formatter.set_align('center')
    main_formatter.set_align('vcenter')
    main_formatter.set_font('Times New Roman')

    # Apply the format to the body cells
    for row in range(1, len(df) + 1):
        worksheet.set_row(row, None, main_formatter)

    # Save your edits
    writer.close()


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
    future_event_list.append({'Event Type': 'Power Off', 'Event Time': uniform(0, 720), 'Patient': None})
    future_event_list.append({'Event Type': 'End of Simulation', 'Event Time': simulation_time, 'Patient': None})
    # print_header()
    while clock < simulation_time:
        sorted_fel = sorted(future_event_list, key=lambda x: x['Event Time'])
        print(sorted_fel)
        # print(data)
        current_event = sorted_fel[0]  # find imminent event
        clock = current_event['Event Time']  # advance time
        patient = current_event['Patient']  # find the patient of that event
        if clock < simulation_time:  # if current_event['Event Type'] != 'End of Simulation'  (Same)
            if current_event['Event Type'] == 'Arrival':
                patient_type = current_event['Patient Type']  # find the patient type
                arrival(future_event_list, state, clock, data, patient, patient_type)

            elif current_event['Event Type'] == 'Laboratory Arrival':
                laboratory_arrival(future_event_list, state, clock, data, patient)

            elif current_event['Event Type'] == 'Laboratory Departure':
                laboratory_departure(future_event_list, state, clock, data, patient)

            elif current_event['Event Type'] == 'Operation Arrival':
                operation_arrival(future_event_list, state, clock, data, patient)

            elif current_event['Event Type'] == 'Operation Departure':
                operation_departure(future_event_list, state, clock, data, patient)

            elif current_event['Event Type'] == 'Condition Deterioration':
                condition_deterioration(future_event_list, state, clock, data, patient)

            elif current_event['Event Type'] == 'Care Unit Departure':
                care_unit_departure(future_event_list, state, clock, data, patient)

            elif current_event['Event Type'] == 'Power Off':
                power_off(future_event_list, state, clock, data)

            elif current_event['Event Type'] == 'Power On':
                power_on(state)

            elif current_event['Event Type'] == 'End of Service':
                end_of_service(future_event_list, state, clock, data, patient)

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
    # Lq = data['Cumulative Stats']['Area Under Queue Length Curve'] / simulation_time
    # Wq = data['Cumulative Stats']['Queue Waiting Time'] / data['Cumulative Stats']['Service Starters']
    # rho = data['Cumulative Stats']['Server Busy Time'] / simulation_time

    # Criteria_1
    average_time_in_system = data['Cumulative Stats']['System Waiting Time'] / data['Cumulative Stats']['Total Patients']

    # Criteria_2
    Full_Emergency_Queue_Probability = data['Cumulative Stats']['Full Emergency Queue Duration'] / simulation_time

    # Criteria_3
    average_complex_operation_reoperations = data['Cumulative Stats']['Number of Repeated Operations For Patients With Complex Operation'] \
        / data['Cumulative Stats']['Patients With Complex Surgery']

    # Criteria_6
    immediately_admitted_emergency_patients_percentage = (data['Cumulative Stats']['Number of Immediately Admitted Emergency Patients']  \
        / data['Cumulative Stats']['Emergency Patients']) * 100

    # Criteria_5
    rho_Emergency = data['Cumulative Stats']['Emergency Server Busy Time'] / simulation_time
    rho_Preoperative = data['Cumulative Stats']['Preoperative Server Busy Time'] / simulation_time
    rho_Laboratory = data['Cumulative Stats']['Laboratory Server Busy Time'] / simulation_time
    rho_Operation = data['Cumulative Stats']['Operation Server Busy Time'] / simulation_time
    rho_General_Ward = data['Cumulative Stats']['General Ward Server Busy Time'] / simulation_time
    rho_ICU = data['Cumulative Stats']['ICU Server Busy Time'] / simulation_time
    rho_CCU = data['Cumulative Stats']['CCU Server Busy Time'] / simulation_time

    # Criteria_4
    # Average Queue Length for each queue
    Lq_Emergency = data['Cumulative Stats']['Area Under Emergency Queue Length Curve'] / simulation_time
    Lq_Preoperative = data['Cumulative Stats']['Area Under Preoperative Queue Length Curve'] / simulation_time
    Lq_Laboratory_Normal = data['Cumulative Stats']['Area Under Laboratory Normal Queue Length Curve'] / simulation_time
    Lq_Laboratory_Urgent = data['Cumulative Stats']['Area Under Laboratory Urgent Queue Length Curve'] / simulation_time
    Lq_Operation_Normal = data['Cumulative Stats']['Area Under Operation Normal Queue Length Curve'] / simulation_time
    Lq_Operation_Urgent = data['Cumulative Stats']['Area Under Operation Urgent Queue Length Curve'] / simulation_time
    Lq_General_Ward = data['Cumulative Stats']['Area Under General Ward Queue Length Curve'] / simulation_time
    Lq_ICU = data['Cumulative Stats']['Area Under ICU Queue Length Curve'] / simulation_time
    Lq_CCU = data['Cumulative Stats']['Area Under CCU Queue Length Curve'] / simulation_time

    # Average Waiting Time in each queue
    Wq_Emergency = data['Cumulative Stats']['Emergency Queue Waiting Time'] / data['Cumulative Stats']['Emergency Service Starters']
    Wq_Preoperative = data['Cumulative Stats']['Preoperative Queue Waiting Time'] / data['Cumulative Stats']['Preoperative Service Starters']
    Wq_Laboratory_Normal = data['Cumulative Stats']['Laboratory Normal Queue Waiting Time'] / data['Cumulative Stats']['Laboratory Normal Service Starters']
    Wq_Laboratory_Urgent = data['Cumulative Stats']['Laboratory Urgent Queue Waiting Time'] / data['Cumulative Stats']['Laboratory Urgent Service Starters']
    Wq_Operation_Normal = data['Cumulative Stats']['Operation Normal Queue Waiting Time'] / data['Cumulative Stats']['Operation Normal Service Starters']
    Wq_Operation_Urgent = data['Cumulative Stats']['Operation Urgent Queue Waiting Time'] / data['Cumulative Stats']['Operation Urgent Service Starters']
    Wq_General_Ward = data['Cumulative Stats']['General Ward Queue Waiting Time'] / data['Cumulative Stats']['General Ward Service Starters']
    Wq_ICU = data['Cumulative Stats']['ICU Queue Waiting Time'] / data['Cumulative Stats']['ICU Service Starters']
    Wq_CCU = data['Cumulative Stats']['CCU Queue Waiting Time'] / data['Cumulative Stats']['CCU Service Starters']

    # Maximum waiting time in each queue
    Max_Wq_Preoperative = max(data['Preoperative Queue Waiting Times'].values())
    # Max_Wq_Emergency = max(data['Emergency Queue Waiting Times'].values())
    # Max_Wq_Laboratory_Normal = max(data['Laboratory Normal Queue Waiting Times'].values())
    # Max_Wq_Laboratory_Urgent = max(data['Laboratory Urgent Queue Waiting Times'].values())
    # Max_Wq_Operation_Normal = max(data['Operation Normal Queue Waiting Times'].values())
    # Max_Wq_Operation_Urgent = max(data['Operation Urgent Queue Waiting Times'].values())
    # Max_Wq_General_Ward = max(data['General Ward Queue Waiting Times'].values())
    # Max_Wq_ICU = max(data['ICU Queue Waiting Times'].values())
    # Max_Wq_CCU = max(data['CCU Queue Waiting Times'].values())

    # Maximum queue length for each queue
    # Max_Lq_Emergency = max(data['Emergency Queue Lengths'].values())
    Max_Lq_Preoperative = max(data['Preoperative Queue Lengths'].values())
    # Max_Lq_Laboratory_Normal = max(data['Laboratory Normal Queue Lengths'].values())
    # Max_Lq_Laboratory_Urgent = max(data['Laboratory Urgent Queue Lengths'].values())
    # Max_Lq_Operation_Normal = max(data['Operation Normal Queue Lengths'].values())
    # Max_Lq_Operation_Urgent = max(data['Operation Urgent Queue Lengths'].values())
    # Max_Lq_General_Ward = max(data['General Ward Queue Lengths'].values())
    # Max_Lq_ICU = max(data['ICU Queue Lengths'].values())
    # Max_Lq_CCU = max(data['CCU Queue Lengths'].values())

    print(f"The average time in the system is: {average_time_in_system}")
    print(f"The possibility that the emergency queue capacity is full is: {Full_Emergency_Queue_Probability}")
    print(f"The average number of reoperations for patients with complex operations is: {average_complex_operation_reoperations}")
    print(f"The percentage of emergency patients who are admitted immediately is: {immediately_admitted_emergency_patients_percentage}")

    print(f'rho_Emergency = {rho_Emergency}')
    print(f'rho_Preoperative = {rho_Preoperative}')
    print(f'rho_Laboratory = {rho_Laboratory}')
    print(f'rho_Operation = {rho_Operation}')
    print(f'rho_General_Ward = {rho_General_Ward}')
    print(f'rho_ICU = {rho_ICU}')
    print(f'rho_CCU = {rho_CCU}')

    print(f'Lq_Emergency = {Lq_Emergency}')
    print(f'Lq_Preoperative = {Lq_Preoperative}')
    print(f'Lq_Laboratory_Normal = {Lq_Laboratory_Normal}')
    print(f'Lq_Laboratory_Urgent = {Lq_Laboratory_Urgent}')
    print(f'Lq_Operation_Normal = {Lq_Operation_Normal}')
    print(f'Lq_Operation_Urgent = {Lq_Operation_Urgent}')
    print(f'Lq_General_Ward = {Lq_General_Ward}')
    print(f'Lq_ICU = {Lq_ICU}')
    print(f'Lq_CCU = {Lq_CCU}')

    # print(f'Max_Lq_Emergency = {Max_Lq_Emergency}')
    print(f'Max_Lq_Preoperative = {Max_Lq_Preoperative}')
    # print(f'Max_Lq_Laboratory_Normal = {Max_Lq_Laboratory_Normal}')
    # print(f'Max_Lq_Laboratory_Urgent = {Max_Lq_Laboratory_Urgent}')
    # print(f'Max_Lq_Operation_Normal = {Max_Lq_Operation_Normal}')
    # print(f'Max_Lq_Operation_Urgent = {Max_Lq_Operation_Urgent}')
    # print(f'Max_Lq_General_Ward = {Max_Lq_General_Ward}')
    # print(f'Max_Lq_ICU = {Max_Lq_ICU}')
    # print(f'Max_Lq_CCU = {Max_Lq_CCU}')

    # print(f'Max_Wq_Emergency = {Max_Wq_Emergency}')
    print(f'Max_Wq_Preoperative = {Max_Wq_Preoperative}')
    # print(f'Max_Wq_Laboratory_Normal = {Max_Wq_Laboratory_Normal}')
    # print(f'Max_Wq_Laboratory_Urgent = {Max_Wq_Laboratory_Urgent}')
    # print(f'Max_Wq_Operation_Normal = {Max_Wq_Operation_Normal}')
    # print(f'Max_Wq_Operation_Urgent = {Max_Wq_Operation_Urgent}')
    # print(f'Max_Wq_General_Ward = {Max_Wq_General_Ward}')
    # print(f'Max_Wq_ICU = {Max_Wq_ICU}')
    # print(f'Max_Wq_CCU = {Max_Wq_CCU}')

    # print(f'Lq = {Lq}')
    # print(f'Wq = {Wq}')
    # print(f'rho = {rho}')

    # print("\nChecking Little's Law")
    # print(f'Lq = {Lq}')
    # print(f'lambda * Wq = {(1 / 20) * Wq}')

    # print('\nDo they match?')
    # print(f'Ratio: {Lq / ((1 / 20) * Wq)}')

    # if 0.9 < Lq / ((1 / 20) * Wq) < 1.1:
    #     print('Well... Almost!')


simulation(2000)
