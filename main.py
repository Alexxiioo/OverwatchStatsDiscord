from replit import db
import os
from keep_alive import keep_alive
import discord
from discord.ext import commands, tasks
import requests
import json
from datetime import datetime, timedelta
import pytz
import schedule
import time
from dateutil import parser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
def statLogger():
  print("Has run")
  for username in db.keys():
    tz_London = pytz.timezone('Europe/London')
    datetime_London = datetime.now(tz_London)
    newUsername=username.replace("#", "-")
    url="https://ow-api.com/v1/stats/pc/eu/"+newUsername+"/profile"
    response = requests.get(url)
    json_data = json.loads(response.text)
    db[username].append(json_data["prestige"]*100+json_data["level"])
    db[username].extend([0,0,0,0])
    for rating in json_data["ratings"]:
      if rating["role"]=="tank":
        db[username][-4]=rating["level"]
      if rating["role"]=="damage":
        db[username][-3]=rating["level"]
      if rating["role"]=="support":
        db[username][-2]=rating["level"]
      db[username][-1]=str(datetime_London)
    print ("pinged")

def storeGetStats(username, ratings, level):
  tz_London = pytz.timezone('Europe/London')
  datetime_London = datetime.now(tz_London)
  if username in db.keys():
    oldStats=[db[username][-5],db[username][-4], db[username][-3], db[username][-2], db[username][-1]]
    db[username].append(level)
    db[username].extend([0,0,0,0])
    for rating in ratings:
      if rating["role"]=="tank":
        db[username][-4]=rating["level"]
      if rating["role"]=="damage":
        db[username][-3]=rating["level"]
      if rating["role"]=="support":
        db[username][-2]=rating["level"]
    db[username][-1]=str(datetime_London)
    return oldStats
  else:
    db[username]=[0,0,0,0,0]
    db[username][0]=level
    for rating in ratings:
      if rating["role"]=="tank":
        db[username][1]=rating["level"]
      if rating["role"]=="damage":
        db[username][2]=rating["level"]
      if rating["role"]=="support":
        db[username][3]=rating["level"]
    db[username][4]=str(datetime_London)
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
    oldStats=storeGetStats(username, json_data["ratings"], json_data["prestige"]*100+json_data["level"])
    if oldStats:
      oldStatsString=""
      if oldStats[1]:
        if tankSR==oldStats[1]:
          pass
        else:
          if tankSR-oldStats[1]>0:
            oldStatsString+="+"
          oldStatsString+=str(tankSR-oldStats[1])+" Tank SR, "
      if oldStats[2]:
        if damageSR==oldStats[2]:
          pass
        else:
          if damageSR-oldStats[2]>0:
            oldStatsString+="+"
          oldStatsString+=str(damageSR-oldStats[2])+" Damage SR, "
      if oldStats[3]:
        if supportSR==oldStats[3]:
          pass
        else:
          if supportSR-oldStats[3]>0:
            oldStatsString+="+"
          oldStatsString+=str(supportSR-oldStats[3])+" Support SR."
      if oldStatsString=="":
        oldStatsString="No changes."
      embed.add_field(name="Overall SR change since last check ("+parser.parse(oldStats[4]).strftime("%H:%M on %d/%m")+"):",value=oldStatsString, inline=False)
    await ctx.channel.send(embed=embed)

@client.command()
async def graph(ctx, typeOfGraph, username, hoursWanted):
  if username in db.keys():
    if typeOfGraph=="level":
      levels=[]
      timestamps=[]
      length=len(db[username])
      tz_London = pytz.timezone('Europe/London')
      datetime_London = datetime.now(tz_London)
      for i in range(0, length-1, 5):
        if parser.parse(db[username][i+4])+timedelta(hours=1)>datetime_London-timedelta(hours=int(hoursWanted)):
          levels.append(db[username][i])
          timestamps.append(parser.parse(db[username][i+4])+timedelta(hours=1))
      plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M/%m'))
      plt.gca().xaxis.set_major_locator(mdates.DayLocator())
      plt.plot(timestamps, levels, label = "Level")
      plt.xlabel('Time')
      plt.ylabel('Level')
      plt.title(username+"'s level over "+str(hoursWanted)+" hours.")
      plt.gcf().autofmt_xdate()
      plt.legend()
      newUsername=username.replace("#", "-")
      plt.savefig(newUsername+'.png')
      await ctx.channel.send(file=discord.File(newUsername+'.png'))
    elif typeOfGraph=="sr" or typeOfGraph=="SR" or typeOfGraph=="Sr":
      tank=[]
      damage=[]
      support=[]
      timestamps=[]
      length=len(db[username])
      tz_London = pytz.timezone('Europe/London')
      datetime_London = datetime.now(tz_London)
      for i in range(0, length-1, 5):
        if parser.parse(db[username][i+4])+timedelta(hours=1)>datetime_London-timedelta(hours=int(hoursWanted)):
          tank.append(db[username][i+1])
          damage.append(db[username][i+2])
          support.append(db[username][i+3])
          timestamps.append(parser.parse(db[username][i+4])+timedelta(hours=1))

      plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M/%m'))
      plt.gca().xaxis.set_major_locator(mdates.DayLocator())
      plt.plot(timestamps, tank, label = "Tank SR")
      plt.plot(timestamps, damage, label = "Damage SR")
      plt.plot(timestamps, support, label = "Support SR")
      plt.xlabel('Time')
      plt.ylabel('Skill Rating')
      plt.title(username+"'s SR over "+str(hoursWanted)+" hours.")
      plt.gcf().autofmt_xdate()
      plt.legend()
      newUsername=username.replace("#", "-")
      plt.savefig(newUsername+'.png')
      await ctx.channel.send(file=discord.File(newUsername+'.png'))
@tasks.loop(minutes=30.0)
async def logStats():
  statLogger()
  tz_London = pytz.timezone('Europe/London')
  print("Logged stats",datetime.now(tz_London))

@logStats.before_loop
async def before():
  await client.wait_until_ready()
  print("Finished waiting")
for key in db.keys():
  print(db[key])
logStats.start()
keep_alive()
client.run(os.environ['TOKEN'])
