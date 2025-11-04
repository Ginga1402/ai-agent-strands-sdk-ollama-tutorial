from strands.models.openai import OpenAIModel
import os


## Configurations and Keys
DB_FILE = 'financial_data.db'

TAVILY_API_KEY = "YOUR-TAVILY-KEY"

OPENAI_KEY = "YOUR-OPENAI-KEY"

os.environ['OPENAI_API_KEY'] = OPENAI_KEY
gpt_model = OpenAIModel(model_id = "gpt-3.5-turbo", 
                        temperature = 0.0,
                        params={
                        "temperature": 0.0 
                        })




