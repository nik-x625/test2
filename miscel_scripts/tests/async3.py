import asyncio
async def get_chat_id(name):
    await asyncio.sleep(3)
    return "chat-%s" % name

async def main():
    id_coroutine = get_chat_id("django")
    result = await id_coroutine