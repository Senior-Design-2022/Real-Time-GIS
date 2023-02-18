from datetime import datetime
import os

class SaveReplay:
    
    def __init__(self, debug):
        self.debug = debug

        # get absolute path to the replays folder
        target_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)),"replays")
        
        # create a file named by the current time
        suffix = datetime.now().strftime("%m-%d-%YT%H-%M-%S") + ".log"
        new_file_path = os.path.join(target_directory, suffix)
        self.replay_file = open(new_file_path, "a")
        

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.replay_file.close()

    # write data to log
    def write_to_log(self, data):
        self.replay_file.write(data.decode().replace("\n","") + "\n")
        self.replay_file.flush()
