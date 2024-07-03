from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
import azure.cognitiveservices.speech as speechsdk

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

#openai text embedding model ADA

azure_openai_endpoint = "https://SDP-OpenAI-Resource.openai.azure.com/openai/deployments/text-embedding-ada-002-2/embeddings?api-version=2023-05-15"
azure_openai_key = "e1c07c8cdee94cc9ada9d5ce56b88cef"
azure_openai_em_name = "text-embedding-ada-002" 
azure_openai_version_em = "2023-05-15"
azure_openai_model_dep_name_em = "text-embedding-ada-002-2"

#CLIENT FOR EMBEDDING
client = AzureOpenAI(
    azure_deployment=azure_openai_model_dep_name_em,
    api_version=azure_openai_version_em,
    azure_endpoint=azure_openai_endpoint,
    api_key=azure_openai_key,
   
)

#getting data from blob storage

AZURE_STORAGE_ACCOUNT_NAME = 'frauddetect1578932446'
AZURE_STORAGE_ACCOUNT_KEY = 'bJEfK0Kj1EaYaKji0jDV7AvgPBUgfPuCwIWtM0R5uuRBQUb07PSyp7PV8mMCwBSOtIVS2+93lq68+AStTZx7zA=='
CONTAINER_NAME = 'unstructureddata'
blob_service_client = BlobServiceClient(account_url=f'https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net', credential=AZURE_STORAGE_ACCOUNT_KEY)
container_client = blob_service_client.get_container_client(container=CONTAINER_NAME)
blob_list = container_client.list_blobs()



#creating document intelligence instance
doc_endpoint = "https://frauddocumentintelligence.cognitiveservices.azure.com/"
doc_apikey = "73ad3d41060f40f9ab4fe5199a9d8b00"
document_client = DocumentAnalysisClient(doc_endpoint,AzureKeyCredential(doc_apikey))

#creating a list of documents.

document_list = []

for blob in blob_list:
    if blob.name == 'llminputdata.json' or blob.name == "llminputdatafinal.json" or blob.name == 'customer_data.json':
        continue
    
    blob_client = container_client.get_blob_client(blob.name)
    downloaded_blob = blob_client.download_blob()
    pdf_content = downloaded_blob.readall()
    poller = document_client.begin_analyze_document("prebuilt-document",pdf_content)
    result = poller.result()
    full_text = ""
    for page in result.pages:
        for line in page.lines:
            full_text += line.content + "\n"
    document_list.append(full_text)


blob_client = container_client.get_blob_client('customer_data.json')
downloaded_blob = blob_client.download_blob()
data= downloaded_blob.readall()
data = json.loads(data)
# with open("./customer_data.json",'r') as f:
#     data = json.load(f)

    

#mapped structured and unstructured data

for i in range(1,11,1):
    for document in document_list:
        if f"CustomerID: {str(i)}" in document:
            for customer in data:
                customer['document_text'] = "a"
                if(customer['CustomerID'] == str(i)):
                   
                    customer['document_text'] += document
                    

                    
# with open("./customer_data.json", 'w') as f:
#     json.dump(data, f, indent=4) 




#creating indexes


index_name = "customer-index9"
service_endpoint = "https://ai-search-fraud.search.windows.net"
admin_key = "DOnPZ8CHtXlQuFoL5EMBrfTSHFR3BeXcEYty20fjdmAzSeDHIuXZ"
search_client = SearchIndexClient(service_endpoint,AzureKeyCredential(admin_key))



fields = [
    SearchableField(name="CustomerID", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
    SearchableField(name="SeriousDlqin2yrs", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="RevolvingUtilizationOfUnsecuredLines", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="Age", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="NumberOfTime30_59DaysPastDueNotWorse", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="DebtRatio", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="MonthlyIncome", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="NumberOfOpenCreditLinesAndLoans", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="NumberOfTimes90DaysLate", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="NumberRealEstateLoansOrLines", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="NumberOfTime60_89DaysPastDueNotWorse", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="NumberOfDependents", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="CreditScore", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="CreditHistoryLength", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="PaymentHistoryScore", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="LTV", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="TotalAssets", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="TotalLiabilities", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="EmploymentStatus_Student", type=SearchFieldDataType.String, filterable=True),
    SearchableField(name="EmploymentStatus_Unemployed", type=SearchFieldDataType.String, filterable=True),
    SearchableField(name="EmploymentStatus_Retired", type=SearchFieldDataType.String, filterable=True),
    SearchableField(name="EducationLevel_Bachelor_Degree", type=SearchFieldDataType.String, filterable=True),
    SearchableField(name="EducationLevel_High_School", type=SearchFieldDataType.String, filterable=True),
    SearchableField(name="EducationLevel_Master_Degree", type=SearchFieldDataType.String, filterable=True),
    SearchableField(name="EducationLevel_PhD", type=SearchFieldDataType.String, filterable=True),
    SearchableField(name="CustomerFeedback", type=SearchFieldDataType.String),
    SearchableField(name="CustomerServiceLog", type=SearchFieldDataType.String),
    SearchableField(name="FeedbackSentimentScore", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="ServiceLogSentimentScore", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchableField(name="document_text", type=SearchFieldDataType.String),
    SearchField(name="cust_id_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="serious_dlqin2yrs_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="revolving_utilization_of_unsecured_lines_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="age_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="num_time_30_59_days_past_due_not_worse_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="debt_ratio_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="monthly_income_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="num_open_credit_lines_and_loans_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="num_times_90_days_late_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="num_real_estate_loans_or_lines_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="num_time_60_89_days_past_due_not_worse_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="num_dependents_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="credit_score_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="credit_history_length_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="payment_history_score_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="ltv_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="total_assets_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="total_liabilities_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="employment_status_retired_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="employment_status_student_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="employment_status_unemployed_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="education_level_bachelor_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="education_level_high_school_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="education_level_master_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="education_level_phd_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="customer_feedback_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="customer_service_log_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="feedback_sentiment_score_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="service_log_sentiment_score_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="document_text_Vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
]



cust_ids = [str(dataitem['CustomerID']) for dataitem in data]
serious_dlqin2yrs = [str(dataitem['SeriousDlqin2yrs']) for dataitem in data]
revolving_utilization_of_unsecured_lines = [str(dataitem['RevolvingUtilizationOfUnsecuredLines']) for dataitem in data]
ages = [str(dataitem['age']) for dataitem in data]
num_time_30_59_days_past_due_not_worse = [str(dataitem['NumberOfTime30_59DaysPastDueNotWorse']) for dataitem in data]
debt_ratios = [str(dataitem['DebtRatio']) for dataitem in data]
monthly_incomes = [str(dataitem['MonthlyIncome']) for dataitem in data]
num_open_credit_lines_and_loans = [str(dataitem['NumberOfOpenCreditLinesAndLoans']) for dataitem in data]
num_times_90_days_late = [str(dataitem['NumberOfTimes90DaysLate']) for dataitem in data]
num_real_estate_loans_or_lines = [str(dataitem['NumberRealEstateLoansOrLines']) for dataitem in data]
num_time_60_89_days_past_due_not_worse = [str(dataitem['NumberOfTime60_89DaysPastDueNotWorse']) for dataitem in data]
num_dependents = [str(dataitem['NumberOfDependents']) for dataitem in data]
credit_scores = [str(dataitem['CreditScore']) for dataitem in data]
credit_history_lengths = [str(dataitem['CreditHistoryLength']) for dataitem in data]
payment_history_scores = [str(dataitem['PaymentHistoryScore']) for dataitem in data]
ltvs = [str(dataitem['LTV']) for dataitem in data]
total_assets = [str(dataitem['TotalAssets']) for dataitem in data]
total_liabilities = [str(dataitem['TotalLiabilities']) for dataitem in data]
employment_status_retired = [str(dataitem['EmploymentStatus_Retired']) for dataitem in data]
employment_status_student = [str(dataitem['EmploymentStatus_Student']) for dataitem in data]
employment_status_unemployed = [str(dataitem['EmploymentStatus_Unemployed']) for dataitem in data]
education_level_bachelor = [str(dataitem['EducationLevel_Bachelor_Degree']) for dataitem in data]
education_level_high_school = [str(dataitem['EducationLevel_High_School']) for dataitem in data]
education_level_master = [str(dataitem['EducationLevel_Master_Degree']) for dataitem in data]
education_level_phd = [str(dataitem['EducationLevel_PhD']) for dataitem in data]
customer_feedback = [dataitem['CustomerFeedback'] for dataitem in data]  # Assuming this is already a string
customer_service_log = [dataitem['CustomerServiceLog'] for dataitem in data]  # Assuming this is already a string
feedback_sentiment_score = [str(dataitem['FeedbackSentimentScore']) for dataitem in data]
service_log_sentiment_score = [str(dataitem['ServiceLogSentimentScore']) for dataitem in data]
document_texts = [str(dataitem['document_text']) for dataitem in data]

#creating the embeddings here

cust_ids_response = client.embeddings.create(input=cust_ids, model=azure_openai_em_name)
cust_id_embeddings = [item.embedding for item in cust_ids_response.data]

serious_dlqin2yrs_response = client.embeddings.create(input=serious_dlqin2yrs, model=azure_openai_em_name)
serious_dlqin2yrs_embeddings = [item.embedding for item in serious_dlqin2yrs_response.data]

revolving_utilization_of_unsecured_lines_response = client.embeddings.create(input=revolving_utilization_of_unsecured_lines, model=azure_openai_em_name)
revolving_utilization_of_unsecured_lines_embeddings = [item.embedding for item in revolving_utilization_of_unsecured_lines_response.data]

ages_response = client.embeddings.create(input=ages, model=azure_openai_em_name)
ages_embeddings = [item.embedding for item in ages_response.data]

num_time_30_59_days_past_due_not_worse_response = client.embeddings.create(input=num_time_30_59_days_past_due_not_worse, model=azure_openai_em_name)
num_time_30_59_days_past_due_not_worse_embeddings = [item.embedding for item in num_time_30_59_days_past_due_not_worse_response.data]

debt_ratios_response = client.embeddings.create(input=debt_ratios, model=azure_openai_em_name)
debt_ratios_embeddings = [item.embedding for item in debt_ratios_response.data]

monthly_incomes_response = client.embeddings.create(input=monthly_incomes, model=azure_openai_em_name)
monthly_incomes_embeddings = [item.embedding for item in monthly_incomes_response.data]

num_open_credit_lines_and_loans_response = client.embeddings.create(input=num_open_credit_lines_and_loans, model=azure_openai_em_name)
num_open_credit_lines_and_loans_embeddings = [item.embedding for item in num_open_credit_lines_and_loans_response.data]

num_times_90_days_late_response = client.embeddings.create(input=num_times_90_days_late, model=azure_openai_em_name)
num_times_90_days_late_embeddings = [item.embedding for item in num_times_90_days_late_response.data]

num_real_estate_loans_or_lines_response = client.embeddings.create(input=num_real_estate_loans_or_lines, model=azure_openai_em_name)
num_real_estate_loans_or_lines_embeddings = [item.embedding for item in num_real_estate_loans_or_lines_response.data]

num_time_60_89_days_past_due_not_worse_response = client.embeddings.create(input=num_time_60_89_days_past_due_not_worse, model=azure_openai_em_name)
num_time_60_89_days_past_due_not_worse_embeddings = [item.embedding for item in num_time_60_89_days_past_due_not_worse_response.data]

num_dependents_response = client.embeddings.create(input=num_dependents, model=azure_openai_em_name)
num_dependents_embeddings = [item.embedding for item in num_dependents_response.data]

credit_scores_response = client.embeddings.create(input=credit_scores, model=azure_openai_em_name)
credit_scores_embeddings = [item.embedding for item in credit_scores_response.data]

credit_history_lengths_response = client.embeddings.create(input=credit_history_lengths, model=azure_openai_em_name)
credit_history_lengths_embeddings = [item.embedding for item in credit_history_lengths_response.data]

payment_history_scores_response = client.embeddings.create(input=payment_history_scores, model=azure_openai_em_name)
payment_history_scores_embeddings = [item.embedding for item in payment_history_scores_response.data]

ltvs_response = client.embeddings.create(input=ltvs, model=azure_openai_em_name)
ltvs_embeddings = [item.embedding for item in ltvs_response.data]

total_assets_response = client.embeddings.create(input=total_assets, model=azure_openai_em_name)
total_assets_embeddings = [item.embedding for item in total_assets_response.data]

total_liabilities_response = client.embeddings.create(input=total_liabilities, model=azure_openai_em_name)
total_liabilities_embeddings = [item.embedding for item in total_liabilities_response.data]

employment_status_retired_response = client.embeddings.create(input=employment_status_retired, model=azure_openai_em_name)
employment_status_retired_embeddings = [item.embedding for item in employment_status_retired_response.data]

employment_status_student_response = client.embeddings.create(input=employment_status_student, model=azure_openai_em_name)
employment_status_student_embeddings = [item.embedding for item in employment_status_student_response.data]

employment_status_unemployed_response = client.embeddings.create(input=employment_status_unemployed, model=azure_openai_em_name)
employment_status_unemployed_embeddings = [item.embedding for item in employment_status_unemployed_response.data]

education_level_bachelor_response = client.embeddings.create(input=education_level_bachelor, model=azure_openai_em_name)
education_level_bachelor_embeddings = [item.embedding for item in education_level_bachelor_response.data]

education_level_high_school_response = client.embeddings.create(input=education_level_high_school, model=azure_openai_em_name)
education_level_high_school_embeddings = [item.embedding for item in education_level_high_school_response.data]

education_level_master_response = client.embeddings.create(input=education_level_master, model=azure_openai_em_name)
education_level_master_embeddings = [item.embedding for item in education_level_master_response.data]

education_level_phd_response = client.embeddings.create(input=education_level_phd, model=azure_openai_em_name)
education_level_phd_embeddings = [item.embedding for item in education_level_phd_response.data]

customer_feedback_response = client.embeddings.create(input=customer_feedback, model=azure_openai_em_name)
customer_feedback_embeddings = [item.embedding for item in customer_feedback_response.data]

customer_service_log_response = client.embeddings.create(input=customer_service_log, model=azure_openai_em_name)
customer_service_log_embeddings = [item.embedding for item in customer_service_log_response.data]

feedback_sentiment_score_response = client.embeddings.create(input=feedback_sentiment_score, model=azure_openai_em_name)
feedback_sentiment_score_embeddings = [item.embedding for item in feedback_sentiment_score_response.data]

service_log_sentiment_score_response = client.embeddings.create(input=service_log_sentiment_score, model=azure_openai_em_name)
service_log_sentiment_score_embeddings = [item.embedding for item in service_log_sentiment_score_response.data]

document_texts_response = client.embeddings.create(input=document_texts, model=azure_openai_em_name)
document_texts_embeddings = [item.embedding for item in document_texts_response.data]

#adding the vectors to each data item in the data

for i, dataitem in enumerate(data):
    dataitem['cust_id_Vector'] = cust_id_embeddings[i]
    dataitem['serious_dlqin2yrs_Vector'] = serious_dlqin2yrs_embeddings[i]
    dataitem['revolving_utilization_of_unsecured_lines_Vector'] = revolving_utilization_of_unsecured_lines_embeddings[i]
    dataitem['age_Vector'] = ages_embeddings[i]
    dataitem['num_time_30_59_days_past_due_not_worse_Vector'] = num_time_30_59_days_past_due_not_worse_embeddings[i]
    dataitem['debt_ratio_Vector'] = debt_ratios_embeddings[i]
    dataitem['monthly_income_Vector'] = monthly_incomes_embeddings[i]
    dataitem['num_open_credit_lines_and_loans_Vector'] = num_open_credit_lines_and_loans_embeddings[i]
    dataitem['num_times_90_days_late_Vector'] = num_times_90_days_late_embeddings[i]
    dataitem['num_real_estate_loans_or_lines_Vector'] = num_real_estate_loans_or_lines_embeddings[i]
    dataitem['num_time_60_89_days_past_due_not_worse_Vector'] = num_time_60_89_days_past_due_not_worse_embeddings[i]
    dataitem['num_dependents_Vector'] = num_dependents_embeddings[i]
    dataitem['credit_score_Vector'] = credit_scores_embeddings[i]
    dataitem['credit_history_length_Vector'] = credit_history_lengths_embeddings[i]
    dataitem['payment_history_score_Vector'] = payment_history_scores_embeddings[i]
    dataitem['ltv_Vector'] = ltvs_embeddings[i]
    dataitem['total_assets_Vector'] = total_assets_embeddings[i]
    dataitem['total_liabilities_Vector'] = total_liabilities_embeddings[i]
    dataitem['employment_status_retired_Vector'] = employment_status_retired_embeddings[i]
    dataitem['employment_status_student_Vector'] = employment_status_student_embeddings[i]
    dataitem['employment_status_unemployed_Vector'] = employment_status_unemployed_embeddings[i]
    dataitem['education_level_bachelor_Vector'] = education_level_bachelor_embeddings[i]
    dataitem['education_level_high_school_Vector'] = education_level_high_school_embeddings[i]
    dataitem['education_level_master_Vector'] = education_level_master_embeddings[i]
    dataitem['education_level_phd_Vector'] = education_level_phd_embeddings[i]
    dataitem['customer_feedback_Vector'] = customer_feedback_embeddings[i]
    dataitem['customer_service_log_Vector'] = customer_service_log_embeddings[i]
    dataitem['feedback_sentiment_score_Vector'] = feedback_sentiment_score_embeddings[i]
    dataitem['service_log_sentiment_score_Vector'] = service_log_sentiment_score_embeddings[i]
    dataitem['document_text_Vector'] = document_texts_embeddings[i]

# with open('./llminputdatafinal.json', "w+") as f:
   
#     json.dump(data, f)

#indexing process
new_blob_name = 'llminputdatafinal.json'
new_blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=new_blob_name)

# Open the local file and upload its contents
data_string = json.dumps(data)
new_blob_client.upload_blob(data_string, overwrite=True)

print(f"File {new_blob_name} uploaded to Azure Blob Storage in container {CONTAINER_NAME}")

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
index = SearchIndex(name=index_name, fields=fields,
                    vector_search=vector_search)
result = search_client.create_or_update_index(index)
print(f' {result.name} created')


# #getting the mapped and embedded data from the blob
# blob_client = container_client.get_blob_client('llminputdatafinal.json')
# blob_data = blob_client.download_blob()

# json_data = json.loads(blob_data.readall())

# #uploaded the documents to the vector store
# search_client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=AzureKeyCredential(admin_key))
# result = search_client.upload_documents(json_data)
# print(f"Uploaded {len(json_data)} documents") 




# # function to vectorize the prompt
# fields_string = "cust_id_Vector, serious_dlqin2yrs_Vector, revolving_utilization_of_unsecured_lines_Vector, age_Vector, num_time_30_59_days_past_due_not_worse_Vector, debt_ratio_Vector"

# # monthly_income_Vector, num_open_credit_lines_and_loans_Vector, num_times_90_days_late_Vector, num_real_estate_loans_or_lines_Vector, num_time_60_89_days_past_due_not_worse_Vector, num_dependents_Vector, credit_score_Vector, credit_history_length_Vector, payment_history_score_Vector, ltv_Vector, total_assets_Vector, total_liabilities_Vector, employment_status_retired_Vector, employment_status_student_Vector, employment_status_unemployed_Vector, education_level_bachelor_Vector, education_level_high_school_Vector, education_level_master_Vector, education_level_phd_Vector, customer_feedback_Vector, customer_service_log_Vector, feedback_sentiment_score_Vector, service_log_sentiment_score_Vector, document_text_Vector"

# #speech to text part
# import azure.cognitiveservices.speech as speechsdk

# query = ""
# if(True):
#     speech_key = "8b12a9b9ef7a4eefa4a175aab2e3f115"
#     speech_region = "eastus"
#     speech_config = speechsdk.SpeechConfig(subscription="YourSpeechKey", region="YourSpeechRegion")
#     def from_mic():
#         speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    
#         speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

#         st.write("speak into microphone")
#         result = speech_recognizer.recognize_once_async().get()
#         return result.text

#     query = from_mic()


# print(query)


# def get_embedding(query):
#     embedding = client.embeddings.create(input=query, model=azure_openai_em_name).data[0].embedding
#     vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=3, fields=fields_string)
#     return vector_query

# content = get_embedding(query)

# select = [
#     'CustomerID', 
#     'CreditScore',
#     'document_text'
# ]

# results = search_client.search(
#     search_text=None,
#     vector_queries=[content],
#     select = select
   
# )





# context = next(results)




   
# #integrating openAI


# api_base = "https://sdp-openai-resource.openai.azure.com/"
# api_key = "e1c07c8cdee94cc9ada9d5ce56b88cef"
# deployment_name = "gpt-4o"
# api_version = '2024-05-01-preview'


# client = AzureOpenAI(
#     api_key = api_key,
#     api_version = api_version,
#     base_url=f"{api_base}/openai/deployments/{deployment_name}"

# )
# response = client.chat.completions.create(
#     model=deployment_name,
#     messages=[
#         {"role": "system", "content": "You are a helpful and smart banking officer."},
#         {"role": "user", "content": f"This is the search query: {query}, this is the content:{context}  Make a detailed report taking into consideration all the fields and evaluate how creditworthy the customer is. Point out specific details about positives and negatives and how the customer can improve their credit score in order to make their financial journey smooth, tell whether the user is credit worthy or not."}
#     ],
#     max_tokens=4000
# )

# st.write(response.choices[0].message.content)

