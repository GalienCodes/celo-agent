import json
from collections import defaultdict
from concurrent.futures import Future, ThreadPoolExecutor
from heapq import nlargest
from itertools import islice
from string import punctuation
from typing import Any, Dict, Generator, List, Optional, Tuple, Callable

# Import Gemini API client (assuming you have one)
from gemini_api_client import GeminiClient

client: Optional[GeminiClient] = None


class GeminiClientManager:
    """Client context manager for Gemini API."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def __enter__(self) -> GeminiClient:
        global client
        if client is None:
            client = GeminiClient(api_key=self.api_key)
        return client

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        global client
        if client is not None:
            client.close()
            client = None

TRADE_PROMPT = """
You are a trading AI inside a multi-agent system that takes in a prompt of a user requesting trading advice for two tokens.
You are provided with an input under the label "USER_PROMPT". You must follow the instructions
under the label "INSTRUCTIONS". You must provide your response in the format specified under "OUTPUT_FORMAT".

INSTRUCTIONS
* Read the input under the label "USER_PROMPT" delimited by three backticks.
* The "USER_PROMPT" specifies two tokens for trading advice.
* Provide the latest market data for the two tokens such as current prices, trading volume, and trends.
* Using the Pairs Trading Strategy, You must provide advice on whether to hold and not sell or buy, to buy more of token 1 and sell token 2, or to buy token 2 and sell token 1.
* You must provide your response in the format specified under "OUTPUT_FORMAT".
* Do not include any other contents in your response.

USER_PROMPT:
```
{user_prompt}
```
OUTPUT_FORMAT
* Your output response must be only a single JSON object to be parsed by Python's "json.loads()".
* The JSON must contain three fields: "decision", "confidence", and "info_utility".
   - "decision": Your advice decision. It can be "hold", "buy_token1_sell_token2", or "buy_token2_sell_token1".
   - "confidence": A value between 0 and 1 indicating the confidence in the decision. 0 indicates lowest
     confidence value; 1 maximum confidence value.
   - "info_utility": Utility of the information provided in "ADDITIONAL_INFORMATION" to help you make the decision.
     0 indicates lowest utility; 1 maximum utility.
* Output only the JSON object. Do not include any other contents in your response.
"""


def run(**kwargs) -> Tuple[str, Optional[str], Optional[Dict[str, Any]], Any]:
    """Run the trading task"""
    tool = kwargs["tool"]
    prompt = kwargs["prompt"]
    api_keys = kwargs.get("api_keys", {})
    engine = TOOL_TO_ENGINE[tool]

    if tool not in ALLOWED_TOOLS:
        raise ValueError(f"Tool {tool} is not supported.")

    # Construct trading prompt for Gemini API
    trading_prompt = TRADE_PROMPT.format(user_prompt=prompt)

    # Call Gemini API for trading decision
    with GeminiClientManager(api_keys["gemini"]):
        # Replace with your specific Gemini API call for trading advice (keys and trading pair)
        # This is a placeholder to demonstrate the change
        response_json = client.give_trading_advice(prompt=trading_prompt,
                                                    engine=engine,
                                                    max_tokens=max_tokens,
                                                    temperature=temperature)

        # Handle potential errors from the API call
        if "error" in response_json:
            return (f"Error from Gemini API: {response_json['error']}",
                    None,
                    None,
                    None)

        # Extract relevant information from the response (assuming structure)
        decision = response_json.get("decision")
        confidence = response_json.get("confidence")
        info_utility = response_json.get("info_utility")

    # Return the result (assuming response structure)
    return (
        "",  # Replace with actual response content from Gemini API
        trading_prompt,
        {"decision": decision, "confidence": confidence, "info_utility": info_utility},
        None,
    )
