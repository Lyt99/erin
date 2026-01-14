import hashlib
import json
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

# In-memory cache: maps cache_key -> function_code
_cache: dict[str, str] = {}


def generate_cache_key(
    function_name: str,
    parameters: List[Tuple[str, str]]
) -> str:
    """
    Generate a cache key based on function name, parameter names, and parameter types.

    Args:
        function_name: Name of the function
        parameters: List of (param_name, param_type) tuples

    Returns:
        A hash string representing the cache key
    """
    # Create a deterministic representation
    # Keep parameters in original order as parameter position matters for function signature
    # Create a dictionary representation
    cache_data = {
        "function_name": function_name,
        "parameters": parameters
    }

    # Convert to JSON string (deterministic)
    json_str = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)

    # Generate hash
    hash_obj = hashlib.sha256(json_str.encode('utf-8'))
    cache_key = hash_obj.hexdigest()

    logger.debug(f"Generated cache key: {cache_key} for function {function_name} with parameters {parameters}")
    return cache_key


def get_cached_code(
    function_name: str,
    parameters: List[Tuple[str, str]]
) -> Optional[str]:
    """
    Retrieve cached function code if it exists.

    Args:
        function_name: Name of the function
        parameters: List of (param_name, param_type) tuples

    Returns:
        Cached function code if found, None otherwise
    """
    cache_key = generate_cache_key(function_name, parameters)

    if cache_key not in _cache:
        logger.debug(f"Cache miss for function {function_name} with parameters {parameters}")
        return None

    code = _cache[cache_key]
    logger.info(f"Cache hit for function {function_name} with parameters {parameters}")
    logger.debug(f"Retrieved cached code, length: {len(code)} characters")
    return code


def set_cached_code(
    function_name: str,
    parameters: List[Tuple[str, str]],
    code: str
) -> None:
    """
    Store function code in cache.

    Args:
        function_name: Name of the function
        parameters: List of (param_name, param_type) tuples
        code: The generated function code to cache
    """
    cache_key = generate_cache_key(function_name, parameters)
    _cache[cache_key] = code

    logger.info(f"Cached function code for {function_name} with parameters {parameters}")
    logger.debug(f"Cached code length: {len(code)} characters")


def clear_cache() -> None:
    """Clear all cached function codes."""
    _cache.clear()
    logger.info("Cache cleared")

