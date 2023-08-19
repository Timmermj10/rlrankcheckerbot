import discord
from discord.ext import tasks
import responses
import os
import tokens
import time
import asyncio

PAUSE = False
cooldown_start_time = "21"

async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

def run_discord_bot():
    TOKEN = tokens.discord_token
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running')

        # Start the daily cooldown task
        daily_cooldown.start()

    @client.event
    async def on_message(message):
        global PAUSE
        # Maybe insead use a time module that checks the time and pauses for 10 minutes when it gets to that point
        # split_message = message.split('/')
        if message.author == client.user:
            return
        
        if PAUSE:
            await message.channel.send('Currently updating daily MMR, please wait for 15 minutes')
            return
        
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        # Special Don Request handling
        if username == 'africanooo#0' and 'hi' in user_message:
            await message.channel.send('Hi Mr. Africano <:happycat:1017291567519780894>')

        print(f'{username} said: "{user_message}" in {channel}')

        if user_message[0] == '!' and PAUSE != True:
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=False)

    @client.event
    async def startcooldown(duration: int):
        channel = client.get_channel(1115029693289201687) #851942788936630292
        await channel.send('Daily update starting. This process will take 15 minutes to complete')
        await asyncio.sleep(duration)
        await channel.send('Daily update has completed. Feel free to use the commands')

    @tasks.loop(hours=1)
    async def daily_cooldown():
        global cooldown_start_time
        global PAUSE
        now = time.strftime("%H")

        if now == cooldown_start_time:
            print('Sleeping!')
            PAUSE = True
            await startcooldown(900)
            PAUSE = False
            print('Awoken')
    client.run(TOKEN)