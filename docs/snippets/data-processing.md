---
sidebar_position: 3
title: "数据处理片段"
description: "CSV/Excel读写、数据清洗、格式转换的即用代码片段"
keywords: [数据处理, CSV, Excel, pandas, Python, 数据清洗]
---

# 数据处理片段

这里收集了常用的数据处理代码片段，专门用于处理Excel、CSV等表格数据。

## 准备工作

运行这些代码前，需要安装pandas库：

```bash
pip install pandas openpyxl xlrd
```

## 读取数据

### 读取Excel文件

```python
import pandas as pd

# 基础读取
df = pd.read_excel('文件名.xlsx')

# 读取指定工作表
df = pd.read_excel('文件名.xlsx', sheet_name='Sheet1')

# 读取所有工作表
all_sheets = pd.read_excel('文件名.xlsx', sheet_name=None)
# 返回字典：{'Sheet1': df1, 'Sheet2': df2, ...}

# 跳过前几行
df = pd.read_excel('文件名.xlsx', skiprows=2)

# 指定列名
df = pd.read_excel('文件名.xlsx', names=['列1', '列2', '列3'])
```

### 读取CSV文件

```python
import pandas as pd

# 基础读取
df = pd.read_csv('文件名.csv')

# 指定编码（中文常用gbk或utf-8）
df = pd.read_csv('文件名.csv', encoding='gbk')
# 或
df = pd.read_csv('文件名.csv', encoding='utf-8')

# 指定分隔符（制表符分隔）
df = pd.read_csv('文件名.txt', sep='\t')

# 没有表头
df = pd.read_csv('文件名.csv', header=None)
```

### 读取多个文件并合并

```python
import pandas as pd
import os

# 配置区
folder_path = 'C:/数据文件夹'
file_pattern = '.xlsx'  # 文件类型

# 读取所有文件
all_data = []
for filename in os.listdir(folder_path):
    if filename.endswith(file_pattern):
        file_path = os.path.join(folder_path, filename)
        df = pd.read_excel(file_path)
        df['来源文件'] = filename  # 标记来源
        all_data.append(df)

# 合并
combined_df = pd.concat(all_data, ignore_index=True)
print(f"合并完成，共 {len(combined_df)} 行")
```

## 数据清洗

### 删除重复行

```python
import pandas as pd

df = pd.read_excel('数据.xlsx')

# 删除完全重复的行
df_clean = df.drop_duplicates()

# 基于特定列去重（保留第一次出现的）
df_clean = df.drop_duplicates(subset=['姓名', '身份证号'])

# 保留最后一次出现的
df_clean = df.drop_duplicates(subset=['姓名'], keep='last')

print(f"原始行数: {len(df)}, 去重后: {len(df_clean)}")
```

### 处理空值

```python
import pandas as pd

df = pd.read_excel('数据.xlsx')

# 查看空值情况
print(df.isnull().sum())

# 删除包含空值的行
df_clean = df.dropna()

# 删除特定列为空的行
df_clean = df.dropna(subset=['姓名', '电话'])

# 填充空值
df['薪资'] = df['薪资'].fillna(0)  # 用0填充
df['部门'] = df['部门'].fillna('未分配')  # 用固定值填充
df['年龄'] = df['年龄'].fillna(df['年龄'].mean())  # 用平均值填充
```

### 数据类型转换

```python
import pandas as pd

df = pd.read_excel('数据.xlsx')

# 转换为数字
df['金额'] = pd.to_numeric(df['金额'], errors='coerce')  # 无法转换的变为NaN

# 转换为日期
df['日期'] = pd.to_datetime(df['日期'], errors='coerce')

# 转换为字符串
df['编号'] = df['编号'].astype(str)

# 格式化日期
df['日期字符串'] = df['日期'].dt.strftime('%Y-%m-%d')
```

### 文本清洗

```python
import pandas as pd

df = pd.read_excel('数据.xlsx')

# 去除空格
df['姓名'] = df['姓名'].str.strip()  # 去除首尾空格
df['地址'] = df['地址'].str.replace(' ', '')  # 去除所有空格

# 统一大小写
df['邮箱'] = df['邮箱'].str.lower()
df['代码'] = df['代码'].str.upper()

# 替换文本
df['状态'] = df['状态'].str.replace('已完成', '完成')
df['状态'] = df['状态'].str.replace('未完成', '待处理')

# 提取部分文本
df['区号'] = df['电话'].str[:3]  # 前3位
df['手机后四位'] = df['手机'].str[-4:]  # 后4位
```

## 数据筛选

### 条件筛选

```python
import pandas as pd

df = pd.read_excel('数据.xlsx')

# 单条件筛选
result = df[df['部门'] == '技术部']
result = df[df['薪资'] > 10000]
result = df[df['状态'] != '已离职']

# 多条件筛选（且）
result = df[(df['部门'] == '技术部') & (df['薪资'] > 10000)]

# 多条件筛选（或）
result = df[(df['部门'] == '技术部') | (df['部门'] == '产品部')]

# 包含筛选
result = df[df['部门'].isin(['技术部', '产品部', '设计部'])]

# 文本包含
result = df[df['姓名'].str.contains('张')]
result = df[df['地址'].str.contains('北京|上海')]  # 包含北京或上海
```

### 日期筛选

```python
import pandas as pd

df = pd.read_excel('数据.xlsx')
df['入职日期'] = pd.to_datetime(df['入职日期'])

# 筛选特定日期之后
result = df[df['入职日期'] >= '2024-01-01']

# 筛选日期范围
result = df[(df['入职日期'] >= '2024-01-01') & (df['入职日期'] <= '2024-03-31')]

# 筛选特定年份/月份
result = df[df['入职日期'].dt.year == 2024]
result = df[df['入职日期'].dt.month == 1]
```

## 数据汇总

### 分组统计

```python
import pandas as pd

df = pd.read_excel('数据.xlsx')

# 按单列分组计数
result = df.groupby('部门').size().reset_index(name='人数')

# 按单列分组求和
result = df.groupby('部门')['薪资'].sum().reset_index(name='薪资总额')

# 多种聚合
result = df.groupby('部门').agg({
    '姓名': 'count',      # 计数
    '薪资': ['mean', 'sum', 'max', 'min']  # 多种计算
}).reset_index()

# 重命名列
result = df.groupby('部门').agg({
    '姓名': 'count',
    '薪资': 'mean'
}).rename(columns={
    '姓名': '人数',
    '薪资': '平均薪资'
}).reset_index()
```

### 透视表

```python
import pandas as pd

df = pd.read_excel('销售数据.xlsx')

# 创建透视表
pivot = pd.pivot_table(
    df,
    values='销售额',        # 值
    index='产品',           # 行
    columns='月份',         # 列
    aggfunc='sum',          # 聚合方式
    fill_value=0            # 空值填充
)

print(pivot)
```

### 交叉表

```python
import pandas as pd

df = pd.read_excel('数据.xlsx')

# 计数交叉表
cross = pd.crosstab(df['部门'], df['职级'])

# 带汇总行列
cross = pd.crosstab(df['部门'], df['职级'], margins=True, margins_name='合计')

print(cross)
```

## 数据合并

### 横向合并（关联）

```python
import pandas as pd

# 读取两个表
df1 = pd.read_excel('员工表.xlsx')  # 包含：员工ID, 姓名, 部门ID
df2 = pd.read_excel('部门表.xlsx')  # 包含：部门ID, 部门名称

# 左连接（保留左表所有行）
result = pd.merge(df1, df2, on='部门ID', how='left')

# 内连接（只保留匹配的行）
result = pd.merge(df1, df2, on='部门ID', how='inner')

# 不同列名关联
result = pd.merge(df1, df2, left_on='部门编号', right_on='部门ID', how='left')
```

### 纵向合并（追加）

```python
import pandas as pd

df1 = pd.read_excel('1月数据.xlsx')
df2 = pd.read_excel('2月数据.xlsx')
df3 = pd.read_excel('3月数据.xlsx')

# 纵向合并
result = pd.concat([df1, df2, df3], ignore_index=True)

# 只合并共同列
result = pd.concat([df1, df2, df3], ignore_index=True, join='inner')
```

## 保存数据

### 保存为Excel

```python
import pandas as pd

# 基础保存
df.to_excel('输出.xlsx', index=False)

# 保存到指定工作表
df.to_excel('输出.xlsx', sheet_name='数据', index=False)

# 保存多个工作表
with pd.ExcelWriter('输出.xlsx') as writer:
    df1.to_excel(writer, sheet_name='汇总', index=False)
    df2.to_excel(writer, sheet_name='明细', index=False)
```

### 保存为CSV

```python
import pandas as pd

# 基础保存
df.to_csv('输出.csv', index=False)

# 指定编码
df.to_csv('输出.csv', index=False, encoding='utf-8-sig')  # Excel兼容的UTF-8

# GBK编码（适合Excel打开）
df.to_csv('输出.csv', index=False, encoding='gbk')
```

## 实用组合示例

### 示例1：销售数据月度汇总

```python
import pandas as pd

# 读取数据
df = pd.read_excel('销售明细.xlsx')

# 转换日期
df['日期'] = pd.to_datetime(df['日期'])
df['年月'] = df['日期'].dt.strftime('%Y-%m')

# 按月汇总
monthly = df.groupby('年月').agg({
    '订单号': 'count',
    '销售额': 'sum',
    '利润': 'sum'
}).rename(columns={
    '订单号': '订单数',
    '销售额': '销售总额',
    '利润': '利润总额'
}).reset_index()

# 计算利润率
monthly['利润率'] = (monthly['利润总额'] / monthly['销售总额'] * 100).round(2)

# 保存
monthly.to_excel('月度汇总.xlsx', index=False)
print(monthly)
```

### 示例2：员工数据清洗

```python
import pandas as pd

# 读取数据
df = pd.read_excel('员工原始数据.xlsx')

print(f"原始数据: {len(df)} 行")

# 1. 去除重复
df = df.drop_duplicates(subset=['身份证号'])
print(f"去重后: {len(df)} 行")

# 2. 处理空值
df = df.dropna(subset=['姓名', '身份证号'])  # 必填字段不能为空
df['电话'] = df['电话'].fillna('未填写')

# 3. 文本清洗
df['姓名'] = df['姓名'].str.strip()
df['部门'] = df['部门'].str.strip()

# 4. 数据标准化
df['性别'] = df['性别'].replace({'男性': '男', '女性': '女', 'M': '男', 'F': '女'})

# 5. 日期格式统一
df['入职日期'] = pd.to_datetime(df['入职日期'], errors='coerce')
df['入职日期'] = df['入职日期'].dt.strftime('%Y-%m-%d')

# 保存
df.to_excel('员工清洗后.xlsx', index=False)
print(f"清洗完成，保存 {len(df)} 行")
```

### 示例3：多表对账

```python
import pandas as pd

# 读取两份数据
df_system = pd.read_excel('系统数据.xlsx')  # 系统导出
df_bank = pd.read_excel('银行数据.xlsx')    # 银行流水

# 标准化订单号格式
df_system['订单号'] = df_system['订单号'].astype(str).str.strip()
df_bank['订单号'] = df_bank['订单号'].astype(str).str.strip()

# 找出系统有、银行没有的记录
system_only = df_system[~df_system['订单号'].isin(df_bank['订单号'])]

# 找出银行有、系统没有的记录
bank_only = df_bank[~df_bank['订单号'].isin(df_system['订单号'])]

# 找出金额不一致的记录
merged = pd.merge(df_system, df_bank, on='订单号', suffixes=('_系统', '_银行'))
amount_diff = merged[merged['金额_系统'] != merged['金额_银行']]

# 保存对账结果
with pd.ExcelWriter('对账结果.xlsx') as writer:
    system_only.to_excel(writer, sheet_name='系统有银行无', index=False)
    bank_only.to_excel(writer, sheet_name='银行有系统无', index=False)
    amount_diff.to_excel(writer, sheet_name='金额不一致', index=False)

print(f"系统有银行无: {len(system_only)} 条")
print(f"银行有系统无: {len(bank_only)} 条")
print(f"金额不一致: {len(amount_diff)} 条")
```

## 下一步

- **文件操作** → [文件操作片段](./file-operations)
- **API请求** → [API请求片段](./api-request)
- **完整工作流** → [Excel处理工作流](/docs/workflows/excel)

---

**提示**：pandas功能强大，遇到更复杂的需求，把需求描述给AI，让它帮你写代码。
