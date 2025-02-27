import psutil

# CPU Information
cpu_info = {
    "CPU Model": " ".join(psutil.cpu_info()[0].values()),
    "CPU Cores": psutil.cpu_count(logical=False),
    "CPU Threads": psutil.cpu_count(logical=True),
}

print("CPU Information:")
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
