from multiple_clients import StreamSimulator
import threading

import sys

def create_stream(host_ip, host_port, target_id, table_name, src, config_filename):
    stream = StreamSimulator(host_ip, host_port, target_id, table_name, src, config_filename)
    rows, header_row = stream.get_CoT_from_db(table_name, src, target_id)
    print(header_row, len(rows))
    stream.simulate_CoT_stream(rows, header_row, host_ip, host_port)

if __name__ == "__main__":
    table_name = "ToCoTData"
    src = "20220901ADSB.sq3"
    host_ip = "127.0.0.1"
    host_port = 1870

    # Some sample targets for testing:
    # 11279804.N88ZA -- what we've been using the most
    # 10531224.N144AM
    # 10797116.N405LP
    # 11329446.N929AN
    # 11133841.N736YX
    # 11124112.N727AC
    # 11123333.N726H
    sample_target_ids = [  
                    "11279804.N88ZA",
                    "10531224.N144AM",
                    "10797116.N405LP",
                    "11329446.N929AN",
                    "11133841.N736YX",
                    "11124112.N727AC"
                 ]

    #
    #   Change this number to set how many streams to simulate.
    #
    '''
    number_of_streams = 2

    if (number_of_streams > len(sample_target_ids)):
        print(f'Error: Invalid number of streams. Must be greater than zero and less than {len(target_ids)}.')
    else:
        for i in range(0, number_of_streams):
            thread = threading.Thread(target=create_stream, args=(host_ip, host_port, target_ids[i], table_name, src), daemon=True)
            print("thread crated!")
            thread.start()
    '''
    idx = int(sys.argv[1])
    config_filename = sys.argv[2]
    '''
    for idxi in [idx, idx + 1]:
        source_id = sample_target_ids[idxi]
        print(f"our proc will handle the source {source_id}!")
        thread = threading.Thread(target=create_stream, args=(host_ip, host_port, source_id, table_name, src), daemon=True)
        print(f"thread crated! (id = {source_id})")
        thread.start()
        print(f"thread started? (id = {source_id})")
    '''
    source_id = sample_target_ids[idx]
    print(f"our proc will handle the source {source_id}!")
    thread = threading.Thread(target=create_stream, args=(host_ip, host_port, source_id, table_name, src, config_filename), daemon=True)
    print(f"thread crated! (id = {source_id})")
    thread.start()
    print(f"thread started? (id = {source_id})")

    while True:
        continue



