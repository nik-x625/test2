import asyncio
import time

async def say_after(delay, what):
    await time.sleep(delay)
    print(what)

async def main():
    
    print(f" The starting time: {time.strftime('%X')} ")
    
    t1 = asyncio.create_task(say_after(2,'hello from t1'))
    t2 = asyncio.create_task(say_after(3,'hello from t2'))
    t3 = asyncio.create_task(say_after(2,'hello from t3'))
    t4 = asyncio.create_task(say_after(3,'hello from t4'))
    t5 = asyncio.create_task(say_after(1,'hello from t5'))
    
    await t1
    await t2
    await t3
    await t4
    await t5

    print(f" The finishing time: {time.strftime('%X')} ")
    
asyncio.run(main())