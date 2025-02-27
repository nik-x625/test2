import subprocess
import time

# Function to check if a process is running
def is_process_running(process_name):
    try:
        subprocess.check_output(["ps", "aux"] , stderr=subprocess.STDOUT).decode('utf-8').lower().count(process_name.lower())
        return True
    except subprocess.CalledProcessError:
        return False

# Function to start a process using the init script
def start_process(process_name):
    print(f"Starting {process_name}...")
    # Call the init script to start the process
    subprocess.Popen(["/etc/init.d/" + process_name, "start"])

    # Wait until the process is running (you may need to adjust the timeout and sleep time)
    timeout = 30
    sleep_interval = 1
    count = 0

    while not is_process_running(process_name):
        time.sleep(sleep_interval)
        count += 1
        if count >= timeout:
            print(f"Failed to start {process_name} within timeout.")
            exit(1)

    print(f"{process_name} is started.")

# List of processes to start
processes_to_start = ["clickhouse-server", "gunicorn"]

# Start each process sequentially
for process in processes_to_start:
    start_process(process)
