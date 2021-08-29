'''Bartleby the Chickadee: A simple discord bot

# To run the bot environment: bot-env\Scripts\activate.bat
# To run Bartleby: py bartleby.py
#
# Required libraries:
#   - discord.py -- https://discordpy.readthedocs.io/
#   - discord-py-slash-command -- https://discord-py-slash-command.readthedocs.io/
#   - pyown -- https://pyowm.readthedocs.io/
'''

import discord
from discord_slash import SlashCommand
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option, create_choice
from discord.ext import commands
from bartlekeys import my_discord_bot_token, my_openweather_api_key
from pyowm.owm import OWM 
import datetime
import time

# the keys/tokens below should remain hidden from public view
bot_token = my_discord_bot_token
owm = OWM(my_openweather_api_key)

tz_min = -12 # inclusive
tz_max = 14 # inclusive

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
slash = SlashCommand(bot, sync_commands=True) # declare slash commands through the bot

@bot.event
async def on_ready():
    # update bot status
    await bot.change_presence(activity=discord.Game(name='picking pecking!'))
    print('We have logged in as {0.user}'.format(bot))

guild_ids = [677704068789174304] # Server id for the server we wants the bot to run in

@slash.slash(name="beep",
            description="This is a simple test function.",
            guild_ids=guild_ids) # declares a guild (server) command
async def beep(ctx): # defines a new context (ctx) command called beep
    await ctx.send(f"boop!")

@slash.slash(name="timetest",
            description="Bartleby will tell you the time.",
            guild_ids=guild_ids,
            options=[
                create_option(
                    name="tz", # time zone variable
                    description="Enter your time zone, relative to UTC. (Range: -12 to 14)",
                    option_type=SlashCommandOptionType.INTEGER,
                    required=True
                    )
                ])
async def timetest(ctx, tz: int):
    try:
        if tz >= tz_min and tz <= tz_max:
            # input timezone was valid
            utc = datetime.datetime.now(datetime.timezone.utc) # get current utc time
            time_delta = datetime.timedelta(hours=tz) # set up difference between utc and input timezone
            time_zone = datetime.timezone(time_delta) # create new time zone from delta
            offset_time = utc.astimezone(time_zone) # get current time of input timezone 
            await ctx.send(offset_time.strftime("%A, %B %d, %Y -- %I:%M%p")) # Format: weekday, month day, year - hour:minute(AM/PM)
        else:
            # input timezone was invalid
            await ctx.send("Sorry, that timezone is invalid!")
            await ctx.send("Try again with a tz >= {} and tz <= {}.".format(tz_min, tz_max))
    except Exception as err:
        # something went wrong
        print(err)
        await ctx.send("Sorry, an error occured and I could not perform the time function!")

@slash.slash(name="weather",
            description="Bartleby will tell you the weather.",
            guild_ids=guild_ids,
            options=[
                create_option(
                    name="city",
                    description="Enter a city, to find out about it's current whether.",
                    option_type=SlashCommandOptionType.STRING,
                    required=True
                    ),
                create_option(
                    name="country",
                    description="Please enter the country code your city is in. (E.g. Canada = CA, Norway = NO)",
                    option_type=SlashCommandOptionType.STRING,
                    required=True)
                ])
async def weather(ctx, city: str, country: str):
    try:
        location_string = city + "," + country # required format = city,countrycode
        mngr = owm.weather_manager()
        observation = mngr.weather_at_place(location_string)
        my_weather = observation.weather
        temp_dict = my_weather.temperature("celsius")
        await ctx.send(str(my_weather.detailed_status))
        await ctx.send(str(temp_dict["temp"]))
    except Exception as err:
        print(err)
        await ctx.send("Sorry, an error occured and I could not perform the weather function!")

@slash.slash(name="logout",
            description="This logs Bartleby out of Discord.",
            guild_ids=guild_ids)
async def logout(ctx):
    await ctx.send("Bye bye!")
    await ctx.bot.close()
    print("{0.user} has logged out.".format(bot))
    time.sleep(1) # this is required to logout without error: it breaks if I don't have it/possibly an API issue?

bot.run(bot_token)