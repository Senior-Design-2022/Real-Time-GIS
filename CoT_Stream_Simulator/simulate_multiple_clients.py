from multiple_clients import StreamSimulator
import threading
import time

def create_stream(host_ip, host_port, target_id, table_name, src):
    stream = StreamSimulator(host_ip, host_port, target_id, table_name, src)
    stream.create_UDP_sender(stream.get_CoT_from_db(table_name, src, target_id), host_ip, host_port)

if __name__ == "__main__":
    table_name = "ToCoTData"
    src = "20220901ADSB.sq3"
    host_ip = "127.0.0.1"
    host_port = 1870

    # Some sample targets for testing
    target_ids = [  
                    "11279804.N88ZA",
                    "10531224.N144AM",
                    "10797116.N405LP",
                    "11329446.N929AN",
                    "11133841.N736YX",
                    "11124112.N727AC",
                    "11123333.N726H"
                 ]

    #
    #   Change this number to set how many streams to simulate.
    #
    number_of_streams = 3

    if (number_of_streams > len(target_ids)):
        print(f'Error: Invalid number of streams. Must be greater than zero and less than {len(target_ids)}.')
    else:
        for i in range(0, number_of_streams):
            thread = threading.Thread(target=create_stream, args=(host_ip, host_port, target_ids[i], table_name, src), daemon=True)
            thread.start()

    while True:
        continue



