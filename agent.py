from dotenv import load_dotenv

from livekit import agents
from livekit.agents import (
    AgentServer,
    AgentSession,
    Agent,
    inference,
    room_io,
)

from livekit.plugins import silero, groq

from prompt import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import get_weather, search_web, send_email

load_dotenv(".env")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            tools=[get_weather, search_web, send_email],
        )


server = AgentServer()


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: agents.JobContext):

    session = AgentSession(

        # Speech-to-Text
        stt=inference.STT(
            model="deepgram/nova-3",
            language="en",
        ),

        # ✅ Switched to llama-3.1-8b-instant which handles tool-use
        # flow in voice much more cleanly than 70b-versatile.
        # 70b tends to narrate its own function calls out loud.
        llm=groq.LLM(
            model="llama-3.1-8b-instant",
            temperature=0.7,
        ),

        # Text-to-Speech
        tts=inference.TTS(
            model="cartesia/sonic-3",
            voice="79a125e8-cd45-4c13-8a67-188112f4dd22",
        ),

        # Voice Activity Detection
        vad=silero.VAD.load(),

        # Prevent FRIDAY from hearing herself and re-triggering
        allow_interruptions=False,
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            video_input=True,
        ),
    )

    await session.generate_reply(
        instructions=SESSION_INSTRUCTION
    )


if __name__ == "__main__":
    agents.cli.run_app(server)