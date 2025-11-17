from agents import Agent, ModelSettings, Runner

agent = Agent(
    name="agent",
    instructions="You are an AI agent that assists with various tasks.",
    model="gpt-4o",
    model_settings=ModelSettings(temperature=0, max_tokens=2048),
    tools=[]
)

async def bot_request(input_text: str) -> str:
    response = await Runner.run(agent, input_text)
    return response