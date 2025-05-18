import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "✅ Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.message_content = True  # 🟢 This is critical

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')


@bot.command()
async def events(ctx):
    result = get_upcoming_events()
    await ctx.send(result if len(result) <
                   1900 else "✅ Too long — check the logs.")
    print(result)


def get_upcoming_events():
    url = "https://ctftime.org/"
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "lxml")

        table = soup.find("table", class_="upcoming-events")
        if not table:
            return "❌ Could not find the Upcoming Events table."

        rows = table.find_all("tr")[1:]  # skip header row
        events = []

        for row in rows[:5]:  # Limit to top 5
            cols = row.find_all("td")
            if len(cols) >= 3:
                name_tag = cols[1].find("a")
                if name_tag:
                    name = name_tag.text.strip()
                    link = "https://ctftime.org" + name_tag["href"]
                    date = cols[2].text.strip()
                    events.append(f"📢 **{name}**\n🗓️ {date}\n🔗 {link}\n")

        return "\n".join(events) if events else "😴 No upcoming CTFs found."

    except Exception as e:
        return f"🔥 Error: {e}"


token = os.getenv("DISCORD_TOKEN")
if not token:
    print("Error: DISCORD_TOKEN not found in environment variables!")
    exit(1)

keep_alive()
bot.run(token)
