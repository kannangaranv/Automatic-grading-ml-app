import json
from fastapi import APIRouter, HTTPException
from schema import GradingRequest, GradingResponse
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage, AIMessage

router = APIRouter()

# Configuration
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

def get_content_from_response(response: GradingResponse):
    if response and response.choices and len(response.choices) > 0:
        choice = response.choices[0]
        if choice and choice.message:
            return choice.message.content
    return None



@router.post("/auto-grade")
def grade_writing_task(request: GradingRequest):
    print("Request received: ", request)

    task_description = (
        f"The topic is: \"{request.question}\". The user's answer is: \"{request.answers}\". "
        f"Teacher's instructions: \"{request.teachers_instructions}\"."
    )

    user_message_content = (
        f"Please grade the student's answer and provide the result (score) and feedback in the following JSON format: \n"
        f"{{ \"result\": [score], \"feedback\": {{\"message\": [feedback]}}, \"resource_citations\": [] }}\n\n"
        f"Here is the task description:\n{task_description}"
    )

    messages = [
        HumanMessage(content="You are an examiner."),
        HumanMessage(content=user_message_content)
    ]

    try:
        response = llm(messages)
        if isinstance(response, AIMessage):
            parsed_response = json.loads(response.content)
            print("Parsed response: ", parsed_response)

            # Ensure types match Java expectations
            result = float(parsed_response.get("result", 0))
            feedback = parsed_response.get("feedback", "No feedback provided")
            resource_citations = parsed_response.get("resource_citations", [])

            return {
                "result": result,
                "feedback": feedback,
                "resource_citations": resource_citations
            }
        else:
            raise HTTPException(status_code=500, detail="Unexpected response format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))