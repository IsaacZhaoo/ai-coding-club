---
sidebar_position: 3
title: "File Operation Snippets"
description: "Small Python snippets for renaming, moving, finding, and organizing files."
keywords: [file operations, Python, rename files, organize files]
---

# File Operation Snippets

These snippets help automate common file tasks. Test on a copy of the folder first.

## List Files In A Folder

~~~python
from pathlib import Path

folder = Path("files")
for path in folder.iterdir():
    if path.is_file():
        print(path.name)
~~~

## Rename Files With A Prefix

~~~python
from pathlib import Path

folder = Path("files")
prefix = "project_"

for path in folder.iterdir():
    if path.is_file():
        new_path = path.with_name(prefix + path.name)
        path.rename(new_path)
~~~

## Replace Text In File Names

~~~python
from pathlib import Path

folder = Path("files")
old_text = "draft"
new_text = "final"

for path in folder.iterdir():
    if path.is_file() and old_text in path.name:
        path.rename(path.with_name(path.name.replace(old_text, new_text)))
~~~

## Move Files By Extension

~~~python
from pathlib import Path
import shutil

source = Path("downloads")
target_root = Path("organized")

for path in source.iterdir():
    if not path.is_file():
        continue

    extension = path.suffix.lower().lstrip(".") or "no_extension"
    target_dir = target_root / extension
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(path), target_dir / path.name)
~~~

## Find Large Files

~~~python
from pathlib import Path

folder = Path("files")
min_size_mb = 50

for path in folder.rglob("*"):
    if path.is_file() and path.stat().st_size > min_size_mb * 1024 * 1024:
        print(path, round(path.stat().st_size / 1024 / 1024, 1), "MB")
~~~

## Safety Prompt

~~~text
Review this file operation script before I run it.
Tell me which lines rename, move, overwrite, or delete files.
Suggest a dry-run mode that prints actions without changing files.
~~~
