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
import sys

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
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
    curr_time = 0
    curr_quantum = 0
    num_tasks = len(process_list)
    sched_queue = list()
    
    schedule = list()
    waiting_time = 0
    prev_process_done = False

    # while process_list not empty
    while len(process_list) != 0 or len(sched_queue) != 0:
        # get processes where (curr_t >= task_arrival_t)
        new_process_list = [p for p in process_list if curr_time >= p.arrive_time]
        # sort new_process_list by arrival time
        new_process_list = sorted(new_process_list, key=lambda p: p.arrive_time)
        process_list = list(set(process_list) - set(new_process_list))
        
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
        
        print(curr_time, sched_queue)        

        # update total waiting time
        for p in new_process_list:
            waiting_time += curr_time - p.arrive_time
    
        if len(sched_queue) > 0:
            # pop task from circular queue
            curr_process = sched_queue.pop(0)
            # update schedule
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
            curr_time += curr_process.burst_time
            prev_process_done = True
           
    # compute average_waiting_time
    average_waiting_time = waiting_time/float(num_tasks)
    
    return schedule, average_waiting_time

def SRTF_scheduling(process_list):
    return (["to be completed, scheduling process_list on SRTF, using process.burst_time to calculate the remaining time of the current process "], 0.0)

def SJF_scheduling(process_list, alpha):
    return (["to be completed, scheduling SJF without using information from process.burst_time"],0.0)


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
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])

