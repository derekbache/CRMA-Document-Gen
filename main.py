import json

# Read the JSON file
with open('json/predictiveFrameworkDash.json','r') as file:
    json_data = json.load(file)

# Takes in filter values as a list, outputs filter statement
def parse_filters(filters):
    try:
        def format_filter(filter):
            field, values, operator = filter
            if operator == '>=<=':
                operator = 'between'
            value_str = ', '.join(str(value) for value in values)
            if operator == 'in' or operator == 'not in':
                return f'{value_str} {operator} {field}'
            else:
                return f'{field} {operator} {value_str}'
        
        formatted_filters = [format_filter(filter) for filter in filters]
        return formatted_filters
    except Exception as e:
        return [f'Error: {str(e)}']

# Converts shortened visualization type and returns it in a more readable format
def convert_chart_type(input_value):
    chart_type_mapping = {
        "bubblemap": "Bubble Map",
        "calheatmap": "Calendar Heat Map",
        "choropleth": "Choropleth (Map)",
        "combo": "Lines and Bars to Show Multiple Metrics",
        "flatgauge": "Flat Gauge",
        "funnel": "Funnel",
        "hbar": "Horizontal Bar",
        "hdot": "Horizontal Dot Plot",
        "heatmap": "Heat Map",
        "matrix": "Matrix",
        "origami": "Origami",
        "parallelcoords": "Parallel Coordinates",
        "pie": "Donut",
        "pivottable": "Pivot Table",
        "polargauge": "Polar Gauge",
        "pyramid": "Pyramid",
        "rating": "Rating",
        "scatter": "Scatter Plot",
        "stackhbar": "Stacked Horizontal Bar",
        "stackpyramid": "Stacked Pyramid",
        "stackvbar": "Stacked Vertical Bar",
        "stackwaterfall": "Stacked Waterfall",
        "time": "Timeline",
        "time-bar": "Time Bar",
        "time-combo": "Time Bar",
        "treemap": "Tree Map",
        "vbar": "Vertical Bar",
        "vdot": "Vertical Dot Plot",
        "waterfall": "Waterfall"
    }
    
    return chart_type_mapping.get(input_value, input_value)

# Must figure out way to capture mydomain, for now input will do
mydomain = 'https://searchdiscoverydemo.lightning.force.com'
markdown = ''
name = json_data['label']

# Header
markdown += f'# {name} Documentation\n\n'
markdown += f'## Description  \n'

# Dataset
datasets = json_data['datasets']
markdown += '## Datasets\n\n'
for index, dataset in enumerate(datasets, start=1):
    datasetid = dataset['url'].split('/')[-1]
    markdown += f'{index}. ' + '[' + f'{dataset["name"]}' + '](' + f'{mydomain}' + '/lightning/r/EdgeMart/' f'{datasetid}' + '/view)\n\n'

# Filters
filters = json_data['state']['filters']
markdown += '## Global Filters\n\n'
for index, filter in enumerate(filters , start=1):
    markdown += f'{index}. **{filter["fields"][0]}** from the ***{filter["dataset"]["name"]}*** dataset  \n'

# Widgets
charts = json_data['state']['widgets']
markdown += '\n## Charts\n\n'
chart_number = 1
for chartname, chartdata in charts.items():
    if chartdata['type'] == 'number':
        chart_title = chartdata['parameters']['title']
        if not chart_title:
            chart_title = 'N/A'
        chart_step = chartdata['parameters']['step']
        markdown += f'{chart_number}. **{chartname}**  \n'
        markdown += f'    * Type: {chartdata["type"]}  \n'
        markdown += f'    * Title: {chart_title}  \n'
        markdown += f'    * Query: {chart_step}  \n'
    elif chartdata['type'] == 'chart':
        chart_title = chartdata['parameters']['title']['label']
        if not chart_title:
            chart_title = 'N/A'
        chart_step = chartdata['parameters']['step']
        chart_visual = convert_chart_type(chartdata['parameters']['visualizationType'])
        chart_columnMap_trellis = chartdata['parameters']['columnMap']['trellis']
        if not chart_columnMap_trellis:
            chart_columnMap_trellis = ['N/A']
        if 'dimension' in chartdata['parameters']['columnMap']:
            chart_columnMap_dimension = chartdata['parameters']['columnMap']['dimension']
        elif 'dimensionAxis' in chartdata['parameters']['columnMap']:
            chart_columnMap_dimension = chartdata['parameters']['columnMap']['dimensionAxis']
        else:
            chart_columnMap_dimension = ['N/A']
        chart_columnMap_plots = chartdata['parameters']['columnMap']['plots']
        if not chart_columnMap_plots:
            chart_columnMap_plots = ['N/A']
        markdown += f'{chart_number}. **{chartname}**  \n'
        markdown += f'    * Type: {chartdata["type"]}  \n'
        markdown += f'    * Title: {chart_title}  \n'
        markdown += f'    * Query: {chart_step}  \n'
        markdown += f'    * Visualization: {chart_visual}  \n'
        markdown += f'    * Trellis: {", ".join(str(trellis) for trellis in chart_columnMap_trellis)}  \n'
        markdown += f'    * Dimension(s): {", ".join(str(dimension) for dimension in chart_columnMap_dimension)}  \n'
        markdown += f'    * Plot(s): {", ".join(str(plot) for plot in chart_columnMap_plots)}  \n'
    else:
        continue
    markdown += '</br> \n'
    chart_number += 1

# Steps
# Does not support apex or grain Step Types https://developer.salesforce.com/docs/atlas.en-us.bi_dev_guide_json.meta/bi_dev_guide_json/bi_dbjson_steps_properties.htm
queries = json_data['state']['steps']
step_number = 1
query_dict = {'aggregateflex':{},'saqlsoql':{},'staticflex':{}} 

for queryname, querydata in queries.items():
    if querydata['type'] == 'aggregateflex':
        for dataset in querydata['datasets']:
            dataset_label = dataset['label']
            query_label = querydata.get('label')
            if not query_label:
                query_label = queryname
            query = {queryname:{'orders':querydata['query']['orders'], 'sources':querydata['query']['sources']}}
            if dataset_label in query_dict['aggregateflex']:
                query_dict['aggregateflex'][dataset_label].append(query)
            else:
                query_dict['aggregateflex'][dataset_label] = [query]
            
    elif querydata['type'] == 'saql' or querydata['type'] == 'soql':
        query_label = querydata.get('label')
        if not query_label:
            query_label = queryname
        query = querydata['query']
        query_dict['saqlsoql'][query_label] = query
    elif querydata['type'] == 'staticflex':
        query_label = querydata.get('label')
        if not query_label:
            query_label = queryname
        headers = list(querydata['columns'].keys())
        rows = [[item[column] for column in headers] for item in querydata['values']]
        query_dict['staticflex'][query_label] = {'headers':headers,'rows':rows}

markdown += '\n## Query Definitions  \n\n'
for datasetname, stepdata in query_dict['aggregateflex'].items():
    markdown += f'### Dataset: {datasetname}\n\n'
    for i, step in enumerate(stepdata, start=1):
        markdown += f'{i}. **{next(iter(step))}**  \n'
        markdown += '   * **Columns:**  \n\n'
        column_list= step[next(iter(step))]["sources"][0]["columns"]
        for column in column_list:
            markdown += f'     - {column["name"]} = {column["field"]}  \n\n'
        markdown += '   * **Filters:**  \n\n'
        filter_list= step[next(iter(step))]["sources"][0]["filters"]
        parsed_filters = parse_filters(filter_list)
        if not parsed_filters:
            markdown += '     N/A\n'
        else:
            for filter in parse_filters(filter_list):
                markdown += f'     - {filter}\n'
        markdown += '\n</br>\n\n'
    markdown += '\n'
markdown += '### SAQL/SOQL Queries\n'
for i, (queryname, querydata) in enumerate(query_dict['saqlsoql'].items(), start = 1):
    markdown += f'{i}. {queryname}\n'
    markdown += f'```\n{querydata}\n ```'
    markdown += '\n'
markdown += '### StaticFlex Tables\n'
for i, (queryname, querydata) in enumerate(query_dict['staticflex'].items(), start = 1):
    markdown += f'{i}. {queryname}\n\n'
    markdown += f'| {" | ".join(querydata["headers"])} |\n| {" | ".join(["---"] * len(headers))} |\n'
    for row in querydata['rows']:
        markdown += f'| {" | ".join(row)} |\n'
# Create Markdown file
with open(f'docs/{name}.md','w') as md_file:
    md_file.write(markdown)
# print(query_dict['aggregateflex'])
print('Md Docs created successfully!')