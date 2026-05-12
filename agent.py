from dotenv import load_dotenv
import asyncio
import time
import logging
import numpy as np

from livekit import agents, rtc
from livekit.agents import (
    AgentServer,
    AgentSession,
    Agent,
    inference,
    room_io,
)

from livekit.plugins import silero, groq

from prompt import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import (
    get_weather,
    search_web,
    send_email,
    play_spotify,
    get_stock_price,
    get_global_news,
    get_indian_news,
)

load_dotenv(".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("friday")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            tools=[
                get_weather,
                search_web,
                send_email,
                play_spotify,
                get_stock_price,
                get_global_news,
                get_indian_news,
            ],
        )


server = AgentServer()


# ─────────────────────────────────────────────
# CLAP DETECTOR
# Runs on a SEPARATE audio stream from the main
# session so it never blocks STT or VAD
# ─────────────────────────────────────────────
class ClapDetector:
    def __init__(
        self,
        threshold: int = 800,
        min_gap: float = 0.15,
        max_gap: float = 1.5,
        cooldown: float = 2.0,
    ):
        self.threshold = threshold
        self.min_gap = min_gap
        self.max_gap = max_gap
        self.cooldown = cooldown
        self._last_clap_time: float | None = None
        self._last_triggered: float = 0.0
        self._in_clap: bool = False
        self._silence_frames: int = 0
        self.on_double_clap = None
        self._debug_max: int = 0
        self._debug_last_print: float = time.monotonic()

    def process_frame(self, frame: rtc.AudioFrame):
        samples = np.frombuffer(frame.data, dtype=np.int16)
        amplitude = int(np.abs(samples).mean())
        now = time.monotonic()

        # Print peak amplitude every 5s so you can tune threshold
        self._debug_max = max(self._debug_max, amplitude)
        if now - self._debug_last_print >= 5.0:
            logger.info(f"[Clap] Peak amplitude: {self._debug_max} | threshold: {self.threshold}")
            self._debug_max = 0
            self._debug_last_print = now

        if amplitude > self.threshold:
            if not self._in_clap:
                self._in_clap = True
                self._silence_frames = 0
                logger.info(f"[Clap] Onset detected amplitude={amplitude}")
                if self._last_clap_time is None:
                    self._last_clap_time = now
                    logger.info("[Clap] First clap — waiting for second...")
                else:
                    gap = now - self._last_clap_time
                    if self.min_gap <= gap <= self.max_gap:
                        if (now - self._last_triggered) > self.cooldown:
                            logger.info("[Clap] ✅ Double clap! Triggering FRIDAY...")
                            self._last_triggered = now
                            self._last_clap_time = None
                            if self.on_double_clap:
                                asyncio.ensure_future(self.on_double_clap())
                    elif gap > self.max_gap:
                        self._last_clap_time = now
        else:
            if self._in_clap:
                self._silence_frames += 1
                if self._silence_frames >= 3:
                    self._in_clap = False
                    self._silence_frames = 0
            if self._last_clap_time and (now - self._last_clap_time) > self.max_gap:
                self._last_clap_time = None


def attach_clap_detector(track: rtc.Track, detector: ClapDetector):
    """
    Creates its own AudioStream separate from the session's STT stream.
    This is safe — LiveKit allows multiple consumers of the same track.
    """
    audio_stream = rtc.AudioStream(
        track=track,
        sample_rate=48000,
        num_channels=1,
    )

    async def _read():
        logger.info(f"[Clap] Listening on track {track.sid}")
        async for event in audio_stream:
            detector.process_frame(event.frame)

    # Run as a background task — does NOT block session audio pipeline
    asyncio.ensure_future(_read())


# ─────────────────────────────────────────────
# RTC SESSION
# ─────────────────────────────────────────────
@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: agents.JobContext):

    session = AgentSession(
        stt=inference.STT(
            model="deepgram/nova-3",
            language="en",
        ),
        llm=groq.LLM(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
        ),
        tts=inference.TTS(
            model="cartesia/sonic-3",
            voice="79a125e8-cd45-4c13-8a67-188112f4dd22",
        ),
        vad=silero.VAD.load(),

        # ✅ allow_interruptions=True so STT stays active
        # and FRIDAY can hear you while she is not speaking
        allow_interruptions=True,
    )

    clap_detector = ClapDetector(threshold=800)
    briefing_given = False

    async def on_double_clap():
        nonlocal briefing_given
        if briefing_given:
            return
        briefing_given = True
        await session.generate_reply(
            instructions=(
                "The boss just double-clapped to activate you. "
                "Greet them with your FRIDAY personality, then give a morning briefing: "
                "call get_global_news for top global headlines, "
                "call get_indian_news for top Indian headlines, "
                "call get_stock_price for AAPL then TSLA then RELIANCE.NS, "
                "then offer to play music. "
                "Deliver everything naturally in your voice. "
                "No raw symbols, no colons, no function names out loud."
            )
        )

    clap_detector.on_double_clap = on_double_clap

    # Attach to already-present tracks
    for participant in ctx.room.remote_participants.values():
        for publication in participant.track_publications.values():
            if (
                publication.track is not None
                and publication.kind == rtc.TrackKind.KIND_AUDIO
            ):
                attach_clap_detector(publication.track, clap_detector)

    # Attach to future tracks
    @ctx.room.on("track_subscribed")
    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.RemoteTrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            logger.info(f"[Clap] New track from {participant.identity}")
            attach_clap_detector(track, clap_detector)

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