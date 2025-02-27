import subprocess
import time

# Function to check if a process is running
def is_process_running(process_name):
    try:
        subprocess.check_output(["ps", "aux"] , stderr=subprocess.STDOUT).decode('utf-8').lower().count(process_name.lower())
        return True
    except subprocess.CalledProcessError:
        return False

# Function to stop a process using the init script
def stop_process(process_name):
    pid = None
    print(f"Stopping {process_name}...")
    # Call the init script to stop the process
    subprocess.call(["/etc/init.d/" + process_name, "stop"])

    # Wait until the process is not running (you may need to adjust the timeout and sleep time)
    timeout = 30
    sleep_interval = 1
    count = 0

    while is_process_running(process_name):
        pid = subprocess.check_output(["ps", "aux"] , stderr=subprocess.STDOUT).decode('utf-8')
        time.sleep(sleep_interval)
        count += 1
        if count >= timeout:
            break

    if is_process_running(process_name):
        # If the process is still running, forcefully terminate it using 'kill -9'
        if pid:
            pid = int(pid.split()[1])
            print(f"Forcefully terminating {process_name} (PID: {pid})...")
            subprocess.call(["kill", "-9", str(pid)])
        print(f"Failed to stop {process_name} within timeout.")
        exit(1)

    print(f"{process_name} is stopped.")

# List of processes to stop (in reverse order)
processes_to_stop = ["gunicorn", "clickhouse"]

# Stop each process in reverse order
for process in processes_to_stop:
    stop_process(process)
