import logging
import os
import smtplib
import subprocess
import webbrowser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from urllib.parse import quote

import requests
import yfinance as yf
from newsapi import NewsApiClient
from langchain_community.tools import DuckDuckGoSearchRun
from livekit.agents import RunContext, function_tool

# Try importing spotipy — use it if premium is confirmed working,
# otherwise fall back to webbrowser URL launch
try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    SPOTIPY_AVAILABLE = True
except ImportError:
    SPOTIPY_AVAILABLE = False


# ─────────────────────────────────────────────
# WEATHER
# ─────────────────────────────────────────────
@function_tool()
async def get_weather(context: RunContext, city: str) -> str:
    """Get the current weather for a given city.
    Args:
        city: Name of the city to get weather for.
    """
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3")
        if response.status_code == 200:
            raw = response.text.strip()
            if ":" in raw:
                raw = raw.split(":", 1)[1].strip()
            clean = (
                raw
                .replace("°C", " degrees Celsius")
                .replace("°F", " degrees Fahrenheit")
                .replace("+", "")
                .replace("⛅️", "").replace("🌧️", "").replace("☀️", "")
                .replace("🌩️", "").replace("❄️", "").replace("🌫️", "")
                .replace("🌦️", "").replace("⛈️", "").replace("🌤️", "")
                .replace("🌥️", "").strip()
            )
            return f"The current weather in {city} is {clean}."
        return f"I was unable to retrieve the weather for {city} at the moment, sir."
    except Exception as e:
        logging.error(f"Weather error: {e}")
        return f"I ran into an error fetching the weather for {city}, boss."


# ─────────────────────────────────────────────
# WEB SEARCH
# ─────────────────────────────────────────────
@function_tool()
async def search_web(context: RunContext, query: str) -> str:
    """Search the web for a given query using DuckDuckGo.
    Args:
        query: The search query string.
    """
    try:
        results = DuckDuckGoSearchRun().run(tool_input=query)
        if len(results) > 500:
            results = results[:500].rsplit(" ", 1)[0] + "."
        return results
    except Exception as e:
        logging.error(f"Search error: {e}")
        return "I hit a snag searching for that one, boss. Try again in a moment."


# ─────────────────────────────────────────────
# SEND EMAIL
# ─────────────────────────────────────────────
@function_tool()
async def send_email(
    context: RunContext,
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None,
) -> str:
    """Send an email through Gmail SMTP.
    Args:
        to_email: Recipient email address.
        subject: Subject of the email.
        message: Body of the email.
        cc_email: Optional CC email address.
    """
    try:
        sender_email = os.environ["Gmail_Address"]
        sender_password = os.environ["Gmail_App_Password"]
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        if cc_email:
            msg["Cc"] = cc_email
        msg.attach(MIMEText(message, "plain"))
        recipients = [to_email] + ([cc_email] if cc_email else [])
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, msg.as_string())
        return f"Email sent successfully to {to_email}, sir."
    except KeyError as e:
        return f"Email config error, boss. Missing environment variable {str(e)}."
    except Exception as e:
        logging.error(f"Email error: {e}")
        return f"I ran into a problem sending that email, sir. {str(e)}"


# ─────────────────────────────────────────────
# SPOTIFY — Dual mode: API (premium) or URL fallback
# ─────────────────────────────────────────────
@function_tool()
async def play_spotify(context: RunContext, song: str, artist: str = "") -> str:
    """Search and play a song on Spotify.
    Args:
        song: The name of the song to play. Example: 'Thunderstruck'.
        artist: The artist name. Example: 'ACDC'. Leave empty if unknown.
    """
    # Build a precise query using Spotify's field filters
    if artist:
        query = f"track:{song} artist:{artist}"
    else:
        query = f"track:{song}"

    # ── Method 1: Spotipy API (requires confirmed premium) ──
    if SPOTIPY_AVAILABLE:
        try:
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=os.environ["SPOTIFY_CLIENT_ID"],
                client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
                redirect_uri=os.environ["SPOTIFY_REDIRECT_URI"],
                scope="user-modify-playback-state user-read-playback-state",
            ))

            results = sp.search(q=query, type="track", limit=1)
            tracks = results.get("tracks", {}).get("items", [])

            # If precise search found nothing, fall back to plain text search
            if not tracks:
                fallback_query = f"{song} {artist}".strip()
                results = sp.search(q=fallback_query, type="track", limit=1)
                tracks = results.get("tracks", {}).get("items", [])

            if tracks:
                track = tracks[0]
                track_uri = track["uri"]
                track_name = track["name"]
                artist_name = track["artists"][0]["name"]

                devices = sp.devices().get("devices", [])
                if devices:
                    device_id = devices[0]["id"]
                    sp.start_playback(device_id=device_id, uris=[track_uri])
                    return f"Playing {track_name} by {artist_name} on Spotify now, boss."

            # Track found but no device — fall through to URL method
        except Exception as e:
            logging.warning(f"Spotipy API failed, falling back to URL method: {e}")

    # ── Method 2: URL fallback — opens Spotify search in browser ──
    try:
        plain_query = f"{song} {artist}".strip()
        encoded_query = quote(plain_query)
        spotify_url = f"spotify:search:{encoded_query}"
        web_url = f"https://open.spotify.com/search/{encoded_query}"

        try:
            subprocess.Popen(["start", spotify_url], shell=True)
        except Exception:
            webbrowser.open(web_url)

        return f"Opening Spotify and searching for {plain_query}, sir. You may need to hit play."

    except Exception as e:
        logging.error(f"Spotify URL fallback error: {e}")
        return f"I had trouble opening Spotify, boss. Try opening it manually and searching for {query}."


# ─────────────────────────────────────────────
# STOCK PRICE
# ─────────────────────────────────────────────
@function_tool()
async def get_stock_price(context: RunContext, symbol: str) -> str:
    """Get the current stock price for a given ticker symbol.
    Args:
        symbol: Stock ticker. Examples: AAPL, TSLA, RELIANCE.NS, TCS.NS, INFY.NS
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.fast_info
        price = info.last_price
        currency = getattr(info, "currency", "USD")

        if price is None:
            return f"I could not find a price for {symbol}, sir. Please check the ticker symbol."

        return f"{symbol.upper()} is currently trading at {price:.2f} {currency}, sir."
    except Exception as e:
        logging.error(f"Stock error: {e}")
        return f"I had trouble fetching the stock price for {symbol}, boss."


# ─────────────────────────────────────────────
# GLOBAL NEWS
# ─────────────────────────────────────────────
@function_tool()
async def get_global_news(context: RunContext) -> str:
    """Get the latest top global headlines."""
    try:
        client = NewsApiClient(api_key=os.environ["NEWS_API_KEY"])
        response = client.get_top_headlines(language="en", page_size=5)
        articles = response.get("articles", [])

        if not articles:
            return "I could not retrieve global headlines at the moment, sir."

        headlines = [a["title"] for a in articles if a.get("title")]
        summary = ". Next, ".join(headlines[:5])
        return f"Here are the top global headlines, sir. {summary}."
    except Exception as e:
        logging.error(f"Global news error: {e}")
        return "I had trouble fetching global news, boss."


# ─────────────────────────────────────────────
# INDIAN NEWS
# ─────────────────────────────────────────────
@function_tool()
async def get_indian_news(context: RunContext) -> str:
    """Get the latest top news headlines from India."""
    try:
        client = NewsApiClient(api_key=os.environ["NEWS_API_KEY"])
        response = client.get_top_headlines(country="in", language="en", page_size=5)
        articles = response.get("articles", [])

        if not articles:
            return "I could not retrieve Indian headlines at the moment, sir."

        headlines = [a["title"] for a in articles if a.get("title")]
        summary = ". Next, ".join(headlines[:5])
        return f"Here are the top headlines from India, sir. {summary}."
    except Exception as e:
        logging.error(f"Indian news error: {e}")
        return "I had trouble fetching Indian news, boss."