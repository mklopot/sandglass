#!/usr/bin/env python3

import psutil
import re
import time
import os.path
import datetime


def find_proc_by_regex(regex, username):
    "Return a list of processes matching 'cmdline' and 'username'."
    my_regex = re.compile(regex)
    for p in psutil.process_iter(['cmdline', 'username', 'pid']):
            if (my_regex.search(" ".join(p.info['cmdline'])) is not None) and \
               (p.info['username'] == username):
                return p

def time_used(process):
    time_now = time.time()
    process_start = process.create_time()
    used =  time_now - process_start 

    print("time now: {}".format(time_now))
    print("process started: {}".format(process_start))
    print("seconds used by this instance: {}".format(used))
    return used


def track_process(process, timebudget, grace, time_granularity):
    print("Entering track_process(), time budget is {}".format(timebudget))
    used = 0
    while process.is_running():
        print("Tracking process {}".format(process))
        used = time_used(process) 
        if timebudget <= used:
            print("Terminating target process")
            process.terminate()
            time.sleep(grace)
            if process.is_running():
                print("Killing target process")
                process.kill()
            print("Process terminated/killed")
        time.sleep(time_granularity)
    return used
            

def main(name, regex, username, timelimit, grace, time_granularity):
    filepath = os.path.join('/tmp', name + "_seconds_used")
    while True:
        print("Checking for matching process")
        process = find_proc_by_regex(regex, username)
        if process:
            used = 0
            if os.path.isfile(filepath): 
                # check that timestamp is from today
                if datetime.datetime.fromtimestamp(os.path.getmtime(filepath)).day == \
                    datetime.date.today().day:
                        with open(filepath) as f:
                            try:
                                used = float(f.read())
                            except:
                                pass
            used += track_process(process, timelimit - used, grace, time_granularity)
            print("Process exited after using {} seconds".format(used))
            with open(os.path.join('/tmp', name + "_seconds_used"), 'w+') as f:
                f.write(str(used))
        else:
            print("No matching process found")

        time.sleep(time_granularity)
        


if __name__ == "__main__":

    name = 'minecraft'
    regex = 'java.*minecraft'
    username = 'ian'
    #timelimit = 60 * 60 * 3
    timelimit = 60 * 200
    grace = 5
    time_granularity = 10

    main(name, regex, username, timelimit, grace, time_granularity)


    
