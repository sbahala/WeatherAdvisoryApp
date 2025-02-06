from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

app = FastAPI()

# Enable CORS to allow frontend requests from React (http://localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change "*" to specific frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# LangChain model
chat_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# Memory for conversation
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Weather API function
def get_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        weather_desc = data["weather"][0]["description"]
        return f"The temperature in {city} is {temp}°C with {weather_desc}."
    return "Could not retrieve weather data."

# Custom Tool for LangChain
weather_tool = Tool(
    name="Weather Info",
    func=get_weather,
    description="Provides weather information based on city name."
)

# Initialize LangChain Agent
agent_executor = initialize_agent(
    tools=[weather_tool],
    llm=chat_model,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)

# Request Model
class WeatherRequest(BaseModel):
    city: str

# Explicitly Handle OPTIONS Requests (Fix for 405 Error)
@app.options("/get_weather")
async def options_get_weather(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Main Endpoint
@app.post("/get_weather")
async def get_weather_info(request: WeatherRequest):
    weather_info = get_weather(request.city)
    response = agent_executor.run(f"Based on the weather: {weather_info}, what type of clothing should someone wear?")
    return {"weather_info": weather_info, "recommendation": response}
