import functools
import logging
import sys
import types
import openai
import os
from typing import Callable, Optional, Any
from erin.prompt import format_prompt
from erin.executor import FunctionExecutor
from typing import List, Tuple

# Configure logging
logger = logging.getLogger(__name__)

_openai_client_kwargs = {
    "api_key": os.getenv("OPENAI_API_KEY"),
}

base_url = os.getenv("OPENAI_BASE_URL")
if base_url:
    _openai_client_kwargs["base_url"] = base_url
    logger.info(f"Using custom base_url: {base_url}")
else:
    logger.info("Using default OpenAI base_url")

openai_client = openai.OpenAI(**_openai_client_kwargs)
logger.info("OpenAI client initialized")

model = os.getenv("OPENAI_MODEL")
if model is None:
    model = "gpt-4o-mini"
logger.debug(f"Using model: {model}")




class LLMCallable(Callable):
    function_name = None
    docstring = None

    def chat(self, prompt: str, system_prompt: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
        )
        logger.info(f"Chat response: {response.choices[0].message.content}")
        return response.choices[0].message.content


    def __init__(self, function_name, docstring=None):
        self.function_name = function_name
        self.docstring = docstring

    def __call__(self, *args):
        logger.info(f"Calling function: {self.function_name}, arguments: {args}")
        formatted_args: List[Tuple[str, str]] = [
            ((f"arg{i}", type(arg).__name__)) for i, arg in enumerate(args)
        ]
        logger.debug(f"Formatted arguments: {formatted_args}")

        # Prepare parameter values list
        parameter_values: List[Tuple[str, Any]] = [
            (f"arg{i}", arg) for i, arg in enumerate(args)
        ]
        logger.debug(f"Parameter values: {parameter_values}")

        logger.debug(f"Function documentation: {self.docstring }")
        prompt = format_prompt(self.function_name, formatted_args, parameter_values, self.docstring)
        logger.debug(f"Generated prompt length: {len(prompt)} characters")

        logger.info("Calling OpenAI API to generate function code...")
        try:
            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )
            code = response.choices[0].message.content
            logger.info(
                f"Successfully generated function code, code length: {len(code)} characters"
            )
            logger.debug(f"Generated code:\n{code}")
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}", exc_info=True)
            raise

        executor = FunctionExecutor(self.function_name, code, self.chat)
        logger.info("Executing generated function...")
        try:
            result = executor(*args)
            logger.info(f"Function executed successfully, return value: {result}")
            return result
        except Exception as e:
            logger.error(f"Function execution failed: {e}", exc_info=True)
            raise


def erin(func: Optional[Callable] = None, *, name: Optional[str] = None) -> Callable:
    def _decorate(f: Callable):
        llm = LLMCallable(name or f.__name__, docstring=f.__doc__)
        functools.update_wrapper(llm, f)
        return llm

    return _decorate if func is None else _decorate(func)


def __getattr__(name):
    return LLMCallable(name)


class _ErinModule(types.ModuleType):
    def __call__(self, func: Optional[Callable] = None, *, name: Optional[str] = None):
        return erin(func, name=name)


sys.modules[__name__].__class__ = _ErinModule
