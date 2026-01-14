import logging
import inspect
from typing import List, Tuple, Any, Dict

logger = logging.getLogger(__name__)

# Maximum parameter value string length, values exceeding this will be simplified or skipped
MAX_PARAM_VALUE_LENGTH = 500

PROMPT = """
You are a Python function synthesizer named Erin. You will receive a function name and parameter types, and you must infer the most plausible behavior from the name and types, then implement the function in Python.

Input you will receive:

    function_name:
    parameters: a list of (param_name: type) pairs, e.g., x: int, items: list[int], data: dict[str, float]
    parameter_values: example values for each parameter (when available), including structure definitions for objects
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
    For complex problems that require reasoning, analysis, or natural language processing, you can call the `chat` function (which is available in the execution environment) to interact with a large language model and get results. The `chat` function signature is: `chat(prompt: str, system_prompt: str = None) -> str`. It takes a required string prompt and an optional system_prompt string, and returns a string response.

    IMPORTANT: You should PREFER using `chat` over hardcoded lookup tables or mapping dictionaries when the mapping or judgment requires:
        - Semantic understanding (e.g., text_to_emoji, where "eye" maps to "👁️" based on meaning)
        - Cultural or domain knowledge (e.g., is_person_male, where you need to know if a name like "Elon Musk" is typically male)
        - Natural language processing or interpretation
        - Complex reasoning or multi-step problem solving
        - Cases where the mapping space is large or open-ended (e.g., any text to emoji, any name to gender)

    Instead of creating large dictionaries or if-else chains for these cases, use `chat` to have the model perform the mapping or judgment dynamically. Only use hardcoded lookup tables when the mapping is small, fixed, and purely algorithmic (e.g., simple mathematical conversions, predefined status codes).

    When calling `chat`, you can optionally provide a `system_prompt` parameter to set the system role context for the conversation, which helps guide the model's behavior and response style.
    Prefer deterministic behavior. Avoid randomness unless the name clearly implies it.

Output format:

    Output only the Python code for the function (and at most tiny inner helpers if absolutely necessary), DO NOT INCLUDE QUOTE.
    Do not include explanations, backticks, or extra text. Just the function definition.
    Do not include any docstrings, code only.

Now wait for my specification in the following format:

function_name: <function name>
optional_context: <one short line, optional>

parameters:
    <param_name>: <param type>
    <param_name>: <param type>
parameter_values:
    <param_name>: <example value or structure definition>
    <param_name>: <example value or structure definition>

Here is the specification:

function_name: {function_name}
{optional_context}

parameters:
{parameters}
parameter_values:
{parameter_values}
"""

def format_param_value(value: Any, visited: set = None) -> str:
    """
    Format parameter value, handling overly long values and object structures.
    Returns formatted string, or None if value is too long or cannot be formatted.
    """
    if visited is None:
        visited = set()

    try:
        # Handle None
        if value is None:
            return "None"

        # Handle strings
        if isinstance(value, str):
            if len(value) > MAX_PARAM_VALUE_LENGTH:
                return f'"{value[:100]}..." (truncated, total length: {len(value)})'
            return repr(value)

        # Handle numbers and booleans
        if isinstance(value, (int, float, bool)):
            return repr(value)

        # Handle lists
        if isinstance(value, list):
            if len(value) > 20:  # List too long, simplify
                if len(str(value)) > MAX_PARAM_VALUE_LENGTH:
                    return f"[{format_param_value(value[0]) if value else '...'}, ...] (list with {len(value)} items)"
                # Try to show first few elements
                preview = [format_param_value(item, visited.copy()) for item in value[:3]]
                return f"[{', '.join(preview)}, ...] (list with {len(value)} items)"
            else:
                items = []
                for item in value:
                    item_str = format_param_value(item, visited.copy())
                    if item_str and len(item_str) < 100:
                        items.append(item_str)
                    else:
                        items.append("...")
                    if len(', '.join(items)) > MAX_PARAM_VALUE_LENGTH:
                        items.append("...")
                        break
                result = f"[{', '.join(items)}]"
                if len(result) > MAX_PARAM_VALUE_LENGTH:
                    return f"[...] (list with {len(value)} items, too long to display)"
                return result

        # Handle dictionaries
        if isinstance(value, dict):
            if len(value) > 10:  # Dictionary too large, simplify
                preview_items = []
                for i, (k, v) in enumerate(value.items()):
                    if i >= 3:
                        break
                    key_str = format_param_value(k, visited.copy())
                    val_str = format_param_value(v, visited.copy())
                    if key_str and val_str and len(key_str) + len(val_str) < 150:
                        preview_items.append(f"{key_str}: {val_str}")
                return f"{{{', '.join(preview_items)}, ...}} (dict with {len(value)} items)"
            else:
                items = []
                for k, v in value.items():
                    key_str = format_param_value(k, visited.copy())
                    val_str = format_param_value(v, visited.copy())
                    if key_str and val_str and len(key_str) + len(val_str) < 150:
                        items.append(f"{key_str}: {val_str}")
                    else:
                        items.append("...")
                    if len('{' + ', '.join(items) + '}') > MAX_PARAM_VALUE_LENGTH:
                        items.append("...")
                        break
                result = f"{{{', '.join(items)}}}"
                if len(result) > MAX_PARAM_VALUE_LENGTH:
                    return f"{{...}} (dict with {len(value)} items, too long to display)"
                return result

        # Handle tuples
        if isinstance(value, tuple):
            if len(value) > 10:
                preview = [format_param_value(item, visited.copy()) for item in value[:3]]
                return f"({', '.join(preview)}, ...) (tuple with {len(value)} items)"
            items = [format_param_value(item, visited.copy()) for item in value]
            result = f"({', '.join(items)})"
            if len(result) > MAX_PARAM_VALUE_LENGTH:
                return f"(...) (tuple with {len(value)} items, too long to display)"
            return result

        # Handle custom objects
        obj_structure = format_object_structure(value, visited)
        if obj_structure:
            return obj_structure

        # Other types, try to convert to string
        value_str = str(value)
        if len(value_str) > MAX_PARAM_VALUE_LENGTH:
            return f"{value_str[:100]}... (truncated, type: {type(value).__name__})"
        return value_str

    except Exception as e:
        logger.debug(f"Error formatting param value: {e}")
        return None


def format_object_structure(obj: Any, visited: set = None) -> str:
    """
    Format object structure, returning structure definition and example values.
    For custom objects, extract their attributes and example values.
    """
    if visited is None:
        visited = set()

    obj_id = id(obj)
    if obj_id in visited:
        return "... (circular reference)"
    visited.add(obj_id)

    try:
        # Check if it's a custom class instance (not a builtin type)
        if hasattr(obj, '__class__') and obj.__class__.__module__ != 'builtins':
            class_name = obj.__class__.__name__
            module_name = obj.__class__.__module__

            # Get all attributes
            attrs = {}
            for key in dir(obj):
                if not key.startswith('_'):
                    try:
                        value = getattr(obj, key)
                        if not inspect.ismethod(value) and not inspect.isfunction(value):
                            attrs[key] = value
                    except:
                        pass

            # Format attribute example values
            attr_examples = []
            for key, value in list(attrs.items())[:10]:  # Limit to 10 attributes max
                try:
                    value_str = format_param_value(value, visited.copy())
                    if value_str and len(value_str) < 200:  # Attribute value should not be too long
                        attr_examples.append(f"        {key}: {value_str}")
                except:
                    attr_examples.append(f"        {key}: <unable to format>")

            if attr_examples:
                return f"<{class_name} object> with structure:\n" + "\n".join(attr_examples)
            else:
                return f"<{class_name} object>"
        else:
            return None
    except Exception as e:
        logger.debug(f"Error formatting object structure: {e}")
        return None
    finally:
        visited.discard(obj_id)


def format_prompt(
    function_name: str,
    parameters: List[Tuple[str, str]],
    parameter_values: List[Tuple[str, Any]] = None,
    optional_context: str = None
) -> str:
    logger.debug(f"Formatting prompt: function_name={function_name}, parameters={parameters}, parameter_values={parameter_values}, optional_context={optional_context}")

    params_str = "\n".join([f"    {param_name}: {param_type}" for param_name, param_type in parameters])

    # Format parameter values
    param_values_str = ""
    if parameter_values:
        value_lines = []
        for param_name, param_value in parameter_values:
            formatted_value = format_param_value(param_value)
            if formatted_value:
                # If value is multi-line (e.g., object structure), need proper indentation
                if '\n' in formatted_value:
                    value_lines.append(f"    {param_name}:")
                    for line in formatted_value.split('\n'):
                        value_lines.append(f"        {line}")
                else:
                    value_lines.append(f"    {param_name}: {formatted_value}")
            else:
                value_lines.append(f"    {param_name}: <unable to format>")
        param_values_str = "\n".join(value_lines)
    else:
        param_values_str = "    (no example values provided)"

    context_str = ""
    if optional_context:
        context_str = f"optional_context: {optional_context}"

    formatted = PROMPT.format(
        function_name=function_name,
        parameters=params_str,
        parameter_values=param_values_str,
        optional_context=context_str
    )

    logger.debug(f"Prompt formatting completed, total length: {len(formatted)} characters")
    return formatted
