import sqlite3
import json
from strands import tool, Agent
from typing import List,Dict,Any,Optional
import yfinance as yf
import os
from strands_tools.tavily import tavily_search as official_tavily_search
import asyncio
from strands.models.openai import OpenAIModel
from strands.handlers.callback_handler import PrintingCallbackHandler



from configuration import TAVILY_API_KEY,DB_FILE,gpt_model

os.environ['TAVILY_API_KEY'] = TAVILY_API_KEY


# from colorama import Fore, Style, init

# # Initialize colorama
# init()


# =============================================================================
# TOOLS
# =============================================================================


@tool
def sql_query_tool(query: str) -> str :
    """Executes a read-only SQL select query yo fetch the data"""

    conn = None

    try:

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)

        columns = [description[0] for description in cursor.description]
        results = cursor.fetchall()

        data = [dict(zip(columns, row)) for row in results ]


        return json.dumps(data)
    
    except Exception as e:
        return f"An error occurred: {e.args}"

    finally:

        if conn:
            conn.close()



@tool
def sql_update_tool(ticker: str, official_name: str, common_name: str) -> str:
    """Updates the company's ticker and name into the database"""

    conn = None

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Use INSERT OR REPLACE to update if the ticker already exists
        cursor.execute("""            
        INSERT OR REPLACE INTO company_metadata(official_name, common_name, ticker) VALUES (?, ?, ?)
        """, (official_name,common_name,ticker))

        conn.commit()
        return f"DataBase updated successfully: Ticker {ticker} added/replaced"
    
    except Exception as e:
        return f"An error occurred: {e.args}"
    
    finally:
        if conn:
            conn.close()



@tool
def financial_data_tool(ticker: str) -> str:
    """
    Retrieves the current market price and Price-to-Earnings (P/E) ratio 
    for a given stock ticker symbol. Use this tool ONLY when you need live, 
    up-to-date fundamental financial metrics for a valid stock ticker.
    
    Args:
        ticker: The official stock ticker symbol (e.g., 'AAPL', 'MSFT').
        
    Returns:
        A JSON string containing the 'currentPrice', 'trailingPE', and 
        the 'sector' of the company, or an error message if the ticker is invalid 
        or data is unavailable.
    """
    try:
        stock = yf.Ticker(ticker=ticker)

        info = stock.info

        # Check if basic data is available (yfinance sometimes returns empty info for bad tickers)
        if not info or 'regularMarketPrice' not in info:
            return f"Financial Data Error: Could not retrieve market data for ticker '{ticker}'. It may be an invalid or unsupported symbol."

        data = {
            "ticker" : ticker.upper(),
            "currentPrice": info.get('regularMarketPrice'),
            "trailingPE" :  info.get('trailingPE'),
            "sector" : info.get('sector', 'N/A'),
            "marketCap" : info.get("marketCap")
        }

        # Check for non-numeric PE ratio and return a friendly N/A if needed
        if data['trailingPE'] is None:
            data['trailingPE'] = 'N/A'

        return json.dumps(data)
    

    except Exception as e :
        return f"Financial Data Error: Could not retrieve market data for ticker '{ticker}'. It may be an invalid or unsupported symbol."



@tool
def news_search_tool(query: str, max_results: int = 3) -> str:
    """
    Performs a real-time, AI-optimized web search to retrieve the latest news and 
    sources relevant to a financial query. Use this tool when the user asks for 
    current news, articles, or market sentiment.

    Args:
        query: The specific search query (e.g., 'AAPL latest earnings news').
        max_results: The maximum number of relevant search results to return.

    Returns:
        A JSON string containing the title, URL, and content snippet of the 
        top results, or an error message.
    """

    async def async_search():
        return await official_tavily_search(
            query=query,
            search_depth="basic",
            topic="news",
            max_results=max_results
        )

    try:
        result = asyncio.run(async_search())
        
        if result.get("status") == "success":
            content_text = result["content"][0]["text"]
            import ast
            actual_data = ast.literal_eval(content_text)
            return json.dumps(actual_data)
        else:
            return json.dumps(result)
    
    except Exception as e:
        return f"Tavily Search Tool Error: Could not complete search for '{query}'. Ensure TAVILY_API_KEY is set. Error: {e}"
    





# =============================================================================
# AGENTS
# =============================================================================


@tool
async def data_analyst_agent(query: str) -> str:
    """
    Specialized agent for data identification and database management. 
    It resolves company names to official ticker symbols using a multi-step, 
    self-correction process (SQL Lookup -> Web Search -> Database Update).
    
    Args:
        query: The common company name (e.g., 'Big Fruit Corp' or 'Nvidia').

    Returns:
        The official stock ticker symbol as a string (e.g., 'AAPL'), 
        or the exact phrase 'TICKER_NOT_FOUND'.
    """
    
    # 1. Define the tools this specific agent can use
    # It needs ALL tools: the SQL tools for its main job, and the 
    # news agent for its self-correction backup plan.
    agent_tools = [sql_query_tool, sql_update_tool, news_research_agent]

    # 2. Define the agent's persona for the *first attempt* (SQL lookup)
    sql_agent = Agent(
        name="SQL_DataAnalyst",
        model=gpt_model,
        system_prompt=f"""
        You are a highly specialized SQL query agent. 
        Your task is to find the stock ticker for the company: {query}.
        
        Database schema:
        - ticker (TEXT): Stock ticker symbol
        - official_name (TEXT): Full company name  
        - common_name (TEXT): Common alias

        RULES:
        1. Use the `sql_query_tool` to search the 'company_metadata' table.
        2. Search both 'official_name' and 'common_name' columns.
        3. **CRITICAL:** If a ticker is found, you MUST return ONLY the ticker symbol (e.g., 'MSFT').
        4. **CRITICAL:** If no ticker is found, you MUST return ONLY the exact text: 'TICKER_NOT_FOUND'.
        
        **Do NOT add ANY conversational text, pre-amble, or explanation.**
        """,
        tools=[sql_query_tool], # Only give it the SQL tool for the first pass,
        callback_handler=None
    )

    try:
        # --- STEP A: Initial SQL Lookup ---
        # print(f"{Fore.CYAN}--- DataAnalyst: Attempting SQL Lookup for '{query}' ---{Style.RESET_ALL}")
        result = sql_agent(f"Find ticker for: {query}")
        initial_ticker = result.message["content"][0]["text"].strip()

        # --- STEP B: Check if the lookup was successful ---
        if initial_ticker != "TICKER_NOT_FOUND":
            # print(f"{Fore.GREEN}--- DataAnalyst: Found ticker '{initial_ticker}' in DB ---{Style.RESET_ALL}")
            return initial_ticker # Success! Return the ticker.
            
        # -----------------------------------------------------------
        # --- STEP C: SELF-CORRECTION / LEARNING LOOP ---
        # -----------------------------------------------------------
        # print(f"{Fore.RED}\n--- DataAnalyst: Ticker not in DB. Starting self-correction... ---{Style.RESET_ALL}")
        
        # 1. Use the News Agent to find the real ticker
        # print(f"{Fore.CYAN}--- DataAnalyst: Calling NewsResearchAgent to find ticker... ---{Style.RESET_ALL}")
        # We need a new agent prompt to find the ticker *and* official name
        
        research_prompt = f"""
        You are a financial data researcher. 
        Your ONLY goal is to find the official stock ticker and official 
        company name for: '{query}'.
        You MUST use the 'news_search_tool'.
        
        Return ONLY a JSON object with this exact format:
        {{"ticker": "FOUND_TICKER", "official_name": "FOUND_NAME"}}
        
        If you cannot find it, return:
        {{"ticker": "null", "official_name": "null"}}
        """
        
        research_agent = Agent(
            name="TickerFinder",
            model=gpt_model,
            system_prompt=research_prompt,
            tools=[news_search_tool],
            callback_handler=None
        )
        
        # We must 'await' the agent call because its tool is async
        research_result_str = (research_agent(f"Find ticker for {query}")).message["content"][0]["text"].strip()
        
        # 2. Parse the JSON result from the research
        research_data = json.loads(research_result_str)
        new_ticker = research_data.get("ticker")
        new_official_name = research_data.get("official_name")

        if new_ticker and new_ticker != "null":
            # print(f"{Fore.GREEN}--- DataAnalyst: Web search found Ticker: {new_ticker} ---{Style.RESET_ALL}")
            
            # 3. Use the SQL Update Tool to "learn"
            # print(f"{Fore.CYAN}--- DataAnalyst: Calling sql_update_tool to save new data... ---{Style.RESET_ALL}")
            update_result = sql_update_tool(
                ticker=new_ticker, 
                official_name=new_official_name, 
                common_name=query # Save the user's query as the new common_name
            )
            # print(f"{Fore.YELLOW}*** LEARNING COMPLETE: {update_result} ***{Style.RESET_ALL}")
            
            # 4. Return the newly found ticker
            return new_ticker
        else:
            # print(f"{Fore.RED}--- DataAnalyst: Web search could not find ticker. ---{Style.RESET_ALL}")
            return "TICKER_NOT_FOUND"

    except Exception as e:
        # print(f"{Fore.RED}Agent error (DataAnalyst): {e}{Style.RESET_ALL}")
        return "TICKER_NOT_FOUND_ERROR"




@tool
async def news_research_agent(ticker: str) -> str:
    """
    Specialized agent for fetching and summarizing real-time news headlines.
    Use this tool when the user requests current news or sentiment for a stock.
    
    NOTE: This function is 'async' because its tool 'news_search_tool' is async.

    Args:
        ticker: The official stock ticker symbol (e.g., 'GOOGL').

    Returns:
        A concise, paragraph-based summary of the latest news.
    """
    
    # 1. Define the tools this specific agent can use
    agent_tools = [news_search_tool] # The async Tavily tool
    
    # 2. Define the agent's persona and objective
    research_agent = Agent(
        name="NewsResearchAnalyst",
        model=gpt_model,
        system_prompt="""
        You are a world-class News Research Analyst. 
        Your task is to perform a web search for the provided ticker and 
        synthesize the results into a concise, professional summary (3-4 sentences).
        You MUST use the 'news_search_tool' and base your answer ONLY on the results.
        Do NOT add conversational pre-amble.
        """,
        tools=agent_tools,
        callback_handler=None

    )
    
    # 3. Run the agent and return the result
    try:
        # We give the agent a natural language query
        query = f"Latest news and market sentiment for {ticker}"
        
        # We must 'await' the agent call because its tool (news_search_tool) is async
        result = research_agent(query) 
        
        final_text = result.message["content"][0]["text"].strip()
        return final_text
    
    except Exception as e:
        # print(f"Agent error (NewsResearch): {e}")
        return f"Error fetching news: {e}"
    


@tool
def financial_metrics_agent(ticker: str) -> str:
    """
    Specialized agent for fetching live financial metrics.
    Use this tool ONLY when you have a confirmed, valid stock ticker 
    and need the latest Price-to-Earnings (P/E) ratio and current price.

    Args:
        ticker: The official stock ticker symbol (e.g., 'MSFT').

    Returns:
        A raw, unformatted JSON string from the 'financial_data_tool'.
    """
    
    # 1. Define the tools this specific agent can use
    agent_tools = [financial_data_tool] # Only the yfinance tool
    
    # 2. Define the agent's persona and objective (SUPER STRICT)
    metrics_agent = Agent(
        name="FinancialMetricsSpecialist",
        model=gpt_model, # Use the fixed OpenAI model loader
        system_prompt="""
        You are a robot. You have one task:
        1. You MUST call the 'financial_data_tool' with the user's ticker.
        2. You MUST return the tool's raw, unmodified JSON output.
        
        Do NOT add markdown, code blocks (```json), or any conversational text.
        Your entire response MUST be the JSON string from the tool.
        """,
        tools=agent_tools,
        callback_handler=None
    )
    
    # 3. Run the agent and return the result (SIMPLE LOGIC)
    try:
        # Let the agent run its full loop (no max_cycles=1)
        result = metrics_agent(ticker) 
        
        # Extract the final text message
        final_text = result.message["content"][0]["text"].strip()
        return final_text
    
    except Exception as e:
        # print(f"Agent error (FinancialMetrics): {e}")
        return f'{{"error": "Failed to fetch financial data: {e}"}}'
