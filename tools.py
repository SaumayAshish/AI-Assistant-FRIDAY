import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import requests
from langchain_community.tools import DuckDuckGoSearchRun
from livekit.agents import RunContext, function_tool


@function_tool()
async def get_weather(
    context: RunContext,
    city: str,
) -> str:
    """
    Get the current weather for a given city.

    Args:
        city: Name of the city to get weather for.
    """
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3")
        if response.status_code == 200:
            raw = response.text.strip()
            logging.info(f"Raw weather data for {city}: {raw}")

            # Raw response looks like: "Delhi: ⛅️ +28°C"
            # We clean it up into natural speech so FRIDAY doesn't
            # read out colons, symbols, or weird characters
            # Remove the city prefix "CityName: " from the response
            if ":" in raw:
                raw = raw.split(":", 1)[1].strip()

            # Remove degree symbol and common weather emoji characters
            # that TTS will either skip or mispronounce
            clean = (
                raw
                .replace("°C", " degrees Celsius")
                .replace("°F", " degrees Fahrenheit")
                .replace("+", "")
                .replace("⛅️", "")
                .replace("🌧️", "")
                .replace("☀️", "")
                .replace("🌩️", "")
                .replace("❄️", "")
                .replace("🌫️", "")
                .replace("🌦️", "")
                .replace("⛈️", "")
                .replace("🌤️", "")
                .replace("🌥️", "")
                .strip()
            )

            # Return as a naturally speakable sentence
            return f"The current weather in {city} is {clean}."
        else:
            logging.error(f"Failed to get weather for {city}. Status: {response.status_code}")
            return f"I was unable to retrieve the weather for {city} at the moment, sir."
    except Exception as e:
        logging.error(f"Error retrieving weather for {city}: {str(e)}")
        return f"I ran into an error fetching the weather for {city}, boss."


@function_tool()
async def search_web(
    context: RunContext,
    query: str,
) -> str:
    """
    Search the web for a given query using DuckDuckGo.

    Args:
        query: The search query string.
    """
    try:
        results = DuckDuckGoSearchRun().run(tool_input=query)
        logging.info(f"Search results for '{query}': {results}")

        # Trim result to a reasonable spoken length so FRIDAY
        # doesn't read out an entire Wikipedia article
        if len(results) > 500:
            results = results[:500].rsplit(" ", 1)[0] + "."

        return results
    except Exception as e:
        logging.error(f"Error searching web for '{query}': {str(e)}")
        return f"I hit a snag searching for that one, boss. You may want to try again."


@function_tool()
async def send_email(
    context: RunContext,
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None,
) -> str:
    """
    Send an email through Gmail SMTP.

    Args:
        to_email: Recipient's email address.
        subject: Subject of the email.
        message: Body of the email.
        cc_email: Optional CC email address.
    """
    try:
        smtp_server = "smtp.gmail.com"
        port = 587

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

        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, msg.as_string())

        logging.info(f"Email sent successfully to {to_email}")
        return f"Email sent successfully to {to_email}, sir."

    except KeyError as e:
        logging.error(f"Missing environment variable: {str(e)}")
        return f"Email configuration error, boss. The environment variable {str(e)} is missing from the config."
    except Exception as e:
        logging.error(f"Error sending email to {to_email}: {str(e)}")
        return f"I ran into a problem sending that email, sir. Here is what went wrong: {str(e)}"