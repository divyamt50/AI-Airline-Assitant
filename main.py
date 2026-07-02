import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import gradio as gr
from models import *
from ticket_prices import ticket_prices_map
from database import engine, get_session
from fastapi import Depends
import asyncio
from sqlalchemy import select

load_dotenv()

GROQ_API_KEY= os.getenv("GROQ_API_KEY")
GROQ_BASE_URL= os.getenv("GROQ_BASE_URL")
GROQ_MODEL= os.getenv("GROQ_MODEL")
GRADIO_PASSWORD= os.getenv("GRADIO_PASSWORD")

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url=GROQ_BASE_URL   
)

system_prompt = '''
You are a helpful assistant for an Airline called FlightAI.
Give short, courteous answers, no more than 1 sentence.
Always be accurate. If you don't know the answer, say so.
'''

system_message = [{"role":"system", "content":system_prompt}]


'''
1 - make the function to make the table and insert//
2 - make the tools//
3 - make the tool call function
4 - make the get prices function//
5 - make the chat function
'''


async def create_and_insert():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async for session in get_session():
        for item in ticket_prices_map:
            for city, price in item.items():
                stmt = select(TicketPrices).where(TicketPrices.city_name == city)
                existing = (await session.execute(stmt)).scalar_one_or_none()
                if not existing:
                    ticket_price = TicketPrices(city_name = city, price = price)
                    session.add(ticket_price)
        await session.commit()

asyncio.run(create_and_insert())

async def get_ticket_price_by_city(city_name:str):
    async for session in get_session():
        result = await session.execute(select(TicketPrices)
                                       .where(TicketPrices.city_name == city_name))
        ticket = result.scalar_one_or_none()

        if not result:
            raise ValueError(f"No ticket price found for the {city_name}")

        return ticket.price

tools = [
    {
        "type":"function",
        "function":{
            "name":"get_ticket_price_by_city",
            "description":"fetches ticket price",
            "parameters":{
                "type":"object",
                "properties":{
                    "city":{
                        "type": "string",
                        "description":"The name of the destination city"
                    }
                },
                "required":["city"]
            }
        }
    }
]

async def chat(message, history):
    formatted_history = []

    for h in history:
        history.append({"role":h.get("role"), "content":h.get("content")})

    messages = system_message + formatted_history + [{"role":"user", "content":message}]

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    relevant_response = resp.choices[0].message

    while relevant_response.tool_calls:
        tool_responses = await call_tool(relevant_response)
        messages.append(relevant_response)
        messages.extend(tool_responses)

        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            tools=tools,           
            tool_choice="auto"
        )

        relevant_response = resp.choices[0].message
    return relevant_response.content or "I'm sorry, I couldn't formulate a response."

async def call_tool(message):
    responses = []
    for tool_call in message.tool_calls:
        if tool_call.function.name == "get_ticket_price_by_city":
            arguments = json.loads(tool_call.function.arguments)
            city = arguments.get("city")
            price_detail = await get_ticket_price_by_city(city)

            responses.append( {
                "role":"tool",
                "content":str(price_detail),
                "tool_call_id":tool_call.id
            })
    return responses

gr.ChatInterface(fn=chat).launch(inbrowser=True)