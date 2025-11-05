# 💹 Multi-Agent Financial Analyst: Self-Correcting System with Strands & OpenAI

**A sophisticated, self-learning CLI tool built with the Strands Agents SDK that uses a multi-agent (Orchestrator) system to answer complex financial queries. It features specialist agents for SQL, live financial data (yfinance), and real-time news (Tavily), including a self-correcting loop to find and save new stock tickers.**

## 🎯 Project Description

This project is a powerful, interactive Command-Line Interface (CLI) application that functions as a **Multi-Agent Financial Analyst**. Built using the **Strands Agents SDK**, it serves as a practical demonstration of a robust, modular, and intelligent agentic architecture.

Instead of relying on a single, monolithic AI model, this system employs a **Hierarchical Delegation** (or "Agent-as-a-Tool") pattern. A central **Orchestrator Agent** acts as the "manager," interpreting complex user queries and delegating specific sub-tasks to a team of specialized agents.

### The Specialist Agent Team

This system's intelligence is distributed among three specialist agents, each with a distinct and precise role:

* **Data Analyst Agent:** The "gatekeeper" for all company data. It's responsible for converting company names (like "Apple") into official stock tickers ("AAPL").
* **Financial Metrics Agent:** The "quant." A precision-focused agent that fetches live financial data (like P/E ratio and stock price) using the `yfinance` API.
* **News Research Agent:** The "researcher." It uses the `Tavily` API to scan the web for real-time news and generates concise, human-readable summaries.


### 🏗️ Technical Architecture

This system is built on the **Strands Agents SDK** and utilizes a **Hierarchical Delegation ("Agent-as-a-Tool")** architecture. This modular pattern separates the main Orchestrator from its specialized agents, enabling complex, multi-step, and self-correcting task execution.

### Strands Agent-as-a-Tool
* The system features one main **Orchestrator Agent** (`main.py`) that serves as the "Lead Financial Analyst."
* The Orchestrator manages a team of **Specialist Agents** (`agent-tools.py`) which are defined as callable tools.
* Specialist agents are designed for single-responsibility tasks:
    * `data_analyst_agent`: Manages data lookup and self-correction.
    * `financial_metrics_agent`: Fetches live financial data.
    * `news_research_agent`: Fetches and summarizes web news.

### Self-Correction & Learning Loop
* The `data_analyst_agent` implements a Python-based **self-healing loop**.
* When a primary tool (e.g., `sql_query_tool`) fails to find a ticker (a `TICKER_NOT_FOUND` state), the agent automatically triggers a secondary protocol.
* It calls the `news_research_agent` to find the missing data from the web.
* It then uses the `sql_update_tool` to **permanently save the new ticker** to the SQLite database, allowing the agent to learn.

### LLM Integration
* **Model:** `gpt-3.5-turbo` (Configurable via `agent-tools.py`).
* **Provider:** OpenAI API.
* **Framework:** Utilizes the Strands' native `OpenAIModel` provider.
* **Context Handling:** Relies on **strict, role-based system prompts** for each specialist agent to ensure deterministic outputs (e.g., raw JSON, single tickers) and minimize hallucinations.

### Data & API Layer
* **Database:** SQLite (via Python's built-in `sqlite3`) for persistent storage of company ticker symbols.
* **Live Financials:** `yfinance` API, wrapped in the `financial_data_tool`.
* **Web Research:** `Tavily` API, wrapped in the `news_search_tool` for agent-optimized search results.
* **Memory:** `mem0_memory` tool provides a FAISS-backed vector store for the Orchestrator to persist conversational memory.

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/cc43a73e-501e-46eb-9ada-e8121deea9c7" />

---


### ✨ Key Features

* **🧠 Hierarchical Multi-Agent System:** Built on the **Strands Agents SDK**, this project uses an "Agent-as-a-Tool" architecture. A central **Orchestrator Agent** (the "manager") intelligently delegates complex tasks to a team of specialized, single-purpose agents.
* **🔄 Autonomous Self-Correction Loop:** Features a "smart" **Data Analyst Agent** that automatically detects when a stock ticker is missing. It then triggers a self-healing protocol: it uses the `news_research_agent` to find the ticker on the web and then uses the `sql_update_tool` to permanently save the new information to its SQLite database.
* **⛓️ Specialized Multi-Source Integration:** Combines data from distinct, real-world sources by dedicating an agent to each one:
    * **Database:** `sqlite3` for persistent, local ticker data.
    * **Live Market Data:** `yfinance` API for real-time stock prices and P/E ratios.
    * **Web Research:** `Tavily API` for agent-optimized, live news summarization.
* **💻 Professional CLI Interface:** A clean, asynchronous `asyncio` command-line interface. It features a multi-threaded **spinner** (`⣾ Orchestrator is thinking...`) and a smart callback handler that neatly separates agent "thinking" (tool calls) from the final, streamed answer.


## 📁 Project Structure
```
📦 strands-openai-financial-agent
│
├── configuration.py        # Environment setup and configurations
├── agent-tools.py          # Core strands workflow and agent logic
├── main.py                 # CLI frontend for user interaction
├── db_setup.py             # Sqltite DataBase creation script
└── README.md
└── License

```

### 💡 Use Cases

* **Complex Financial Analysis:** Ask multi-step questions that require data from multiple sources. For example: "Compare the P/E ratio of Apple and Google, and get me the latest news for Apple."
* **Autonomous Company Research:** Perform research on new or unknown companies. The agent will autonomously find the official ticker, save it to the database for future use, and then proceed with the financial analysis.
* **Real-time Data Retrieval:** Get instant, up-to-the-minute information without leaving the terminal. Ask for "the latest news for Microsoft" or "the current price of Tesla" to get live data from web APIs.
* **Financial Power-Tool:** Use as a high-speed tool for financial analysts, traders, or hobbyists to quickly gather and synthesize market data directly from their CLI.
* **Agent Architecture Demo:** Serve as a working, production-ready example of a **Hierarchical Multi-Agent System** (Agent-as-a-Tool) and a **Self-Correcting Loop** for other developers to learn from and build upon.

---

## 🧭 Demo Sample Images

**CLI Interface**

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/e0a60cd7-3f7f-4dcb-94b2-479f41799486" />

---

## 🛠️ Installation Instructions

### Prerequisites
- Python 3.10+
- CUDA-compatible GPU (optional, for faster processing)
- 8GB+ RAM recommended

### Step 1: Clone Repository
```bash
git clone https://github.com/Ginga1402/strands-openai-financial-agent.git
cd strands-openai-financial-agent
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Paths
Update the paths in `configuration.py` to match your system:
```python
TAVILY_API_KEY = "YOUR-TAVILY-KEY"
OPENAI_KEY = "YOUR-OPENAI-KEY"
DB_FILE = 'financial_data.db'
```

## 📖 Usage

### Starting the Application

1. **Start the CLI Application**:
```bash
python main.py
```


### ⚙️ Basic Workflow


1. **User Input** → The user asks a complex, natural-language question (e.g., "Compare the P/E ratio of Nvidia and Apple, and get me the latest news for Nvidia."). 
2. **Deconstruct Query** → The main Orchestrator Agent (the "Lead Analyst") receives the query and its LLM deconstructs it into a multi-step plan (e.g., [Find Ticker: "Nvidia"], [Find Ticker:   "Apple"], [Get Finance Data: Ticker 1], [Get Finance Data: Ticker 2], [Get News: Ticker 1]). 
3. **Resolve Tickers (Self-Correction)** → The Orchestrator calls the data_analyst_agent for each company name.

    1. This specialist agent queries the local SQLite database.
    2. If the ticker is missing, it automatically triggers its self-correction loop: it calls the news_research_agent (using Tavily) to find the ticker on the web, then saves it to the SQLite DB using the sql_update_tool.
      
4. **Execute Data Calls** → The Orchestrator, now holding the correct tickers (e.g., "NVDA", "AAPL"), executes the next steps of its plan by calling the other specialists:

    1. financial_metrics_agent (which calls the yfinance API).
    2. news_research_agent (which calls the Tavily API).
       
5. **Synthesize Response** → The Orchestrator's LLM receives all the structured data (raw JSON from financial_metrics_agent) and unstructured data (text summaries from news_research_agent). 
6. **Generate Final Answer** → The Orchestrator synthesizes all the gathered information into a single, comprehensive, human-readable response, which is streamed to the user in the CLI.

**Workflow Graph:**  
 
START → deconstruct_query → resolve_tickers → execute_data_calls → synthesize_response → generate_final_answer → END

---

### 🧱 Technologies Used

| Technology | Description | Link |
|---|---|---|
| **Strands Agents SDK** | A lightweight, model-driven framework for building AI agents. | [Strands SDK (GitHub)](https://github.com/strands-agents/sdk-python) |
| **OpenAI** | Used for LLM inference, powering all agent reasoning. | [OpenAI](https://openai.com) |
| **`gpt-3.5-turbo`** | The specific model used for its balance of speed, cost, and tool-calling. | [OpenAI Models](https://platform.openai.com/docs/models) |
| **Tavily API** | AI-optimized search engine for real-time web research. | [Tavily](https://tavily.com) |
| **yfinance** | Python library for fetching live financial data from Yahoo! Finance. | [yfinance (PyPI)](https://pypi.org/project/yfinance/) |
| **SQLite** | Lightweight, built-in database used for persistent ticker storage. | [SQLite](https://sqlite.org) |
| **mem0** | The memory tool used by the Orchestrator for FAISS-backed vector memory. | [mem0 (GitHub)](https://github.com/mem0ai/mem0) |
| **Colorama** | Python library for producing colored terminal text and a professional CLI UI. | [Colorama (PyPI)](https://pypi.org/project/colorama/) |
| **Asyncio** | Python's built-in library for managing the asynchronous CLI loop. | [Asyncio (Python Docs)](https://docs.python.org/3/library/asyncio.html) |

## 🤝 Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌟 Star History

If you find strands-openai-financial-agent useful, please consider giving it a star ⭐ on GitHub!
