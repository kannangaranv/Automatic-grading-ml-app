import json
from fastapi import APIRouter, HTTPException
from schema import GradingRequest, GradingResponse, ChatBotRequest
from config import llm
from langchain.schema import HumanMessage, AIMessage
from langchain.prompts import PromptTemplate

router = APIRouter()

def get_content_from_response(response: GradingResponse):
    if response and response.choices and len(response.choices) > 0:
        choice = response.choices[0]
        if choice and choice.message:
            return choice.message.content
    return None

english_tutor_prompt = PromptTemplate(
    template="""
    You are an English Language Tutor, a helpful and friendly chatbot dedicated to helping users improve their English skills. Your goal is to:
    
    1. Provide clear, concise explanations of grammar, vocabulary, or pronunciation when asked.
    2. Correct any grammatical, spelling, or phrasing mistakes in the user's sentences, explaining why the correction was made.
    3. Suggest better ways to phrase sentences for improved clarity or fluency.
    4. Answer language-related questions with simple and easy-to-understand examples.
    5. Offer encouragement and constructive feedback to help users build confidence in using English.
    6. Keep the tone friendly, approachable, and supportive.
    
    Guidelines for your responses:
    - If the user asks for help with a specific sentence or phrase, correct and explain it step-by-step.
    - If the user makes a general request to practice English, engage them with questions or exercises that match their proficiency level.
    - If the user requests vocabulary help, provide definitions, usage examples, and synonyms.
    - Always adapt your responses to the user's proficiency level, avoiding overly complex explanations unless explicitly requested.
    
    Example:
    User: "How do I use the word 'elaborate' in a sentence?"
    You: "The word 'elaborate' means to explain something in detail. For example: 'Can you elaborate on your plan for the project?' Here, it means to provide more details about the plan."
    
    Now, start by analyzing the user's input, understanding their request, and providing an appropriate response to help them improve their English.
    """,
    input_variables=[]  # If dynamic variables are needed, you can specify them here
)

@router.post("/chatbot")
def chatbot(chatbot_request: ChatBotRequest):
    user_input = chatbot_request.conversation[-1]["content"]
    print("Request received: ", user_input)

    # Generate the prompt
    prompt = english_tutor_prompt.template + f"\nUser: \"{user_input}\""
    messages = [HumanMessage(content=prompt)]
    
    # Call the language model to get the response
    llm_response = llm(messages)
    print("Raw Response: ", llm_response)

    # Construct the response in the required format
    response_content = llm_response.content  # Assuming the LLM returns content directly
    
    # Example references (you can replace this with dynamically generated references if available)
    references = [
        {
            "title": "English Grammar Guide",
            "content": "Provides detailed rules and examples on the usage of grammar structures."
        },
        {
            "title": "Vocabulary Builder",
            "content": "A guide to improve vocabulary with examples and synonyms."
        }
    ]

    return {
        "response": {
            "role": "assistant",
            "content": response_content
        },
        "references": references  # Replace with dynamically generated references if needed
    }


    
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