# RAG 文档聊天助手 / RAG Document Chat Assistant

> 中文 | [English](#english)
<img width="589" height="587" alt="image" src="https://github.com/user-attachments/assets/9bb04f55-de4a-4eb8-a587-fa806a204206" />


这是一个基于检索增强生成（RAG）技术的文档问答系统，支持多种文档格式。

This is a document Q&A system based on Retrieval-Augmented Generation (RAG) technology, supporting multiple document formats.

## 环境配置 / Environment Configuration

### 必需环境变量 / Required Environment Variables

在项目根目录创建 `.env` 文件，并配置以下必需的环境变量：

Create a `.env` file in the project root directory and configure the following required environment variables:

```bash
# OpenAI API 配置 / OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# 数据库配置（RAG专用） / Database Configuration (RAG specific)
RAG_DATABASE_URL=sqlite:///./rag_documents.db

# 可选：原数据库URL（如果需要） / Optional: Original database URL (if needed)
DATABASE_URL=sqlite:///./data.db
```

### 环境变量说明 / Environment Variables Description

| 变量名 / Variable Name | 必需 / Required | 默认值 / Default | 说明 / Description |
|--------|------|--------|------|
| `OPENAI_API_KEY` | ✅ | 无 / None | OpenAI API密钥，用于LLM和嵌入 / OpenAI API key for LLM and embeddings |
| `OPENAI_MODEL` | ❌ | `gpt-4o-mini` | 使用的GPT模型 / GPT model to use |
| `OPENAI_EMBEDDING_MODEL` | ❌ | `text-embedding-3-small` | 嵌入模型 / Embedding model |
| `RAG_DATABASE_URL` | ✅ | 无 / None | RAG系统专用数据库URL / RAG system specific database URL |
| `DATABASE_URL` | ❌ | 无 / None | 通用数据库URL（可选） / General database URL (optional) |

### 获取OpenAI API密钥 / Get OpenAI API Key

1. 访问 [OpenAI平台](https://platform.openai.com/) / Visit [OpenAI Platform](https://platform.openai.com/)
2. 登录或注册账户 / Login or register an account
3. 进入API Keys页面 / Go to API Keys page
4. 创建新的API密钥 / Create a new API key
5. 复制密钥并添加到 `.env` 文件中 / Copy the key and add it to the `.env` file

### 数据库配置选项 / Database Configuration Options

#### SQLite（推荐用于开发） / SQLite (Recommended for development)
```bash
RAG_DATABASE_URL=sqlite:///./rag_documents.db
```

#### PostgreSQL（推荐用于生产） / PostgreSQL (Recommended for production)
```bash
RAG_DATABASE_URL=postgresql://username:password@localhost:5432/rag_docs
```

### 验证配置 / Verify Configuration

运行以下命令验证环境配置是否正确：

Run the following commands to verify that the environment configuration is correct:

```bash
# 检查环境变量 / Check environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', '***' + os.getenv('OPENAI_API_KEY', 'NOT SET')[-4:]); print('DB URL:', os.getenv('RAG_DATABASE_URL', 'NOT SET'))"

# 运行服务器（会自动验证配置） / Run server (automatically validates configuration)
python run_server.py
```

### 常见配置问题 / Common Configuration Issues

1. **API密钥无效** / **Invalid API Key**: 检查密钥是否正确复制，是否有余额 / Check if the key is copied correctly and has balance
2. **数据库连接失败** / **Database Connection Failed**: 检查URL格式，PostgreSQL需要确保数据库存在 / Check URL format, PostgreSQL requires database to exist
3. **权限问题** / **Permission Issues**: 确保有写入数据库文件的权限 / Ensure write permissions for database files
4. **网络问题** / **Network Issues**: 确保能访问OpenAI API（可能需要代理） / Ensure access to OpenAI API (may need proxy)

## 快速开始 / Quick Start

1. 安装依赖 / Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. 设置环境变量（见上方环境配置部分） / Set environment variables (see Environment Configuration section above)

3. 运行应用 / Run the application:
   ```bash
   # 方式1：使用演示脚本（推荐） / Method 1: Use demo script (recommended)
   python run_server.py

   # 方式2：直接使用uvicorn / Method 2: Use uvicorn directly
   uvicorn api:app --reload --host 0.0.0.0 --port 8000
   ```

4. 打开浏览器访问 / Open browser and visit: http://localhost:8000

## 功能特性 / Features

- 📁 支持多种文档格式：TXT、PDF、Word (.docx/.doc) / Support multiple document formats: TXT, PDF, Word (.docx/.doc)
- 💬 智能问答：基于文档内容进行准确回答 / Intelligent Q&A: Accurate answers based on document content
- 🌐 现代化Web界面：直观的上传和对话界面 / Modern Web UI: Intuitive upload and chat interface
- 🌍 多语言支持：中文和英文界面 / Multilingual support: Chinese and English interface
- 🔍 语义搜索：使用OpenAI嵌入进行高效检索 / Semantic search: Efficient retrieval using OpenAI embeddings
- 📊 RESTful API：完整的后端API支持 / RESTful API: Complete backend API support

## Web界面使用 / Web Interface Usage

### 语言切换 / Language Switching
- 点击右上角的"中文"或"English"按钮切换界面语言 / Click the "中文" or "English" button in the top right to switch interface language
- 所有文本会实时更新 / All text updates in real-time

### 上传文档 / Upload Documents
1. 点击"选择文件"按钮，选择要上传的文档 / Click "Select File" button, choose document to upload
2. 可选：输入自定义文档ID / Optional: Enter custom document ID
3. 点击"上传文档"按钮 / Click "Upload Document" button

### 提问 / Ask Questions
1. 在"选择文档ID"中输入已上传文档的ID / Enter uploaded document ID in "Select Document ID"
2. 在"输入问题"中输入您的问题 / Enter your question in "Enter Question"
3. 点击"提问"按钮或按回车键 / Click "Ask" button or press Enter

### 查看对话历史 / View Chat History
- 所有问答记录会显示在聊天历史区域 / All Q&A records are displayed in the chat history area

## API 端点 / API Endpoints

### GET /
- 重定向到前端界面 / Redirect to frontend interface

### GET /health
- 健康检查 / Health check
- 响应 / Response: `{"status": "ok"}`

### POST /upload
- 上传文档并建立索引 / Upload document and create index
- 请求 / Request:
  - `file`: 文件（支持 .txt, .pdf, .docx, .doc） / File (supports .txt, .pdf, .docx, .doc)
  - `doc_id` (可选): 文档ID，默认为文件名 / Document ID (optional), defaults to filename
- 响应 / Response: `{"ingested": {"doc_id": "<id>", "chunks_added": <n>}}`

### POST /ask
- 基于文档内容回答问题 / Answer questions based on document content
- 请求体 / Request body: `{"doc_id": "文档ID", "question": "问题"}` / `{"doc_id": "Document ID", "question": "Question"}`
- 响应 / Response: `{"answer": "回答内容", "raw": {...}}` / `{"answer": "Answer content", "raw": {...}}`

## 技术栈 / Tech Stack

- **后端 / Backend**: FastAPI (Python)
- **数据库 / Database**: SQLite/PostgreSQL (通过SQLAlchemy / via SQLAlchemy)
- **嵌入 / Embeddings**: OpenAI Embeddings
- **LLM**: OpenAI GPT 模型 / OpenAI GPT models
- **文档处理 / Document Processing**: PyMuPDF (PDF), python-docx (Word)
- **前端 / Frontend**: 纯HTML/CSS/JavaScript / Pure HTML/CSS/JavaScript

## 开发 / Development

### 运行测试 / Run Tests
```bash
python test_api.py  # API集成测试 / API integration tests
python test_agent.py  # 代理功能测试 / Agent functionality tests
```

### 项目结构 / Project Structure
```
aidocumentchat/
├── api.py              # FastAPI应用和路由 / FastAPI app and routes
├── agent.py            # RAG代理和工具 / RAG agent and tools
├── db.py               # 数据库配置 / Database configuration
├── tools_schema.py     # OpenAI工具模式定义 / OpenAI tools schema definition
├── static/
│   └── index.html      # 前端界面 / Frontend interface
├── test_*.py           # 测试文件 / Test files
├── requirements.txt    # Python依赖 / Python dependencies
└── README_API.md       # 本文档 / This document
```

## 注意事项 / Notes

- 确保设置正确的OpenAI API密钥 / Make sure to set the correct OpenAI API key
- 对于生产环境，建议使用PostgreSQL数据库 / For production environment, PostgreSQL database is recommended
- 大文件上传可能需要调整服务器配置 / Large file uploads may require server configuration adjustments
- API默认运行在 http://localhost:8000 / API runs on http://localhost:8000 by default

---

## English

# RAG Document Chat Assistant

This is a document Q&A system based on Retrieval-Augmented Generation (RAG) technology, supporting multiple document formats.

[中文](#中文) | English

### Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables (see Environment Configuration section above)

3. Run the application:
   ```bash
   # Method 1: Use demo script (recommended)
   python run_server.py

   # Method 2: Use uvicorn directly
   uvicorn api:app --reload --host 0.0.0.0 --port 8000
   ```

4. Open browser and visit: http://localhost:8000

### Features

- 📁 Support multiple document formats: TXT, PDF, Word (.docx/.doc)
- 💬 Intelligent Q&A: Accurate answers based on document content
- 🌐 Modern Web UI: Intuitive upload and chat interface
- 🌍 Multilingual support: Chinese and English interface
- 🔍 Semantic search: Efficient retrieval using OpenAI embeddings
- 📊 RESTful API: Complete backend API support

### Web Interface Usage

#### Language Switching
- Click the "中文" or "English" button in the top right to switch interface language
- All text updates in real-time

#### Upload Documents
1. Click "Select File" button, choose document to upload
2. Optional: Enter custom document ID
3. Click "Upload Document" button

#### Ask Questions
1. Enter uploaded document ID in "Select Document ID"
2. Enter your question in "Enter Question"
3. Click "Ask" button or press Enter

#### View Chat History
- All Q&A records are displayed in the chat history area

### API Endpoints

#### GET /
- Redirect to frontend interface

#### GET /health
- Health check
- Response: `{"status": "ok"}`

#### POST /upload
- Upload document and create index
- Request:
  - `file`: File (supports .txt, .pdf, .docx, .doc)
  - `doc_id` (optional): Document ID, defaults to filename
- Response: `{"ingested": {"doc_id": "<id>", "chunks_added": <n>}}`

#### POST /ask
- Answer questions based on document content
- Request body: `{"doc_id": "Document ID", "question": "Question"}`
- Response: `{"answer": "Answer content", "raw": {...}}`

### Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite/PostgreSQL (via SQLAlchemy)
- **Embeddings**: OpenAI Embeddings
- **LLM**: OpenAI GPT models
- **Document Processing**: PyMuPDF (PDF), python-docx (Word)
- **Frontend**: Pure HTML/CSS/JavaScript

### Development

#### Run Tests
```bash
python test_api.py  # API integration tests
python test_agent.py  # Agent functionality tests
```

#### Project Structure
```
aidocumentchat/
├── api.py              # FastAPI app and routes
├── agent.py            # RAG agent and tools
├── db.py               # Database configuration
├── tools_schema.py     # OpenAI tools schema definition
├── static/
│   └── index.html      # Frontend interface
├── test_*.py           # Test files
├── requirements.txt    # Python dependencies
└── README_API.md       # This document
```

### Notes

- Make sure to set the correct OpenAI API key
- For production environment, PostgreSQL database is recommended
- Large file uploads may require server configuration adjustments
- API runs on http://localhost:8000 by default

## 功能特性

- 📁 支持多种文档格式：TXT、PDF、Word (.docx/.doc)
- 💬 智能问答：基于文档内容进行准确回答
- 🌐 现代化Web界面：直观的上传和对话界面
- 🔍 语义搜索：使用OpenAI嵌入进行高效检索
- 📊 RESTful API：完整的后端API支持

## Web界面使用

1. **上传文档**：
   - 点击"选择文件"按钮，选择要上传的文档
   - 可选：输入自定义文档ID
   - 点击"上传文档"按钮

2. **提问**：
   - 在"选择文档ID"中输入已上传文档的ID
   - 在"输入问题"中输入您的问题
   - 点击"提问"按钮或按回车键

3. **查看对话历史**：
   - 所有问答记录会显示在聊天历史区域

## API 端点

### GET /
- 重定向到前端界面

### GET /health
- 健康检查
- 响应：`{"status": "ok"}`

### POST /upload
- 上传文档并建立索引
- 请求：
  - `file`: 文件（支持 .txt, .pdf, .docx, .doc）
  - `doc_id` (可选): 文档ID，默认为文件名
- 响应：`{"ingested": {"doc_id": "<id>", "chunks_added": <n>}}`

### POST /ask
- 基于文档内容回答问题
- 请求体：`{"doc_id": "文档ID", "question": "问题"}`
- 响应：`{"answer": "回答内容", "raw": {...}}`

## 技术栈

- **后端**: FastAPI (Python)
- **数据库**: SQLite/PostgreSQL (通过SQLAlchemy)
- **嵌入**: OpenAI Embeddings
- **LLM**: OpenAI GPT 模型
- **文档处理**: PyMuPDF (PDF), python-docx (Word)
- **前端**: 纯HTML/CSS/JavaScript

## 开发

### 运行测试
```bash
python test_api.py  # API集成测试
python test_agent.py  # 代理功能测试
```

### 项目结构
```
aidocumentchat/
├── api.py              # FastAPI应用和路由
├── agent.py            # RAG代理和工具
├── db.py               # 数据库配置
├── tools_schema.py     # OpenAI工具模式定义
├── static/
│   └── index.html      # 前端界面
├── test_*.py           # 测试文件
├── requirements.txt    # Python依赖
└── README_API.md       # 本文档
```

## 注意事项

- 确保设置正确的OpenAI API密钥
- 对于生产环境，建议使用PostgreSQL数据库
- 大文件上传可能需要调整服务器配置
- API默认运行在 http://localhost:8000
