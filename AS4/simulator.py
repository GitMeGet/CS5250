'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
'''
import copy
import sys

input_file = 'input.txt'

class Process:
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.initial_burst_time = burst_time
        self.burst_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrival_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
    process_list_copy = copy.deepcopy(process_list)
    curr_time = 0
    sched_queue = list()
    prev_process_done = False
    
    # to be returned by function
    schedule = list()
    waiting_time = 0

    # while process_list not empty
    while len(process_list_copy) != 0 or len(sched_queue) != 0:
        # get processes where (curr_t >= task_arrival_t)
        new_process_list = [p for p in process_list_copy if curr_time >= p.arrive_time]
        # sort new_process_list by arrival time
        new_process_list = sorted(new_process_list, key=lambda p: p.arrive_time)
        process_list_copy = list(set(process_list_copy) - set(new_process_list))
        
        if prev_process_done == True:
            sched_queue.extend(new_process_list)
        else:
            # place new processes ahead of last_process, in circular queue
            try:
                last_process = sched_queue.pop()
            except:
                last_process = None
            sched_queue.extend(new_process_list)
            if last_process is not None:
                sched_queue.append(last_process)
        
        #print(curr_time, sched_queue)        
    
        if len(sched_queue) > 0:
            # pop task from circular queue
            curr_process = sched_queue.pop(0)
            # update schedule
            if len(schedule) == 0:
                schedule.append((curr_time, curr_process.id))
            elif len(schedule) > 0 and schedule[-1][1] != curr_process.id:
                schedule.append((curr_time, curr_process.id))
                
        else:
            curr_time += 1
            continue
                
        # curr_process not done executing 
        if time_quantum < curr_process.burst_time:
            curr_time += time_quantum
            curr_process.burst_time -= time_quantum
            # re-insert task into circular queue since it's not done
            sched_queue.append(curr_process)
            prev_process_done = False
        # curr_process done
        else:
            # update total waiting time
            curr_time += curr_process.burst_time
            waiting_time += curr_time - curr_process.arrive_time - curr_process.initial_burst_time
            prev_process_done = True
           
    # compute average_waiting_time
    # divisor: count += 1 when a process is scheduled
    average_waiting_time = waiting_time/float(len(process_list))
    
    return schedule, average_waiting_time

# smallest remaining time first
# https://en.wikipedia.org/wiki/Shortest_remaining_time
# - is a preemptive version of shortest job next scheduling
# - processes will always run until they complete or a new process is added that requires a smaller amount of time.
def SRTF_scheduling(process_list):
    process_list_copy = copy.deepcopy(process_list)    
    curr_time = 0
    sched_list = list()
    prev_process = None
    
    # to be returned by function
    schedule = list()
    waiting_time = 0
    
    while len(process_list_copy) != 0 or len(sched_list) != 0:
        # add arrived processes into sched_list
        if len(process_list_copy) != 0 and curr_time >= process_list_copy[0].arrive_time:
            sched_list.append(process_list_copy.pop(0))
        # if there is a runnable process
        if len(sched_list) != 0:
            # get process w/ lowest burst time 
            curr_process = min(sched_list, key=lambda p: p.burst_time)
            sched_list.remove(curr_process)
            # if curr_p != prev_p, update schedule (context switch)
            if prev_process is None or curr_process.burst_time < prev_process.burst_time:
                schedule.append((curr_time, curr_process.id))
            else:
                # if curr_process and prev_process tied for burst_time, execute prev_process (don't context switch)
                curr_process = prev_process
                        
            # update process burst time
            curr_process.burst_time -= 1
            # if curr_process not done executing
            if curr_process.burst_time != 0:
                sched_list.append(curr_process)
                prev_process = curr_process
            else:
                # update total waiting time
                waiting_time += curr_time + 1 - curr_process.arrive_time - curr_process.initial_burst_time
                prev_process = None

        # increment time
        curr_time += 1

    average_waiting_time = waiting_time/float(len(process_list))
        
    return schedule, average_waiting_time

# non preemptive
def SJF_scheduling(process_list, alpha):
    process_list_copy = copy.deepcopy(process_list)
    curr_time = 0
    sched_list = list()
    pred_list = [-1]*len(process_list_copy)
    
    schedule = list()
    waiting_time = 0
    
    while len(process_list_copy) != 0 or len(sched_list) != 0:
        # add process where (curr_t >= task_arrival_t) to sched_list
        for p in process_list_copy:
            if curr_time >= p.arrive_time:
                if pred_list[p.id] == -1:
                    # initial guess for each process is 5 cpu cycles
                    predicted_burst_time = pred_list[p.id] = 5
                else:
                    predicted_burst_time = pred_list[p.id]
                process_list_copy.remove(p)
                sched_list.append((p, predicted_burst_time))
        
        if len(sched_list) != 0:
            # choose process from sched_list based on predicted_burst_time
            # how to decide ties? earliest added to sched_list
            curr_process_tuple = min(sched_list, key=lambda tuple: tuple[1])
            curr_process = curr_process_tuple[0]
            # update schedule
            schedule.append((curr_time, curr_process.id))
            # update waiting time
            waiting_time += curr_time - curr_process.arrive_time
            # update pred_list to predict next cpu burst of process when it finishes
            pred_list[curr_process.id] = alpha*curr_process.burst_time + (1-alpha)*pred_list[curr_process.id]
            # update curr_time
            curr_time += curr_process.burst_time
            # remove from sched_list
            sched_list.remove(curr_process_tuple)
        else:
            curr_time += 1

    average_waiting_time = waiting_time/float(len(process_list))
        
    return schedule, average_waiting_time

def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print(FCFS_avg_waiting_time)
    
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print(RR_avg_waiting_time)

    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print(SRTF_avg_waiting_time)

    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )
    print(SJF_avg_waiting_time)


if __name__ == '__main__':
    main(sys.argv[1:])

