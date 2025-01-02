import boto3
import pandas as pd
from botocore.exceptions import ClientError
import time
import os
import sys

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

access_key = os.environ['ACCESS_KEY']
secret_key = os.environ['SECRET_KEY']
session_token = os.environ["SESSION_TOKEN"]
region = 'eu-west-1'

domain_name = 'te-dip'
project_name = 'Admin'
excel_file_path="/Users/nehal.chaurasia/Library/CloudStorage/OneDrive-CollinsonCentralServicesLimited/Collinson Business Glossary v1.1.xlsx"
sheet_name = 'Business Glossary'

# Create a Glossary.
def create_glossary(domain_name_id, glossary_name, description, project_id):
    response = datazone_client.create_glossary(
        domainIdentifier=domain_name_id,
        name=glossary_name,
        description=description,
        owningProjectIdentifier=project_id
    )
    
# Create a Business Term.
def create_business_term(domain_name_id, glossary_id, description, business_term):
    response = datazone_client.create_glossary_term(
        domainIdentifier=domain_name_id,
        glossaryIdentifier=glossary_id,
        longDescription=description,
        name=business_term,
        status='ENABLED'
    )

def create_glossary_list():
    response = datazone_client.search(domainIdentifier=domain_id.get(domain_name), searchScope='GLOSSARY')
    glossary_id = {}
    for glossary in response['items']:
        glossary_name = glossary['glossaryItem']['name']
        glossary_name_id = glossary['glossaryItem']['id']
        glossary_id[glossary_name] = glossary_name_id
    return glossary_id

# Create Boto3 client for AWS DataZone
datazone_client = boto3.client(
                    'datazone',
                    region_name = 'eu-west-1',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    aws_session_token = session_token,
                    verify=False)

# Create list of domain's
response = datazone_client.list_domains()
domain_id = {}
for domain in response['items']:
    domain_name = domain['name']
    domain_name_id = domain['id']
    domain_id[domain_name] = domain_name_id

# Create list of project's
response = datazone_client.list_projects(domainIdentifier=domain_id.get(domain_name))
project_id = {}
for project in response['items']:
    project_name = project['name']
    project_name_id = project['id']
    project_id[project_name] = project_name_id

# Read excel file in a df
glossary_df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
glossary_df = glossary_df.dropna(subset=["Glossary"])
glossary_df = glossary_df.dropna(subset=["Business Term"])
glossary_df["Description"] = glossary_df["Description"].fillna("")
# glossary_df = glossary_df[glossary_df['Glossary'] == 'AI Model']

for index, row in glossary_df.iterrows():
    glossary = row["Glossary"]
    business_term = row["Business Term"]
    description = row["Description"] 
    
    glossary = str(glossary)

    # Create glossay
    glossary_id = create_glossary_list()
    if not glossary.lower() in (key.lower() for key in glossary_id):
        create_glossary(domain_id.get(domain_name), glossary, 'No Description', project_id.get(project_name))
        time.sleep(30)
    
    glossary_id = create_glossary_list()
    if glossary not in glossary_id.keys():
        print("Sleeping for 2 mins for glossary to get created.")
        time.sleep(120)

    # Create business term
    glossary_id = create_glossary_list()
    try:
        create_business_term(domain_id.get(domain_name), glossary_id.get(glossary), description, business_term)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConflictException':
            print(f"Business term '{business_term}' already exists in glossary. Skipping.")
    except Exception as e:
        print(f"Glossary Name : {glossary}")
        print(f"Glossary Identifier : {glossary_id.get(glossary)}")
        print(f"Glossary Term : {business_term}")
        print(f"An unexpected error occurred: {e}")
    