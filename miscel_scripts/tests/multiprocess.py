from multiprocessing import Process
import random
import time

def print_func(continent='Asia'):
    myrand = random.randint(1,6)
    print('random number: ',myrand)
    dummy_res=pow(100000,10000000)
    if dummy_res:
        print('res is ready for: ',continent)
    
    #print('The name of continent is : ', continent)
    #time.sleep(myrand)

if __name__ == "__main__":  # confirms that the code is under main function
    names = ['America', 'Europe', 'Africa']
    procs = []
    #proc = Process(target=print_func)  # instantiating without any argument
    #procs.append(proc)
    #proc.start()

    # instantiating process with arguments
    for name in names:
        # print(name)
        proc = Process(target=print_func, args=(name,))
        procs.append(proc)
        proc.start()

    # complete the processes
    for proc in procs:
        proc.join()