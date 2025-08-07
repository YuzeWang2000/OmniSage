# OmniSage Backend

OmniSage 后端是一个基于 FastAPI 和 LangChain 的智能问答系统，支持知识库管理、RAG 检索增强生成和 Wiki 知识集成。

## 功能特性

- **用户认证与授权**: 基于 JWT 的用户认证系统
- **知识库管理**: 支持文档上传、处理和向量化存储
- **RAG 检索增强生成**: 基于 Chroma 向量数据库的语义检索
- **Wiki 知识集成**: 支持在线和离线维基百科知识检索
- **对话管理**: 多轮对话历史记录和上下文管理
- **API 接口**: RESTful API 设计，支持前端集成

## 技术栈

- **Web 框架**: FastAPI
- **数据库**: SQLAlchemy + MySQL
- **向量数据库**: Chroma
- **AI 框架**: LangChain
- **嵌入模型**: Ollama (nomic-embed-text)
- **文档处理**: Unstructured
- **认证**: JWT

## 项目结构

```
backend/
├── app/                          # 主应用目录
│   ├── config.py                 # 配置文件
│   ├── database.py               # 数据库连接
│   ├── models.py                 # 数据模型
│   ├── schemas.py                # Pydantic 模式
│   ├── routers/                  # API 路由
│   │   ├── auth.py              # 认证相关 API
│   │   ├── chat.py              # 聊天 API
│   │   ├── conversation.py      # 对话管理 API
│   │   ├── rag.py               # RAG 相关 API
│   │   └── api_keys.py          # API 密钥管理
│   ├── services/                 # 业务逻辑服务
│   │   ├── database_service.py  # 数据库服务
│   │   ├── knowledgebase_service.py # 知识库服务
│   │   ├── llm_service.py       # LLM 服务
│   │   ├── rag_chain_service.py # RAG 链服务
│   │   └── wiki_service.py      # Wiki 服务
│   └── utils/                    # 工具函数
│       ├── prompts.py           # 提示词模板
│       ├── reranker.py          # 重排序器
│       ├── text_splitter.py     # 文本分割器
│       └── title_enhancer.py    # 标题增强器
├── scripts/                      # 脚本和工具
│   ├── create_tables.py         # 数据库表创建
│   ├── init_wiki_data.py        # Wiki 数据初始化
│   └── reset_project_data.py    # 项目数据重置
├── chroma_db/                    # Chroma 向量数据库
├── wiki_data/                    # Wiki 数据存储
├── uploaded_files/               # 用户上传文件
├── main.py                       # 应用入口
├── pyproject.toml               # 依赖配置
└── README.md                     # 项目文档
```

## 快速开始

### 1. 环境要求

- Python 3.11+
- MySQL 8.0+
- Ollama (用于本地嵌入模型)
- uv (Python 包管理器)

#### 安装 uv

```bash
# 使用 pip 安装 uv
pip install uv

# 或者使用官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 安装依赖

```bash
# 安装项目依赖
uv sync
```

### 3. 配置数据库

1. 创建 MySQL 数据库
2. 修改 `app/config.py` 中的数据库连接配置
3. 运行数据库初始化脚本：

```bash
uv run python scripts/create_tables.py
```

### 4. 启动服务

```bash
uv run python main.py
```

服务将在 `http://localhost:8000` 启动。

## API 文档

启动服务后，可以访问以下地址查看 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 脚本说明

### create_tables.py
创建数据库表结构，首次运行项目时必须执行。

```bash
uv run python scripts/create_tables.py
```

### init_wiki_data.py
初始化维基百科数据，用于 Wiki 知识检索功能。

```bash
uv run python scripts/init_wiki_data.py
```

### reset_project_data.py
重置项目数据，会清空所有用户数据、知识库和对话记录（谨慎使用）。

```bash
uv run python scripts/reset_project_data.py
```

## 依赖管理

本项目使用 uv 进行依赖管理，配置文件为 `pyproject.toml`。

### 常用 uv 命令

```bash
# 安装依赖
uv sync

# 添加新依赖
uv add package_name

# 添加开发依赖
uv add --dev package_name

# 运行 Python 脚本
uv run python script.py

# 激活虚拟环境
uv shell
```

## 配置说明

### 环境变量

创建 `.env` 文件配置以下环境变量：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://username:password@localhost/omnissage

# LLM 配置
DEEPSEEK_API_KEY=your_deepseek_api_key
OLLAMA_BASE_URL=http://localhost:11434

# 其他配置
SECRET_KEY=your_secret_key
```

### 模型配置

系统支持多种 LLM 模型：

- **DeepSeek**: 需要 API 密钥
- **Ollama**: 本地部署的模型

## 主要 API 端点

### 认证相关
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `POST /auth/refresh` - 刷新令牌

### 知识库管理
- `POST /rag/upload` - 上传文档
- `GET /rag/knowledge-bases` - 获取知识库列表
- `DELETE /rag/knowledge-bases/{kb_id}` - 删除知识库

### 聊天功能
- `POST /chat/` - 发送聊天消息
- `GET /conversation/` - 获取对话历史
- `DELETE /conversation/{conversation_id}` - 删除对话

### API 密钥管理
- `POST /api-keys/` - 创建 API 密钥
- `GET /api-keys/` - 获取 API 密钥列表
- `DELETE /api-keys/{key_id}` - 删除 API 密钥

## 开发指南

### 添加新功能

1. 在 `app/routers/` 中添加新的路由
2. 在 `app/services/` 中添加业务逻辑
3. 在 `app/models/` 中添加数据模型
4. 更新 API 文档

### 代码规范

- 使用 Python 类型注解
- 遵循 PEP 8 代码风格
- 添加适当的注释和文档

### 依赖管理最佳实践

- 使用 `uv add` 添加新依赖
- 定期运行 `uv sync` 更新依赖
- 在 `pyproject.toml` 中明确指定版本范围

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否启动
   - 验证数据库连接字符串

2. **模型加载失败**
   - 检查 Ollama 服务是否启动
   - 验证模型名称是否正确

3. **依赖安装失败**
   - 确保使用正确的 Python 版本（3.11+）
   - 尝试重新运行 `uv sync`

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](../LICENSE) 文件。 