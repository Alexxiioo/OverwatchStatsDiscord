from replit import db
import os
from keep_alive import keep_alive
import discord
from discord.ext import commands
import requests
import json
from datetime import datetime
import pytz

def storeGetStats(username, ratings):
  tz_London = pytz.timezone('Europe/London')
  datetime_London = datetime.now(tz_London)
  lastTime=datetime_London.strftime("%H:%M on %-d/%m")
  if username in db.keys():
    oldStats=db[username]
    db[username]=[False, False, False, False]
    for rating in ratings:
      if rating["role"]=="tank":
        db[username][0]=rating["level"]
      if rating["role"]=="damage":
        db[username][1]=rating["level"]
      if rating["role"]=="support":
        db[username][2]=rating["level"]
    db[username][3]=lastTime
    return oldStats
  else:
    db[username]=[False, False, False, False]
    for rating in ratings:
      if rating["role"]=="tank":
        db[username][0]=rating["level"]
      if rating["role"]=="damage":
        db[username][1]=rating["level"]
      if rating["role"]=="support":
        db[username][2]=rating["level"]
    db[username][3]=lastTime
    return False
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
      overallSR=json_data["rating"]
      embed.add_field(name="Overall SR", value=overallSR, inline=True)
      embed.set_author(name=username, url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", icon_url=json_data["ratingIcon"])
    if "ratings" in json_data:
      for ratings in json_data["ratings"]:
        if ratings["role"]=="tank":
          tankSR=ratings["level"]
        if ratings["role"]=="damage":
          damageSR=ratings["level"]
        if ratings["role"]=="support":
          supportSR=ratings["level"]
        embed.add_field(name=ratings["role"].capitalize()+" SR", value=str(ratings["level"])+" - "+getRank(ratings["level"]), inline=True)
    if "competitiveStats" in json_data:
      embed.add_field(name="Competitive win rate", value=str(round((json_data["competitiveStats"]["games"]["won"]/json_data["competitiveStats"]["games"]["played"])*100, 2))+"%", inline=True)
    oldStats=storeGetStats(username, json_data["ratings"])
    if oldStats:
      oldStatsString=""
      if oldStats[0]:
        if tankSR==oldStats[0]:
          pass
        else:
          if tankSR-oldStats[0]>0:
            oldStatsString+="+"
          oldStatsString+=str(tankSR-oldStats[0])+" Tank SR, "
      if oldStats[1]:
        if damageSR==oldStats[1]:
          pass
        else:
          if damageSR-oldStats[1]>0:
            oldStatsString+="+"
          oldStatsString+=str(damageSR-oldStats[0])+" Damage SR, "
      if oldStats[2]:
        if supportSR==oldStats[2]:
          pass
        else:
          if supportSR-oldStats[2]>0:
            oldStatsString+="+"
          oldStatsString+=str(damageSR-oldStats[0])+" Support SR."
      if oldStatsString=="":
        oldStatsString="No changes."
      embed.add_field(name="Overall SR change since last check ("+oldStats[3]+"):",value=oldStatsString, inline=False)
    await ctx.channel.send(embed=embed)
keep_alive()
client.run(os.environ['TOKEN'])
