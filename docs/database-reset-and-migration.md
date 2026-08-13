# 数据库重置与迁移

采用干净重构。旧 `user_api_keys` 无法表达多连接/地域/Workspace，旧 ChatHistory 和裸模型字符串不能可靠映射到 ContentPart 与 connection-scoped key，因此不自动迁移。会丢失：用户、会话、旧问答、旧明文 Key、知识库数据库元数据；普通 database-only 重置保留上传、Chroma、Wiki 与 Ollama 模型文件，但保留文件可能因元数据丢失成为孤立数据。

```powershell
python backend/scripts/reset_database.py --dry-run
python backend/scripts/reset_database.py --database-only --backup --yes
python backend/scripts/reset_database.py --include-vector-data --yes
python backend/scripts/reset_database.py --include-uploads --include-vector-data --yes
python backend/scripts/reset_database.py --restore-from backend/omnisage.<timestamp>.bak --yes
```

默认无操作；非交互无 `--yes` 拒绝；文件目录必须位于 DATA_DIR 且不能是根、Home、工作区或 backend 根。只有 `--include-uploads`、`--include-vector-data`、`--include-wiki` 删除对应文件，可能不可恢复。生产执行前必须验证备份。

SQLite 的 `--backup` 复制数据库为时间戳 `.bak`；恢复时停服，将 `.bak` 复制回原 DATABASE_URL 文件，再启动并运行 `scripts/inspect_database.py`。MySQL 当前工具只通过 SQLAlchemy `drop_all/create_all` 删除项目已知表，不删除 Server/Schema；先用 `mysqldump`，恢复用 `mysql`。没有 `--drop-schema`。PostgreSQL 未支持。

空库初始化运行 `python backend/scripts/create_tables.py`；策略是 SQLAlchemy metadata，不是 Alembic。重置后用 inspect、FastAPI OpenAPI 和登录/连接创建验证。重置不在启动路径且无 HTTP API。

SQLite 备份在重置前执行 `PRAGMA integrity_check`；恢复命令只接受目标数据库同目录内的有效 SQLite `.bak`。`APP_ENV=production` 时，重置必须显式指定 `--backup --production-confirm --yes`，恢复必须指定 `--production-confirm --yes`。普通数据库重置会重建全部已知 SQLAlchemy 表，不存在“仅清 AI cache”的隐式模式。
