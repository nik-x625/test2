import psutil
import platform

# Function to parse /proc/cpuinfo
def parse_cpu_info():
    cpu_info = {}
    try:
        with open('/proc/cpuinfo', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if ':' in line:
                    key, value = map(str.strip, line.split(':', 1))
                    cpu_info[key] = value
    except FileNotFoundError:
        pass
    return cpu_info

# Get CPU information
cpu_info = parse_cpu_info()
cpu_model = platform.processor()
cpu_cores = psutil.cpu_count(logical=False)
cpu_threads = psutil.cpu_count(logical=True)

# Print CPU information
print(f"CPU Model: {cpu_model}")
print(f"CPU Cores: {cpu_cores}")
print(f"CPU Threads: {cpu_threads}")

# Additional information from /proc/cpuinfo
if cpu_info:
    print("\nAdditional CPU Information from /proc/cpuinfo:")
    for key, value in cpu_info.items():
        print(f"{key}: {value}")

# CPU Utilization
cpu_percent = psutil.cpu_percent(interval=1, percpu=True)

print("\nCPU Utilization:")
for i, percent in enumerate(cpu_percent):
    print(f"CPU Core {i}: {percent}%")

# Top 10 Processes using CPU
top_processes = sorted(
    psutil.process_iter(attrs=["pid", "name", "cpu_percent"]),
    key=lambda x: x.info["cpu_percent"],
    reverse=True,
)[:10]

print("\nTop 10 Processes using CPU:")
for process in top_processes:
    print(
        f"PID: {process.info['pid']}, Name: {process.info['name']}, CPU %: {process.info['cpu_percent']}"
    )
