#ALL THE REQUIRED IMPORTS
from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
import azure.cognitiveservices.speech as speechsdk
import streamlit as st
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
import streamlit as st

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
st.set_page_config(layout="wide")
st.header("CREDISHIELD: THE CREDIT WORTHINESS COPILOT")

col1, col2 = st.columns(2)



#ALL THE NECESSARY DATA AND KEYS AND NAMES AND ENDPOINTS

index_name = "customer-index9"
service_endpoint = "https://ai-search-fraud.search.windows.net"
admin_key = "DOnPZ8CHtXlQuFoL5EMBrfTSHFR3BeXcEYty20fjdmAzSeDHIuXZ"
search_client = SearchIndexClient(service_endpoint,AzureKeyCredential(admin_key))
AZURE_STORAGE_ACCOUNT_NAME = 'frauddetect1578932446'
AZURE_STORAGE_ACCOUNT_KEY = 'bJEfK0Kj1EaYaKji0jDV7AvgPBUgfPuCwIWtM0R5uuRBQUb07PSyp7PV8mMCwBSOtIVS2+93lq68+AStTZx7zA=='
CONTAINER_NAME = 'unstructureddata'
blob_service_client = BlobServiceClient(account_url=f'https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net', credential=AZURE_STORAGE_ACCOUNT_KEY)
container_client = blob_service_client.get_container_client(container=CONTAINER_NAME)
blob_list = container_client.list_blobs()
azure_openai_endpoint = "https://SDP-OpenAI-Resource.openai.azure.com/openai/deployments/text-embedding-ada-002-2/embeddings?api-version=2023-05-15"
azure_openai_key = "e1c07c8cdee94cc9ada9d5ce56b88cef"
azure_openai_em_name = "text-embedding-ada-002" 
azure_openai_version_em = "2023-05-15"
azure_openai_model_dep_name_em = "text-embedding-ada-002-2"




#ADA-002 MODEL FOR EMBEDDING
client = AzureOpenAI(
    azure_deployment=azure_openai_model_dep_name_em,
    api_version=azure_openai_version_em,
    azure_endpoint=azure_openai_endpoint,
    api_key=azure_openai_key,
   
)


#

search_client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=AzureKeyCredential(admin_key))
fields_string = "cust_id_Vector, serious_dlqin2yrs_Vector, revolving_utilization_of_unsecured_lines_Vector, age_Vector, num_time_30_59_days_past_due_not_worse_Vector, debt_ratio_Vector"
# monthly_income_Vector, num_open_credit_lines_and_loans_Vector, num_times_90_days_late_Vector, num_real_estate_loans_or_lines_Vector, num_time_60_89_days_past_due_not_worse_Vector, num_dependents_Vector, credit_score_Vector, credit_history_length_Vector, payment_history_score_Vector, ltv_Vector, total_assets_Vector, total_liabilities_Vector, employment_status_retired_Vector, employment_status_student_Vector, employment_status_unemployed_Vector, education_level_bachelor_Vector, education_level_high_school_Vector, education_level_master_Vector, education_level_phd_Vector, customer_feedback_Vector, customer_service_log_Vector, feedback_sentiment_score_Vector, service_log_sentiment_score_Vector, document_text_Vector"


with col1:

    speech_bool = st.button("TALK TO COPILOT")
with col2:

    text_bool = st.button("CHAT WITH COPILOT")
    
     


#SPEECH TO TEXT -  GETTING THE QUERY FOR RAG AFTER THE USER SPEAKS INTO IT
import azure.cognitiveservices.speech as speechsdk

query = ""

# if(text_bool):
#    #logic for the text input
    


if(speech_bool):
    
    speech_key = "8b12a9b9ef7a4eefa4a175aab2e3f115"
    speech_region = "eastus"
    speech_config = speechsdk.SpeechConfig(subscription="YourSpeechKey", region="YourSpeechRegion")
    def from_mic():
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

        st.write("Listening.......")
        result = speech_recognizer.recognize_once_async().get()
        return result.text

    query = from_mic()


   



# CREATES EMBEDDING FOR THAT QUERY FROM ADA-002
if(query):
    st.write(f"Your query is: {query}")
    def get_embedding(query):
        embedding = client.embeddings.create(input=query, model=azure_openai_em_name).data[0].embedding
        vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=3, fields=fields_string)
        return vector_query

    content = get_embedding(query)


    #VECTOR SEARCH

    select = [
        'CustomerID', 
        'CreditScore',
        'document_text'
    ]

    results = search_client.search(
        search_text=None,
        vector_queries=[content],
        select = select
   
    )





    context = next(results)




   
    #OPENAI REPORT GENERATION


    api_base = "https://sdp-openai-resource.openai.azure.com/"
    api_key = "e1c07c8cdee94cc9ada9d5ce56b88cef"
    deployment_name = "gpt-4o"
    api_version = '2024-05-01-preview'


    client = AzureOpenAI(
        api_key = api_key,
        api_version = api_version,
        base_url=f"{api_base}/openai/deployments/{deployment_name}"

    )   
    with st.spinner("ANALYSING THE DATA AND GENERATING REPORT"):
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful and smart banking officer."},
                {"role": "user", "content": f"This is the search query: {query}, this is the content:{context}  Make a detailed report taking into consideration all the fields and evaluate how creditworthy the customer is. Point out specific details about positives and negatives and how the customer can improve their credit score in order to make their financial journey smooth, tell whether the user is credit worthy or not."}
            ],
            max_tokens=4000
        )

        st.write(response.choices[0].message.content)


