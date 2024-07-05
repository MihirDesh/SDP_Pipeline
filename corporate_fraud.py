from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from azure.search.documents.indexes.models import (
    SearchFieldDataType,
    SearchableField,
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch,
    SearchIndex
)
import json

# OpenAI text embedding model ADA
azure_openai_endpoint = "https://SDP-OpenAI-Resource.openai.azure.com/openai/deployments/text-embedding-ada-002-2/embeddings?api-version=2023-05-15"
azure_openai_key = "e1c07c8cdee94cc9ada9d5ce56b88cef"
azure_openai_em_name = "text-embedding-ada-002" 
azure_openai_version_em = "2023-05-15"
azure_openai_model_dep_name_em = "text-embedding-ada-002-2"

# CLIENT FOR EMBEDDING
client = AzureOpenAI(
    azure_deployment=azure_openai_model_dep_name_em,
    api_version=azure_openai_version_em,
    azure_endpoint=azure_openai_endpoint,
    api_key=azure_openai_key,
)

# Getting data from blob storage
AZURE_STORAGE_ACCOUNT_NAME = 'frauddetect1578932446'
AZURE_STORAGE_ACCOUNT_KEY = 'bJEfK0Kj1EaYaKji0jDV7AvgPBUgfPuCwIWtM0R5uuRBQUb07PSyp7PV8mMCwBSOtIVS2+93lq68+AStTZx7zA=='
CONTAINER_NAME = 'corporatefraud'
blob_service_client = BlobServiceClient(account_url=f'https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net', credential=AZURE_STORAGE_ACCOUNT_KEY)
container_client = blob_service_client.get_container_client(container=CONTAINER_NAME)
blob_list = container_client.list_blobs()

# Creating document intelligence instance
doc_endpoint = "https://frauddocumentintelligence.cognitiveservices.azure.com/"
doc_apikey = "73ad3d41060f40f9ab4fe5199a9d8b00"
document_client = DocumentAnalysisClient(doc_endpoint, AzureKeyCredential(doc_apikey))

# Creating a list of documents
document_list = []
for blob in blob_list:
    if blob.name == 'llminput.json' or blob.name == 'corporate_dataset.json':
        continue
    
    blob_client = container_client.get_blob_client(blob.name)
    downloaded_blob = blob_client.download_blob()
    pdf_content = downloaded_blob.readall()
    poller = document_client.begin_analyze_document("prebuilt-document", pdf_content)
    result = poller.result()
    full_text = ""
    for page in result.pages:
        for line in page.lines:
            full_text += line.content + "\n"
    document_list.append(full_text)

with open('./corporate_dataset.json', 'r') as f:
    data = json.load(f)

#mapped structured and unstructured data

for i in range(1,11,1):
    for document in document_list:
        if f"CompanyID = {str(i)}" in document:
            for customer in data:
                customer['document_text'] = "a"
                if(customer['CompanyID'] == str(i)):
                    customer['document_text'] += document


index_name = "corporate-index4"
service_endpoint = "https://ai-search-fraud.search.windows.net"
admin_key = "DOnPZ8CHtXlQuFoL5EMBrfTSHFR3BeXcEYty20fjdmAzSeDHIuXZ"
search_client = SearchIndexClient(service_endpoint,AzureKeyCredential(admin_key))

fields = [
    SearchableField(name="CompanyID", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
    SearchableField(name="Date", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="Debit_Credit", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="Amount", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="CompanyAccount", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="TransactionDescription", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="FinalBalance", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="TransactionID", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="MerchantFirmName", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="MerchantID", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="document_text", type=SearchFieldDataType.String),
    SearchField(name="company_id_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="date_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="debit_credit_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="amount_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="company_account_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="transaction_description_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="final_balance_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="transaction_id_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="merchant_firm_name_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="merchant_id_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="document_text_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
]

company_id = [str(dataitem['CompanyID']) for dataitem in data]
date_new = [str(dataitem['Date']) for dataitem in data]
debit_credit = [str(dataitem['Debit_Credit']) for dataitem in data]
amount = [str(dataitem['Amount']) for dataitem in data]
company_account = [str(dataitem['CompanyAccount']) for dataitem in data]
transaction_description = [str(dataitem['TransactionDescription']) for dataitem in data]
final_balance = [str(dataitem['FinalBalance']) for dataitem in data]
transaction_id = [str(dataitem['TransactionID']) for dataitem in data]
merchant_firm_name = [str(dataitem['MerchantFirmName']) for dataitem in data]
merchant_id = [str(dataitem['MerchantID']) for dataitem in data]
document_texts = [str(dataitem['document_text']) for dataitem in data]

# Creating embeddings
company_id_response = client.embeddings.create(input=company_id, model=azure_openai_em_name)
company_id_embeddings = [item.embedding for item in company_id_response.data]

date_response = client.embeddings.create(input=date_new, model=azure_openai_em_name)
date_embeddings = [item.embedding for item in date_response.data]

debit_credit_response = client.embeddings.create(input=debit_credit, model=azure_openai_em_name)
debit_credit_embeddings = [item.embedding for item in debit_credit_response.data]

amount_response = client.embeddings.create(input=amount, model=azure_openai_em_name)
amount_embeddings = [item.embedding for item in amount_response.data]

company_account_response = client.embeddings.create(input=company_account, model=azure_openai_em_name)
company_account_embeddings = [item.embedding for item in company_account_response.data]

transaction_description_response = client.embeddings.create(input=transaction_description, model=azure_openai_em_name)
transaction_description_embeddings = [item.embedding for item in transaction_description_response.data]

final_balance_response = client.embeddings.create(input=final_balance, model=azure_openai_em_name)
final_balance_embeddings = [item.embedding for item in final_balance_response.data]

transaction_id_response = client.embeddings.create(input=transaction_id, model=azure_openai_em_name)
transaction_id_embeddings = [item.embedding for item in transaction_id_response.data]

merchant_firm_name_response = client.embeddings.create(input=merchant_firm_name, model=azure_openai_em_name)
merchant_firm_name_embeddings = [item.embedding for item in merchant_firm_name_response.data]

merchant_id_response = client.embeddings.create(input=merchant_id, model=azure_openai_em_name)
merchant_id_embeddings = [item.embedding for item in merchant_id_response.data]

document_texts_response = client.embeddings.create(input=document_texts, model=azure_openai_em_name)
document_texts_embeddings = [item.embedding for item in document_texts_response.data]

# Adding the vectors to each data item in the data
for i, dataitem in enumerate(data):
    dataitem['company_id_Vector'] = company_id_embeddings[i]
    dataitem['date_Vector'] = date_embeddings[i]
    dataitem['debit_credit_Vector'] = debit_credit_embeddings[i]
    dataitem['amount_Vector'] = amount_embeddings[i]
    dataitem['company_account_Vector'] = company_account_embeddings[i]
    dataitem['transaction_description_Vector'] = transaction_description_embeddings[i]
    dataitem['final_balance_Vector'] = final_balance_embeddings[i]
    dataitem['transaction_id_Vector'] = transaction_id_embeddings[i]
    dataitem['merchant_firm_name_Vector'] = merchant_firm_name_embeddings[i]
    dataitem['merchant_id_Vector'] = merchant_id_embeddings[i]
    dataitem['document_text_Vector'] = document_texts_embeddings[i]
    
#indexing process
new_blob_name = 'llminput.json'
new_blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=new_blob_name)

# Open the local file and upload its contents
data_string = json.dumps(data)
new_blob_client.upload_blob(data_string, overwrite=True)
print(f"File {new_blob_name} uplaoded to Azure Blob Storage in container {CONTAINER_NAME}")

#defining the vector search algorithm
vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(
            name="myHnsw"
        )
    ],
    profiles=[
        VectorSearchProfile(
            name="myHnswProfile",
            algorithm_configuration_name="myHnsw",
        )
    ]
)

# Create the search index and defining the algorithm we previously created
index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)
result = search_client.create_or_update_index(index)
print(f'{result.name} created')

# Getting the mapped and embedded data from the blob
blob_client = container_client.get_blob_client('llminput.json')
blob_data = blob_client.download_blob()

json_data = json.loads(blob_data.readall())

# Upload the documents to the vector store
search_client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=AzureKeyCredential(admin_key))
results = search_client.upload_documents(json_data)
print(f"Uploaded {len(json_data)} documents")

# Function to vectorize the prompt
field_string = "company_id_Vector, final_balance_Vector, transaction_id_Vector, merchant_firm_name_Vector, merchant_id_Vector, document_text_Vector"

query = "Provide all the details of CompanyID: 1 transactions"

def get_embedding(query):
    embedding = client.embeddings.create(input=query, model=azure_openai_em_name).data[0].embedding
    vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=3, fields=field_string)
    return vector_query

content = get_embedding(query)

select = [
    "CompanyID",
    "Date",
    "Debit_Credit",
    "Amount",
    "CompanyAccount",
    "TransactionDescription",
    "FinalBalance",
    "TransactionID",
    "MerchantFirmName",
    "MerchantID",
    "document_text"
]

results = search_client.search(
    search_text=None,
    vector_queries=[content],
    select=select
  
)
try:
    context = next(results)
    print("Search results found. Proceeding with analysis.")
except StopIteration:
    print("No search results found. The query didn't match any documents.")
    context = None

if context:
    # Integrating OpenAI
    api_base = "https://sdp-openai-resource.openai.azure.com/"
    api_key = "e1c07c8cdee94cc9ada9d5ce56b88cef"
    deployment_name = "gpt-4o"
    api_version = '2024-05-01-preview'

    client = AzureOpenAI(
        api_key = api_key,
        api_version = api_version,
        base_url=f"{api_base}/openai/deployments/{deployment_name}"
    )

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": "You are an expert financial specializing in corporate fraud detection."},
            {"role": "user", "content": f"This is the search query: {query}, this is the content: {context}. Based on the transaction data and company information provide a detailed report on the potential fraud indicators and overall financial health. Also show the document text not the vector, just the text in that object. give a detailed explanation of document text."}
        ],
        max_tokens=4000
    )

    print(response.choices[0].message.content)
else:
    print("Unable to proceed with OpenAI analysis due to lack of search results.")

