---
sidebar_position: 4
title: "API请求片段"
description: "HTTP请求、JSON处理、数据获取的即用代码片段"
keywords: [API, HTTP请求, JSON, Python, requests, 数据获取]
---

# API请求片段

这里收集了常用的网络请求和数据获取代码片段，可以用于获取网络数据、调用API接口等。

## 准备工作

运行这些代码前，需要安装requests库：

```bash
pip install requests
```

## 基础请求

### GET请求

```python
import requests

# 基础GET请求
url = 'https://api.example.com/data'
response = requests.get(url)

# 检查状态
if response.status_code == 200:
    data = response.json()  # 如果返回JSON
    print(data)
else:
    print(f"请求失败: {response.status_code}")
```

### 带参数的GET请求

```python
import requests

url = 'https://api.example.com/search'
params = {
    'keyword': '搜索词',
    'page': 1,
    'limit': 10
}

response = requests.get(url, params=params)
# 实际请求URL: https://api.example.com/search?keyword=搜索词&page=1&limit=10

if response.status_code == 200:
    data = response.json()
    print(data)
```

### POST请求

```python
import requests

url = 'https://api.example.com/submit'
data = {
    'username': '用户名',
    'email': 'user@example.com'
}

# 发送表单数据
response = requests.post(url, data=data)

# 发送JSON数据
response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    print(result)
```

### 带请求头的请求

```python
import requests

url = 'https://api.example.com/data'
headers = {
    'Authorization': 'Bearer your_token_here',
    'Content-Type': 'application/json',
    'User-Agent': 'MyApp/1.0'
}

response = requests.get(url, headers=headers)
```

## JSON数据处理

### 解析JSON响应

```python
import requests
import json

response = requests.get('https://api.example.com/data')
data = response.json()

# 访问数据
print(data['name'])
print(data['items'][0]['id'])

# 遍历列表
for item in data['items']:
    print(f"ID: {item['id']}, Name: {item['name']}")
```

### 读取JSON文件

```python
import json

# 读取JSON文件
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(data)
```

### 保存JSON文件

```python
import json

data = {
    'name': '张三',
    'age': 30,
    'items': ['item1', 'item2']
}

# 保存为JSON文件
with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

### JSON与字符串转换

```python
import json

# 字典转JSON字符串
data = {'name': '张三', 'age': 30}
json_string = json.dumps(data, ensure_ascii=False)
print(json_string)  # {"name": "张三", "age": 30}

# JSON字符串转字典
json_string = '{"name": "张三", "age": 30}'
data = json.loads(json_string)
print(data['name'])  # 张三
```

## 实用场景

### 获取天气数据

```python
import requests

# 使用免费天气API示例（需要替换为实际API）
def get_weather(city):
    # 这里以wttr.in为例（免费无需API key）
    url = f'https://wttr.in/{city}?format=j1'

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            return {
                '温度': current['temp_C'] + '°C',
                '天气': current['weatherDesc'][0]['value'],
                '湿度': current['humidity'] + '%'
            }
    except Exception as e:
        return {'错误': str(e)}

# 使用
weather = get_weather('Beijing')
print(weather)
```

### 获取汇率数据

```python
import requests

def get_exchange_rate(from_currency, to_currency):
    # 使用免费汇率API示例
    url = f'https://api.exchangerate-api.com/v4/latest/{from_currency}'

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            rate = data['rates'].get(to_currency)
            return rate
    except Exception as e:
        print(f"获取汇率失败: {e}")
        return None

# 使用
rate = get_exchange_rate('USD', 'CNY')
if rate:
    print(f"1 USD = {rate} CNY")
```

### 批量请求数据

```python
import requests
import time

urls = [
    'https://api.example.com/data/1',
    'https://api.example.com/data/2',
    'https://api.example.com/data/3',
]

results = []

for url in urls:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            results.append(response.json())
        else:
            results.append({'error': f'状态码 {response.status_code}'})
    except Exception as e:
        results.append({'error': str(e)})

    # 避免请求过快
    time.sleep(0.5)

print(f"成功获取 {len([r for r in results if 'error' not in r])} 条数据")
```

### 下载文件

```python
import requests
import os

def download_file(url, save_path):
    """下载文件到指定路径"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"下载完成: {save_path}")
            return True
        else:
            print(f"下载失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"下载出错: {e}")
        return False

# 使用
download_file(
    'https://example.com/file.pdf',
    'C:/下载/file.pdf'
)
```

### 分页获取所有数据

```python
import requests

def fetch_all_pages(base_url, params=None):
    """获取所有分页数据"""
    if params is None:
        params = {}

    all_data = []
    page = 1

    while True:
        params['page'] = page
        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            break

        data = response.json()
        items = data.get('items', [])

        if not items:
            break

        all_data.extend(items)
        print(f"已获取第 {page} 页，共 {len(items)} 条")

        # 检查是否还有下一页
        if page >= data.get('total_pages', page):
            break

        page += 1

    return all_data

# 使用
all_data = fetch_all_pages('https://api.example.com/list', {'limit': 100})
print(f"总共获取 {len(all_data)} 条数据")
```

## 错误处理

### 完整的请求模板

```python
import requests
from requests.exceptions import Timeout, RequestException

def safe_request(url, method='GET', **kwargs):
    """安全的HTTP请求，带错误处理"""
    try:
        # 设置默认超时
        kwargs.setdefault('timeout', 10)

        if method.upper() == 'GET':
            response = requests.get(url, **kwargs)
        elif method.upper() == 'POST':
            response = requests.post(url, **kwargs)
        else:
            return {'success': False, 'error': f'不支持的方法: {method}'}

        # 检查状态码
        response.raise_for_status()

        # 尝试解析JSON
        try:
            data = response.json()
        except:
            data = response.text

        return {'success': True, 'data': data}

    except Timeout:
        return {'success': False, 'error': '请求超时'}
    except RequestException as e:
        return {'success': False, 'error': str(e)}
    except Exception as e:
        return {'success': False, 'error': f'未知错误: {e}'}

# 使用
result = safe_request('https://api.example.com/data')
if result['success']:
    print(result['data'])
else:
    print(f"请求失败: {result['error']}")
```

### 重试机制

```python
import requests
import time

def request_with_retry(url, max_retries=3, delay=1):
    """带重试的请求"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code >= 500:
                # 服务器错误，等待后重试
                print(f"服务器错误 {response.status_code}，重试中...")
            else:
                # 客户端错误，不重试
                return {'error': f'请求失败: {response.status_code}'}
        except requests.exceptions.Timeout:
            print(f"请求超时，重试中 ({attempt + 1}/{max_retries})...")
        except Exception as e:
            print(f"请求出错: {e}")
            return {'error': str(e)}

        if attempt < max_retries - 1:
            time.sleep(delay * (attempt + 1))  # 递增延迟

    return {'error': '达到最大重试次数'}

# 使用
data = request_with_retry('https://api.example.com/data')
```

## 数据导出组合

### API数据导出到Excel

```python
import requests
import pandas as pd

def api_to_excel(api_url, output_file, params=None):
    """从API获取数据并导出到Excel"""
    try:
        response = requests.get(api_url, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()

            # 假设数据是列表格式
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and 'items' in data:
                df = pd.DataFrame(data['items'])
            else:
                df = pd.DataFrame([data])

            df.to_excel(output_file, index=False)
            print(f"导出成功: {output_file}")
            return True
        else:
            print(f"API请求失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"导出失败: {e}")
        return False

# 使用
api_to_excel(
    'https://api.example.com/users',
    'users.xlsx',
    params={'limit': 100}
)
```

### 从Excel读取后调用API

```python
import requests
import pandas as pd
import time

def process_excel_with_api(input_file, api_url, id_column, output_file):
    """读取Excel，逐行调用API，保存结果"""

    # 读取Excel
    df = pd.read_excel(input_file)
    results = []

    for idx, row in df.iterrows():
        item_id = row[id_column]

        # 调用API
        try:
            response = requests.get(f"{api_url}/{item_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                results.append({
                    'id': item_id,
                    'status': '成功',
                    'data': str(data)
                })
            else:
                results.append({
                    'id': item_id,
                    'status': f'失败({response.status_code})',
                    'data': ''
                })
        except Exception as e:
            results.append({
                'id': item_id,
                'status': f'错误',
                'data': str(e)
            })

        # 避免请求过快
        time.sleep(0.3)
        print(f"处理进度: {idx + 1}/{len(df)}")

    # 保存结果
    result_df = pd.DataFrame(results)
    result_df.to_excel(output_file, index=False)
    print(f"处理完成，结果保存到: {output_file}")

# 使用
process_excel_with_api(
    'input.xlsx',
    'https://api.example.com/item',
    'item_id',
    'output.xlsx'
)
```

## 常见问题

### Q1: SSL证书错误

```python
# 方法1：忽略SSL验证（不推荐用于生产）
response = requests.get(url, verify=False)

# 方法2：指定证书
response = requests.get(url, verify='/path/to/certificate.pem')
```

### Q2: 中文编码问题

```python
response = requests.get(url)

# 手动设置编码
response.encoding = 'utf-8'
text = response.text

# 或者使用apparent_encoding
response.encoding = response.apparent_encoding
text = response.text
```

### Q3: 代理设置

```python
proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'http://proxy.example.com:8080'
}

response = requests.get(url, proxies=proxies)
```

### Q4: Session保持登录状态

```python
# 创建session
session = requests.Session()

# 登录
login_data = {'username': 'user', 'password': 'pass'}
session.post('https://example.com/login', data=login_data)

# 后续请求会自动带上cookie
response = session.get('https://example.com/profile')
```

## 下一步

- **文件操作** → [文件操作片段](./file-operations)
- **数据处理** → [数据处理片段](./data-processing)
- **邮件发送** → [邮件处理工作流](/docs/workflows/email)

---

**提示**：使用API时注意阅读API文档，了解请求频率限制和认证方式。如果需要调用特定API，把API文档发给AI，让它帮你写代码。
