import discord
from discord.ext import commands

# Your bot token
TOKEN = 'YOUR_BOT_TOKEN'

# Create a bot instance
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

# Run the bot
bot.run(TOKEN)