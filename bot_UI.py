import discord
from discord import Embed, Intents, utils
from discord.ext import commands
from connection_db import *
from main_code import *
from subscriber_map import *
import typing as t
import asyncio

subscribe_channel_id = 773835398165692458
bot_id = 716211383754031155
owner_id = 384236785393205250

intents = Intents.default()
Intents.members = True
client = commands.Bot(command_prefix = '!', help_command=None, intents=intents)
client.ticket_id = None
client.botvar = None

flag = False
ghv = []

@client.event
async def on_reaction_add(reaction, user):

    if user.id == bot_id:
        return
    
    user_name = user.name.replace(' ', '-').lower()

    # Ticket Channel
    if reaction.message.id == client.ticket_id and user.bot == False and not discord.utils.get(reaction.message.guild.channels, name=f'ticket-{user_name}'):
        
        await reaction.remove(user)
        category = discord.utils.get(reaction.message.guild.categories, name='tickets')
        await category.create_text_channel(f"Ticket {user.name}")
        await reaction.message.guild.create_role(name=f'Support {user.name}')
        await user.add_roles(discord.utils.get(reaction.message.guild.roles, name=f"Support {user.name}"))
        
        channel = discord.utils.get(reaction.message.guild.channels, name=f'ticket-{user_name}'.lower())
        await channel.set_permissions(discord.utils.get(reaction.message.guild.roles, name='@everyone'), read_messages=False)
        await channel.set_permissions(discord.utils.get(reaction.message.guild.roles, name=f'Support {user.name}'), read_messages=True)
        msg2 = await channel.send("Please react to this message to close this ticket. ")
        await msg2.add_reaction("❌")


    if f"ticket-{user_name}" in reaction.message.channel.name:
        await reaction.message.channel.delete()
        await user.remove_roles(discord.utils.get(reaction.message.guild.roles, name=f'Support {user.name}'))


    if reaction.message.channel.id == subscribe_channel_id:
        
        global flag, ghv
        flag = True
        
        #discord id of tipster
        ghv = msg_to_discord_id(reaction.message.id)[0][0]
        
        await reaction.remove(user)
        category = discord.utils.get(reaction.message.guild.categories, name='confirm')
        await category.create_text_channel(f"{user.id} {ghv}")
        await reaction.message.guild.create_role(name=f'Confirm {user.name}')
        await user.add_roles(discord.utils.get(reaction.message.guild.roles, name=f"Confirm {user.name}"))

        channel = discord.utils.get(reaction.message.guild.channels, name=f'{user.id}-{ghv}')

        await channel.set_permissions(discord.utils.get(reaction.message.guild.roles, name='@everyone'), read_messages=False)
        await channel.set_permissions(discord.utils.get(reaction.message.guild.roles, name=f'Confirm {user.name}'), read_messages=True)
        msg2 = await channel.send("Please react to this message to confirm your payment")
        await msg2.add_reaction("✅")

        await asyncio.sleep(10)
        await user.remove_roles(discord.utils.get(reaction.message.guild.roles, name=f'Confirm {user.name}'))
        await channel.delete()
    

    if flag is True and f"{user.id}-{ghv}" in reaction.message.channel.name:
        
        await user.send(add_vip(user.id, ghv)[1])
        print("Confrim Reaction msg if statement.")
        await reaction.message.channel.delete()
        await user.remove_roles(discord.utils.get(reaction.message.guild.roles, name=f'Confirm {user.name}'))
        flag = False
        



@client.command()
async def ticketset(ctx, channel_id: int):
    channel = discord.utils.get(ctx.guild.text_channels, name='tickets')
    msg = await channel.send("React to the message open a ticket!")
    client.ticket_id = msg.id
    await msg.add_reaction("📧")

@client.event
async def on_ready():
    print("BOT FUNCTION OPTIMAL")

@client.command()
async def help(ctx):
    
    e = Embed(title="Help", colour = 0xff916d)

    # Tipster Commands
    e.add_field(name = "!addtipster <tipster_discord_id> <price> <period> <img_url>", value = "Adds new tipster", inline=False)
    e.add_field(name = "!disabletipsterservice <tipster_discord_id>", value = "Dsiables tipster's service", inline=False)
    e.add_field(name = "!deltipster <tipster_discord_id>", value = "Removes Tipster", inline=False)
    e.add_field(name = "!settipsterprice <tipster_discord_id> <price> <days>", value = "Sets the price and days for tipster's service", inline=False)
    e.add_field(name = "!settipsterbalance <tipster_discord_id> <points>", value = "Sets the points in the bank for a tipster", inline=False)


    # User Commands
    e.add_field(name = "!setuserpoints <user_discord_id> <points>", value = "Sets points to the user", inline=False)
    e.add_field(name = "!delvip <user_discord_id> <tipster_discord_id>", value = "Removes user's VIP subscription", inline=False)
    e.add_field(name = "!points <user_discord_id>", value = "Shows points for a user", inline=False)

    await ctx.send(embed = e)



# Add Tipster


@client.command()
async def addtipster(ctx, member: discord.Member, price: int, days: int, logo_url, spreadsheet):
    
    # Front End calls
    category = discord.utils.get(ctx.guild.categories, name='Tipsters')
    
    await category.create_text_channel(f"Tipster {member.name}")
    await ctx.guild.create_role(name=f'Tipster {member.name}')
    await member.add_roles(discord.utils.get(ctx.guild.roles, name=f"Tipster {member.name}"))

    channel = discord.utils.get(ctx.guild.channels, name=f'tipster-{member.name}'.lower())

    await channel.set_permissions(discord.utils.get(ctx.guild.roles, name='@everyone'), read_messages=False)


    await ctx.send(f'Made {member.mention} a tipster!\nThey currently cost {str(price)} points for {str(days)} days')
    

    e = Embed(title=f"__**Tipster Profile**__", colour = 0xff916d, url=spreadsheet)
    e.set_image(url=logo_url)
    e.set_footer(text="React to the message below to subscribe")
    e.add_field(name="‎", value=f"{member.mention}", inline=False)
    e.add_field(name=f"Price: __{price}__ points for __{days}__ days.", value="‎")

    msg = await discord.utils.get(ctx.guild.channels, name=f'subscribe-here').send(embed=e)
    await msg.add_reaction('👍')

    # Back End calls
    update_tipster(str(member.id), msg.id, price, days, 0)


@client.command()
async def disabletipsterservice(ctx, member: discord.Member):
    
    # Back End calls
    del_tipster(str(member.id))

    # Front end calls
    await ctx.send(f"Disabled subscription for tipster {member.mention}")
    msg = await discord.utils.get(ctx.guild.channels, name=f'subscribe-here').fetch_message(discord_to_msg_id(member.id)[0][0])
    await msg.delete()


@client.command()
async def deltipster(ctx, member: discord.Member):
    user_name = member.name.replace(' ', '-').lower()
    
    # Back End calls
    del_tipster(str(member.id))

    # Front end calls
    await member.remove_roles(discord.utils.get(ctx.guild.roles, name=f"Tipster {member.name}"))
    await ctx.send(f"Removed {member.mention} as a tipster.")
    await discord.utils.get(ctx.guild.text_channels, name=f"tipster-{user_name}").delete()
    msg = await discord.utils.get(ctx.guild.channels, name=f'subscribe-here').fetch_message(discord_to_msg_id(member.id)[0][0])
    await msg.delete()


@client.command()
async def settipsterprice(ctx, member: discord.Member, price: int,  days: int):
    
    set_tipster_price(str(member.id), price)
    set_tipster_period(str(member.id), days)

    await ctx.send(f"Updated {member.mention}'s price to {str(price)} points for duration of {days} days")


@client.command()
async def settipsterbalance(ctx, member: discord.Member, points: int):
    
    set_tipster_points(discord.Member, points)
    await ctx.send(f"Updated {member.mention}'s balance to {str(points)} points")



# USER COMMANDS


@client.command()
async def setuserpoints(ctx, member: discord.Member, points: int):
    
    # Back end
    set_user_points(f"{str(member.id)}", points)
    ret_points = show_user_points(f"{str(member.id)}")

    # Front end
    await ctx.send(f"{member.mention} now has {ret_points[0][0]} points!")


@client.command()
async def delvip(ctx, user_member: discord.Member, tipster_member: discord.Member):
    
    # Back end
    remove_vip(user_member, tipster_member)

    # Front end
    await ctx.send(f"Deleted user {user_member.mention}'s VIP access to tipster {tipster_member.metion}'s service.")


@client.command()
async def points(ctx, user_member: t.Optional[discord.Member]):
    
    if user_member and ctx.author.id == owner_id:
        res = show_user_points(user_member.id)
        await ctx.send(f"Points for user {user_member.mention} is {res[0][0]}.")
    else:
        res = show_user_points(ctx.author.id)
        await ctx.send(f"Points for user {ctx.author.mention} is {res[0][0]}.")
    


client.run('')