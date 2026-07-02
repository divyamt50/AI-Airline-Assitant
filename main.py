import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import gradio as gr
from models import *
from ticket_prices import ticket_prices_map
from database import AsyncSession, get_session
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
    async for session in get_session():

        for city, price in ticket_prices_map.items():
            ticket_price = TicketPrices(
                city = city,
                price = price
            )
            await session.commit(ticket_price)
    return "ticket prices added"


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
    history = [{"role":h["role"], "content":h["content"]} for h in history]

    messages = system_message + history + [{"role":"user", "content":message}]

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    relevant_response = resp.choices[0].message

    if relevant_response.tool_calls:
        response = list(await call_tool(relevant_response))
        messages.append(relevant_response)
        messages.extend(response)

        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages
        )

        if resp.choices[0].delta.content:
            for chunk in resp.choices[0].delta.content:
                yield chunk

async def call_tool(message):
    tool_call = message.tool_calls[0]
    if tool_call.function.name == "get_ticket_price_by_city":
        arguments = json.load(tool_call.function.arguments)
        city = arguments.get("city_name")
        response = await get_ticket_price_by_city(city)

        return {
            "role":"tool",
            "content":response,
            "tool_call_id":tool_call.id
        }
