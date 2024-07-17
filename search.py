# Queries the database with the user's question and returns the 4 most similar opportunities

from dotenv import load_dotenv
import openai
import psycopg2
from sentence_transformers import SentenceTransformer
import sys
from sentence_transformers import CrossEncoder
import json


import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
if __name__ == "__main__":
    query = sys.argv[1]
    my_input = query

load_dotenv()

def findSimilarVectors(user_tuple):
    """
    This function performs a similarity search on the database and returns the page content of the 4 opportunities that are most similar to the user's ideal RFP

    Args:
        user_tuple (tuple): A tuple containing the vectorized version of the fake RFP that was created and the user's query (vectorized fake rfp, query)

    Returns:
        str: A string containing the original question that was asked by the user followed by the page content of the 4 most similar opportunities
    """
    # Generic connection to PostgreSQL
    connection = psycopg2.connect(
        host="localhost",
        port="5432",
        database="totem",
        user="postgres"
    )

    # Create a cursor
    cursor = connection.cursor()

    # Perform cosine similarity search
    # Returns the page contents of the 4 most similar opportunities
    insert_query = """
    SELECT page_contents, (embeddings <=> (%s::vector)) AS cosine_distance
    FROM totemembeddings
    ORDER BY cosine_distance
    LIMIT 4;
    """

    cursor.execute(insert_query, (user_tuple[0],))

    # Fetch and process the results
    results = cursor.fetchall()
    output = ""
    i = 0
    choices = ["one", "another", "yet another", "another"]
    for row in results:
        page_contents, similarity_score = row
        intro = ("Here are the details of " + choices[i] + " relevant opportunity with a similarity score of " + str(similarity_score) + ":\n")
        output += intro 
        output += (str(page_contents) + "\n")
        # print("Page Contents: ", page_contents)
        # print("Similarity Score: ", similarity_score)
        i += 1

    # Close cursor and connection
    cursor.close()
    connection.close()

    return user_tuple[1] + output


def ranker(vector):
    """
    This function performs a similarity search on the embeddings in the database and returns the 25 most similar opportunities
    
    Args:
        user_tuple (tuple): A tuple containing the vectorized version of the fake RFP that was created and the user's query. (vectorized fake rfp, query)
        
    Returns:
        list: A list of the 25 most similar opportunities
    """
    # Generic connection to PostgreSQL
    connection = psycopg2.connect(
        host="localhost",
        port="5432",
        database="totem",
        user="postgres"
    )

    # Create a cursor
    cursor = connection.cursor()

    # Perform cosine similarity search
    # Returns the page contents of the 25 most similar opportunities
    insert_query = """
    SELECT page_contents, (embeddings <=> (%s::vector)) AS cosine_distance
    FROM totemembeddings
    ORDER BY cosine_distance
    LIMIT 25;
    """

    cursor.execute(insert_query, (vector,))

    # Fetch and process the results
    results = cursor.fetchall()

    # Close cursor and connection
    cursor.close()
    connection.close()
    return results


def reranker(query, relevant_opportunities):
    """
    This function re-ranks the opportunities based on the user's query

    Args:
        query (str): The user's query
        opportunities (list): A list of the 25 most similar opportunities

    Returns:
        list: A list of the 4 most similar opportunities re-ranked based on the user's query
    """
    ce = CrossEncoder('BAAI/bge-reranker-large')

    # Create pairs of the user's query and the page content of the opportunities
    pairs = [(query, opp[0]) for opp in relevant_opportunities]

    scores = ce.predict(pairs)

    print(scores)

    # Pair up the scores and opportunities for sorting
    scored_opportunities = list(zip(scores, relevant_opportunities))

    # Sort by score in descending order
    scored_opportunities.sort(key=lambda x: x[0])

    # Get the top 4 opportunities
    top_opportunities = [opp for score, opp in scored_opportunities[:4]]

    output = ""
    i = 0
    choices = ["one", "another", "yet another", "another"]
    for opp in top_opportunities:
        page_contents = opp[0]
        intro = ("Here are the details of " + choices[i] + " relevant opportunity:\n")
        output += intro 
        output += (str(page_contents) + "\n")
        i += 1

    return query + output


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
    This function uses GPT-3.5-turbo to respond to a prompt

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
                    "opportunity1": {
                        "type": "object",
                        "description": "A dictionary containing the details of the first opportunity.",
                        "properties": {
                            "OpportunityTitle": {"type": "string"},
                            "OpportunityID": {"type": "integer"},
                            "OpportunityNumber": {"type": "string"},
                            "CFDANumber": {"type": "string"},
                            "Description": {"type": "string"},
                        },
                        "required": ["OpportunityTitle", "OpportunityID", "OpportunityNumber", "CFDANumber", "Description"]
                    },
                    "opportunity2": {
                        "type": "object",
                        "description": "A dictionary containing the details of the second opportunity.",
                        "properties": {
                            "OpportunityTitle": {"type": "string"},
                            "OpportunityID": {"type": "integer"},
                            "OpportunityNumber": {"type": "string"},
                            "CFDANumber": {"type": "string"},
                            "Description": {"type": "string"},
                        },
                        "required": ["OpportunityTitle", "OpportunityID", "OpportunityNumber", "CFDANumber", "Description"]
                    },
                    "opportunity3": {
                        "type": "object",
                        "description": "A dictionary containing the details of the third opportunity.",
                        "properties": {
                            "OpportunityTitle": {"type": "string"},
                            "OpportunityID": {"type": "integer"},
                            "OpportunityNumber": {"type": "string"},
                            "CFDANumber": {"type": "string"},
                            "Description": {"type": "string"},
                        },
                        "required": ["OpportunityTitle", "OpportunityID", "OpportunityNumber", "CFDANumber", "Description"]
                    },
                    "opportunity4": {
                        "type": "object",
                        "description": "A dictionary containing the details of the fourth opportunity.",
                        "properties": {
                            "OpportunityTitle": {"type": "string"},
                            "OpportunityID": {"type": "integer"},
                            "OpportunityNumber": {"type": "string"},
                            "CFDANumber": {"type": "string"},
                            "Description": {"type": "string"},
                        },
                        "required": ["OpportunityTitle", "OpportunityID", "OpportunityNumber", "CFDANumber", "Description"]
                    },
                },
                "required": [],
            },
        }
        }, {
            "type": "function",
            "function": {
                "name": "ideal_rfp_formatter",
                "description": "Use this output format if the user wants to see the ideal RFP for the user's query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "OpportunityTitle": {
                            "type": "string",
                            "description": "The title of the opportunity",
                        },
                        "OpportunityCategory": {
                            "type": "string",
                            "description": "The category of the opportunity",
                        },
                        "FundingInstrumentType": {
                            "type": "string",
                            "description": "The funding instrument type of the opportunity",
                        },
                        "CategoryOfFundingActivity": {
                            "type": "string",
                            "description": "The category of funding activity of the opportunity",
                        },
                        "EligibleApplicants": {
                            "type": "string",
                            "description": "The eligible applicants for the opportunity",
                        },
                        "AdditionalInformationOnEligibility": {
                            "type": "string",
                            "description": "Additional information on the eligibility of the opportunity",
                        },
                        "AgencyName": {
                            "type": "string",
                            "description": "The name of the agency of the opportunity",
                        },
                        "Description": {
                            "type": "string",
                            "description": "The description of the opportunity",
                        }
                    },
                    "required": ["OpportunityTitle", "OpportunityCategory", "FundingInstrumentType", "CategoryOfFundingActivity", "EligibleApplicants", "AdditionalInformationOnEligibility", "AgencyName", "Description"],
                    }
                },
        }
    ]

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # Choose the GPT model,
        messages=messages,
        tool_choice=({"type": "function", "function": {"name": function}}) if function != "auto" else function, 
        tools=tools,
        temperature=0.0
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
                opportunity1=function_args.get("opportunity1"),
                opportunity2=function_args.get("opportunity2"),
                opportunity3=function_args.get("opportunity3"),
                opportunity4=function_args.get("opportunity4"),
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


def opportunity_output_formatter(opportunity1=None, opportunity2=None, opportunity3=None, opportunity4=None):
    """
    This function reformats the output of the LLM model

    Args:
        opportunity1 (dictionary): A list containing the details of the first opportunity in the format: {Opportunity Title : OpportuintyTitle, Opportunity ID : OpportunityID, Opportunity Number : OpportunityNumber, CFDA Number : CFDANumber, Description : Description}
        opportunity2 (dictionary): A list containing the details of the second opportunity in the format: {Opportunity Title : OpportuintyTitle, Opportunity ID : OpportunityID, Opportunity Number : OpportunityNumber, CFDA Number : CFDANumber, Description : Description}
        opportunity3 (dictionary): A list containing the details of the third opportunity in the format: {Opportunity Title : OpportuintyTitle, Opportunity ID : OpportunityID, Opportunity Number : OpportunityNumber, CFDA Number : CFDANumber, Description : Description}
        opportunity4 (dictionary): A list containing the details of the fourth opportunity in the format: {Opportunity Title : OpportuintyTitle, Opportunity ID : OpportunityID, Opportunity Number : OpportunityNumber, CFDA Number : CFDANumber, Description : Description}

    Returns:
        str: A string containing the reformatted output
    """

    output = ""
    if opportunity1:
        output += "-<1>-\n"
        output += f"Opportunity Title: {opportunity1['OpportunityTitle']}\n"
        output += f"Opportunity ID: {opportunity1['OpportunityID']}\n"
        output += f"Opportunity Number: {opportunity1['OpportunityNumber']}\n"
        output += f"CFDA Number: {opportunity1['CFDANumber']}\n"
        output += f"Description: {opportunity1['Description']}\n"
    else:
        return "I'm sorry, I couldn't find any relevant opportunities for you. Please try again with a different query."
    if opportunity2:
        output += "\n-<2>-:\n"
        output += f"Opportunity Title: {opportunity2['OpportunityTitle']}\n"
        output += f"Opportunity ID: {opportunity2['OpportunityID']}\n"
        output += f"Opportunity Number: {opportunity2['OpportunityNumber']}\n"
        output += f"CFDA Number: {opportunity2['CFDANumber']}\n"
        output += f"Description: {opportunity2['Description']}\n"
    else:
        return output
    if opportunity3:
        output += "\n-<3>-:\n"
        output += f"Opportunity Title: {opportunity3['OpportunityTitle']}\n"
        output += f"Opportunity ID: {opportunity3['OpportunityID']}\n"
        output += f"Opportunity Number: {opportunity3['OpportunityNumber']}\n"
        output += f"CFDA Number: {opportunity3['CFDANumber']}\n"
        output += f"Description: {opportunity3['Description']}\n"
    else:
        return output
    if opportunity4:
        output += "\n-<4>-:\n"
        output += f"Opportunity Title: {opportunity4['OpportunityTitle']}\n"
        output += f"Opportunity ID: {opportunity4['OpportunityID']}\n"
        output += f"Opportunity Number: {opportunity4['OpportunityNumber']}\n"
        output += f"CFDA Number: {opportunity4['CFDANumber']}\n"
        output += f"Description: {opportunity4['Description']}\n"
    return output



# First, we need to create a fake RFP that would be perfect for the user's question so that the similarity search can be performed
ideal_opportunity = chatWithLLM("I want you to create one fake RFP that would be ideal for someone who has this question:" + my_input + ". Make sure to include the corresponding fake OpportunityTitle, OpportunityCategory, FundingInstrumentType, CategoryOfFundingActivity, EligibleApplicants, AdditionalInformationOnEligibility, AgencyName, and Description.", "ideal_rfp_formatter")

# Next, we need to vectorize the fake RFP so that it can be compared to the other opportunities in the database
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
vectorized_ideal_opportunity = model.encode(ideal_opportunity)

fully_formatted_ideal_opportunty = [embedding.tolist() for embedding in vectorized_ideal_opportunity]

# Now, we can perform the similarity search, turning the output into a prompt and then passing this into the LLM model
print("\n\nResults: ")
llmInput = promptMaker(reranker(my_input, ranker(fully_formatted_ideal_opportunty)))
# print("llmInput:", llmInput)
llmResponse = chatWithLLM(llmInput, "opportunity_output_formatter")

print(llmResponse)
my_input = "quit"
