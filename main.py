import json
import time
import re
import os
import requests

from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from urllib.parse import urlparse, quote

# *** TO DO LIST ***
# Add in support for other widgets https://developer.salesforce.com/docs/atlas.en-us.bi_dev_guide_json.meta/bi_dev_guide_json/bi_dbjson_widgets_parameters.htm
# Doesn't support multiple tabs
#  **** USE SELENIUM? TO OBTAIN JSON **** 

# Takes in filter data as a list, outputs filters in readable format as a list
def parse_filters(filters):
    try:
        def format_filter(filter):
            field, values, operator = filter
            if operator == '>=<=':
                operator = 'between'
            if operator == 'isnotnull':
                operator = 'is not null'
            if operator == 'isnull':
                operator = 'is null'
            value_str = ', '.join(str(value) for value in values)
            if operator == 'in' or operator == 'not in':
                return f'{value_str} {operator} {field}'
            else:
                return f'{field} {operator} {value_str}'
        
        formatted_filters = [format_filter(filter) for filter in filters]
        return formatted_filters
    except:
        return filters
    
# Takes in column data as a list, outputs them in readable format as a list
def parse_column(column):
    try:
        if len(column) == 1:
            return column
        operation, field = column
        if field == '*':
            field = 'Rows'
        formatted_column = f'{operation.capitalize()} of {field}'
        return formatted_column
    except:
        return column

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

# Capture a screenshot of the widget using the widget name as input
# Does not support widgets in secondary tabs, yet
def image_capture(chart_name, pause_seconds=1):
    try:
        element = driver.find_element(By.CLASS_NAME, f'widget-container_{chart_name}')
        driver.execute_script("arguments[0].scrollIntoView();", element)
        screenshot_path = f'documentation/img/{chart_name}.png'
        time.sleep(pause_seconds);
        element.screenshot(screenshot_path)
    except Exception as e:
        return [f'Error: {str(e)}']

# Download PNG of Dashboard, in progress
def download_png(dashboard_name, dashboard_id, domain):
    image_url = f'{domain}/analytics/download/lightning-dashboard/{dashboard_id}.png'
    folder_path = 'documentation/img'

    image_file_path = os.path.join(folder_path, f'{dashboard_name}.png')

    response = requests.get(image_url)

    if response.status_code == 200:
        with open(image_file_path, 'wb') as image_file:
            image_file.write(response.content)
        print(f"Image saved to {image_file_path}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}")


# Load env variables
# .env file in root must contain USERNAME, PASSWORD, DASHBOARD_URL, NAME, EMAIL variables
load_dotenv()

# Ensure project folders exist; create them if not
base_directory = os.path.dirname(__file__)
folders_to_create = ['documentation', 'documentation/img', 'documentation/json']

for folder_path in folders_to_create:
    full_path = os.path.join(base_directory, folder_path)
    if not os.path.exists(full_path):
        os.makedirs(full_path)

# Open env variables to get dashboard URL and mydomain
dashboard_url = os.getenv('DASHBOARD_URL')
submittername = os.getenv('NAME')
submitteremail = os.getenv('EMAIL')

# Parse URL to obtain domain
mydomain = f'https://{urlparse(dashboard_url).netloc}'

# Use a regular expression to extract the 18-character digit ID
match = re.search(r'/dashboard/([A-Za-z0-9]{18})', urlparse(dashboard_url).path)

if match:
    dashboard_id = match.group(1)
    # download_png(dashboard_id)
else:
    print("Dashboard ID not found.")

# Selenium opens dashboard in Chrome so it can take images of number/chart widgets
driver = webdriver.Chrome()
driver.set_window_size(1920,1080)
driver.get(dashboard_url)

# Login
time.sleep(1);
driver.find_element(By.ID,"username").send_keys(os.getenv('USERNAME'));
driver.find_element(By.ID,"password").send_keys(os.getenv('PASSWORD'));
driver.find_element(By.ID,"Login").click();

# Pause for dashboard loading
time.sleep(5)

# Read the JSON file
with open('documentation/json/predictiveFrameworkDash.json','r') as file:
    json_data = json.load(file)
    
# Create initial markdown text
markdown = ''
name = json_data['label']

# Header
markdown += f'# {name} Documentation\n\n'
today = date.today()
markdown += f'Documentation Created: {today.strftime("%B %d, %Y")}  \n'
markdown += f'Documentation Created By: {submittername} @ [{submitteremail}](mailto:{submitteremail}?subject={quote(name)})  \n'
markdown += f'Dashboard Link: [{name}]({dashboard_url})  \n'
markdown += f'## Description  \n'

# Dataset
datasets = json_data['datasets']
markdown += '## Datasets\n\n'
for index, dataset in enumerate(datasets, start=1):
    datasetid = dataset['url'].split('/')[-1]
    markdown += f'{index}. [{dataset["name"]}]({mydomain}/lightning/r/EdgeMart/{datasetid}/view)  \n\n'

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
        image_capture(chartname)
        chart_title = chartdata['parameters'].get('title')
        if not chart_title:
            chart_title = 'N/A'
        chart_step = chartdata['parameters']['step']

        markdown += f'{chart_number}. **{chartname}**  \n'
        markdown += f'    * Type: {chartdata["type"]}  \n'
        markdown += f'    * Title: {chart_title}  \n'
        markdown += f'    * Query: {chart_step}  \n'
        if os.path.exists(f'./documentation/img/{chartname}.png'):
            markdown += f'    ![image](/documentation/img/{chartname}.png)  \n'
    elif chartdata['type'] == 'chart':
        chart_title = chartdata['parameters']['title']['label']
        if not chart_title:
            chart_title = 'N/A'
        chart_step = chartdata['parameters']['step']
        chart_visual = convert_chart_type(chartdata['parameters']['visualizationType'])
        if chart_visual == 'bubblemap':
            image_capture(chartname, 3)
        else:
            image_capture(chartname)
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
        if os.path.exists(f'./documentation/img/{chartname}.png'):
            markdown += f'    ![image](/documentation/img/{chartname}.png)  \n'
    elif chartdata['type'] == 'table':
        image_capture(chartname)
        chart_step = chartdata['parameters']['step']
        columns = chartdata['parameters']['columns']
        markdown += f'{chart_number}. **{chartname}**  \n'
        markdown += f'    * Type: {chartdata["type"]}  \n'
        markdown += f'    * Query: {chart_step}  \n'
        markdown += f'    * Columns: {", ".join(columns)}  \n'
        if os.path.exists(f'./documentation/img/{chartname}.png'):
            markdown += f'    ![image](/documentation/img/{chartname}.png)  \n'
    else:
        continue
    markdown += '</br> \n'
    chart_number += 1

# Steps
# Does not support apex or grain Step Types https://developer.salesforce.com/docs/atlas.en-us.bi_dev_guide_json.meta/bi_dev_guide_json/bi_dbjson_steps_properties.htm
queries = json_data['state']['steps']
step_number = 1
query_dict = {'aggregateflex':{},'saqlsoql':{},'staticflex':{}} 

# Restructures how steps are organized
for queryname, querydata in queries.items():
    if querydata['type'] == 'aggregateflex':
        for dataset in querydata['datasets']:
            dataset_label = dataset['label']
            query_label = querydata.get('label')
            if not query_label:
                query_label = queryname
            query = {query_label:{'orders':querydata['query']['orders'], 'sources':querydata['query']['sources'], 'sourceFilters':querydata['query']['sourceFilters']}}
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

markdown += '\n## Query Definitions  \n'
for datasetname, stepdata in query_dict['aggregateflex'].items():
    markdown += f'### Dataset: {datasetname}  \n'
    for i, step in enumerate(stepdata, start=1):
        markdown += f'{i}. **{next(iter(step))}**  \n'
        markdown += '   * **Columns:**  \n'
        column_list = step[next(iter(step))]["sources"][0]["columns"]
        for column in column_list:
            markdown += f'     - {column["name"]} = {parse_column(column["field"])}  \n'
        filter_list = step[next(iter(step))]["sources"][0]["filters"]
        parsed_filters = parse_filters(filter_list)
        if parsed_filters:
            markdown += '   * **Column Filters:**  \n'
            for filter in parse_filters(filter_list):
                markdown += f'     - {filter}  \n'
        markdown += '   * **Group By:**  \n'
        group_list = step[next(iter(step))]["sources"][0]["groups"]
        for group in group_list:
            markdown += f'     - {group}  \n'
        source_filter_list = step[next(iter(step))].get('sourceFilters')
        print('source_filter_list')
        print(source_filter_list)
        if source_filter_list:
            for source, filter in source_filter_list.items():
                markdown += '   * **Source Filters:**  \n'
                for filter in parse_filters(filter["filters"]):
                    markdown += f'     - {filter}  \n'
                # print('step:')
                # print(step[next(iter(step))])
                # print('source = ' + source)
                # print('filters:')
                # print(parse_filters(filter['filters']))
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
with open(f'documentation/{name}.md','w') as md_file:
    md_file.write(markdown)

print('Md documentation created successfully!')