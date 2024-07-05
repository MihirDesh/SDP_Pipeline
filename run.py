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
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.chat_models import AzureChatOpenAI

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

# Initialize session state
if 'initial_response' not in st.session_state:
    st.session_state.initial_response = ""
if 'conversation' not in st.session_state:
    st.session_state.conversation = None
if 'follow_up_response' not in st.session_state:
    st.session_state.follow_up_response = ""

col1, col2 = st.columns(2)

# ALL THE NECESSARY DATA AND KEYS AND NAMES AND ENDPOINTS
index_name = "customer-index9"
service_endpoint = "https://ai-search-fraud.search.windows.net"
admin_key = "DOnPZ8CHtXlQuFoL5EMBrfTSHFR3BeXcEYty20fjdmAzSeDHIuXZ"
search_client = SearchIndexClient(service_endpoint, AzureKeyCredential(admin_key))
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

# ADA-002 MODEL FOR EMBEDDING
client = AzureOpenAI(
    azure_deployment=azure_openai_model_dep_name_em,
    api_version=azure_openai_version_em,
    azure_endpoint=azure_openai_endpoint,
    api_key=azure_openai_key,
)

search_client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=AzureKeyCredential(admin_key))
fields_string = "cust_id_Vector, serious_dlqin2yrs_Vector, revolving_utilization_of_unsecured_lines_Vector, age_Vector, num_time_30_59_days_past_due_not_worse_Vector, debt_ratio_Vector"

# Initialize Langchain components
if st.session_state.conversation is None:
    memory = ConversationBufferMemory()
    llm = AzureChatOpenAI(
        azure_endpoint="https://sdp-openai-resource.openai.azure.com/",
        api_key="e1c07c8cdee94cc9ada9d5ce56b88cef",
        api_version="2024-05-01-preview",
        deployment_name="gpt-4o",
    )
    st.session_state.conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )

with col1:
    speech_bool = st.button("TALK TO COPILOT")

query = ""

if speech_bool:
    # Your existing speech-to-text code
    speech_key = "8b12a9b9ef7a4eefa4a175aab2e3f115"
    speech_region = "eastus"
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    def from_mic():
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
        st.write("Listening.......")
        result = speech_recognizer.recognize_once_async().get()
        return result.text

    query = from_mic()
else:
    with col2:
        input = st.text_input("Enter your query")
        text_bool = st.button("CHAT WITH COPILOT")

        if text_bool:
            query = input

if query:
    st.write(f"Your query is: {query}")
    def get_embedding(query):
        embedding = client.embeddings.create(input=query, model=azure_openai_em_name).data[0].embedding
        vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=3, fields=fields_string)
        return vector_query

    content = get_embedding(query)

    select = [
        'CustomerID', 
        'CreditScore',
        'document_text'
    ]

    results = search_client.search(
        search_text=None,
        vector_queries=[content],
        select=select
    )

    context = next(results)

    with st.spinner("ANALYSING THE DATA AND GENERATING REPORT"):
        # Use your existing OpenAI client for the initial response
        api_base = "https://sdp-openai-resource.openai.azure.com/"
        api_key = "e1c07c8cdee94cc9ada9d5ce56b88cef"
        deployment_name = "gpt-4o"
        api_version = '2024-05-01-preview'

        openai_client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            base_url=f"{api_base}/openai/deployments/{deployment_name}"
        )   

        response = openai_client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful and smart banking officer."},
                {"role": "user", "content": f"This is the search query: {query}, this is the content:{context}  Make a detailed report taking into consideration all the fields and evaluate how creditworthy the customer is. Point out specific details about positives and negatives and how the customer can improve their credit score in order to make their financial journey smooth, tell whether the user is credit worthy or not."}
            ],
            max_tokens=4000
        )

        st.session_state.initial_response = response.choices[0].message.content
        st.write(st.session_state.initial_response)

        # Add the initial interaction to Langchain memory
        st.session_state.conversation.predict(input=f"User: {query}\nAI: {st.session_state.initial_response}")

# Display the initial response if it exists
if st.session_state.initial_response:
    st.write("Initial Report:")
    st.write(st.session_state.initial_response)

# Option for follow-up questions using Langchain
st.write("You can ask follow-up questions about the report:")
follow_up = st.text_input("Follow-up question:", key="follow_up")
if st.button("Ask Follow-up"):
    follow_up_response = st.session_state.conversation.predict(input=follow_up)
    st.session_state.follow_up_response = follow_up_response
    st.experimental_rerun()

# Display the follow-up response if it exists
if st.session_state.follow_up_response:
    st.write("Follow-up Response:")
    st.write(st.session_state.follow_up_response)