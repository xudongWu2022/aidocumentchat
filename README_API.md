# RAG 文档聊天助手

这是一个基于检索增强生成（RAG）技术的文档问答系统，支持多种文档格式。

## 快速开始

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 设置环境变量（在 `.env` 文件中）：
   ```
   OPENAI_API_KEY=sk-your-openai-api-key
   DATABASE_URL=sqlite:///./data.db
   ```

3. 运行应用：
   ```bash
   uvicorn api:app --reload --host 0.0.0.0 --port 8000
   ```

4. 打开浏览器访问：http://localhost:8000

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
