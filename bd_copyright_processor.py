#!/usr/bin/env python

import argparse
# import json
import logging
import sys
import os

# from blackduck.HubRestApi import HubInstance
from blackduck import Client

# import html2text
# from copyrightmanager import CopyrightManager
from componentlist import ComponentList
from copyrightprocessor import CopyrightProcessor

import asyncdata
script_version = '2.1'


def check_projver(bd, proj, ver):
	params = {
		'q': "name:" + proj,
		'sort': 'name',
	}

	projects = bd.get_resource('projects', params=params)
	for p in projects:
		if p['name'] == proj:
			versions = bd.get_resource('versions', parent=p, params=params)
			for v in versions:
				if v['versionName'] == ver:
					return p, v
			break
	else:
		print("Version '{}' does not exist in project '{}'".format(ver, proj))
		sys.exit(2)

	print("Project '{}' does not exist".format(proj))
	print('Available projects:')
	projects = bd.get_resource('projects')
	for proj in projects:
		print(proj['name'])
	sys.exit(2)


def get_bom_components(bd, verdict):
	comp_dict = {}
	res = bd.list_resources(verdict)

	blocksize = 1000

	projver = res['href']
	thishref = projver + f"/components?limit={blocksize}"
	headers = {
		'accept': "application/vnd.blackducksoftware.bill-of-materials-6+json",
	}
	res = bd.get_json(thishref, headers=headers)
	if 'totalCount' in res and 'items' in res:
		total_comps = res['totalCount']
	else:
		return comp_dict

	downloaded_comps = 0
	while downloaded_comps < total_comps:
		downloaded_comps += len(res['items'])

		bom_comps = res['items']

		for comp in bom_comps:
			if 'componentVersion' not in comp:
				continue
			compver = comp['componentVersion']

			comp_dict[compver] = comp

		thishref = projver + f"/components?limit={blocksize}&offset={downloaded_comps}"
		res = bd.get_json(thishref, headers=headers)
		if 'totalCount' not in res or 'items' not in res:
			break

	return comp_dict


def get_all_projects(bd):
	projs = bd.get_resource('projects', items=True)

	projlist = []
	for proj in projs:
		projlist.append(proj['name'])
	return projlist


logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', stream=sys.stderr, level=logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


parser = argparse.ArgumentParser("bd_copyright_procssor", description='Description: Generate filtered copyrights')
parser.add_argument("project", help="The name of the project in Blackduck")
parser.add_argument("version", help="The name of the version in Blackduck")
parser.add_argument("--blackduck_url", type=str,
					help="Black Duck server URL (can also be set as env-var BLACKDUCK_URL)", default="")
parser.add_argument("--blackduck_api_token", type=str,
					help="Black Duck API token URL (can also be set as env-var BLACKDUCK_API_TOKEN)", default="")
parser.add_argument("--blackduck_trust_cert", help="BLACKDUCK trust cert", action='store_true')
parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
# parser.add_argument("-f","--file")
# parser.add_argument("-nf","--not_filtered", action="store_true")
# parser.add_argument("-nd","--no_date", action="store_true",)
parser.add_argument("-so", "--show_orig", action="store_true",
					help="Show all original copyrights as well as processed copyrights")
parser.add_argument("-o", "--output-text", help="Output report as text")
parser.add_argument("-oh", "--output-html", help="Output report as html")
parser.add_argument("-l", "--max_lines", default=2, help="Maximum processed copyright lines")
parser.add_argument("-c", "--code_languages", default="all",
					help="Specify which code fragments should be removed (optional): csharp,c,python,java,js,shell,xml,sql")
parser.add_argument("-n", "--notstrict", action="store_true", help="Include copyright text which does not contain a year or date")
parser.add_argument("-v", "--script_version", action="store_true", help="Print script version")
# parser.add_argument("-r","--recursive", action="store_true", help="Process projects in projects")

args = parser.parse_args()

if args.debug:
	logging.getLogger("requests").setLevel(logging.DEBUG)
	logging.getLogger("urllib3").setLevel(logging.DEBUG)
	logging.getLogger().setLevel(logging.DEBUG)

if args.script_version:
	print(f'Script version {script_version}')
	sys.exit(0)

if not args.output_text and not args.output_html:
	print("You must specify either html (-oh|--output-html)  or text (-o|--output-text) output file")
	parser.print_help()
	sys.exit(1)

url = os.environ.get('BLACKDUCK_URL')
if args.blackduck_url:
	url = args.blackduck_url

api = os.environ.get('BLACKDUCK_API_TOKEN')
if args.blackduck_api_token:
	api = args.blackduck_api_token

verify = True
if args.blackduck_trust_cert:
	verify = False

if url == '' or url is None:
	print('BLACKDUCK_URL not set or specified as option --blackduck_url')
	sys.exit(2)

if api == '' or api is None:
	print('BLACKDUCK_API_TOKEN not set or specified as option --blackduck_api_token')
	sys.exit(2)

bd = Client(
	token=api,
	base_url=url,
	verify=verify,  # TLS certificate verification
	timeout=60
)

# projlist = []
# if args.recursive:
# 	print('Getting all projects for recursive processing ...')
# 	projlist = get_all_projects(bd)

# logging.info("Requesting bom from hub")
# hub = HubInstance()
# project = hub.get_project_by_name(args.project_name)
# version = hub.get_version_by_name(project, args.version)
project, version = check_projver(bd, args.project, args.version)

bom_components = get_bom_components(bd, version)
# logging.debug("bom_components: {}".format(bom_components))

# PROCESS SUB-PROJECTS
# if not args.use_json:
# 	new_components=[]
# 	for bom_component in bom_components:
# 		logging.debug("Checking component {} for sub components".format(bom_component['componentName']))
# 		if bom_component['matchTypes'][0] == "MANUAL_BOM_COMPONENT" and bom_component['componentName'] in proj_list:
# 			sub_project = hub.get_project_by_name(bom_component['componentName'])
# 			if sub_project != "" and sub_project != None:
# 				sub_version = hub.get_version_by_name(sub_project, bom_component['componentVersionName'])
# 				if sub_version != "" and sub_version != None:
# 					logging.debug("Processing project within project '{}'".format(bom_component['componentName']))
# 					sub_bom_components = hub.get_version_components(sub_version).get('items', [])
#
# 					new_components.extend(sub_bom_components)
# 					logging.debug("Number of components:"+str(len(new_components)))
# 	bom_components.extend(new_components)

# if args.save_json:
# 	with open(args.save_json, "w", encoding="utf-8") as f:
# 		json.dump(bom_components, f)


all_origins = dict()
all_origin_info = {}
scan_cache = {}
# licenses = {}
# license_by_component={}
copyrights = {}
duplicate_check = {}


def process_bom(bd, bom_components):
	logging.info("Processing {} bom entries ...".format(len(bom_components)))

	logging.info("Downloading Async data ...")
	all_copyrights = asyncdata.get_data_async(bd, bom_components, args.blackduck_trust_cert)

	copyrightprocessor = CopyrightProcessor(args.code_languages.split(','), int(args.max_lines))

	componentlist = ComponentList()
	componentlist.process_bom(bd, bom_components, all_copyrights, copyrightprocessor, args.notstrict)

	all_comp_count = len(bom_components)
	ignored_comps = componentlist.count_ignored_comps()
	comps_with_copyrights = componentlist.count_comps()
	active_copyright_count = componentlist.count_active_copyrights()
	inactive_copyright_count = componentlist.count_inactive_copyrights()
	total_copyright_count = active_copyright_count + inactive_copyright_count
	final_copyright_count = componentlist.count_final_copyrights()

	print(f"Processed project {args.project} version {args.version}")
	print(f"Component counts:\n- Total Components {all_comp_count}")
	print(f"- Ignored Components {ignored_comps}")
	print(f"- Components with Copyrights {comps_with_copyrights}")
	print(f"Copyright counts:\n- Total Original Copyrights {total_copyright_count}")
	print(f"- Active Original Copyrights {active_copyright_count}")
	print(f"- Output Copyrights {final_copyright_count}")

	return componentlist


# def generate_html_report():
#
# 	output="""
# <!doctype html>
#
# <html lang="en">
# <head>
#   <meta charset="utf-8">
#
#   <title>Notices Report</title>
#   <meta name="description" content="Notice Report">
#   <meta name="author" content="BlackDuck">
# </head>
#
# <body>
# <h1>{} {}<h1>
# """.format(args.project_name,args.version)
#
# 	for component in duplicate_check.keys():
# 		output = output + "<h2>{}</h2>".format(component)
# 		# if component in license_by_component:
# 		# 	output = output + "<h4>License: {}</h4>\n".format(license_by_component[component])
# 		output = output + "<h4>Copyrights:</h4>\n"
# 		if not component in copyrights:
# 			output = output + "<p> No Copyrights found </p>\n"
# 			continue
# 		output = output + "<ul>"
# 		for origin in copyrights[component]:
#
# 			if not copyrights[component][origin]:
# 				continue
# 			for copyright in copyrights[component][origin]['copyrights']:
# 				output=output+"<li>{}</li>\n".format(copyright)
# 			# if args.show_rejected:
# 			# 	for copyright in copyrights[component][origin]['rejected']:
# 			# 		output = output + "<li style=\"color:red;\">REJECTED: {}</li>\n".format(
# 			# 			html2text.html2text(copyright))
#
# 			output = output + "</ul>"
#
# 	# output=output+"<h1>Licenses</h1>"
# 	# for license in licenses:
# 	# 	output=output+"<h2>{}</h2>".format(license)
# 	# 	output=output+"<h3>({})</h3>".format(','.join(licenses[license]['components']))
# 	# 	output=output+"<pre>{}<pre>".format(licenses[license]['text'])
#
#
# 	output = output + """
# 	  <script src="js/scripts.js"></script>
# 	</body>
# 	</html>
# 	"""
#
# 	return output


# if args.use_json:
# 	with open(args.use_json) as f:
# 		all_origin_info = json.load(f)
# else:

if True:
	complist = process_bom(bd, bom_components)
	if args.output_html:
		with open(args.output_html, "w", encoding="UTF-8") as html:
			logging.info("Writing html output to:{}".format(args.output_html))
			html.write(complist.generate_html_report(args.project, args.version, args.show_orig))
			print(f'Output file {args.output_html} created')

	if args.output_text:
		with open(args.output_text, "w", encoding="UTF-8") as text:
			logging.info("Writing text output to:{}".format(args.output_text))
			text.write(complist.generate_text_report(args.project, args.version, args.show_orig))
			print(f'Output file {args.output_text} created')
