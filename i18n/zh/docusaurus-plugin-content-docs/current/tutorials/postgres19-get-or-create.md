---
title: "PostgreSQL 去重与回查：用事务验证 email 报名编号"
description: "在 PostgreSQL 19 中实测同一邮箱重复报名，对照 DO SELECT 和 DO NOTHING 的返回值，验证已有报名编号和姓名。"
tags: ["tutorial", "postgresql", "sql"]
---

# PostgreSQL 去重与回查：用事务验证 email 报名编号

## 目标场景
用户通过表单提交报名。同一邮箱被多次提交：
- 第一次：需要返回该邮箱对应的报名编号（id）。
- 第二次及以后：需要拿到“第一次”的 id，而不是覆盖它。

下面的 SQL 以 `psql` 会话内、PostgreSQL 19 的临时表为例，演示“插入时冲突如何处理 + 如何拿回原值/返回行数”。

## 完整可运行的 psql 脚本

```sql
BEGIN;
CREATE TEMP TABLE signup (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email text UNIQUE NOT NULL,
  display_name text NOT NULL
);
INSERT INTO signup (email, display_name) VALUES ('reader@example.test', 'First')
ON CONFLICT (email) DO SELECT RETURNING id, display_name;
INSERT INTO signup (email, display_name) VALUES ('reader@example.test', 'Retry')
ON CONFLICT (email) DO SELECT RETURNING id, display_name;
INSERT INTO signup (email, display_name) VALUES ('reader@example.test', 'Retry')
ON CONFLICT (email) DO NOTHING RETURNING id, display_name;
SELECT count(*) AS stored_rows FROM signup;
ROLLBACK;
```

## 期望结果与判读

假设你在 `psql` 中逐条执行，典型输出如下：

1. 第一次 INSERT（创建记录）
   - 返回：一行 `id = 1, display_name = 'First'`
   - 含义：邮箱不存在，成功插入第一条报名。

2. 第二次 INSERT（重试，带 DO SELECT）
   - 返回：一行 `id = 1, display_name = 'First'`
   - 含义：
     - `email` 已存在 → 触发冲突；
     - `DO SELECT` 执行“冲突分支”，但没有修改任何列；
     - `RETURNING` 拿到的是表中已有行（id=1），证明“不是覆盖，而是回查”。

3. 第三次 INSERT（重试，带 DO NOTHING + RETURNING）
   - 返回：零行（或 `(0 rows)`）
   - 含义：
     - 冲突再次发生；
     - `DO NOTHING` 什么都不做，不插入也不更新；
     - `RETURNING` 在此场景下没有产生行，用于确认“确实没插进去”。

4. 查询计数
   - `SELECT count(*) AS stored_rows FROM signup;`
   - 返回：`stored_rows = 1`

- 执行 `ROLLBACK` 后，整个 `BEGIN` 到 `ROLLBACK` 范围内的 DDL 和 DML 全部撤销；
- `signup` 临时表消失；
