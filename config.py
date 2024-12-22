from langchain.chat_models import AzureChatOpenAI

API_KEY = "0735062a40e64a93bdde408e4ac83e74"
OPENAI_ENDPOINT = "https://enfluent-eastus2.openai.azure.com/openai/deployments/enfluent-gpt-4o/chat/completions?api-version=2023-03-15-preview"

# Initialize Azure OpenAI Client
llm = AzureChatOpenAI(
    openai_api_base=OPENAI_ENDPOINT,
    openai_api_version="2023-03-15-preview",
    deployment_name="enfluent-gpt-4o",
    openai_api_key=API_KEY,
    openai_api_type="azure"
)
