import aiohttp
import asyncio
import platform


def get_data_async(bd, comps, trustcert):
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    return asyncio.run(async_main(bd, comps, trustcert))


async def async_main(bd, comps, trustcert):
    token = bd.session.auth.bearer_token

    async with aiohttp.ClientSession() as session:
        copyright_tasks = []
        # comment_tasks = []
        # file_tasks = []
        # lic_tasks = []
        # url_tasks = []
        # supplier_tasks = []
        # child_tasks = []
        count = 0
        for url, comp in comps.items():
            # if config.args.debug:
            #     print(comp['componentName'] + '/' + comp['componentVersionName'])

            if 'origins' in comp:
                for orig in comp['origins']:
                    orig_url = orig['origin']
                    copyright_task = asyncio.ensure_future(async_get_copyrights(session, token, orig_url,
                                                                                not trustcert))
                    copyright_tasks.append(copyright_task)

            # comment_task = asyncio.ensure_future(async_get_comments(session, comp, token))
            # comment_tasks.append(comment_task)
            #
            # file_task = asyncio.ensure_future(async_get_files(session, comp, token))
            # file_tasks.append(file_task)
            #
            # lic_task = asyncio.ensure_future(async_get_licenses(session, comp, token))
            # lic_tasks.append(lic_task)
            #
            # url_task = asyncio.ensure_future(async_get_url(session, comp, token))
            # url_tasks.append(url_task)
            #
            # supplier_task = asyncio.ensure_future(async_get_supplier(session, comp, token))
            # supplier_tasks.append(supplier_task)

        all_copyrights = dict(await asyncio.gather(*copyright_tasks))
        # all_comments = dict(await asyncio.gather(*comment_tasks))
        # all_files = dict(await asyncio.gather(*file_tasks))
        # all_lics = dict(await asyncio.gather(*lic_tasks))
        # all_urls = dict(await asyncio.gather(*url_tasks))
        # all_suppliers = dict(await asyncio.gather(*supplier_tasks))

        # all_children = dict(await asyncio.gather(*child_tasks))
        await asyncio.sleep(0.250)
        print(f'Got {count} component data elements')

    return all_copyrights


async def async_get_copyrights(session, token, origurl, verify=True):
    if not verify:
        ssl = False
    else:
        ssl = None

    thishref = origurl + '/copyrights?limit=1000'
    # ToDo: manage pagination of more than 1000 copyrights
    headers = {
        # 'accept': "application/vnd.blackducksoftware.bill-of-materials-6+json",
        'Authorization': f'Bearer {token}',
    }
    # resp = globals.bd.get_json(thishref, headers=headers)
    async with session.get(thishref, headers=headers, ssl=ssl) as resp:
        result_data = await resp.json()
    return origurl, result_data['items']


# async def async_get_comments(session, comp, token):
#     if not globals.verify:
#         ssl = False
#     else:
#         ssl = None
#
#     annotations = []
#     hrefs = comp['_meta']['links']
#
#     link = next((item for item in hrefs if item["rel"] == "comments"), None)
#     if link:
#         thishref = link['href']
#         headers = {
#             'Authorization': f'Bearer {token}',
#             'accept': "application/vnd.blackducksoftware.bill-of-materials-6+json",
#         }
#         # resp = globals.bd.get_json(thishref, headers=headers)
#         async with session.get(thishref, headers=headers, ssl=ssl) as resp:
#             result_data = await resp.json()
#             mytime = datetime.datetime.now()
#             # mytime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
#             for comment in result_data['items']:
#                 annotations.append(
#                     {
#                         "annotationDate": spdx.quote(mytime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
#                         "annotationType": "OTHER",
#                         "annotator": spdx.quote("Person: " + comment['user']['email']),
#                         "comment": spdx.quote(comment['comment']),
#                     }
#                 )
#     return comp['componentVersion'], annotations
#
#
# async def async_get_files(session, comp, token):
#     if not globals.verify:
#         ssl = False
#     else:
#         ssl = None
#
#     retfile = "NOASSERTION"
#     hrefs = comp['_meta']['links']
#
#     link = next((item for item in hrefs if item["rel"] == "matched-files"), None)
#     if link:
#         thishref = link['href']
#         headers = {
#             'Authorization': f'Bearer {token}',
#             'accept': "application/vnd.blackducksoftware.bill-of-materials-6+json",
#         }
#
#         async with session.get(thishref, headers=headers, ssl=ssl) as resp:
#             result_data = await resp.json()
#             cfile = result_data['items']
#             if len(cfile) > 0:
#                 rfile = cfile[0]['filePath']['path']
#                 for ext in ['.jar', '.ear', '.war', '.zip', '.gz', '.tar', '.xz', '.lz', '.bz2', '.7z',
#                             '.rar', '.rar', '.cpio', '.Z', '.lz4', '.lha', '.arj', '.rpm', '.deb', '.dmg',
#                             '.gz', '.whl']:
#                     if rfile.endswith(ext):
#                         retfile = rfile
#     return comp['componentVersion'], retfile
#
#
# async def async_get_licenses(session, lcomp, token):
#     if not globals.verify:
#         ssl = False
#     else:
#         ssl = None
#
#     # Get licenses
#     lic_string = "NOASSERTION"
#     quotes = False
#     if 'licenses' in lcomp.keys():
#         proc_item = lcomp['licenses']
#
#         if len(proc_item[0]['licenses']) > 1:
#             proc_item = proc_item[0]['licenses']
#
#         for lic in proc_item:
#             thislic = ''
#             if 'spdxId' in lic:
#                 thislic = lic['spdxId']
#                 if thislic in spdx.spdx_deprecated_dict.keys():
#                     thislic = spdx.spdx_deprecated_dict[thislic]
#             else:
#                 # Custom license
#                 try:
#                     thislic = 'LicenseRef-' + spdx.clean_for_spdx(lic['licenseDisplay'] + '-' + lcomp['componentName'])
#                     lic_ref = lic['license'].split("/")[-1]
#                     headers = {
#                         'accept': "text/plain",
#                         'Authorization': f'Bearer {token}',
#                     }
#                     # resp = globals.bd.session.get('/api/licenses/' + lic_ref + '/text', headers=headers)
#                     thishref = f"{globals.bd.base_url}/api/licenses/{lic_ref}/text"
#                     async with session.get(thishref, headers=headers, ssl=ssl) as resp:
#                         # lic_text = await resp.content.decode("utf-8")
#                         lic_text = await resp.text('utf-8')
#                         if thislic not in globals.spdx_lics:
#                             mydict = {
#                                 'licenseID': spdx.quote(thislic),
#                                 'extractedText': spdx.quote(lic_text)
#                             }
#                             globals.spdx["hasExtractedLicensingInfos"].append(mydict)
#                             globals.spdx_lics.append(thislic)
#                 except Exception as exc:
#                     pass
#             if lic_string == "NOASSERTION":
#                 lic_string = thislic
#             else:
#                 lic_string = lic_string + " AND " + thislic
#                 quotes = True
#
#         if quotes:
#             lic_string = "(" + lic_string + ")"
#
#     return lcomp['componentVersion'], lic_string
#
#
# async def async_get_url(session, comp, token):
#     if not globals.verify:
#         ssl = False
#     else:
#         ssl = None
#
#     url = "NOASSERTION"
#     if 'component' not in comp.keys():
#         return comp['componentVersion'], url
#
#     link = comp['component']
#     headers = {
#         'accept': "application/vnd.blackducksoftware.bill-of-materials-6+json",
#         'Authorization': f'Bearer {token}',
#     }
#     # resp = globals.bd.get_json(thishref, headers=headers)
#     async with session.get(link, headers=headers, ssl=ssl) as resp:
#         result_data = await resp.json()
#         if 'url' in result_data.keys():
#             url = result_data['url']
#     return comp['componentVersion'], url
#
#
# async def async_get_supplier(session, comp, token):
#     if not globals.verify:
#         ssl = False
#     else:
#         ssl = None
#
#     supplier_name = ''
#     hrefs = comp['_meta']['links']
#
#     link = next((item for item in hrefs if item["rel"] == "custom-fields"), None)
#     if link:
#         thishref = link['href']
#         headers = {
#             'Authorization': f'Bearer {token}',
#             'accept': "application/vnd.blackducksoftware.bill-of-materials-6+json",
#         }
#
#         async with session.get(thishref, headers=headers, ssl=ssl) as resp:
#             result_data = await resp.json()
#             cfields = result_data['items']
#             sbom_field = next((item for item in cfields if item['label'] == globals.SBOM_CUSTOM_SUPPLIER_NAME),
#                               None)
#
#             if sbom_field is not None and len(sbom_field['values']) > 0:
#                 supplier_name = sbom_field['values'][0]
#
#     return comp['componentVersion'], supplier_name
