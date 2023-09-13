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
markdown += '\n## Query Definitions\n\n'
step_number = 1
datasets = {}
for queryname, querydata in queries.items():
    if 'datasets' in querydata:
        for dataset in querydata['datasets']:
            print(dataset)
            print(type(dataset))
            dataset_label = dataset['label']
            print('dataset_label = ' + dataset_label)
            query_label = querydata.get('label')
            if not query_label:
                query_label = queryname
            if dataset_label in datasets:
                datasets[dataset_label].append(query_label)
            else:
                datasets[dataset_label] = [query_label]
print(datasets) # Need to use dict to add to markdown now

# Create Markdown file
with open(f'docs/{name}.md','w') as md_file:
    md_file.write(markdown)
    
# will likely use nested for loops to accomplish widget + queries
queries = json_data['state']['steps']

print('Md Docs created successfully!')