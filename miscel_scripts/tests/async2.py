import asyncio
import time
#from web_scraping_library import read_from_site_async

urls = ['http://site1.com','http://othersite.com','http://newsite.com']


async def read_from_site_async(url):
    print('going to process url: '+str(url))
    time.sleep(1)
    return 'URL job done'

async def main(url_list):
    print('in the main func')
    return await asyncio.gather(*[read_from_site_async(_) for _ in url_list])

results = asyncio.run(main(urls))
print (results)