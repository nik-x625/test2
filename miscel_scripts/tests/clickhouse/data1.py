import psutil
# gives a single float value
cpu = psutil.cpu_percent()
# gives an object with many fields
mem = psutil.virtual_memory()
# you can convert that object to a dictionary 
mem_dict = dict(psutil.virtual_memory()._asdict())
# you can have the percentage of used RAM
mem_used_perc = psutil.virtual_memory().percent
#79.2
# you can calculate percentage of available memory
mem_av_perc = psutil.virtual_memory().available * 100 / psutil.virtual_memory().total
#20.8

print('cpu: '+str(cpu))
print('mem: '+str(mem))
print('mem_dict: '+str(mem_dict))
print()
print((psutil.cpu_percent()))