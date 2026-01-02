import discord
from discord.ext import commands
from dotenv import load_dotenv # type: ignore
import os
import logging
from logging.handlers import SysLogHandler
import socket
import aiohttp

LOG_ADDRESS = '/dev/log'
API_URL = "http://tradefly-tradeflydjango-otrt2b/api/banditMessages/"


load_dotenv()

token = os.getenv('DISCORD_TOKEN')


######## LOGGING CODE ########

#handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
logger = logging.getLogger('bandit')
logger.setLevel(logging.INFO)

try:
    if os.path.exists(LOG_ADDRESS):
        handler = SysLogHandler(address=LOG_ADDRESS, facility=SysLogHandler.LOG_DAEMON)
        
        # Optional: Define the format of the message in the system log
        formatter = logging.Formatter('%(name)s: %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    else:
        raise FileNotFoundError(f"SysLog socket not found at {LOG_ADDRESS}")

except (FileNotFoundError, OSError) as e:
    # Fallback if the /dev/log socket isn't present (e.g., on Windows or specific non-standard setups)
    print(f"Warning: SysLog logging disabled ({e}). Logging to console.")
    logger.addHandler(logging.StreamHandler())

######## END LOGGING CODE #########



intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def send_startup_check():
    """Sends a blank message to the API to verify connectivity on startup."""
    payload = {
        "channel_id": "0",
        "channel_name": "Startup Check",
        "message": ""
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload) as response:
                if response.status == 201:
                    logger.info("Startup API check successful: Message sent.")
                else:
                    logger.error(f"Startup API check failed. Status: {response.status}, Response: {await response.text()}")
    except Exception as e:
        logger.error(f"Startup API check failed. Could not connect to {API_URL}. Error: {e}")

@bot.event
async def on_ready():
    logger.info(f"we are ready to go: {bot.user.name}")
    #print(f"we are ready to go: {bot.user.name}")
    await send_startup_check()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    hrj = 1370614665649979472
    fj = 1379787390155096105
    squid = 1375506611195351131
    tradefly = 1378750234334597191
    bydfi_scalp = 1421331231282298950
    bydfi_swing = 1421331173073748030
    bydfi_copy = 1421331378506694797
    shenanigans = 1362101608984481938
    gen_chat = 1350316337909731373
    flex = 1350317108927401984
    pumpamentals = 1358833841959337984
    squad_charts = 1350317442861105212


    channel_list = [hrj, fj]
    
    if message.channel.id in channel_list:
        #print(" \nFound in Channel List")
        logger.info(f"Message received in monitored channel: {message.channel.name}")
        
        payload = {
            "channel_id": str(message.channel.id),
            "channel_name": message.channel.name,
            "message": message.content
        }
        
        # Send the POST request asynchronously
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL, json=payload) as response:
                    if response.status == 201:
                        logger.info(f"Successfully sent message from '{message.channel.name}' to API.")
                    else:
                        logger.error(f"Failed to send message to API. Status: {response.status}, Response: {await response.text()}")
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Could not connect to the API endpoint at {API_URL}. Please ensure the Django server is running. Error: {e}")

    await bot.process_commands(message)


#bot.run(token, log_handler=logger, log_level=logging.INFO)
bot.run(token)