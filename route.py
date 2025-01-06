import json
from fastapi import APIRouter, HTTPException
from schema import GradingRequest, GradingResponse, ChatBotRequest
from config import llm, logger
from langchain.schema import HumanMessage, AIMessage
from langchain.prompts import PromptTemplate

router = APIRouter()

def get_content_from_response(response: GradingResponse):
    try:
        if response and response.choices and len(response.choices) > 0:
            choice = response.choices[0]
            if choice and choice.message:
                return choice.message.content
        return None
    except Exception as e:
        logger.error("Error extracting content from response: %s", str(e))
        raise HTTPException(status_code=500, detail="Error extracting content from response")

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
    input_variables=[]
)

@router.post("/chatbot")
def chatbot(chatbot_request: ChatBotRequest):
    user_input = chatbot_request.conversation[-1]["content"]
    logger.info("Chatbot request received: %s", user_input)

    try:
        # Generate the prompt
        prompt = english_tutor_prompt.template + f"\nUser: \"{user_input}\""
        messages = [HumanMessage(content=prompt)]
        
        # Call the language model to get the response
        llm_response = llm(messages)
        logger.info("Raw response from LLM: %s", llm_response)

        # Extract content from response
        response_content = llm_response.content if llm_response else "No response content available"

        references = [
            {"title": "English Grammar Guide", "content": "Provides detailed rules and examples on the usage of grammar structures."},
            {"title": "Vocabulary Builder", "content": "A guide to improve vocabulary with examples and synonyms."}
        ]

        return {
            "response": {"role": "assistant", "content": response_content},
            "references": references
        }
    except Exception as e:
        logger.error("Error processing chatbot request: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to process chatbot request")

@router.post("/auto-grade")
def grade_writing_task(request: GradingRequest):
    logger.info("Grading request received: %s", request)

    try:
        task_description = (
            f"The topic is: \"{request.question}\". The user's answer is: \"{request.answers}\". "
            f"Teacher's instructions: \"{request.teachers_instructions}\"."
        )

        user_message_content = (
            f"Please grade the student's answer and provide the result (band score) and feedback in the following JSON format: \n"
            f"{{\n"
            f"  \"result\": [band_score],\n"
            f"  \"feedback\": {{\n"
            f"    \"reason\": [why the user got this band score],\n"
            f"    \"improvement\": [how to improve to the desired band score],\n"
            f"    \"sample_answer\": [an example of a high-quality answer]\n"
            f"  }},\n"
            f"  \"resource_citations\": []\n"
            f"}}\n\n"
            f"Here is the task description:\n{task_description}"
        )

        messages = [
            HumanMessage(content="You are an examiner."),
            HumanMessage(content=user_message_content)
        ]

        response = llm(messages)
        if not isinstance(response, AIMessage):
            logger.error("Unexpected LLM response format")
            raise HTTPException(status_code=500, detail="Unexpected response format")

        parsed_response = json.loads(response.content)
        logger.info("Parsed response: %s", parsed_response)

        band_score = float(parsed_response.get("result", 0))
        feedback = parsed_response.get("feedback", {})
        resource_citations = parsed_response.get("resource_citations", [])

        if not isinstance(feedback, dict):
            logger.error("Invalid feedback format in LLM response")
            raise HTTPException(status_code=500, detail="Invalid feedback format")

        percentage = round((band_score / 9.0) * 100, 2)

        formatted_feedback = {
            "reason": feedback.get("reason", "No reason provided."),
            "improvement": feedback.get("improvement", "No improvement suggestions provided."),
            "sample_answer": feedback.get("sample_answer", "No sample answer provided.")
        }

        return {
            "result": percentage,
            "feedback": formatted_feedback,
            "resource_citations": resource_citations
        }
    except Exception as e:
        logger.error("Error grading writing task: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to grade writing task")
