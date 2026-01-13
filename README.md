# Erin

[English](README.md) | [中文](README_cn.md)

Erin is an OpenAI-based Python function auto-generation tool. By analyzing function names and parameter types, Erin can automatically infer function intent and generate corresponding Python implementation code.

## Features

- 🤖 **Smart Function Generation**: Automatically generates function implementations based on function names and parameter types
- 🔧 **Dynamic Execution**: Generated functions can be executed immediately
- 📝 **Type Inference**: Automatically infers parameter types from argument values
- 🎨 **Decorator Support**: Supports `@erin` decorator, automatically uses function docstrings as context
- 🔌 **Configurable**: Supports custom OpenAI API endpoints and models
- 📊 **Logging**: Complete logging system for debugging and monitoring

## Installation

### Using uv (Recommended)

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### Using pip

```bash
pip install -e .
```

## Configuration

### Environment Variables

Erin supports the following environment variables:

| Environment Variable | Description | Required | Default |
|---------------------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `OPENAI_BASE_URL` | Custom API endpoint (e.g., for OpenAI-compatible services) | No | OpenAI official endpoint |
| `OPENAI_MODEL` | Model name to use | No | `gpt-4o-mini` |

### Setting Environment Variables

**Linux/macOS:**
```bash
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # Optional
export OPENAI_MODEL="gpt-4o-mini"  # Optional
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
$env:OPENAI_BASE_URL="https://api.openai.com/v1"  # Optional
$env:OPENAI_MODEL="gpt-4o-mini"  # Optional
```

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=your-api-key-here
set OPENAI_BASE_URL=https://api.openai.com/v1
set OPENAI_MODEL=gpt-4o-mini
```

## Usage

### Basic Usage

```python
import erin

# Directly call function names, Erin will automatically generate implementations based on function name and arguments
result = erin.calculate_sum(1, 2, 3)
print(result)  # Output: 6

# Calculate average
avg = erin.calculate_average([1, 2, 3, 4, 5])
print(avg)  # Output: 3.0

# Check if even
is_even = erin.is_even(4)
print(is_even)  # Output: True
```

### Decorator Usage

Erin supports using decorators to define functions. The decorator automatically uses the function's docstring as context hints to help generate more accurate function implementations:

```python
import erin

# Use @erin decorator
@erin
def calculate_sum(a, b, c):
    """Calculate the sum of three numbers"""
    pass

result = calculate_sum(1, 2, 3)
print(result)  # Output: 6

# Use @erin(name="...") to specify function name
@erin(name="add_numbers")
def my_function(x, y):
    """Add two numbers together"""
    pass

result = my_function(5, 10)
print(result)  # Output: 15

# You can also use erin module directly as a decorator
@erin
def reverse_string(s):
    """Reverse a string"""
    pass

reversed_str = reverse_string("hello")
print(reversed_str)  # Output: "olleh"
```

**Decorator Advantages**:
- 📝 **Automatic Docstring Usage**: The function's `__doc__` is automatically passed as `optional_context` to the prompt, helping the LLM better understand function intent
- 🎯 **More Accurate Implementation**: By providing context through docstrings, the generated function implementations are usually more aligned with expectations
- 🔄 **Preserve Function Signature**: Uses `functools.update_wrapper` to preserve original function metadata

### How It Works

1. **Function Call**: When you call `erin.function_name(...)` or use a decorator, Erin will:
   - Infer parameter types from argument values
   - Generate a prompt based on the function name (if using a decorator, it will also include the function's docstring as context)
   - Call OpenAI API to generate function code
   - Dynamically execute the generated code and return the result

2. **Type Inference**: Erin automatically infers types from argument values:
   - `1` → `int`
   - `"hello"` → `str`
   - `[1, 2, 3]` → `list`
   - `{"key": "value"}` → `dict`

3. **Decorator Pattern**: When using the `@erin` decorator:
   - The function's `__doc__` is automatically extracted and passed as `optional_context` to the prompt
   - You can customize the function name via the `name` parameter (defaults to the decorated function's name)
   - The decorated function preserves original metadata (via `functools.update_wrapper`)

### More Examples

```python
import erin

# String operations
reversed_str = erin.reverse_string("hello")
print(reversed_str)  # "olleh"

# List operations
unique_items = erin.remove_duplicates([1, 2, 2, 3, 3, 4])
print(unique_items)  # [1, 2, 3, 4]

# Dictionary operations
merged = erin.merge_dicts({"a": 1}, {"b": 2})
print(merged)  # {"a": 1, "b": 2}

# Math operations
factorial = erin.calculate_factorial(5)
print(factorial)  # 120

# Using decorator to define functions (recommended approach)
@erin
def find_max_value(numbers):
    """Find the maximum value from a list of numbers"""
    pass

max_val = find_max_value([3, 1, 4, 1, 5, 9, 2, 6])
print(max_val)  # 9

@erin(name="custom_name")
def my_custom_function(data):
    """Process data and return processed results"""
    pass
```

## Logging Configuration

Erin has a built-in complete logging system. To enable logging, you need to configure Python's logging module:

```python
import logging

# Configure logging level
logging.basicConfig(
    level=logging.INFO,  # Or logging.DEBUG for more detailed information
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now you'll see log output when using erin
import erin
result = erin.calculate_sum(1, 2, 3)
```

### Log Levels

- **INFO**: Records key operations (function calls, API calls, execution results)
- **DEBUG**: Records detailed information (parameter formatting, prompt content, code generation, etc.)

### Log Output Example

```
2024-01-01 12:00:00 - erin - INFO - OpenAI client initialized
2024-01-01 12:00:01 - erin - INFO - Calling function: calculate_sum, arguments: (1, 2, 3)
2024-01-01 12:00:01 - erin - INFO - Calling OpenAI API to generate function code...
2024-01-01 12:00:02 - erin - INFO - Successfully generated function code, code length: 45 characters
2024-01-01 12:00:02 - erin - INFO - Executing generated function...
2024-01-01 12:00:02 - erin - INFO - Function executed successfully, return value: 6
```

## Notes

1. **First Call**: Each function name generates code on the first call, and subsequent calls will regenerate (current version does not support caching)

2. **API Costs**: Each function call will invoke the OpenAI API, please be aware of API usage costs

3. **Security**: Generated code will execute in the current Python environment, please ensure function names and parameters are from trusted sources

4. **Error Handling**: If the generated code has errors, Erin will raise exceptions and log detailed information

5. **Type Inference Limitations**: The current version infers types from argument values, complex types (such as `list[int]`) may be inferred as `list`

## Project Structure

```
erin/
├── __init__.py      # Main module, contains LLMCallable class
├── prompt.py         # Prompt formatting module
└── executor.py       # Function executor module
```

## Development

### Running Tests

```bash
# Using uv
uv run python -m pytest

# Or using pip
pytest
```

### Code Formatting

```bash
# Using ruff (if configured)
ruff format .
ruff check .
```

## License

This project is licensed under the [WTFPL](LICENSE) (Do What The F*ck You Want To Public License).

You are free to use, modify, and distribute the code of this project without any restrictions.

## Contributing

Issues and Pull Requests are welcome!
