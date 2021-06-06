import os
import discord
from discord.ext import commands
import requests
import json
def getRank(compSR):
  if compSR<1500:
      return "Bronze"
  elif compSR>=1500 and compSR<2000:
    return "Silver"
  elif compSR>=2000 and compSR<2500:
    return "Gold"
  elif compSR>=2500 and compSR<3000:
    return "Platinum"
  elif compSR>=3000 and compSR<3500:
    return "Diamond"
  elif compSR>=3500 and compSR<4500:
    return "Masters"
  elif compSR>=4500 and compSR<5000:
    return "Grandmaster"

client = commands.Bot(command_prefix = "$")

@client.event
async def on_ready():
  print("We have logged in as {0.user}".format(client))

@client.command()
async def stats(ctx, username):
  newUsername=username.replace("#", "-")
  url="https://ow-api.com/v1/stats/pc/eu/"+newUsername+"/profile"
  response = requests.get(url)
  json_data = json.loads(response.text)
  if "error" in json_data:
    await ctx.send("Incorrect username. Try again.")
  elif json_data["private"]==True:
    embed=discord.Embed(
      title = "Overwatch Stats",
      description = "This career profile is private.",
      url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      colour = discord.Colour.orange()
    )
    embed.set_footer(text="Requested by "+ctx.author.display_name)
    embed.set_thumbnail(url=json_data["icon"])
    embed.add_field(name="Level", value=json_data["prestige"]*100+json_data["level"], inline=True)
    await ctx.channel.send(embed=embed)
  else:
    embed=discord.Embed(
      title = "Overwatch Stats",
      colour = discord.Colour.orange()
    )
    embed.set_footer(text="Requested by "+ctx.author.display_name)
    embed.set_thumbnail(url=json_data["icon"])
    embed.add_field(name="Level", value=json_data["prestige"]*100+json_data["level"], inline=False)
    if "rating" in json_data:
      embed.add_field(name="Overall SR", value=json_data["rating"], inline=False)
      embed.set_author(name=username, url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", icon_url=json_data["ratingIcon"])
    if "ratings" in json_data:
      for ratings in json_data["ratings"]:
        embed.add_field(name=ratings["role"].capitalize()+" SR", value=str(ratings["level"])+" - "+getRank(ratings["level"]), inline=True)
    if "competitiveStats" in json_data:
      embed.add_field(name="Competitive win rate", value=str(round(json_data["competitiveStats"]["games"]["won"]/json_data["competitiveStats"]["games"]["played"], 2))+"%")
    await ctx.channel.send(embed=embed)
client.run(os.environ['TOKEN'])
