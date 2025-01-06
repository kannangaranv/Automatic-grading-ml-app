from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Load the API key and endpoint from the environment variables

API_KEY = os.getenv("API_KEY")
OPENAI_ENDPOINT = os.getenv("ENDPOINT")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")  

# Initialize Azure OpenAI Client
llm = AzureChatOpenAI(
    openai_api_base=OPENAI_ENDPOINT,
    openai_api_version="2023-03-15-preview",
    deployment_name=DEPLOYMENT_NAME,
    openai_api_key=API_KEY,
    openai_api_type="azure"
)
