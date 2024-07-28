from fastapi import FastAPI, Request, Form
# from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from models import Opportunity
import openai
import os
import json
from sentence_transformers import CrossEncoder
from fastapi.responses import HTMLResponse
from ranker import ranker





app = FastAPI()


# Load environment variables
load_dotenv()

# # Mount static directory (if needed)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Load templates directory (if needed)
templates = Jinja2Templates(directory="templates")

# Initialize models and connections
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
openai.api_key = os.getenv("OPENAI_API_KEY")


def promptMaker(input):
    """
    This function creates a prompt for the LLM model to respond to

    Args:
        input (str): The user's question followed by the info about the 4 most re;evant opportunities

    Returns:
        str: A string containing the prompt that the LLM model will respond to
    """

    prompt = (
        "You are a world-class advisor to nonprofits seeking the best grants for their organization. "
        "You will receive the user's query and relevant context. Use this context to answer the query. "
        "If none of the opportunities are suitable, inform the user.\n\n"
        "User's query and context:\n"
        f"{input}"
    )

    return prompt


def chatWithLLM(my_prompt, function="auto"):
    """
    This function uses gpt-4o to respond to a prompt

    Args:
        my_prompt (str): The prompt that the LLM model will respond to
        function (str): The function that the LLM model will use to format the output
    
    Returns:
        str: The response from the LLM model
    """
    messages = [{"role": "user", "content": my_prompt}]

    tools = [
    {
        "type": "function",
        "function": {
            "name": "opportunity_output_formatter",
            "description": "Use this format if the user wants to see the details of the top four real opportunities that are relevant to their question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "opportunities": {
                        "type": "array",
                        "maxItems": 4,
                        "items": {
                            "type": "object",
                            "properties": {
                                "OpportunityTitle": {"type": "string"},
                                "OpportunityID": {"type": "integer"},
                                "OpportunityNumber": {"type": "string"},
                                "CFDANumber": {"type": "string"},
                                "Description": {"type": "string", "description": "The description of the opportunity. This is normally several sentences long and it ends with '|'."},
                                "Grants.gov URL": {"type": "string", "description": "URL in the format: https://www.grants.gov/search-results-detail/{OpportunityID}"},
                                "AdditionalInformationURL": {"type": "string", "description": "URL found in the opportunity database or 'Not Found'."}
                            },
                            "required": ["OpportunityTitle", "OpportunityID", "OpportunityNumber", "CFDANumber", "Description", "Grants.gov URL", "AdditionalInformationURL"]
                        }
                    }
                },
                "required": ["opportunities"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ideal_rfp_formatter",
            "description": "Use this output format if the user wants to see the ideal RFP for the user's query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "OpportunityTitle": {
                        "type": "string",
                        "description": "The title of the opportunity"
                    },
                    "OpportunityCategory": {
                        "type": "string",
                        "description": "The category of the opportunity"
                    },
                    "FundingInstrumentType": {
                        "type": "string",
                        "description": "The funding instrument type of the opportunity"
                    },
                    "CategoryOfFundingActivity": {
                        "type": "string",
                        "description": "The category of funding activity of the opportunity"
                    },
                    "EligibleApplicants": {
                        "type": "string",
                        "description": "The eligible applicants for the opportunity"
                    },
                    "AdditionalInformationOnEligibility": {
                        "type": "string",
                        "description": "Additional information on the eligibility of the opportunity"
                    },
                    "AgencyName": {
                        "type": "string",
                        "description": "The name of the agency of the opportunity"
                    },
                    "Description": {
                        "type": "string",
                        "description": "The description of the opportunity"
                    }
                },
                "required": ["OpportunityTitle", "OpportunityCategory", "FundingInstrumentType", "CategoryOfFundingActivity", "EligibleApplicants", "AdditionalInformationOnEligibility", "AgencyName", "Description"]
            }
        }
    }
]


    response = openai.chat.completions.create(
        model="gpt-4o",  # Choose the GPT model,
        messages=messages,
        tool_choice=({"type": "function", "function": {"name": function}}) if function != "auto" else function, 
        tools=tools,
        temperature=0.0,
    )

    output_message = response.choices[0].message
    tool_calls = output_message.tool_calls
    function_response = output_message.content
    if tool_calls:
        available_functions = {
            "ideal_rfp_formatter": ideal_rfp_formatter,
            "opportunity_output_formatter": opportunity_output_formatter 
        }
        if tool_calls[0].function.name == "ideal_rfp_formatter":
            function_name = tool_calls[0].function.name
            function_to_call = available_functions.get(function_name)
            function_args = json.loads(tool_calls[0].function.arguments)
            function_response = function_to_call(
                OpportunityTitle=function_args.get("OpportunityTitle"),
                OpportunityCategory=function_args.get("OpportunityCategory"),
                FundingInstrumentType=function_args.get("FundingInstrumentType"),
                CategoryOfFundingActivity=function_args.get("CategoryOfFundingActivity"),
                EligibleApplicants=function_args.get("EligibleApplicants"),
                AdditionalInformationOnEligibility=function_args.get("AdditionalInformationOnEligibility"),
                AgencyName=function_args.get("AgencyName"),
                Description=function_args.get("Description"),
            )
        if tool_calls[0].function.name == "opportunity_output_formatter":
            function_name = tool_calls[0].function.name
            function_to_call = available_functions.get(function_name)
            function_args = json.loads(tool_calls[0].function.arguments)
            function_response = function_to_call(
                opportunities=function_args.get("opportunities")
            )
    return function_response


def ideal_rfp_formatter(OpportunityTitle, OpportunityCategory, FundingInstrumentType, CategoryOfFundingActivity, EligibleApplicants, AdditionalInformationOnEligibility, AgencyName, Description):
    """
    This function formats the ideal RFP for the user

    Args:
        OpportunityTitle (str): The title of the opportunity
        OpportunityCategory (str): The category of the opportunity
        FundingInstrumentType (str): The funding instrument type of the opportunity
        CategoryOfFundingActivity (str): The category of funding activity of the opportunity
        EligibleApplicants (str): The eligible applicants for the opportunity
        AdditionalInformationOnEligibility (str): Additional information on the eligibility of the opportunity
        AgencyName (str): The name of the agency of the opportunity
        Description (str): The description of the opportunity

    Returns:
        str: A string containing the formatted ideal RFP
    """
    return f"The OpportunityTitle is {OpportunityTitle}. The OpportunityCategory is {OpportunityCategory}. The FundingInstrumentType is {FundingInstrumentType}. The CategoryOfFundingActivity is {CategoryOfFundingActivity}. The EligibleApplicants is {EligibleApplicants}. The AdditionalInformationOnEligibility is {AdditionalInformationOnEligibility}. The AgencyName is {AgencyName}. The Description is {Description}."


def opportunity_output_formatter(opportunities):
    """
    This function reformats the output of the LLM model

    Args:
        opportunities (list): A list of dictionaries, each containing the details of an opportunity.
                             Each dictionary should have keys: 'OpportunityTitle', 'OpportunityID',
                             'OpportunityNumber', 'CFDANumber', 'Description', 'Grants.gov URL', 'AdditionalInformationURL'.

    Returns:
        str: A string containing the reformatted output
    """

    if not opportunities:
        return "I'm sorry, I couldn't find any relevant opportunities for you. Please try again with a different query."

    output = ""
    for idx, opportunity in enumerate(opportunities, start=1):
        output += f"\n-<{idx}>-\n"
        output += f"Opportunity Title: {opportunity['OpportunityTitle']}\n"
        output += f"Opportunity ID: {opportunity['OpportunityID']}\n"
        output += f"Opportunity Number: {opportunity['OpportunityNumber']}\n"
        output += f"CFDA Number: {opportunity['CFDANumber']}\n"
        output += f"Description: {opportunity['Description']}\n"
        output += f"Grants.gov Results Detail: {opportunity['Grants.gov URL']}\n"
        output += f"Additional Info: {opportunity['AdditionalInformationURL']}\n"

    return output




@app.get("/", response_class=HTMLResponse)
@app.post("/", response_class=HTMLResponse)
async def home(request: Request, query: str = Form(None)):
    response = None


    if query:
        ideal_opportunity = chatWithLLM(f"I want you to create one fake RFP that would be ideal for someone who has this question: {query}. Make sure to include the corresponding fake OpportunityTitle, OpportunityCategory, FundingInstrumentType, CategoryOfFundingActivity, EligibleApplicants, AdditionalInformationOnEligibility, AgencyName, and Description.", "ideal_rfp_formatter")

        vectorized_ideal_opportunity = model.encode(ideal_opportunity, normalize_embeddings=False)
        fully_formatted_ideal_opportunity = [embedding.tolist() for embedding in vectorized_ideal_opportunity]

        

        llm_input = promptMaker(ranker(query, fully_formatted_ideal_opportunity))

        print(llm_input)

        response = chatWithLLM(llm_input, "opportunity_output_formatter")


    return templates.TemplateResponse("local_home.html", {"request": request, "query": query, "response": response})


