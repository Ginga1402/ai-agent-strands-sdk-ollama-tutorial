"""
Professional Multi-Agent Financial Analyst CLI
Enhanced with colorama styling and professional UI components
"""


import asyncio
import sys
import time
import threading
import itertools
import os
from typing import Any, Dict, Optional
from colorama import Fore, Style, Back, init

# Strands Core Imports
from strands import Agent
from strands.models.openai import OpenAIModel

# Custom Agent Tools
from agent_tools import (
    data_analyst_agent,
    financial_metrics_agent,
    news_research_agent
)
from strands_tools import mem0_memory

from configuration import gpt_model



# Initialize colorama for cross-platform color support
init(autoreset=True)

# Environment setup
os.environ["POSTHOG_DISABLED"] = "1"

# Configure mem0 for local operation
# try:
#     mem0_memory.update_config({
#         "embedder": {
#             "provider": "local"
#         }
#     })
# except Exception as e:
#     print(f"{Fore.YELLOW}⚠️  Warning: Could not configure local embedder for mem0: {e}{Style.RESET_ALL}")

# try:
#     mem0_memory.update_config({
#         "embedder": {
#             "provider": "local"
#             # You can also specify a model, e.g.:
#             # "model": "all-MiniLM-L6-v2"
#         }
#     })
#     print(f"{Fore.GREEN}✅ mem0 configured for local embedding successfully.{Style.RESET_ALL}")
# except Exception as e:
#     print(f"{Fore.YELLOW}⚠️  Warning: Could not configure local embedder for mem0: {e}{Style.RESET_ALL}")


# =============================================================================
# PROFESSIONAL UI COMPONENTS
# =============================================================================

class EnhancedSpinner:
    """Professional animated spinner with customizable styling."""
    
    SPINNER_STYLES = {
        'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
        'braille': ['⣾', '⣷', '⣯', '⣟', '⡧', '⣏', '⣧', '⣼'],
        'arrows': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
        'pulse': ['●', '○', '●', '○']
    }
    
    def __init__(self, message: str = "Processing", style: str = 'braille', color: str = Fore.CYAN):
        self.spinner = itertools.cycle(self.SPINNER_STYLES.get(style, self.SPINNER_STYLES['braille']))
        self.delay = 0.1
        self.running = False
        self.message = message
        self.color = color
        self.thread = None

    def _animate(self):
        """Animation loop running in separate thread."""
        while self.running:
            frame = next(self.spinner)
            sys.stdout.write(f"\r{self.color}{frame} {Style.DIM}{self.message}...{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(self.delay)

    def start(self):
        """Start the spinner animation."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._animate, daemon=True)
            self.thread.start()

    def stop(self):
        """Stop the spinner and clear the line."""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=0.5)
            # Clear the spinner line
            sys.stdout.write(f"\r{' ' * (len(self.message) + 10)}\r")
            sys.stdout.flush()

class ProfessionalUI:
    """Professional UI components and styling utilities."""
    
    @staticmethod
    def print_header():
        """Display professional application header."""
        header_lines = [
            "╭─────────────────────────────────────────────────────────────────╮",
            "│                                                                 │",
            "│    🏦 Multi-Agent Financial Analyst                            │",
            "│    Powered by Strands AI Framework                             │",
            "│                                                                 │",
            "╰─────────────────────────────────────────────────────────────────╯"
        ]
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}")
        for line in header_lines:
            print(f"  {line}")
        print(f"{Style.RESET_ALL}")
        
        print(f"{Style.DIM}  Your AI specialists are ready to assist with financial analysis.")
        print(f"  Example: {Fore.WHITE}Compare P/E ratios of Apple and Google{Style.RESET_ALL}")
        print(f"{Style.DIM}  Commands: {Fore.CYAN}exit{Style.RESET_ALL}{Style.DIM} | {Fore.CYAN}quit{Style.RESET_ALL}{Style.DIM} | {Fore.CYAN}help{Style.RESET_ALL}\n")

    @staticmethod
    def print_separator(char: str = "─", length: int = 80, color: str = Fore.BLUE):
        """Print a styled separator line."""
        print(f"{color}{Style.DIM}{char * length}{Style.RESET_ALL}")

    @staticmethod
    def print_status(message: str, status_type: str = "info"):
        """Print styled status messages."""
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "thinking": "🤔"
        }
        
        colors = {
            "info": Fore.BLUE,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
            "thinking": Fore.MAGENTA
        }
        
        icon = icons.get(status_type, "•")
        color = colors.get(status_type, Fore.WHITE)
        
        print(f"{color}{icon} {message}{Style.RESET_ALL}")

    @staticmethod
    def print_tool_call(tool_name: str):
        """Display professional tool call notification."""
        print(f"{Style.DIM}  {Fore.BLUE}▶{Style.RESET_ALL} {Style.DIM}Calling specialist: {Fore.CYAN}{tool_name}{Style.RESET_ALL}")

    @staticmethod
    def print_analyst_header():
        """Display the lead analyst response header."""
        print(f"\n{Back.BLUE}{Fore.WHITE} 📊 Lead Financial Analyst {Style.RESET_ALL}")

class ProfessionalCallbackHandler:
    """Enhanced callback handler with professional styling and spinner management."""
    
    def __init__(self, spinner: EnhancedSpinner):
        self.spinner = spinner
        self.final_answer_started = False
        self.current_tool = ""
        self.ui = ProfessionalUI()

    def __call__(self, **kwargs: Any) -> None:
        """Handle agent callbacks with professional styling."""
        
        # Filter for Orchestrator events only
        if "Orchestrator" not in kwargs.get("agent_name", "Orchestrator"):
            return

        # Handle tool calls
        if "current_tool_use" in kwargs:
            tool_call = kwargs.get("current_tool_use", {})
            tool_name = tool_call.get("name", "Unknown Tool")
            
            # Display new tool calls
            if tool_name and tool_name != self.current_tool:
                self.current_tool = tool_name
                self.spinner.stop()
                self.ui.print_tool_call(tool_name)
                self.spinner.start()

        # Handle final answer streaming
        elif "data" in kwargs and "tool_result" not in kwargs:
            token = kwargs.get("data", "")
            if isinstance(token, str):
                # Stop spinner and show analyst header
                if not self.final_answer_started:
                    self.spinner.stop()
                    self.ui.print_analyst_header()
                    self.final_answer_started = True
                
                # Stream the response with professional styling
                print(f"{Fore.WHITE}{token}{Style.RESET_ALL}", end="", flush=True)

    def reset(self):
        """Reset handler state for new query."""
        self.final_answer_started = False
        self.current_tool = ""



# =============================================================================
# ORCHESTRATOR AGENT
# =============================================================================



def create_orchestrator(callback_handler: ProfessionalCallbackHandler) -> Optional[Agent]:
    """Create the main orchestrator agent with professional configuration."""
    
    model = gpt_model #get_openai_model()
    if not model:
        return None
    
    specialist_tools = [
        data_analyst_agent,
        financial_metrics_agent,
        news_research_agent,
        mem0_memory
    ]

    system_prompt = """
    You are the Lead Financial Analyst, a sophisticated AI orchestrator managing a team of specialist agents.
    Your mission is to provide comprehensive financial analysis by coordinating with your specialist team.

    🎯 SPECIALIST TEAM:
    
    1. data_analyst_agent:
       • Primary function: Convert company names to stock tickers
       • Usage: Call FIRST for any company name resolution
       • Input: Company name (e.g., "Apple", "Microsoft")
       • Output: Stock ticker (e.g., "AAPL", "MSFT")

    2. financial_metrics_agent:
       • Primary function: Retrieve live financial metrics
       • Usage: Call AFTER obtaining ticker from data_analyst_agent
       • Input: Stock ticker (e.g., "AAPL")
       • Output: Financial data (P/E ratio, price, market cap, etc.)

    3. news_research_agent:
       • Primary function: Gather and summarize latest news
       • Usage: Call AFTER obtaining ticker from data_analyst_agent
       • Input: Stock ticker (e.g., "AAPL")
       • Output: Summarized news analysis

    4. mem0_memory:
       • Primary function: Store and retrieve user preferences
       • Usage: Remember user preferences and context
       • Critical: Always use user_id from invocation_state
       • Example: mem0_memory(action="store", content="User prefers P/E analysis", user_id=invocation_state["user_id"])

    🔄 WORKFLOW PROTOCOL:
    1. Parse user query and identify required companies/tickers
    2. Use data_analyst_agent to resolve all company names to tickers
    3. Execute parallel calls to financial_metrics_agent and news_research_agent as needed
    4. Synthesize all data into a comprehensive, professional response
    5. Store relevant preferences using mem0_memory when appropriate

    📋 RESPONSE STANDARDS:
    • Always provide a complete, synthesized final answer
    • Include relevant financial metrics with context
    • Highlight key insights and comparisons
    • Use professional financial terminology
    • Ensure accuracy and cite data sources when possible
    """

    try:
        orchestrator = Agent(
            name="Orchestrator",
            model=model,
            system_prompt=system_prompt,
            tools=specialist_tools,
            callback_handler=callback_handler
        )
        return orchestrator
    except Exception as e:
        print(f"{Fore.RED}❌ Error creating orchestrator: {e}{Style.RESET_ALL}")
        return None



# =============================================================================
# MAIN APPLICATION
# =============================================================================

async def main():
    """Main application entry point with professional CLI interface."""
    
    ui = ProfessionalUI()
    ui.print_header()
    
    # Initialize components
    spinner = EnhancedSpinner("Orchestrator is analyzing", style='braille', color=Fore.CYAN)
    callback_handler = ProfessionalCallbackHandler(spinner)
    
    # Create orchestrator
    ui.print_status("Initializing AI specialists...", "info")
    orchestrator = create_orchestrator(callback_handler)
    
    if not orchestrator:
        ui.print_status("Failed to initialize orchestrator agent", "error")
        return
    
    ui.print_status("All specialists ready for financial analysis", "success")
    ui.print_separator()
    
    # Session configuration
    USER_ID = "financial-analyst-user"
    
    # Main interaction loop
    while True:
        try:
            # Reset handler state
            callback_handler.reset()
            
            # Get user input with professional prompt
            user_query = input(f"\n{Fore.CYAN}💼 {Style.BRIGHT}Financial Query{Style.RESET_ALL} {Fore.WHITE}▶{Style.RESET_ALL} ")
            
            # Handle exit commands
            if user_query.lower() in ["exit", "quit", "q"]:
                ui.print_status("Thank you for using Financial Analyst AI", "success")
                break
            
            # Handle help command
            if user_query.lower() in ["help", "h"]:
                print(f"\n{Fore.YELLOW}📖 Available Commands:{Style.RESET_ALL}")
                print(f"  • {Fore.CYAN}Compare P/E ratios of Apple and Google{Style.RESET_ALL}")
                print(f"  • {Fore.CYAN}Get latest news for Tesla{Style.RESET_ALL}")
                print(f"  • {Fore.CYAN}What is Microsoft's current stock price?{Style.RESET_ALL}")
                print(f"  • {Fore.CYAN}help{Style.RESET_ALL} - Show this help")
                print(f"  • {Fore.CYAN}exit{Style.RESET_ALL} - Exit application")
                continue
            
            # Skip empty queries
            if not user_query.strip():
                continue
            
            # Process query
            spinner.start()
            
            try:
                result = orchestrator(
                    user_query,
                    invocation_state={"user_id": USER_ID}
                )
                
                spinner.stop()
                print("\n")  # Clean spacing after response
                
            except Exception as e:
                spinner.stop()
                ui.print_status(f"Analysis error: {str(e)}", "error")
                
        except KeyboardInterrupt:
            spinner.stop()
            ui.print_status("Operation cancelled by user", "warning")
            continue
            
        except Exception as e:
            spinner.stop()
            ui.print_status(f"Unexpected error: {str(e)}", "error")

def run_application():
    """Application runner with proper error handling."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}👋 Shutting down Financial Analyst AI...{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    run_application()


