import logging
from typing import Callable

logger = logging.getLogger(__name__)

class FunctionExecutor(Callable):
    def __init__(self, func_name: str, func_def: str, chat_func: Callable):
        self.func_name = func_name
        self.func_def = func_def
        self.chat_func = chat_func
        logger.debug(f"Initializing FunctionExecutor: {func_name}")

    def __call__(self, *args, **kwargs) -> str:
        logger.debug(f"Executing function {self.func_name}, arguments: args={args}, kwargs={kwargs}")

        globals_ = globals().copy()
        globals_['chat'] = self.chat_func

        logger.debug(f"Code to execute:\n{self.func_def}")
        logger.debug(f"Calling function {self.func_name} with args={args}, kwargs={kwargs}")

        try:
            exec(self.func_def, globals_, globals_)
            logger.debug("Function definition executed successfully")
            globals_['args'] = args
            globals_['kwargs'] = kwargs

            exec(f"__result__ = {self.func_name}(*args, **kwargs)", globals_, globals_)
            result = globals_["__result__"]
            logger.debug(f"Function call succeeded, result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error executing function: {e}", exc_info=True)
            raise
