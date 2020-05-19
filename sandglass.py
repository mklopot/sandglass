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

def time_remaining(process, timelimit):
    time_now = time.time()
    process_start = process.create_time()
    remaining =  timelimit - time_now + process_start 

    print("time now: {}".format(time_now))
    print("process started: {}".format(process_start))
    print("time limit: {}".format(timelimit))
    print("seconds remaining: {}".format(remaining))
    return remaining


def track_process(process, timelimit, grace, time_granularity):
    print("Entering track_process()")
    remaining = timelimit
    while process.is_running():
        print("Tracking process {}".format(process))
        remaining = time_remaining(process, timelimit)
        if remaining <= 0:
            print("Terminating target process")
            process.terminate()
            time.sleep(grace)
            if process.is_running():
                print("Killing target process")
                process.kill()
            print("Process terminated/killed")
            return 0
        time.sleep(time_granularity)

    return remaining
            

def main(name, regex, username, timelimit, grace, time_granularity):
    print("Entering main()")
    filepath = os.path.join('/tmp', name + "_seconds_remaining")
    while True:
        print("Starting `while` loop in main()")
        process = find_proc_by_regex(regex, username)
        if process:
            if os.path.isfile(filepath): 
                # check that timestamp is from today
                if datetime.datetime.fromtimestamp(os.path.getmtime(filepath)).day == \
                    datetime.date.today().day:
                        with open(filepath) as f:
                            try:
                                timelimit = int(f.read())
                            except:
                                pass
            remaining = track_process(process, timelimit, grace, time_granularity)
            with open(os.path.join('/tmp', name + "_seconds_remaining"), 'w+') as f:
                f.write(str(remaining))
        else:
            print("No matching process found")

        time.sleep(time_granularity)
        


if __name__ == "__main__":

    name = 'minecraft'
    regex = 'java.*minecraft'
    username = 'ian'
    #timelimit = 60 * 60 * 3
    timelimit = 60 * 200
    grace = 30
    time_granularity = 20

    main(name, regex, username, timelimit, grace, time_granularity)


    
