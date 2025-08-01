# OmniSage - 智能知识库问答系统

OmniSage 是一个基于 FastAPI 和 Gradio 构建的智能知识库问答系统，支持文档上传、知识库管理和智能问答功能。

## 功能特性

- 📚 **知识库管理**: 支持多种文档格式上传和管理
- 🤖 **智能问答**: 基于 RAG (Retrieval-Augmented Generation) 的智能问答
- 🌐 **Wiki 集成**: 支持维基百科数据导入和处理
- 🎤 **语音识别**: 集成 Vosk 语音识别功能
- 🔐 **用户认证**: 完整的用户注册、登录和权限管理
- 📊 **对话历史**: 完整的对话记录和管理
- 🎨 **现代化 UI**: 基于 Gradio 的直观用户界面

## 技术栈

### 后端
- **FastAPI**: 高性能 Web 框架
- **SQLAlchemy**: ORM 数据库操作
- **LangChain**: LLM 应用开发框架
- **ChromaDB**: 向量数据库
- **Sentence Transformers**: 文本嵌入模型

### 前端
- **Gradio**: 快速构建 ML 应用界面
- **Vosk**: 离线语音识别

## 项目结构

```
OmniSage/
├── backend/                 # 后端服务
│   ├── app/                # 应用核心代码
│   ├── scripts/            # 初始化脚本
│   ├── chroma_db/          # 向量数据库存储
│   ├── uploaded_files/     # 上传文件存储
│   ├── wiki_data/          # 维基百科数据
│   └── main.py            # 后端启动文件
├── frontend/               # 前端服务
│   ├── app.py             # 前端启动文件
│   └── vosk-model-small-cn-0.22/  # 语音识别模型
└── requirements.txt        # 项目依赖
```

## 快速开始

### 1. 环境准备

确保已安装 Python 3.8+ 和 Conda。

### 2. 克隆项目

```bash
git clone <repository-url>
cd OmniSage
```

### 3. 创建 Conda 环境

```bash
# 创建后端环境
conda create -n Omni-backend python=3.9
conda activate Omni-backend

# 创建前端环境
conda create -n Omni-frontend python=3.9
conda activate Omni-frontend
```

### 4. 安装依赖

```bash
# 安装后端依赖
conda activate Omni-backend
cd backend
pip install -r requirements.txt

# 安装前端依赖
conda activate Omni-frontend
cd frontend
pip install -r requirements.txt
```

### 5. 初始化数据库

```bash
# 激活后端环境
conda activate Omni-backend
cd backend

# 创建数据库表
python scripts/create_tables.py

# 初始化维基百科数据（可选）
python scripts/init_wiki_data.py
```

### 6. 启动服务

#### 启动后端服务

```bash
# 激活后端环境
conda activate Omni-backend
cd backend

# 启动后端服务
python main.py
```

后端服务将在 `http://localhost:8000` 启动。

#### 启动前端服务

```bash
# 激活前端环境
conda activate Omni-frontend
cd frontend

# 启动前端服务
python app.py
```

前端服务将在 `http://localhost:7860` 启动。

## 脚本说明

### 后端脚本

- `create_tables.py`: 创建数据库表结构
- `init_wiki_data.py`: 初始化维基百科数据
- `reset_project_data.py`: 重置项目数据（谨慎使用）

### 使用示例

```bash
# 创建数据库表
python scripts/create_tables.py

# 初始化维基百科数据
python scripts/init_wiki_data.py

# 重置项目数据（会清空所有数据）
python scripts/reset_project_data.py
```

## API 文档

启动后端服务后，可以访问以下地址查看 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 主要功能

### 1. 用户管理
- 用户注册和登录
- API 密钥管理
- 用户权限控制

### 2. 知识库管理
- 文档上传（支持 PDF、TXT 等格式）
- 知识库创建和管理
- 文档向量化和存储

### 3. 智能问答
- 基于知识库的智能问答
- 支持维基百科数据查询
- 对话历史记录

### 4. 语音识别
- 离线语音识别
- 支持中文语音输入

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
- **其他**: 可通过配置添加

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否启动
   - 验证数据库连接字符串

2. **模型加载失败**
   - 检查模型文件是否存在
   - 验证模型路径配置

3. **依赖安装失败**
   - 确保使用正确的 Python 版本
   - 尝试使用 conda 安装依赖

### 日志查看

后端日志位于控制台输出，前端日志在 Gradio 界面中显示。

## 开发指南

### 添加新功能

1. 在 `backend/app/routers/` 中添加新的路由
2. 在 `backend/app/services/` 中添加业务逻辑
3. 在 `backend/app/models/` 中添加数据模型
4. 更新前端界面

### 代码规范

- 使用 Python 类型注解
- 遵循 PEP 8 代码风格
- 添加适当的注释和文档

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请通过以下方式联系：

- 提交 Issue
- 发送邮件

---

**注意**: 首次使用前请确保完成所有初始化步骤，特别是数据库表的创建。
