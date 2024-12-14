from __future__ import annotations as _annotations

import asyncio
from datetime import datetime
import os
from dataclasses import dataclass
import pprint
from typing import Any

from dotenv import load_dotenv
import logfire
from devtools import debug
from httpx import AsyncClient

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic import BaseModel, Field

from tavily import TavilyClient, AsyncTavilyClient  #

load_dotenv()

# Setup the Tavily Client
tavily_client = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire="if-token-present")

# Get the current date
current_date = datetime.date(datetime.now())

# Convert the date to a string
date_string = current_date.strftime("%Y-%m-%d")


@dataclass
class Deps:
    client: AsyncClient
    weather_api_key: str | None
    geo_api_key: str | None
    tavily_api_key: str | None
    max_results: int = 5
    todays_date: str = date_string  # to get current news!


@dataclass
class SearchDataclass:
    max_results: int
    todays_date: str


weather_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="""
    Be concise, reply with one sentence. 
    and then, write the weather in the location, as well as giving the temperature in both celsius and farenheit. 
    Also, show the lat and long of the location.
    Make sure to include emojis to make the response more engaging.
    write also a short Heroku style poem about the weather as well as the top 5 news articles for the day in the location.
""",
    deps_type=Deps,
    # added this
    # result_type=WeatherResult,
    retries=2,
)


@weather_agent.tool
async def get_lat_lng(
    ctx: RunContext[Deps], location_description: str
) -> dict[str, float]:
    """
    Get the latitude and longitude of a location.

    Args:
        ctx: The context.
        location_description: A description of a location.
    """
    if ctx.deps.geo_api_key is None:
        return {"lat": 40.7128, "lng": -74.0060}

    params = {
        "q": location_description,
        "api_key": ctx.deps.geo_api_key,
    }
    with logfire.span("calling geocode API", params=params) as span:
        r = await ctx.deps.client.get("https://geocode.maps.co/search", params=params)
        r.raise_for_status()
        data = r.json()
        span.set_attribute("response", data)

    if data:
        return {"lat": data[0]["lat"], "lng": data[0]["lon"]}
    else:
        raise ModelRetry("Could not find the location")


@weather_agent.tool
async def get_weather(ctx: RunContext[Deps], lat: float, lng: float) -> dict[str, Any]:
    """Get the weather at a location.

    Args:
        ctx: The context.
        lat: Latitude of the location.
        lng: Longitude of the location.
    """
    if ctx.deps.weather_api_key is None:
        # if no API key is provided, return a dummy response
        return {"temperature": "21 °C", "description": "Sunny"}

    params = {
        "apikey": ctx.deps.weather_api_key,
        "location": f"{lat},{lng}",
        "units": "metric",
    }
    with logfire.span("calling weather API", params=params) as span:
        r = await ctx.deps.client.get(
            "https://api.tomorrow.io/v4/weather/realtime", params=params
        )
        r.raise_for_status()
        data = r.json()
        span.set_attribute("response", data)

    values = data["data"]["values"]
    # https://docs.tomorrow.io/reference/data-layers-weather-codes
    code_lookup = {
        1000: "Clear, Sunny",
        1100: "Mostly Clear",
        1101: "Partly Cloudy",
        1102: "Mostly Cloudy",
        1001: "Cloudy",
        2000: "Fog",
        2100: "Light Fog",
        4000: "Drizzle",
        4001: "Rain",
        4200: "Light Rain",
        4201: "Heavy Rain",
        5000: "Snow",
        5001: "Flurries",
        5100: "Light Snow",
        5101: "Heavy Snow",
        6000: "Freezing Drizzle",
        6001: "Freezing Rain",
        6200: "Light Freezing Rain",
        6201: "Heavy Freezing Rain",
        7000: "Ice Pellets",
        7101: "Heavy Ice Pellets",
        7102: "Light Ice Pellets",
        8000: "Thunderstorm",
    }
    return {
        "temperature": f'{values["temperatureApparent"]:0.0f}°C',
        "description": code_lookup.get(values["weatherCode"], "Unknown"),
    }


@weather_agent.tool
async def search_news(
    search_data: RunContext[SearchDataclass], query: str, query_number: int
) -> dict[str, Any]:
    """Get the search for a keyword query.

    Args:
        query: keywords to search.
    """
    print(f"Search query {query_number}: {query}")
    max_results = search_data.deps.max_results
    results = await tavily_client.get_search_context(
        query=f"News in {query}", max_results=max_results
    )

    return results


async def main():

    # create a free API key at https://www.tomorrow.io/weather-api/
    weather_api_key = os.getenv("WEATHER_API_KEY")
    # create a free API key at https://geocode.maps.co/
    geo_api_key = os.getenv("GEO_API_KEY")
    taviy_api_key = os.getenv("TAVILY_API_KEY")

    deps = Deps(
        client=AsyncClient(),
        weather_api_key=weather_api_key,
        geo_api_key=geo_api_key,
        tavily_api_key=taviy_api_key,
    )
    result = await weather_agent.run("What is the weather like in London?", deps=deps)
    pprint.pprint(result)


if __name__ == "__main__":
    asyncio.run(main())
