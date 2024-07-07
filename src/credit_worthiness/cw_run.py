import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
import streamlit as st
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from helpers.llm_helpers.gpt4o import gpt4o
from helpers.llm_helpers.gpt4oinit import createlangchainllm
from helpers.vector_helpers.getembedding import get_embedding
from helpers.input_helpers.speech import from_mic

load_dotenv()

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

# ALL THE NECESSARY DATA AND KEYS AND NAMES AND ENDPOINTS......

#Azure blob storage keys and endpoints:

blob_service_client = BlobServiceClient(account_url=f'https://{os.getenv("AZURE_STORAGE_ACCOUNT_NAME")}.blob.core.windows.net', credential=os.getenv("AZURE_STORAGE_ACCOUNT_KEY"))
container_client = blob_service_client.get_container_client(container=os.getenv("CONTAINER_NAME"))
blob_list = container_client.list_blobs()

#AZURE AI SEARCH KEYS AND ENDPOINT
index_name = os.getenv("index_name")

search_client = SearchIndexClient(os.getenv("service_endpoint"), AzureKeyCredential(os.getenv("admin_key")))



# ADA-002 MODEL FOR EMBEDDING
client = AzureOpenAI(
    azure_deployment=os.getenv("azure_openai_model_dep_name_em"),
    api_version=os.getenv("azure_openai_version_em"),
    azure_endpoint=os.getenv("ADA_ENDPOINT"),
    api_key=os.getenv("azure_openai_key"),
)



#MAIN CODE
search_client = SearchClient(endpoint=os.getenv("service_endpoint"), index_name=index_name, credential=AzureKeyCredential(os.getenv("admin_key")))
fields_string = "cust_id_Vector, serious_dlqin2yrs_Vector, revolving_utilization_of_unsecured_lines_Vector, age_Vector, num_time_30_59_days_past_due_not_worse_Vector, debt_ratio_Vector"

# Initialize Langchain components
if st.session_state.conversation is None:
    memory = ConversationBufferMemory()
    llm = createlangchainllm()
    st.session_state.conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )

with col1:
    speech_bool = st.button("TALK TO COPILOT")

query = ""

if speech_bool:
    

    query = from_mic()
else:
    with col2:
        input = st.text_input("Enter your query")
        text_bool = st.button("CHAT WITH COPILOT")

        if text_bool:
            query = input

if query:
    st.write(f"Your query is: {query}")
   
    content = get_embedding(query,fields_string,client)

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
       
      
        prompt = f"This is the search query: {query}, this is the content:{str(context)}  Make a detailed report taking into consideration all the fields and evaluate how creditworthy the customer is. Point out specific details about positives and negatives and how the customer can improve their credit score in order to make their financial journey smooth, tell whether the user is credit worthy or not."
        
        response = gpt4o(prompt,4000,"banking client")

        st.session_state.initial_response = response
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