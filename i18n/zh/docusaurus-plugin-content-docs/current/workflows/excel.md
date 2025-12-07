---
sidebar_position: 2
title: "Excel数据处理工作流"
description: "使用AI完成Excel数据清洗、汇总、转换的完整工作流"
keywords: [Excel, 数据处理, Python, pandas, AI编程]
---

# Excel数据处理工作流

这是一个完整的Excel数据处理工作流教程。你将学会如何用AI处理常见的Excel任务。

## 场景设定

**任务**：你有一个包含500名员工信息的Excel文件，需要：
1. 清洗数据（去重、修正格式）
2. 按部门统计人数和平均薪资
3. 输出汇总报告

**文件结构**：
| 列名 | 类型 | 说明 |
|------|------|------|
| 姓名 | 文本 | 员工姓名 |
| 部门 | 文本 | 所属部门 |
| 入职日期 | 日期 | 格式不统一 |
| 薪资 | 数字 | 月薪 |

## 准备工作

### 1. 安装Python（如果没有）

**Windows用户**：
1. 访问 https://python.org/downloads
2. 下载最新版本
3. 安装时勾选 "Add Python to PATH"

**验证安装**：
```bash
python --version
# 应该显示 Python 3.x.x
```

### 2. 安装必要的库

打开命令提示符（cmd）或终端，运行：
```bash
pip install pandas openpyxl
```

## Step 1: 描述数据给AI

### 提示词模板

```
我有一个Excel文件叫 employees.xlsx，包含员工信息。

列结构：
- 姓名：员工姓名（文本）
- 部门：所属部门（文本）
- 入职日期：入职时间（日期，格式不统一，有"2024-01-15"和"1/15/2024"两种）
- 薪资：月薪（数字）

数据样例（前3行）：
姓名,部门,入职日期,薪资
张三,技术部,2024-01-15,15000
李四,市场部,1/20/2024,12000
王五,技术部,2023-12-01,18000

数据问题：
1. 有些行可能重复
2. 日期格式不统一
3. 薪资列可能有空值

请帮我写一个Python脚本：
1. 读取这个Excel文件
2. 删除重复行
3. 统一日期格式为 YYYY-MM-DD
4. 按部门统计人数和平均薪资
5. 输出汇总结果到新的Excel文件 summary.xlsx
```

### AI可能生成的代码

```python
import pandas as pd

# 读取Excel文件
df = pd.read_excel('employees.xlsx')

# 删除重复行
df = df.drop_duplicates()

# 统一日期格式
df['入职日期'] = pd.to_datetime(df['入职日期']).dt.strftime('%Y-%m-%d')

# 按部门统计
summary = df.groupby('部门').agg({
    '姓名': 'count',
    '薪资': 'mean'
}).rename(columns={
    '姓名': '人数',
    '薪资': '平均薪资'
}).round(2)

# 重置索引，使部门成为普通列
summary = summary.reset_index()

# 输出到Excel
summary.to_excel('summary.xlsx', index=False)

print("处理完成！结果已保存到 summary.xlsx")
print(summary)
```

## Step 2: 运行代码

### 创建脚本文件

1. 打开记事本或任意文本编辑器
2. 粘贴AI生成的代码
3. 保存为 `process_employees.py`
4. 确保文件和 `employees.xlsx` 在同一文件夹

### 运行脚本

```bash
# 进入文件所在目录
cd C:\你的文件夹路径

# 运行脚本
python process_employees.py
```

## Step 3: 验证结果

### 检查输出文件

打开 `summary.xlsx`，应该看到类似：

| 部门 | 人数 | 平均薪资 |
|------|------|----------|
| 技术部 | 120 | 16500.00 |
| 市场部 | 80 | 13200.00 |
| 人事部 | 50 | 11000.00 |
| ... | ... | ... |

### 验证数据准确性

1. **抽样检查**：随机选几个部门，手动在原文件中计算验证
2. **总数核对**：人数总和应该等于（或略小于）原文件行数
3. **逻辑检验**：平均薪资是否在合理范围内

## 常见问题解答

### Q1: 报错 "ModuleNotFoundError: No module named 'pandas'"

**解决方案**：
```bash
pip install pandas openpyxl
```

### Q2: 报错 "FileNotFoundError"

**可能原因**：
- 文件名拼写错误
- 文件不在当前目录

**解决方案**：
- 检查文件名是否正确（包括后缀 .xlsx）
- 使用完整路径：`pd.read_excel('C:/完整路径/employees.xlsx')`

### Q3: 报错 "KeyError: '列名'"

**可能原因**：Excel中的列名与代码不匹配

**解决方案**：
1. 打开Excel确认实际列名
2. 告诉AI正确的列名，让它重新生成代码

### Q4: 日期转换报错

**可能原因**：日期格式比预期的更复杂

**解决方案**：
告诉AI具体的日期样例：
```
日期列的实际样例：
- 2024-01-15
- 1/15/2024
- 2024年1月15日
- Jan 15, 2024

请处理所有这些格式。
```

### Q5: 结果数据有问题

**排查步骤**：
1. 检查原始数据是否有异常值
2. 让AI添加数据验证代码
3. 分步骤处理，每步都输出中间结果

## 提示词模板库

### 数据清洗

```
请帮我写一个Python脚本处理Excel文件：

文件：[文件名]
需要清洗的问题：
1. [具体问题1，如：删除重复行]
2. [具体问题2，如：填充空值]
3. [具体问题3，如：统一格式]

样例数据：
[粘贴2-3行]
```

### 数据筛选

```
我需要从Excel中筛选数据：

文件：[文件名]
筛选条件：
- [条件1，如：部门等于"技术部"]
- [条件2，如：薪资大于10000]
- [条件3，如：入职日期在2024年]

输出：筛选结果保存到新文件
```

### 多表合并

```
我需要合并多个Excel文件：

文件列表：
- file1.xlsx（列：A, B, C）
- file2.xlsx（列：A, B, D）

合并方式：[按A列关联/纵向堆叠]
输出：merged.xlsx
```

### 数据透视

```
请帮我创建数据透视表：

源文件：[文件名]
行：[字段名]
列：[字段名]
值：[字段名]（计算方式：[求和/平均/计数]）

输出为Excel文件。
```

## 进阶技巧

### 保留原始数据

在处理前先备份：
```python
# 在代码开头添加
import shutil
shutil.copy('employees.xlsx', 'employees_backup.xlsx')
```

### 添加处理日志

```python
# 在每个步骤后添加
print(f"原始行数: {len(df_original)}")
print(f"去重后行数: {len(df)}")
print(f"删除了 {len(df_original) - len(df)} 行重复数据")
```

### 处理大文件

对于超大文件（>10万行），让AI生成分块处理的代码：
```
文件很大（约50万行），请分块读取和处理，避免内存问题。
```

## 下一步

- **更多工作流** → [报告生成工作流](./reporting)
- **代码片段** → [数据处理片段](/docs/snippets/data-processing)
- **深入学习** → [Stage 2: 上下文与架构](/docs/roadmap/stage2)

---

**提示**：遇到问题时，把错误信息完整地发给AI，它能帮你定位和修复问题。
