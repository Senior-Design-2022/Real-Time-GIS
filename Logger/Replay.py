"""
Replays a log file of raw XML stored in the /Logger/replays folder

@author: R.Clark
"""

import sys
import time
import os.path
import time
from SocketUtils.SocketUtils import SITQueuedUDPSender

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Replay:
    def __init__(self, replay_file, host_ip, host_port, interval):
        print('starting replay')
        self.replay_file = replay_file
        self.host_ip = host_ip
        self.host_port = host_port
        self.interval = interval

        print(f"{bcolors.HEADER}Replaying {replay_file}{bcolors.ENDC}")
            
        lines = self.read_replay_file(self.replay_file)
        organized_replay = self.group_targets_by_second(lines)
        self.create_grouped_UDP_sender(organized_replay, self.interval, self.host_ip, self.host_port)


        #host_ip = "127.0.0.1"
        #host_port = 1870

        #create_UDP_sender(lines, host_ip, host_port)
            
        # rate at which each second is sent 
        # 1 == real time
        # 0.5 == double speed
        # 2 == half speed
        # interval = 1 


    # read all replay lines in from a file
    def read_replay_file(self, filename):

        # recreate file path
        target_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)),"replays")
        file_path = os.path.join(target_directory, filename)
        
        # read lines from the file
        with open(file_path) as log:
            lines = log.readlines()

        return lines


    # gets the time from the XML string
    # THIS WILL NOT WORK IF THE FORMAT OF THE TIME IS CHANGED
    # PROBABLY NEED TO GENERALIZE
    def get_time(self, element):
        time_index = element.find("time")
        result = element[time_index + 17 : time_index + 25]
        return result


    # create arrays grouping xml by second
    def group_targets_by_second(self, lines):
        
        print(f"{bcolors.HEADER}Grouping XML...{bcolors.ENDC}")

        replay = []

        previous_element = None
        current_element = None

        for i in range(0, len(lines)):
            if i == 0:
                replay.append([lines[i]])
                previous_element = lines[i]
                current_element = lines[i]
            else:
                current_element = lines[i]

                # see if the two times are from the same second
                if (self.get_time(current_element) == self.get_time(previous_element)):
                    replay[len(replay) - 1].append(lines[i]) # add to the previous array
                else:
                    replay.append([lines[i]]) # make a new array
                previous_element = current_element

        print(f"{bcolors.HEADER}Done.{bcolors.ENDC}")

        return replay


    # sends an array full of xml objects -- won't work with the nested arrays of group_targets_by_second
    def create_UDP_sender(self, data, host_ip, host_port):

        with SITQueuedUDPSender(host_ip, default_destination=(host_ip, host_port)) as out:
            out.Debug= False
                
            # will run through each point
            for cot_xml in data:
                time.sleep(1)
                out.putitem(cot_xml)
                print(cot_xml)
        return


    # sends arrays organized by second
    # adjust interval to change speed of replay
    def create_grouped_UDP_sender(self, data, interval, host_ip, host_port):

        with SITQueuedUDPSender(host_ip, default_destination=(host_ip, host_port)) as out:
            out.Debug= False
            
            color_flip = False # to show grouping

            # will run through each point
            for group in data:
                color_flip = not color_flip
                time.sleep(interval)
                for cot_xml in group:
                    if color_flip:
                        print(f"{bcolors.OKBLUE}{cot_xml}{bcolors.ENDC}")
                    else: 
                        print(f"{bcolors.OKGREEN}{cot_xml}{bcolors.ENDC}")
                    out.putitem(cot_xml)

        return

    