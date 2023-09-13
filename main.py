import json

# Read the JSON file
with open('json/predictiveFrameworkDash.json','r') as file:
    json_data = json.load(file)

# Must figure out way to capture mydomain, for now input will do
mydomain = 'https://searchdiscoverydemo.lightning.force.com'
markdown = ''
name = json_data['label']

# Header
markdown += f'# {name} Documentation\n\n'

# Dataset
datasets = json_data['datasets']
markdown += '## Datasets\n\n'
for index, dataset in enumerate(datasets):
    datasetid = dataset['url'].split('/')[-1]
    markdown += f'{index + 1}. ' + '[' + f'{dataset["label"]}' + '](' + f'{mydomain}' + '/lightning/r/EdgeMart/' f'{datasetid}' + '/view)\n\n'

# Filters
filters = json_data['state']['filters']
markdown += '## Global Filters\n\n'
for index, filter in enumerate(filters):
    markdown += f'{index + 1}. {filter["fields"][0]} from the \'{filter["dataset"]["name"]}\' dataset\n'

# Widgets
charts = json_data['state']['widgets']
markdown += '\n## Charts\n\n'
chart_number = 1
for chartname, chartdata in charts.items():
    if chartdata['type'] == 'number':
        chart_title = chartdata['parameters']['title']
        chart_step = chartdata['parameters']['step']
        markdown += f'{chart_number}. {chartname}\n'
        markdown += f'    * Type: {chartdata["type"]}\n'
        markdown += f'    * Title: {chart_title}\n'
        markdown += f'    * Query: {chart_step}\n'
        chart_number += 1
    elif chartdata['type'] == 'chart':
        chart_title = chartdata['parameters']['title']['label']
        chart_step = chartdata['parameters']['step']
        chart_visual = chartdata['parameters']['visualizationType']
        markdown += f'{chart_number}. {chartname}\n'
        markdown += f'    * Type: {chartdata["type"]}\n'
        markdown += f'    * Title: {chart_title}\n'
        markdown += f'    * Query: {chart_step}\n'

# Steps
queries = json_data['state']['steps']
step_number = 1
query_dict = {'aggregateflex':{},'saql':{}} 
# Must add keys for all possible steps https://developer.salesforce.com/docs/atlas.en-us.bi_dev_guide_json.meta/bi_dev_guide_json/bi_dbjson_steps_properties.htm
for queryname, querydata in queries.items():
    if 'datasets' in querydata:
        for dataset in querydata['datasets']:
            dataset_label = dataset['label']
            query_label = querydata.get('label')
            if not query_label:
                query_label = queryname
            if dataset_label in query_dict['aggregateflex']:
                query_dict['aggregateflex'][dataset_label].append(query_label)
            else:
                query_dict['aggregateflex'][dataset_label] = [query_label]
    elif querydata['type'] == 'saql':
        query_label = querydata['label']
        query = querydata['query']
        query_dict['saql'][query_label] = query

markdown += '\n## Query Definitions\n\n'
for datasetname, stepdata in query_dict['aggregateflex'].items():
    markdown += f'### Dataset: {datasetname}\n\n'
    for i, step in enumerate(stepdata):
        markdown += f'{i + 1}. {step}\n'
    markdown += '\n'
markdown += '### SAQL\n'
markdown += f'```\n{query_dict["saql"]["Top 10 Contact Titles by Predicted Won"]}\n ```'

# Create Markdown file
with open(f'docs/{name}.md','w') as md_file:
    md_file.write(markdown)

print('Md Docs created successfully!')