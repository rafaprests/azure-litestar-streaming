from agents import Agent, ModelSettings, Runner 
import logging
from openai.types.responses import ResponseTextDeltaEvent
logger = logging.getLogger("stream-debug")

agent = Agent(
    name="agent",
    instructions="You are an AI agent that assists with various tasks.",
    model="gpt-4o",
    model_settings=ModelSettings(temperature=0, max_tokens=2048),
    tools=[]
)

async def bot_request(input_text: str):
    logger.debug("iniciando streaming")

    response = Runner.run_streamed(agent, input_text)
    logger.debug(f"response: {response}")

    async for event in response.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            yield f"data: {event.data.delta}\n\n"

    yield "data: [DONE]\n\n"
