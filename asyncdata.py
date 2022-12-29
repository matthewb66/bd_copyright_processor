import aiohttp
import asyncio
import platform
import logging


def get_data_async(bd, comps, trustcert):
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    return asyncio.run(async_main(bd, comps, trustcert))


async def async_main(bd, comps, trustcert):
    token = bd.session.auth.bearer_token

    async with aiohttp.ClientSession(trust_env=True) as session:
        copyright_tasks = []
        for url, comp in comps.items():

            if comp['ignored']:
                continue

            if 'origins' in comp:
                for orig in comp['origins']:
                    orig_url = orig['origin']
                    copyright_task = asyncio.ensure_future(async_get_copyrights(session, token, orig_url,
                                                                                not trustcert))
                    copyright_tasks.append(copyright_task)


        copyrights = dict(await asyncio.gather(*copyright_tasks))
        await asyncio.sleep(0.250)
        count = len(copyrights)
        logging.info(f'Downloaded copyrights for {count} component origins - page 1')

        page = 2
        while True:
            copyright_tasks = []
            for key, entry in copyrights.items():
                if len(entry) > 999:
                    arr = key.split('%')
                    copyright_task = asyncio.ensure_future(async_get_copyrights(session, token, arr[0],
                                                                                not trustcert, page))
                    copyright_tasks.append(copyright_task)

            if len(copyright_tasks) == 0:
                break
            page_copyrights = dict(await asyncio.gather(*copyright_tasks))
            await asyncio.sleep(0.250)
            count = len(page_copyrights)
            logging.info(f'Downloaded copyrights for {count} components - page {page}')
            copyrights.update(page_copyrights)
            page += 1

    # Merge copyrights by page
    merged_copyrights = {}
    for key, entry in copyrights.items():
        if len(entry) > 0:
            arr = key.split('%')
            newkey = arr[0]
            if newkey in merged_copyrights:
                merged_copyrights[newkey].extend(entry)
            else:
                merged_copyrights[newkey] = entry

    return merged_copyrights


async def async_get_copyrights(session, token, origurl, verify=True, page=1):
    if not verify:
        ssl = False
    else:
        ssl = None

    offset = (page - 1) * 1000
    thishref = origurl + f'/copyrights?limit=1000&offset={offset}'
    headers = {
        # 'accept': "application/vnd.blackducksoftware.bill-of-materials-6+json",
        'Authorization': f'Bearer {token}',
    }
    # resp = globals.bd.get_json(thishref, headers=headers)
    async with session.get(thishref, headers=headers, ssl=ssl) as resp:
        result_data = await resp.json()
    return f'{origurl}%{page}', result_data['items']
