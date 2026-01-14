import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

PROMPT = """
You are a Python function synthesizer. You will receive a function name and parameter types, and you must infer the most plausible behavior from the name and types, then implement the function in Python.

Input you will receive:

    function_name:
    parameters: a list of (param_name: type) pairs, e.g., x: int, items: list[int], data: dict[str, float]
    optional_context: a one-line hint about intent (optional)

Your task:

    Infer the function’s purpose from its name and parameter types (and optional_context if provided). Use common conventions:
        Names like sum, average, mean, count, min, max imply aggregations.
        Prefixes like is_/has_/can_ imply boolean predicates.
        Words like merge/join/concat/combine imply combining inputs.
        unique/distinct/deduplicate imply removing duplicates while preserving order if sensible.
        sort/ordered/ranked imply returning a sorted result without mutating inputs unless name includes "inplace".
        normalize/standardize/trim/clean imply data cleaning or scaling with safe defaults.
        find/search/index/contains imply lookup logic and clear failure behavior.
        Names like fetch/get/post/request/api/call imply HTTP API calls.
    Choose an appropriate return type. If not obvious, select the most common-sense type and document your assumption in the docstring.
    Write a clean, efficient implementation using only the Python 3.10+ standard library.
    Validate inputs where reasonable (e.g., types, value ranges, emptiness). Raise ValueError or TypeError with clear messages rather than failing silently.
    You may perform HTTP API calls using urllib.request or urllib3 from the standard library when the function name or context suggests network operations. Handle network errors appropriately (e.g., urllib.error.URLError, timeout exceptions). Do not mutate inputs unless the name includes "inplace" or "mutate".
    For complex problems that require reasoning, analysis, or natural language processing, you can call the `chat` function (which is available in the execution environment) to interact with a large language model and get results. The `chat` function signature is: `chat(prompt: str, system_prompt: str = None) -> str`. It takes a required string prompt and an optional system_prompt string, and returns a string response. Use this when the problem involves:
        - Complex reasoning or multi-step problem solving
        - Natural language understanding or generation
        - Data analysis that requires interpretation
        - Any task that would benefit from LLM capabilities
    When calling `chat`, you can optionally provide a `system_prompt` parameter to set the system role context for the conversation, which helps guide the model's behavior and response style.
    Prefer deterministic behavior. Avoid randomness unless the name clearly implies it.

Output format:

    Output only the Python code for the function (and at most tiny inner helpers if absolutely necessary), DO NOT INCLUDE QUOTE.
    Do not include explanations, backticks, or extra text. Just the function definition.
    Do not include any docstrings, code only.

Now wait for my specification in the following format:

function_name: <function name>

parameters:
    <param_name>: <param type>
    <param_name>: <param type>
    optional_context: <one short line, optional>

Here is the specification:

function_name: {function_name}

parameters:
{parameters}
{optional_context}
"""

def format_prompt(
    function_name: str,
    parameters: List[Tuple[str, str]],
    optional_context: str = None
) -> str:
    logger.debug(f"Formatting prompt: function_name={function_name}, parameters={parameters}, optional_context={optional_context}")

    params_str = "\n".join([f"    {param_name}: {param_type}" for param_name, param_type in parameters])
    context_str = ""
    if optional_context:
        context_str = f"optional_context: {optional_context}"

    formatted = PROMPT.format(
        function_name=function_name,
        parameters=params_str,
        optional_context=context_str
    )

    logger.debug(f"Prompt formatting completed, total length: {len(formatted)} characters")
    return formatted
