import discord
from discord import Embed, utils
from discord.ext import commands, tasks
import main_code as m
import typing as tp
import asyncio


intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '!', help_command=None, intents=intents)
client.ticket_id = 774561814545301535
client.owner_id = 384236785393205250
client.subscribe_channel_id = {}
client.bot_id = 716211383754031155
client.flag = {}
client.ghv = None


@tasks.loop(seconds=10)
async def countdown():
    for user_key in m.map_info.keys():
        for tipster_key in m.map_info[f"{user_key}"].keys():
            if int(m.map_info[f'{user_key}'][f'{tipster_key}']) <= 0:
                print(user_key)
                member = client.get_guild(774561814179479572).get_member(int(user_key))
                await member.remove_roles(discord.utils.get(member.guild.roles, name=f'tipster {client.get_guild(774561814179479572).get_member(int(tipster_key)).name}'))
            else:
                m.map_info[f"{user_key}"][f"{tipster_key}"] = str(int(m.map_info[f'{user_key}'][f'{tipster_key}']) - 1)


async def startup():
    await client.wait_until_ready


@client.event
async def on_connect():
    print("BOT Has Connected")
    

@client.event
async def on_message(message):
    m.init_user(message.author.id)

    await client.process_commands(message)


@client.command()
async def start(ctx):

    client.owner_id = ctx.guild.owner_id
    client.bot_id = 716211383754031155

    for role in ctx.guild.roles[1:]:
        if role.name not in ["Vibe"]:

            try: 
                await role.delete()
            except:
                pass
        

    for channel in ctx.guild.text_channels:
        if channel.name not in ["general"]:
            try:
                await channel.delete()
            except:
                pass

    category = discord.utils.get(ctx.guild.categories, name='Text Channels')
    await category.create_text_channel(f"subscribe-here")
    await category.create_text_channel(f"admin")

    category = discord.utils.get(ctx.guild.categories, name='tickets')
    channel = await category.create_text_channel(f"tickets")

    msg = await channel.send("React to the message open a ticket!")
    await msg.add_reaction("📧")
    client.ticket_id = msg.id
    await ctx.send("DONE")
"""

@client.command()
async def ticket(ctx):
    channel = discord.utils.get(ctx.guild.text_channels, name='buy-points')
    msg = await channel.send("React to the message open a ticket!")
    await msg.add_reaction("📧")
    client.ticket_id = msg.id

@client.command()
async def help(ctx):

    e = Embed(title="Help", colour = 0xff916d)

    # Tipster Commands
    e.add_field(name = "!addtipster <tipster_mention> <price> <period> <img_url> <spreadsheet_url>", value = "Adds new tipster", inline=False)
    e.add_field(name = "!disabletipster <tipster_mention>", value = "Dsiables tipster's service", inline=False)
    e.add_field(name = "!deltipster <tipster_mention>", value = "Removes Tipster", inline=False)
    e.add_field(name = "!settipster <price> <days> <logo_url> <spreadsheet_url>", value = "Edits the info of the tipster's service.", inline=False)
    e.add_field(name = "!settipsterbalance <tipster_mention> <points>", value = "Sets the points in the bank for a tipster", inline=False)


    # User Commands
    e.add_field(name = "!setuserpoints <user_mention> <points>", value = "Sets points to the user", inline=False)
    e.add_field(name = "!userpoints <user_mentions>", value = "[Admin] Shows points for mentioned user.", inline=False)
    e.add_field(name = "!points", value = "Shows points for a user and any active subscriptions", inline=False)

    await ctx.send(embed = e)


@commands.is_owner()
@client.command()
async def addtipster(ctx, member: discord.Member, price: int, days: int, logo_url, spreadsheet):
        
    user_name = member.name.replace(' ', '-').lower()
    category = discord.utils.get(ctx.guild.categories, name='vip tips')
    
    await ctx.guild.create_role(name=f'tipster {member.name}')
    await member.add_roles(discord.utils.get(ctx.guild.roles, name=f"tipster {member.name}"))
    await category.create_text_channel(f"tipster {member.name}")

    channel = discord.utils.get(ctx.guild.text_channels, name=f'tipster-{user_name}')

    await channel.set_permissions(discord.utils.get(member.guild.roles, name='@everyone'), read_messages=False)
    await channel.set_permissions(discord.utils.get(member.guild.roles, name=f'tipster {member.name}'), read_messages=True)

    e = Embed(title=f"__**Tipster Profile**__", colour = 0xff916d, url=spreadsheet)
    e.set_image(url=logo_url)
    e.set_footer(text="React to the message below to subscribe")
    e.add_field(name="‎", value=f"{member.mention}", inline=False)
    e.add_field(name=f"Price: __{price}__ points for __{days}__ days.", value="‎")
    
    msg = await discord.utils.get(ctx.guild.text_channels, name=f'list-of-vip-tipsters').send(embed=e)
    await msg.add_reaction('👍')

    client.subscribe_channel_id[f'{member.id}'] = msg.id
    m.update_tipster(member.id, msg.id, price, days, 0)
    m.update_tipstername(member.id, member.name)
    
    await ctx.send(f'Made {member.mention} a tipster!\nThey currently cost {str(price)} points for {str(days)} days')


@commands.is_owner()        
@client.command()
async def disabletipster(ctx, member: discord.Member):

    # Front end calls
    await ctx.send(f"Disabled subscription for tipster {member.mention}")
    msg = await discord.utils.get(ctx.guild.channels, name=f'list-of-vip-tipsters').fetch_message(m.discord_to_msg_id(member.id))
    await msg.delete()


@commands.is_owner()
@client.command()
async def deltipster(ctx, member: discord.Member):

    user_name = member.name.replace(' ', '-').lower()

    # Front end calls
    await member.remove_roles(discord.utils.get(ctx.guild.roles, name=f"tipster {member.name}"))
    await ctx.send(f"Removed {member.mention} as a tipster.")
    await discord.utils.get(ctx.guild.text_channels, name=f"tipster-{user_name}").delete()
    msg = await discord.utils.get(ctx.guild.channels, name=f'list-of-vip-tipsters').fetch_message(m.discord_to_msg_id(member.id))
    await member.remove_roles(discord.utils.get(ctx.guild.roles, name=f'tipster {member.name}'))
    await msg.delete()

    # Back End calls
    m.del_tipster(str(member.id))


@commands.is_owner()
@client.command()
async def settipsterbalance(ctx, member: discord.Member, points: int):
    m.set_tipster_points(member.id, points)
    await ctx.send(f"Updated {member.mention}'s balance to {str(points)} points")


@client.command()
async def settipster(ctx, price: int,  days: int, logo_url, spreadsheet):
    
    if f"tipster {ctx.author.name}" in [x.name for x in ctx.author.roles]:

        m_id = m.discord_to_msg_id(ctx.author.id)

        channel = discord.utils.get(ctx.guild.text_channels, name = "list-of-vip-tipsters")
        msg = await channel.fetch_message(m_id)

        m.set_tipster_price(str(ctx.author.id), price)
        m.set_tipster_period(str(ctx.author.id), days)

        e = Embed(title=f"__**Tipster Profile**__", colour = 0xff916d, url=spreadsheet)
        e.set_image(url=logo_url)
        e.set_footer(text="React to the message below to subscribe")
        e.add_field(name="‎", value=f"{ctx.author.mention}", inline=False)
        e.add_field(name=f"Price: __{price}__ points for __{days}__ days.", value="‎")

        await msg.edit(embed=e)
        await ctx.send(f"Updated {ctx.author.mention}'s price to {str(price)} points for duration of {days} days")

    else:
        await ctx.send("You're not a tipster.")


@commands.is_owner()
@client.command()
async def setuserpoints(ctx, member: discord.Member, points: int):

    # Back end
    m.set_user_points(f"{str(member.id)}", points)
    ret_points = m.show_user_points(f"{str(member.id)}")

    # Front end
    await ctx.send(f"{member.mention} now has {ret_points} points!")


@client.event
async def on_reaction_add(reaction, user):

    if user.id == client.bot_id:
        return
    
    user_name = user.name.replace(' ', '-').lower()

    
    # Ticket Channel
    if reaction.message.id == client.ticket_id and not discord.utils.get(reaction.message.guild.channels, name=f'ticket-{user_name}'):
        
        await reaction.remove(user)
        category = discord.utils.get(reaction.message.guild.categories, name='🌟Points🌟')
        await category.create_text_channel(f"ticket {user.name}")
        await reaction.message.guild.create_role(name=f'support {user.name}')
        await user.add_roles(discord.utils.get(reaction.message.guild.roles, name=f"support {user.name}"))
        
        channel = discord.utils.get(reaction.message.guild.channels, name=f'ticket-{user_name}'.lower())
        await channel.set_permissions(discord.utils.get(reaction.message.guild.roles, name='@everyone'), read_messages=False)
        await channel.set_permissions(discord.utils.get(reaction.message.guild.roles, name=f'support {user.name}'), read_messages=True)
        msg2 = await channel.send("Please react to this message to close this ticket. ")
        await msg2.add_reaction("❌")


    if f"ticket-{user_name}" in reaction.message.channel.name:
        await reaction.message.channel.delete()
        await user.remove_roles(discord.utils.get(reaction.message.guild.roles, name=f'support {user.name}'))

    # code for the confirmation
   
    try:
        if reaction.message.id == client.subscribe_channel_id[f'{m.msg_to_discord_id(reaction.message.id)}'] and not discord.utils.get(reaction.message.guild.channels, name=f"{user.id}-{client.ghv}"):
        
            client.flag[f'{user.id}'] = True
            #discord id of tipster
            client.ghv = m.msg_to_discord_id(reaction.message.id)

            await reaction.remove(user)
            category = discord.utils.get(reaction.message.guild.categories, name='confirm')
            await category.create_text_channel(f"{user.id} {client.ghv}")
            await reaction.message.guild.create_role(name=f'confirm {user.name}')
            await user.add_roles(discord.utils.get(reaction.message.guild.roles, name=f"confirm {user.name}"))

            channel = discord.utils.get(reaction.message.guild.channels, name=f'{user.id}-{client.ghv}')

            await channel.set_permissions(discord.utils.get(reaction.message.guild.roles, name='@everyone'), read_messages=False)
            await channel.set_permissions(discord.utils.get(reaction.message.guild.roles, name=f'confirm {user.name}'), read_messages=True)
            msg2 = await channel.send(f"{user.mention} Please react to this message to confirm your payment")
            await msg2.add_reaction("✅")

            await asyncio.sleep(15)
            await user.remove_roles(discord.utils.get(reaction.message.guild.roles, name=f'confirm {user.name}'))
            await channel.delete()
        
    except:
        print("Bypassed Reactionss........................")
        

    
    try:
        if client.flag[f'{user.id}'] is True and f"{user.id}-{client.ghv}" in reaction.message.channel.name:
            res = m.add_to_map(user.id, client.ghv)
            await user.send(res[1])
            if res[0] == True:
                await user.add_roles(discord.utils.get(reaction.message.guild.roles, name=f'tipster {user.guild.get_member(int(client.ghv)).name}'))
            await reaction.message.channel.delete()
            await user.remove_roles(discord.utils.get(reaction.message.guild.roles, name=f'confirm {user.name}'))
            client.flag[f'{user.id}'] = False
    except:
        print("Bypassed Confirmations........................")


@commands.is_owner()
@client.command()
async def userpoints(ctx, user_member: discord.Member):
    res = m.show_user_points(user_member.id)
    await ctx.send(f"Points for user {user_member.mention} is {res}.")
    await ctx.send(f"Active Subscriptions for user are {m.active_subs(user_member.id)}")

@client.command()
async def points(ctx):
    #print(ctx.guild.members)
    res = m.show_user_points(ctx.author.id)
    await ctx.send(f"{ctx.author.mention} has {res} points")
    
    func = m.active_subs(ctx.author.id)

    e = Embed(title="Active Subscriptions", colour = 0xff916d)

    for keys in func.keys():
        m.fetch_tipstername(keys)
        tem = int(func[keys])
        e.add_field(name={m.fetch_tipstername(keys)}, value = f"Remaining Time: { tem//24 } days and { tem % 24} hours")

    await ctx.send(embed=e)


"""
@commands.is_owner()
@client.command()
async def delvip(ctx, user_member: discord.Member, tipster_member: discord.Member):
    # Back end
    remove_vip(user_member.id, tipster_member)

    # Front end
    await ctx.send(f"Deleted user {user_member.mention}'s VIP access to tipster {tipster_member.metion}'s service.")
"""

countdown.start()

client.run('NzE2MjExMzgzNzU0MDMxMTU1.XtId1A.6vPBJkrm2neBbib-5voHFrpcAzw')
