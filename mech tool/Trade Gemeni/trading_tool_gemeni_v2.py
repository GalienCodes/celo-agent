import json
from collections import defaultdict
from concurrent.futures import Future, ThreadPoolExecutor
from heapq import nlargest
from itertools import islice
from string import punctuation
from typing import Any, Dict, Generator, List, Optional, Tuple, Callable

import google.generativeai as genai


# Set up the model with desired configuration
generation_config = {
    "temperature": 0.8,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

#TOOL_TO_ENGINE = {tool: "gemini-1.0-pro" for tool in ALLOWED_TOOLS}

TRADE_PROMPT = """
You are a trading AI inside a multi-agent system that takes in a prompt of a user requesting trading advice for two tokens.
You are provided with an input under the label "USER_PROMPT". You must follow the instructions
under the label "INSTRUCTIONS". You must provide your response in the format specified under "OUTPUT_FORMAT".

INSTRUCTIONS
*You are a trading AI inside a multi-agent system that takes in a prompt of a user requesting trading advice for two tokens.
*You are provided with an input under the label "USER_PROMPT". 
*You must follow the instructionsunder the label "INSTRUCTIONS". 
*You must provide your response in the format specified under "OUTPUT_FORMAT".INSTRUCTIONS
* Read the input under the label "USER_PROMPT" delimited by three backticks.
* The "USER_PROMPT" specifies two tokens for trading advice.
* Provide the latest market data for the two tokens such as current prices, trading volume, and 5 year historial trends.
* You must provide your response in the format specified under "OUTPUT_FORMAT".* Do not include any other contents in your response.

USER_PROMPT:
```
{user_prompt}
```
OUTPUT_FORMAT
* Your output response must be only a single JSON object to be parsed by Python's "json.loads()". 
* The JSON must contain three fields: "Price", "volume", and "historical trends".


"""

model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)



def trading_advice(json_data):
    # Parse JSON data
    data = json.loads(json_data)
    
    # Extract price information
    prices = data.get("Price", {})
    
    if not prices:
        return "Price data not found"
    
    # Assuming there are only two tokens
    tokens = list(prices.keys())
    
    # Get the current prices of the tokens
    token1_price = prices.get(tokens[0], None)
    token2_price = prices.get(tokens[1], None)
    
    if token1_price is None or token2_price is None:
        return "Price data incomplete"
    
    # Implement Pairs Trading Strategy
    if token1_price > token2_price:
        return "Sell {} and Buy {}".format(tokens[0], tokens[1])
    elif token1_price < token2_price:
        return "Sell {} and Buy {}".format(tokens[1], tokens[0])
    else:
        return "Hold"



def run(**kwargs) -> Tuple[str, Optional[str], Optional[Dict[str, Any]], Any]:
    """Run the trading task"""
    #tool = kwargs["tool"]
    prompt = kwargs["prompt"]
    api_key = kwargs["api_keys"]
    #max_tokens = kwargs.get("max_tokens", generation_config["max_output_tokens"])
    #temperature = kwargs.get("temperature", generation_config["temperature"])
    #engine = TOOL_TO_ENGINE[tool]
    
  
    # Configure GenerativeAI model with API key
    genai.configure(api_key=api_key)
    
    # Construct trading prompt for Gemeni API
    trading_prompt = TRADE_PROMPT.format(user_prompt=prompt)
    
    response = model.generate_content(
    trading_prompt,
    stream=False)
    
    advice = trading_advice(response.text)

    return print(response.text)

dict_1 = dict( prompt = "How should I trade between bitcoin and celo based on the current market data as at 25/02/2024", api_keys="")

x = run(**dict_1)
