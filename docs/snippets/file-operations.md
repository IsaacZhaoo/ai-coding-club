---
sidebar_position: 2
title: "文件操作片段"
description: "批量重命名、格式转换、文件整理的即用代码片段"
keywords: [文件操作, 批量重命名, Python, 文件管理, 自动化]
---

# 文件操作片段

这里收集了常用的文件操作代码片段，可以直接复制使用或让AI帮你修改。

## 批量重命名文件

### 添加前缀

**场景**：给文件夹中所有文件添加日期前缀

```python
import os
from datetime import datetime

# 配置区 - 修改这里
folder_path = "C:/你的文件夹"  # 文件夹路径
prefix = datetime.now().strftime("%Y%m%d_")  # 前缀，例如 20240115_

# 执行重命名
for filename in os.listdir(folder_path):
    old_path = os.path.join(folder_path, filename)
    if os.path.isfile(old_path):
        new_name = prefix + filename
        new_path = os.path.join(folder_path, new_name)
        os.rename(old_path, new_path)
        print(f"重命名: {filename} → {new_name}")

print("完成！")
```

### 替换文件名中的文字

**场景**：把所有文件名中的"旧项目"替换为"新项目"

```python
import os

# 配置区
folder_path = "C:/你的文件夹"
old_text = "旧项目"  # 要替换的文字
new_text = "新项目"  # 替换成的文字

# 执行替换
for filename in os.listdir(folder_path):
    if old_text in filename:
        old_path = os.path.join(folder_path, filename)
        new_name = filename.replace(old_text, new_text)
        new_path = os.path.join(folder_path, new_name)
        os.rename(old_path, new_path)
        print(f"重命名: {filename} → {new_name}")

print("完成！")
```

### 按序号重命名

**场景**：把文件重命名为 001、002、003...

```python
import os

# 配置区
folder_path = "C:/你的文件夹"
prefix = "文档"  # 前缀
start_number = 1  # 起始序号

# 获取文件并排序
files = [f for f in os.listdir(folder_path)
         if os.path.isfile(os.path.join(folder_path, f))]
files.sort()

# 执行重命名
for i, filename in enumerate(files, start=start_number):
    old_path = os.path.join(folder_path, filename)
    ext = os.path.splitext(filename)[1]  # 保留扩展名
    new_name = f"{prefix}_{i:03d}{ext}"  # 003格式
    new_path = os.path.join(folder_path, new_name)
    os.rename(old_path, new_path)
    print(f"重命名: {filename} → {new_name}")

print("完成！")
```

## 文件整理

### 按扩展名分类

**场景**：把文件夹中的文件按类型分到不同子文件夹

```python
import os
import shutil

# 配置区
source_folder = "C:/待整理文件夹"

# 文件类型分类规则
categories = {
    "文档": [".doc", ".docx", ".pdf", ".txt", ".xlsx", ".pptx"],
    "图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "视频": [".mp4", ".avi", ".mov", ".mkv"],
    "音频": [".mp3", ".wav", ".flac"],
    "压缩包": [".zip", ".rar", ".7z"],
}

# 执行分类
for filename in os.listdir(source_folder):
    file_path = os.path.join(source_folder, filename)

    if os.path.isfile(file_path):
        ext = os.path.splitext(filename)[1].lower()

        # 找到对应分类
        target_folder = "其他"
        for category, extensions in categories.items():
            if ext in extensions:
                target_folder = category
                break

        # 创建目标文件夹并移动
        dest_folder = os.path.join(source_folder, target_folder)
        os.makedirs(dest_folder, exist_ok=True)

        dest_path = os.path.join(dest_folder, filename)
        shutil.move(file_path, dest_path)
        print(f"移动: {filename} → {target_folder}/")

print("整理完成！")
```

### 按日期整理照片

**场景**：把照片按拍摄年月整理到文件夹

```python
import os
import shutil
from datetime import datetime

# 配置区
photo_folder = "C:/照片文件夹"

for filename in os.listdir(photo_folder):
    file_path = os.path.join(photo_folder, filename)

    if os.path.isfile(file_path):
        # 获取文件修改时间
        mtime = os.path.getmtime(file_path)
        date = datetime.fromtimestamp(mtime)

        # 创建年月文件夹
        year_month = date.strftime("%Y-%m")
        dest_folder = os.path.join(photo_folder, year_month)
        os.makedirs(dest_folder, exist_ok=True)

        # 移动文件
        dest_path = os.path.join(dest_folder, filename)
        if not os.path.exists(dest_path):
            shutil.move(file_path, dest_path)
            print(f"移动: {filename} → {year_month}/")

print("整理完成！")
```

## 文件搜索

### 查找特定文件

**场景**：在文件夹及子文件夹中查找包含特定关键词的文件

```python
import os

# 配置区
search_folder = "C:/搜索文件夹"
keyword = "报告"  # 搜索关键词
extensions = [".doc", ".docx", ".pdf"]  # 限定文件类型，留空搜索所有

results = []

for root, dirs, files in os.walk(search_folder):
    for filename in files:
        # 检查文件名是否包含关键词
        if keyword.lower() in filename.lower():
            # 检查扩展名
            ext = os.path.splitext(filename)[1].lower()
            if not extensions or ext in extensions:
                full_path = os.path.join(root, filename)
                results.append(full_path)

# 输出结果
print(f"找到 {len(results)} 个文件：\n")
for path in results:
    print(path)
```

### 查找大文件

**场景**：找出文件夹中最大的10个文件

```python
import os

# 配置区
search_folder = "C:/搜索文件夹"
top_n = 10  # 显示前N个

# 收集所有文件及大小
files_with_size = []

for root, dirs, files in os.walk(search_folder):
    for filename in files:
        file_path = os.path.join(root, filename)
        try:
            size = os.path.getsize(file_path)
            files_with_size.append((file_path, size))
        except:
            pass

# 排序并显示
files_with_size.sort(key=lambda x: x[1], reverse=True)

print(f"最大的 {top_n} 个文件：\n")
for path, size in files_with_size[:top_n]:
    size_mb = size / (1024 * 1024)
    print(f"{size_mb:.2f} MB - {path}")
```

### 查找重复文件

**场景**：根据文件大小和名称查找可能的重复文件

```python
import os
from collections import defaultdict

# 配置区
search_folder = "C:/搜索文件夹"

# 按文件大小分组
size_groups = defaultdict(list)

for root, dirs, files in os.walk(search_folder):
    for filename in files:
        file_path = os.path.join(root, filename)
        try:
            size = os.path.getsize(file_path)
            size_groups[size].append(file_path)
        except:
            pass

# 找出大小相同的文件
duplicates = []
for size, paths in size_groups.items():
    if len(paths) > 1:
        duplicates.append((size, paths))

# 输出结果
print("可能的重复文件：\n")
for size, paths in sorted(duplicates, key=lambda x: x[0], reverse=True):
    size_mb = size / (1024 * 1024)
    print(f"\n大小: {size_mb:.2f} MB")
    for path in paths:
        print(f"  - {path}")
```

## 文件转换

### 批量转换图片格式

**场景**：把PNG图片批量转换为JPG

```python
from PIL import Image
import os

# 配置区
source_folder = "C:/原图片文件夹"
output_folder = "C:/转换后文件夹"
source_format = ".png"
target_format = ".jpg"
quality = 85  # JPG质量（1-100）

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(source_folder):
    if filename.lower().endswith(source_format):
        # 读取图片
        source_path = os.path.join(source_folder, filename)
        img = Image.open(source_path)

        # 如果是PNG转JPG，需要处理透明通道
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        # 保存
        new_name = os.path.splitext(filename)[0] + target_format
        output_path = os.path.join(output_folder, new_name)
        img.save(output_path, quality=quality)

        print(f"转换: {filename} → {new_name}")

print("转换完成！")
```

**运行前需要安装**：
```bash
pip install Pillow
```

### 批量压缩图片

**场景**：压缩文件夹中所有图片以减小体积

```python
from PIL import Image
import os

# 配置区
source_folder = "C:/原图片文件夹"
output_folder = "C:/压缩后文件夹"
max_width = 1920  # 最大宽度
max_height = 1080  # 最大高度
quality = 80  # 压缩质量

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(source_folder):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        source_path = os.path.join(source_folder, filename)
        img = Image.open(source_path)

        # 计算新尺寸
        ratio = min(max_width/img.width, max_height/img.height, 1)
        new_size = (int(img.width * ratio), int(img.height * ratio))

        # 调整大小
        if ratio < 1:
            img = img.resize(new_size, Image.LANCZOS)

        # 保存
        output_path = os.path.join(output_folder, filename)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        img.save(output_path, quality=quality, optimize=True)

        # 显示压缩效果
        old_size = os.path.getsize(source_path) / 1024
        new_size = os.path.getsize(output_path) / 1024
        print(f"{filename}: {old_size:.1f}KB → {new_size:.1f}KB ({new_size/old_size*100:.1f}%)")

print("压缩完成！")
```

## 文件备份

### 增量备份

**场景**：只备份新增或修改过的文件

```python
import os
import shutil
from datetime import datetime

# 配置区
source_folder = "C:/源文件夹"
backup_folder = "C:/备份文件夹"

# 创建带时间戳的备份文件夹
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
current_backup = os.path.join(backup_folder, f"backup_{timestamp}")

copied_count = 0

for root, dirs, files in os.walk(source_folder):
    for filename in files:
        source_path = os.path.join(root, filename)

        # 计算相对路径
        rel_path = os.path.relpath(source_path, source_folder)
        backup_path = os.path.join(current_backup, rel_path)

        # 检查是否需要备份（目标不存在或源更新）
        need_backup = True
        if os.path.exists(backup_path):
            source_mtime = os.path.getmtime(source_path)
            backup_mtime = os.path.getmtime(backup_path)
            if source_mtime <= backup_mtime:
                need_backup = False

        if need_backup:
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(source_path, backup_path)
            copied_count += 1
            print(f"备份: {rel_path}")

print(f"\n完成！共备份 {copied_count} 个文件")
```

## 使用技巧

### 安全建议

1. **先测试**：在正式使用前，先在测试文件夹试运行
2. **备份原文件**：操作前备份重要文件
3. **打印预览**：可以先注释掉实际操作代码，只看打印输出

### 修改代码让AI帮忙

**如果需要修改功能**：

```
这段代码的功能是[描述当前功能]。

我想修改为[描述你想要的功能]。

原代码：
[粘贴代码]

请帮我修改。
```

### 常见错误处理

**权限错误**：
```
确保你有文件夹的读写权限，或以管理员身份运行
```

**文件占用**：
```
关闭正在使用这些文件的程序
```

**路径错误**：
```
使用正斜杠 / 或双反斜杠 \\
例如: "C:/文件夹" 或 "C:\\文件夹"
```

## 下一步

- **数据处理** → [数据处理片段](../data-processing/)
- **API请求** → [API请求片段](../api-request/)
- **完整工作流** → [Excel处理工作流](/docs/workflows/excel)

---

**提示**：这些代码片段可以组合使用。如果需要更复杂的功能，把需求描述给AI，让它帮你组合和修改。
