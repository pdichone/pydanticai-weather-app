from dataclasses import dataclass
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext


@dataclass
class TravelDependencies:
    user_id: int
    user_preferences: dict  # User preferences like preferred airline, hotel type, etc.


class TravelPlan(BaseModel):
    destination: str = Field(description="The travel destination")
    dates: str = Field(description="The dates of travel")
    budget: float = Field(description="The user's travel budget")
    itinerary: str = Field(description="The suggested itinerary for the trip")


travel_agent = Agent(
    "openai:gpt-4o",
    deps_type=TravelDependencies,
    result_type=TravelPlan,
    system_prompt=(
        "You are a travel assistant. Based on the user's preferences and input, "
        "generate a detailed travel plan that includes the destination, travel dates, budget, "
        "and a suggested itinerary tailored to their preferences."
    ),
)


@travel_agent.system_prompt
async def add_user_preferences(ctx: RunContext[TravelDependencies]) -> str:
    preferences = ctx.deps.user_preferences
    preferred_airline = preferences.get("preferred_airline", "any airline")
    hotel_type = preferences.get("hotel_type", "standard hotels")
    return (
        f"The user prefers to travel with {preferred_airline} and stay in {hotel_type}."
    )


@travel_agent.tool
async def available_flights(
    ctx: RunContext[TravelDependencies], destination: str, dates: str
) -> list:
    """Returns a list of available flights for the given destination and dates."""
    # Mock implementation for available flights
    return [
        {"flight_number": "DL123", "airline": "Delta", "price": 350},
        {"flight_number": "AF456", "airline": "Air France", "price": 400},
    ]


@travel_agent.tool
async def available_hotels(
    ctx: RunContext[TravelDependencies], destination: str, dates: str
) -> list:
    """Returns a list of available hotels for the given destination and dates."""
    # Mock implementation for available hotels
    return [
        {"hotel_name": "Eiffel Boutique", "price_per_night": 150},
        {"hotel_name": "Paris Luxury Stay", "price_per_night": 300},
    ]


async def main():
    # Example dependencies
    deps = TravelDependencies(
        user_id=123,
        user_preferences={"preferred_airline": "Delta", "hotel_type": "Boutique"},
    )

    # Example query 1: Planning a trip
    # result = await travel_agent.run(
    #     "Plan a trip to Paris for next month under $1500.", deps=deps
    # )
    # print(result.data)
    # """
    # {
    #     "destination": "Paris",
    #     "dates": "2024-01-10 to 2024-01-15",
    #     "budget": 1500.0,
    #     "itinerary": "Day 1: Arrival and city tour; Day 2: Visit Louvre; Day 3: Eiffel Tower; Day 4: Departure."
    # }
    # """

    # Example query 2: Specific details
    result = await travel_agent.run("What are my flight options to Paris?", deps=deps)
    print(result.data)
    """
    [
        {"flight_number": "DL123", "airline": "Delta", "price": 350},
        {"flight_number": "AF456", "airline": "Air France", "price": 400}
    ]
    """


# Run the main function if this script is executed
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
