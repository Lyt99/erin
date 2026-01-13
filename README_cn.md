# Erin

[English](README.md) | [中文](README_cn.md)

Erin 是一个基于 OpenAI 的 Python 函数自动生成工具。通过函数名和参数类型，Erin 可以自动推断函数意图并生成对应的 Python 实现代码。

## 特性

- 🤖 **智能函数生成**：根据函数名和参数类型自动生成函数实现
- 🔧 **动态执行**：生成的函数可以立即执行
- 📝 **类型推断**：自动从参数值推断参数类型
- 🎨 **装饰器支持**：支持 `@erin` 装饰器，自动使用函数文档字符串作为上下文
- 🔌 **可配置**：支持自定义 OpenAI API 端点和模型
- 📊 **日志记录**：完整的日志系统，方便调试和监控

## 安装

### 使用 uv（推荐）

```bash
# 安装 uv（如果还没有）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv sync
```

### 使用 pip

```bash
pip install -e .
```

## 配置

### 环境变量

Erin 支持以下环境变量：

| 环境变量 | 说明 | 必需 | 默认值 |
|---------|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | 是 | - |
| `OPENAI_BASE_URL` | 自定义 API 端点（如使用兼容 OpenAI API 的服务） | 否 | OpenAI 官方端点 |
| `OPENAI_MODEL` | 使用的模型名称 | 否 | `gpt-4o-mini` |

### 设置环境变量

**Linux/macOS:**
```bash
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # 可选
export OPENAI_MODEL="gpt-4o-mini"  # 可选
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
$env:OPENAI_BASE_URL="https://api.openai.com/v1"  # 可选
$env:OPENAI_MODEL="gpt-4o-mini"  # 可选
```

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=your-api-key-here
set OPENAI_BASE_URL=https://api.openai.com/v1
set OPENAI_MODEL=gpt-4o-mini
```

## 使用方法

### 基本用法

```python
import erin

# 直接调用函数名，Erin 会根据函数名和参数自动生成实现
result = erin.calculate_sum(1, 2, 3)
print(result)  # 输出: 6

# 计算平均值
avg = erin.calculate_average([1, 2, 3, 4, 5])
print(avg)  # 输出: 3.0

# 检查是否为偶数
is_even = erin.is_even(4)
print(is_even)  # 输出: True
```

### 装饰器用法

Erin 支持使用装饰器来定义函数，装饰器会自动使用函数的文档字符串（docstring）作为上下文提示，帮助生成更准确的函数实现：

```python
import erin

# 使用 @erin 装饰器
@erin
def calculate_sum(a, b, c):
    """计算三个数的总和"""
    pass

result = calculate_sum(1, 2, 3)
print(result)  # 输出: 6

# 使用 @erin(name="...") 指定函数名
@erin(name="add_numbers")
def my_function(x, y):
    """将两个数字相加"""
    pass

result = my_function(5, 10)
print(result)  # 输出: 15

# 也可以直接使用 erin 模块作为装饰器
@erin
def reverse_string(s):
    """反转字符串"""
    pass

reversed_str = reverse_string("hello")
print(reversed_str)  # 输出: "olleh"
```

**装饰器的优势**：
- 📝 **自动使用文档字符串**：函数的 `__doc__` 会自动作为 `optional_context` 传递给 prompt，帮助 LLM 更好地理解函数意图
- 🎯 **更精确的实现**：通过文档字符串提供上下文，生成的函数实现通常更符合预期
- 🔄 **保持函数签名**：使用 `functools.update_wrapper` 保持原函数的元数据

### 工作原理

1. **函数调用**：当你调用 `erin.function_name(...)` 或使用装饰器时，Erin 会：
   - 从参数值推断参数类型
   - 根据函数名生成 prompt（如果使用装饰器，还会包含函数的文档字符串作为上下文）
   - 调用 OpenAI API 生成函数代码
   - 动态执行生成的代码并返回结果

2. **类型推断**：Erin 会自动从参数值推断类型：
   - `1` → `int`
   - `"hello"` → `str`
   - `[1, 2, 3]` → `list`
   - `{"key": "value"}` → `dict`

3. **装饰器模式**：使用 `@erin` 装饰器时：
   - 函数的 `__doc__` 会自动提取并作为 `optional_context` 传递给 prompt
   - 可以通过 `name` 参数自定义函数名（默认使用被装饰函数的名称）
   - 装饰后的函数保持原有的元数据（通过 `functools.update_wrapper`）

### 更多示例

```python
import erin

# 字符串操作
reversed_str = erin.reverse_string("hello")
print(reversed_str)  # "olleh"

# 列表操作
unique_items = erin.remove_duplicates([1, 2, 2, 3, 3, 4])
print(unique_items)  # [1, 2, 3, 4]

# 字典操作
merged = erin.merge_dicts({"a": 1}, {"b": 2})
print(merged)  # {"a": 1, "b": 2}

# 数学运算
factorial = erin.calculate_factorial(5)
print(factorial)  # 120

# 使用装饰器定义函数（推荐方式）
@erin
def find_max_value(numbers):
    """从数字列表中找到最大值"""
    pass

max_val = find_max_value([3, 1, 4, 1, 5, 9, 2, 6])
print(max_val)  # 9

@erin(name="custom_name")
def my_custom_function(data):
    """处理数据并返回处理后的结果"""
    pass
```

## 日志配置

Erin 内置了完整的日志系统。要启用日志，需要配置 Python 的 logging 模块：

```python
import logging

# 配置日志级别
logging.basicConfig(
    level=logging.INFO,  # 或 logging.DEBUG 查看更详细的信息
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 现在使用 erin 时会看到日志输出
import erin
result = erin.calculate_sum(1, 2, 3)
```

### 日志级别

- **INFO**：记录关键操作（函数调用、API 调用、执行结果）
- **DEBUG**：记录详细信息（参数格式化、prompt 内容、代码生成等）

### 日志输出示例

```
2024-01-01 12:00:00 - erin - INFO - OpenAI 客户端初始化完成
2024-01-01 12:00:01 - erin - INFO - 调用函数: calculate_sum, 参数: (1, 2, 3)
2024-01-01 12:00:01 - erin - INFO - 正在调用 OpenAI API 生成函数代码...
2024-01-01 12:00:02 - erin - INFO - 成功生成函数代码，代码长度: 45 字符
2024-01-01 12:00:02 - erin - INFO - 正在执行生成的函数...
2024-01-01 12:00:02 - erin - INFO - 函数执行成功，返回值: 6
```

## 注意事项

1. **首次调用**：每个函数名在首次调用时会生成代码，后续调用会重新生成（当前版本不支持缓存）

2. **API 成本**：每次函数调用都会调用 OpenAI API，请注意 API 使用成本

3. **安全性**：生成的代码会在当前 Python 环境中执行，请确保函数名和参数来源可信

4. **错误处理**：如果生成的代码有错误，Erin 会抛出异常并记录详细日志

5. **类型推断限制**：当前版本从参数值推断类型，复杂类型（如 `list[int]`）可能被推断为 `list`

## 项目结构

```
erin/
├── __init__.py      # 主模块，包含 LLMCallable 类
├── prompt.py         # Prompt 格式化模块
└── executor.py       # 函数执行器模块
```

## 开发

### 运行测试

```bash
# 使用 uv
uv run python -m pytest

# 或使用 pip
pytest
```

### 代码格式

```bash
# 使用 ruff（如果已配置）
ruff format .
ruff check .
```

## 许可证

本项目采用 [WTFPL](LICENSE) (Do What The F*ck You Want To Public License) 许可证。

你可以自由地使用、修改、分发本项目的代码，无需任何限制。

## 贡献

欢迎提交 Issue 和 Pull Request！

