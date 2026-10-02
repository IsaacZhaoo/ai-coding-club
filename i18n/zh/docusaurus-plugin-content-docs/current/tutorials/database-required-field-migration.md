---
title: "让 AI 协助给 PostgreSQL 已有数据表增加必填字段：兼顾存量数据与发布中的旧应用"
sidebar_label: "PostgreSQL 必填字段迁移"
description: "让 AI 协助为 PostgreSQL 18 已有数据表增加必填字段，分阶段处理旧应用兼容、存量回填、约束验收与回滚。"
keywords: ["PostgreSQL 18", "database migration", "NOT NULL", "AI coding agent"]
sidebar_position: 46
tags: ["tutorial", "agent-engineering"]
---

# 让 AI 协助给 PostgreSQL 已有数据表增加必填字段：兼顾存量数据与发布中的旧应用

目标很明确——读者拿到这套分阶段迁移任务后，能按序完成写入规则收敛、存量回填与 NULL 清零、约束验收与发布节奏控制。

---

## 一、场景与核心问题

假设你有一个 PostgreSQL 18 上的普通表 `customers`：

- 已有字段：
  - `id bigint PRIMARY KEY`
  - `email text NOT NULL`
- 业务现在要求新增一个业务字段：
  - `billing_email text`，未来必须非空（NOT NULL）

核心痛点包括：

1. **存量数据没有值**  
   历史记录的 `billing_email` 是 NULL（或不存在）。需要决定一套合理的初值回填策略。

2. **应用升级是滚动的**  
   - 旧版应用仍在运行，它们对新字段要么省略，要么写 NULL。
   - 新版本应用已经上线，可以正确写入非空值。
   - 不能指望“一刀切”停掉所有旧进程再动表结构。

3. **约束收紧时机敏感**  
   - 过早加 NOT NULL / CHECK → 旧写入路径报错，发布受阻。
   - 过晚收紧 → 脏数据残留、审计困难、规则被长期绕过。

理想结果：

- 新增业务字段 `billing_email`；
- 存量记录回填当时 email（或业务指定的默认值）；
- 所有写入路径收敛后，安全收紧为 NOT NULL；
- 对旧进程发布最小干扰，对数据一致性有明确验收标准。

---

## 二、总体策略：从“可空”到“必填”的四阶段路线

下面这个流程适合大多数非分区表场景，也便于 AI 生成具体脚本。你可以把以下四个阶段作为 Prompt 中的“任务骨架”，让 AI 为你填充细节。

### 何时可以直接用带 DEFAULT 的非空列？
如果你确定业务需求里，“每条旧记录在逻辑上都应等同于这个默认值”，那没必要分阶段：  
- 直接加一列：ALTER TABLE support_tickets ADD COLUMN status TEXT NOT NULL DEFAULT 'open';  

关键点在于常量 DEFAULT（如 'open'）：  
- 不会触发逐行物理更新，适合批量场景。  
- DDL 仍会加锁，所以要在低峰期执行。

### 阶段一：加列（仍可为 NULL）

目标：

- 让旧应用在这一阶段仍可省略该字段；
- 新应用开始写入非空值；
- 为存量 NULL 数据建立一个“统一初值”的入口。

关键规则：

- 列定义为 `text`，不立即加 NOT NULL / CHECK。
- 已有非空值保留，除非业务明确要求重写。
- 回填策略由业务决定，示例中约定：
  - 若 `billing_email` 为 NULL，则初值 = 当时的 `email`。

典型 DDL（可交给 AI 根据实际表结构调整）：

```sql
ALTER TABLE customers ADD COLUMN billing_email text;
```

AI 提示要点（可作为 Prompt 片段）：

> “在 PostgreSQL 18 上给 customers 表增加 billing_email 列，初始可为 NULL。不要加 CHECK / NOT NULL。保留已有非空值。”

### 阶段二：应用侧兼容与写入收敛

目标：

- 识别所有可能“省略”或“写 NULL”的写入路径：
  - 应用 INSERT / UPDATE
  - 批处理脚本、定时任务、ETL 工具
  - 导入/导出、数据迁移脚本
  - ORM/ActiveRecord 层面的默认值与回调
- 对每条路径：
  - 要么升级成显式写入非空值；
  - 要么在代码中加入兼容层（如回退到 email）。

常见坑点提醒（AI 应负责在 Code Review 中标记）：

- `DEFAULT` 不能引用同一行的其他列，比如：
  - `DEFAULT email` 在语法上是非法的。
- 普通 `DEFAULT 'xxx'` 对省略该字段的 INSERT 生效；
  - 显式写入 `NULL` 仍是 NULL，不触发 DEFAULT。
- ActiveRecord 等 ORM 回调在某些批量接口中可能不被调用，
  - 需要检查底层的 SQL / 原生查询路径。

AI 提示要点：

> “列出 customers.billing_email 的所有潜在写入路径（应用层、脚本、批处理、导入），并为每条路径给出具体的修改建议或兼容层写法。”

### 阶段三：回填存量 NULL（在写入者收敛后）

目标：

- 在“所有能写进数据的渠道”都升级到位后，对存量 NULL 进行统一回填；
- 使用分批更新，避免锁表过久、减少并发冲突；
- 每次更新只影响 `billing_email IS NULL` 的行。

示例回填逻辑（PostgreSQL 18）：

```sql
WITH batch AS (
  SELECT id
  FROM customers
  WHERE billing_email IS NULL
  ORDER BY id
  LIMIT 1000
  FOR UPDATE
)
UPDATE customers AS c
SET billing_email = c.email
FROM batch AS b
WHERE c.id = b.id AND c.billing_email IS NULL;
```

验收循环：

```sql
SELECT count(*) AS remaining
FROM customers
WHERE billing_email IS NULL;
```

执行策略建议：

- 每批独立提交，而不是放在一个大事务中；
- 若 `remaining > 0`，则继续下一批；
- 可按负载加节流（例如每批间隔 200–500ms），避免瞬间压力过大。

回填规则要点（AI 应帮你确认）：

- 目标 SQL 必须带 `WHERE billing_email IS NULL`，保护已有业务值；


AI 提示要点：

> “给出一个可重复执行的批处理回填脚本，支持 LIMIT / FOR UPDATE / 独立提交，并加入剩余计数查询与循环退出条件。”

### 阶段四：约束收紧（从 CHECK 到 NOT NULL）
本章节在“所有业务写入者收敛且存量 NULL 已回填清零、旧进程/后台作业/导入也已升级或退场”的背景下执行。从这一刻起，数据库开始用约束验证新写数据，因此节奏与锁策略比之前更敏感。

- INSERT：必须给 billing_email 一个非空值，否则报错。  
- UPDATE：即使你只改了其他列，只要行上的 billing_email 还是 NULL，更新仍会失败。

我们提供两条等效路线，读者可按团队习惯择一：
1）CHECK + SET NOT NULL 路线（本文重点演示）
2）PostgreSQL 18 原生 NOT NULL 路线（更简洁，但同样需要 VALIDATE）

---
CHECK + SET NOT NULL 路线：
- 第一步：用 NOT VALID 先注册约束，跳过存量行扫描。
- 第二步：VALIDATE 才真正校验全表（此时流量应已收敛）。
- 第三步：将列提升为 NOT NULL。由于 CHECK 已证明“所有行都满足”，SET NOT NULL 几乎无额外扫描压力。
- 第四步：删除冗余 CHECK。注意：不能在 SET NOT NULL 同一命令中 DROP CHECK，必须分步执行。

锁的类型决定了你什么时候会被卡住：  
- ACCESS EXCLUSIVE（常用于加/改表结构）：几乎与所有读写操作冲突，包括普通 SELECT、INSERT、UPDATE，所以 VALIDATE 前若选了这种锁，业务会明显受阻。  
- SHARE UPDATE EXCLUSIVE（VALIDATE 阶段常用）：允许普通 SELECT、INSERT、UPDATE 同时发生，只和部分维护型 DDL（如创建索引、重定义表等）冲突。

关键锁与影响（务必看清）：
- ADD CONSTRAINT ... NOT VALID：ACCESS EXCLUSIVE（阻塞写入与多数 DDL），但无全表验证。
- VALIDATE CONSTRAINT：SHARE UPDATE EXCLUSIVE（可与普通读写共存，但仍可能与其他维护/DDL 冲突）。
- SET NOT NULL：ACCESS EXCLUSIVE（同样会阻塞写）。
- DROP CONSTRAINT：ACCESS EXCLUSIVE。
SET lock_timeout = '2s' 用于控制等待锁的上限；对应恢复命令是 RESET lock_timeout;。它限制的是“等锁时长”，不是查询总时间。若事务在显式提交内失败，应回滚该事务再排查；自动提交的单条语句失败，并不意味存在一个长外部事务。

示例 SQL（CHECK 路线）：
```sql
-- 1. 添加 CHECK NOT VALID：注册约束，跳过存量扫描
ALTER TABLE customers ADD CONSTRAINT customers_billing_email_present 
    CHECK (billing_email IS NOT NULL) NOT VALID;

-- 2. 验证约束：开始真正校验全表（此时应已收敛写入）
ALTER TABLE customers VALIDATE CONSTRAINT customers_billing_email_present;

-- 3. 提升为 NOT NULL：利用已有 CHECK 证明，SET NOT NULL 更轻量
ALTER TABLE customers ALTER COLUMN billing_email SET NOT NULL;

-- 4. 删除冗余 CHECK
ALTER TABLE customers DROP CONSTRAINT customers_billing_email_present;
```

原生 NOT NULL 路线（可替代）：
- PostgreSQL 18 允许直接在 ADD CONSTRAINT 中指定 NOT NULL，行为同样是“添加后对新写入生效”，随后用 VALIDATE 完成验证。这条路线无需 SET NOT NULL，也无需删除 CHECK（因为没有引入 CHECK）。

示例 SQL（原生路线）：
```sql
-- 1. 添加 NOT NULL NOT VALID：新数据立即受约束，存量暂不校验
ALTER TABLE customers ADD CONSTRAINT customers_billing_email_nn 
    NOT NULL billing_email NOT VALID;

-- 2. 验证约束
ALTER TABLE customers VALIDATE CONSTRAINT customers_billing_email_nn;
```

---

## 三、关键细节与最佳实践（让 AI 帮你自动化检查）

### 1. 回填与 schema 变更分开提交

- 回填脚本：多次独立 `UPDATE` + `SELECT`；
- DDL（加列/约束/NOT NULL）：尽量聚合在少数几条语句中，但不要在同一个超长大事务内完成“回填 + DDL”。

好处：

- 即使 DDL 失败，回填数据仍在；
- 回滚成本更低，运维更可控。

### 2. 使用 FOR UPDATE 的行锁保护批处理过程
当逐行回填或校验数据时，可用 FOR UPDATE 为选中行加锁，避免并发更新影响计算正确性：
要点澄清：
- LIMIT 1000 只是“最多选中 1000 行”，实际数量取决于符合 WHERE 条件的行数。
- 在 Read Committed 下，FOR UPDATE 会锁定选中行直至 COMMIT；每个事务提交后锁即释放，适合分批处理。
- 若提升到更高隔离级别（如 Repeatable Read / Serializable），可能遇到 serializable failure，需要应用层重试逻辑，不建议将其当作“无条件增强正确性”的手段。
- 本文整体已有并发方案（收敛写入 + 分阶段约束），此处仅说明批处理场景下如何安全加锁，避免过度强化为通用规则。



### 3. 验收指标不只是“NULL 数量 = 0”

约束收紧后的验收应包含：

1. **数据维度**
   - `billing_email IS NULL` 数量应为 0；
   - 已填充的行中，没有意外被改成空字符串/异常值（若业务有格式约束）；
   - 原有非空值完整保留。

2. **结构维度**
   - 列状态：`NOT NULL = true`；
   

3. **行为维度（最重要）**
   - 批处理脚本、导入工具在约束生效后的行为。

### 4. 暂停条件与回退预案
迁移并非线性推进，遇到以下情况应主动暂停：
- 存量中持续出现新的 NULL（说明有未知写入者或后台作业未收敛）。
- 执行 ACCESS EXCLUSIVE 相关语句时长时间等锁，且无法定位持有者。

在未收紧约束阶段：
- 可继续保留“允许 NULL”的列定义，快速回退应用逻辑或发布计划，降低影响面。

在已收紧约束之后：
- 若需回退，先解除数据库侧约束（DROP CONSTRAINT / ALTER ... DROP NOT NULL），保证数据库与旧写入者的兼容性。

```sql
-- CHECK 路线：辅助 CHECK 若仍存在，也需要移除；分开执行。
ALTER TABLE customers DROP CONSTRAINT IF EXISTS customers_billing_email_present;
ALTER TABLE customers ALTER COLUMN billing_email DROP NOT NULL;
```
- 再回退应用逻辑到不强制校验 billing_email 的状态，防止新旧规则冲突引发链路故障。

---

## 四、把这套流程交给 AI 的“任务卡”示例

如果你准备让 coding agent / LLM 生成可执行方案，可以把下面这段作为系统提示或任务描述：

> 角色：PostgreSQL 18 + 生产环境迁移顾问。
> 
> 目标：为表 customers 增加 billing_email 字段，从可空过渡到必填，兼顾存量数据回填和滚动发布中的旧应用。
> 
> 要求输出：
> 1) 分阶段迁移任务（阶段一～四），每阶段给出：
>    - 目标与验收标准
>    - 推荐 DDL / 回填 SQL
>    - 写入路径收敛清单（示例或检查表）
>    - 暂停条件与回退策略
> 2) 针对以下具体场景给出建议：
>    - 存量 billing_email 为 NULL，业务决定初值取当时的 email；
>    - 应用默认值/回调是否覆盖批处理、导入路径；
>    - PostgreSQL 18 的 NOT VALID → VALIDATE → SET NOT NULL 路线对比与推荐。
> 


---

## 五、一句话总结

给 PostgreSQL 已有表加必填字段，关键不在于“一条 ALTER TABLE”有多快，而在于：

- 在写入路径收敛前，允许可空；
- 用分批回填把存量 NULL 安全“洗”成业务认可的初值；
- 利用 NOT VALID / VALIDATE 机制最小化锁与回滚风险；
- 始终保留一个清晰的暂停/回退阶段，让发布节奏服务于数据质量，而不是反过来。

把上面的四阶段框架和验收标准交给 AI，它就能输出一份可审阅、可执行、且带风险提示的迁移方案；你只需要在每一步核对业务规则与锁等待情况，然后按“可控小步”推进即可。

## 参考资料

- [PostgreSQL 18: ALTER TABLE](https://www.postgresql.org/docs/18/sql-altertable.html)
- [PostgreSQL 18: Modifying Tables](https://www.postgresql.org/docs/18/ddl-alter.html)
- [PostgreSQL 18: CREATE TABLE](https://www.postgresql.org/docs/18/sql-createtable.html)
- [PostgreSQL 18: Explicit Locking](https://www.postgresql.org/docs/18/explicit-locking.html)
- [PostgreSQL 18: UPDATE](https://www.postgresql.org/docs/18/sql-update.html)
- [PostgreSQL 18: Client Connection Defaults](https://www.postgresql.org/docs/18/runtime-config-client.html)
- [GitLab: NOT NULL constraints](https://docs.gitlab.com/development/database/not_null_constraints/)
