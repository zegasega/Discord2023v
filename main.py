import discord
from colorama import Back,Fore,Style
from discord.commands import Option
import requests
import json
import datetime
from bs4 import BeautifulSoup
from datetime import datetime
import re
from configs import TOKEN,WEATHER_API,wallet_address
from discord.ext import tasks
import time
import platform
import asyncio




intents = discord.Intents.default()
bot =discord.Bot(intents=intents,debug_guilds=[1005131834306342933]) #your server id



#need some fix for list deployed
#commands
#clan info

@bot.event
async def on_ready():
    prfx = (Back.BLACK +Fore.GREEN + time.strftime('%H:M:S UTC',time.gmtime()) + Back.RESET+Style.BRIGHT)
    print(prfx + ' Logged in as ' + Fore.YELLOW + bot.user.name)
    print(prfx + ' Bot ID' + Fore.YELLOW + str(bot.user.id))
    print(prfx + ' Discord Version ' + Fore.YELLOW + discord.__version__)
    print(prfx + ' Python Version ' + Fore.YELLOW + str(platform.python_version()))
    update_nft_info.start()




@bot.command()
async def kick(ctx,member:discord.Member,*,reason=None):
    if ctx.author.guild_permissions.kick_members:
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention}  kicked for {reason}')
    else:
        await ctx.send('You have no permission to use')

bot.command()
async def ban(ctx,member:discord.Member,*,reason=None):
    if ctx.author.guild_permissions.ban_members:
        await member.ban(reason=reason)
        await ctx.send(f'{member.mention} banned for {reason}')
    else:
        await ctx.send('You have no permission to use')


bot.command()
@bot.command()
async def unban(ctx, *, member):
    if ctx.author.guild_permissions.ban_members:
        banned_users = await ctx.guild.bans()
        member_name, member_disc = member.split('#')

        for ban_record in banned_users:
            user = ban_record.user

            if (user.name, user.discriminator) == (member_name, member_disc):
                await ctx.guild.unban(user)
                await ctx.send(f'{user.mention} unbanned welcomeback.')
                return

        await ctx.send(f'{member} ban listesinde bulunamadı.')
    else:
        await ctx.send("You have to no permission to use.")







@bot.slash_command(description = "merhaba")
async def greet(ctx,user:Option(discord.Member, "deneme12345")):
    await ctx.respond(f'merhaba {user.mention}')


@bot.command()
async def command(ctx):
    """Show the All commands"""
    embed = discord.Embed(title="Bot Commands", description="Below is a list of available commands:", color=discord.Color.blue())
    embed.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/x7LmPtFsMlQVQznP_t8_ufGt6r-HxnaoYbBinLbd_Y4/https/cdn.ety.gg/ety/img/disc/embed.png")

    embed.add_field(name="!scholardash <username>", value="Displays the scholarship status of a user.", inline=False)
    embed.add_field(name="!ownerdash <username>", value="Displays the ownership status of a user's flags.",
                    inline=False)
    embed.add_field(name="!findusername <username>", value="Finds the username of a user by ID.", inline=False)
    embed.add_field(name="!findid <username>", value="Finds the user ID by username.", inline=False)
    embed.add_field(name="!drops", value="Shows the NFT drop event.", inline=False)
    embed.add_field(name="!stats <username>", value="Displays a user's game statistics.", inline=False)
    embed.add_field(name="!cp", value="Shows the weekly CP leaderboard.", inline=False)
    embed.add_field(name="!participants", value="Lists eligible participants for the giveaway.", inline=False)
    embed.add_field(name="!giveaway", value="Starts the giveaway and announces winners.", inline=False)
    embed.add_field(name='!list_deployed', value='Show the list of deployed clan members', inline=False)
    embed.add_field(name='!clan', value='Clan Info', inline=False)

    await ctx.respond(embed=embed)



@bot.command()
async def clan_info(ctx):
    """Clan Info"""

    api_url = 'https://ev.io/group/10919?_format=json'
    response = requests.get(api_url)
    data = json.loads(response.text)

    # target data
    clan_name = data['label'][0]['value']
    date_str = data['created'][0]['value']
    total_cp = data['field_clan_points'][0]['value']
    weekly_cp = data['field_points_this_week'][0]['value']
    original_format = "%Y-%m-%dT%H:%M:%S%z"







    embed = discord.Embed(title="Clan Info", description="honor for eternity", color=0xa31fe0)
    embed.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/x7LmPtFsMlQVQznP_t8_ufGt6r-HxnaoYbBinLbd_Y4/https/cdn.ety.gg/ety/img/disc/embed.png")
    embed.add_field(name="Creator", value="elialol", inline=True)
    embed.add_field(name="Clan Name", value=clan_name, inline=True)
    embed.add_field(name="created", value=f"u+__", inline=True)
    embed.add_field(name="Total Cp", value=total_cp, inline=True)
    embed.add_field(name="Weekly Cp", value=weekly_cp, inline=True)
    embed.add_field(name="Rank", value='#1', inline=True)
    await ctx.respond(embed=embed)




@bot.command(name='scholardash')
async def scholardash(ctx, username):
    """scholardash information"""
    username_url = f'https://ev.io/jsonapi/user/user?filter[name]={username}'
    r = requests.get(username_url)
    data1 = json.loads(r.text)
    id = data1['data'][0]['attributes'].get('drupal_internal__uid')

    scholar_info = f'https://ev.io/scholar/{id}'
    response = requests.get(scholar_info)
    data = json.loads(response.text)

    # İlk 3 veriyi çekme
    titles = []
    percentages = []
    earnings = []
    cap_reset_time = []

    for i in range(len(data)):
        titles.append(data[i]['title'])
        percentages.append(data[i]['field_scholar_earn_percentage'])
        earnings.append(data[i]['field_earned_today'])

        # Unix zaman damgasını saniyelere dönüştürme
        timestamp = int(data[i]["field_reset_time"]) / 1000
        # Unix zaman damgasını datetime nesnesine çevirme
        reset_time = datetime.utcfromtimestamp(timestamp)

        # Saati Discord formatına çevirme
        formatted_reset_time = f"<t:{int(reset_time.timestamp())}:R>"
        cap_reset_time.append(formatted_reset_time)

    # Embed için 1024 karakter sınırını aşmadan bilgileri eklemek için kullanılacak bir değişken
    message = ''

    embed = discord.Embed(title=f'**Scholarship** Dashboard |  **{username}**', description='honor for eternity',colour=0xd7e665)
    embed.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/x7LmPtFsMlQVQznP_t8_ufGt6r-HxnaoYbBinLbd_Y4/https/cdn.ety.gg/ety/img/disc/embed.png")

    if len(data) == 0:
        # Eğer veri yoksa "Veri bulunamadı" mesajını içeren başka bir embed gönderin.
        embed_not_found = discord.Embed(title="Data Not Found", description=f"no data could be found for {username}",
                                        color=discord.Color.red())
        await ctx.respond(embed=embed_not_found)
        return

    for i in range(len(data)):
        #add
        message += f'**{titles[i]}** | split:%{percentages[i]} | 24h e: {earnings[i]}/2500 | cap reset time:{cap_reset_time[i]}\n\n'

        #if message len >1000 or 1024 idk
        if len(message) > 1000:
            # Önceki embed'i gönderin
            await ctx.respond(embed=embed)

            # Yeni bir embed oluşturun
            embed = discord.Embed(title='', description='')

            # 1024 karakteri geçen bilgileri yeni embed'e ekleyin
            embed.add_field(
                name='Continuation',
                value=message,
                inline=False
            )

           #reset
            message = ''


    embed.add_field(
        name='',
        value=message,
        inline=False
    )


    await ctx.respond(embed=embed)




@bot.command(name='ownerdash')
async def ownerdash(ctx, username):

    """Ownerdash Information"""
    username_url = f'https://ev.io/jsonapi/user/user?filter[name]={username}'
    r = requests.get(username_url)
    data1 = json.loads(r.text)
    get_id = data1['data'][0]['attributes'].get('drupal_internal__uid')

    scholar_info = f'https://ev.io/flags/{get_id}'
    response = requests.get(scholar_info)
    data = json.loads(response.text)

    #İlk 3 veriyi çekme
    titles = []
    percentages = []
    earnings = []
    cap_reset_time = []

    for i in range(len(data)):
        titles.append(data[i]['field_skin'])
        percentages.append(data[i]['field_scholar_earn_percentage'])
        earnings.append(data[i]['field_earned_today'])


        timestamp = int(data[i]["field_reset_time"]) / 1000

        if timestamp > 0:

            reset_time = datetime.utcfromtimestamp(timestamp)

            # Saati Discord formatına çevirme
            formatted_reset_time = f"<t:{int(reset_time.timestamp())}:R>"
        else:
            formatted_reset_time = "Geçerli bir zaman yok"

        cap_reset_time.append(formatted_reset_time)

    #1024
    message = ''

    embed = discord.Embed(title=f'**Owners Dashboard** | **{username}**', description='honor for eternity',colour=discord.Color.random())
    embed.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/x7LmPtFsMlQVQznP_t8_ufGt6r-HxnaoYbBinLbd_Y4/https/cdn.ety.gg/ety/img/disc/embed.png")


    if len(data) == 0:
        # Eğer veri yoksa "Veri bulunamadı" mesajını içeren başka bir embed gönderin.
        embed_not_found = discord.Embed(title="Data No Found", description=f"no data could be found for {username}",
                                        color=discord.Color.red())
        await ctx.respond(embed=embed_not_found)
        return

    for i in range(len(data)):
        # Her bir bilgiyi yeni bir satırda message değişkenine ekleyin
        message += f'**{titles[i]}** | split:%{percentages[i]} | 24h e: {earnings[i]}/2500 | cap reset time:  **{cap_reset_time[i]}**\n\n'

        #if embed len > 1000
        if len(message) > 800:  # Örneğin, 800 karaktere kadar izin verin, böylece embed 1024 karakter sınırını aşmaz.
            # Önceki embed'i gönderin
            embed.add_field(
                name='Continuation',
                value=message,
                inline=False
            )
            await ctx.respond(embed=embed)

            # Yeni bir embed oluşturun
            embed = discord.Embed(title='', description='')

            # message değişkenini sıfırlayın
            message = ''

    # Son kalan bilgileri ekleyin
    embed.add_field(
        name='',
        value=message,
        inline=False
    )



    await ctx.respond(embed=embed)



#find the username by user id
@bot.command(name='findid')
async def find_id(ctx,name):
    """Find id and profile link bu username"""
    url = f'https://ev.io/jsonapi/user/user?filter[name]={name}'

    try:
        #filterin the api with re
        username_match = re.search(r'filter\[name\]=(\w+)', url)

        if username_match:
            username = username_match.group(1)

            #get response
            response = requests.get(url)

            if response.status_code == 200:
                data = json.loads(response.text)

                # information from the api
                internal_id = data['data'][0]['attributes'].get('drupal_internal__uid')
                profile_link = f'https://ev.io/user/{internal_id}'
                await ctx.respond(f'name:{name}\nuserid:{internal_id}\nprofile link:{profile_link}')
    except:
        await ctx.respond('error')


#nft drops or event drops embed
@bot.command()
async def drops(ctx):

    """Show the current Drops(ev.io)"""
    url = 'https://ev.io/nft-drops'
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)

        title = data[1]['title']
        tier = data[1]['field_tier']
        left = data[1]['field_quantity_left']
        gamemode = data[1]['field_game_mode_drop']
        dropchance = float(data[1]['field_drop_chance'])
        dropchance_formatted = f'{dropchance * 100:.2f}%'


        embed = discord.Embed(title="ev.io nft drops", description="honor for eternity", color=discord.Color.random())
        embed.set_thumbnail(
            url="https://images-ext-2.discordapp.net/external/kexoTA85NidxuRW65Ac7if_gKMgoZA-5aahsDIHb6LU/https/ev.io/sites/default/files/whitlist_large_thumbs/fractalusdc.png?width=336&height=671")
        embed.add_field(name="drop", value=title, inline=True)
        embed.add_field(name="tier", value=tier, inline=True)
        embed.add_field(name="drop chance", value=dropchance_formatted, inline=True)
        embed.add_field(name="gamemode", value=gamemode, inline=True)
        embed.add_field(name="how many left", value=left, inline=True)

        await ctx.respond(embed=embed)
    else:
        await ctx.respond('error')



#user stats
@bot.command()
async def stats(ctx, name):
    url = f'https://ev.io/jsonapi/user/user?filter[name]={name}'

    try:
        #filtering api with re
        username_match = re.search(r'filter\[name\]=(\w+)', url)

        if username_match:
            username = username_match.group(1)

            #get response from the url
            response = requests.get(url)

            if response.status_code == 200:
                data = json.loads(response.text)


                # information from the api\target infos
                rating = data['data'][0]['attributes'].get('field_rank')
                kills = data['data'][0]['attributes'].get('field_kills')
                deaths = data['data'][0]['attributes'].get('field_deaths')
                kd = data['data'][0]['attributes'].get('field_k_d')
                kpg = data['data'][0]['attributes'].get('field_kills') / data['data'][0]['attributes'].get('field_total_games')
                dpg = data['data'][0]['attributes'].get('field_deaths') / data['data'][0]['attributes'].get('field_total_games')
                cp_w = data['data'][0]['attributes'].get('field_cp_earned_weekly')
                score_w = data['data'][0]['attributes'].get('field_weekly_score')
                score_t = data['data'][0]['attributes'].get('field_score')
                games_t = data['data'][0]['attributes'].get('field_total_games')
                e_balance = data['data'][0]['attributes'].get('field_ev_coins')
                created_date = data['data'][0]['attributes'].get('created')


                #formatted the created datetime
                date_object = datetime.fromisoformat(created_date)
                discord_formatli_tarih = f"<t:{int(date_object.timestamp())}:R>"



                #round dp and kpg
                round_kpg = round(kpg,2)
                round_dpg = round(dpg,2)



               #embed settings
                embed = discord.Embed(title=username, description="honor for eternity", color=discord.Color.random())
                embed.set_thumbnail(
                    url="https://images-ext-2.discordapp.net/external/x7LmPtFsMlQVQznP_t8_ufGt6r-HxnaoYbBinLbd_Y4/https/cdn.ety.gg/ety/img/disc/embed.png")
                embed.add_field(name="rating", value=rating, inline=True)
                embed.add_field(name="kills", value=kills, inline=True)
                embed.add_field(name="deaths", value=deaths, inline=True)
                embed.add_field(name="k/d", value=kd, inline=True)
                embed.add_field(name="kpg", value=round_kpg, inline=True)
                embed.add_field(name="dpg", value=round_dpg, inline=True)
                embed.add_field(name="weekly CP", value=cp_w, inline=True)
                embed.add_field(name="weekly score", value=score_w, inline=True)
                embed.add_field(name="total score", value=score_t, inline=True)
                embed.add_field(name="total games", value=games_t, inline=True)
                embed.add_field(name="e balance", value=e_balance, inline=True)
                embed.add_field(name="account created", value=discord_formatli_tarih, inline=True)
                await ctx.respond(embed=embed)






            else:
                await ctx.respond('API request denied.')

        else:
            await ctx.respond('error : username not found')

    except Exception as e:
        await ctx.respond(f'Error: {e}')




@bot.command()
async def cp_lb(ctx):
    """Show the top 25 cp leaderboard"""
    url = 'https://ev.io/group/10919'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    data_table = soup.find('table', {'class': 'table table-hover table-striped'})
    table_rows = data_table.find_all('tr')

    leaderboard_data = []
    rank = 1

    #filter the data

    for row in table_rows[1:26]:  #for top 25 players
        columns = row.find_all('td')
        if len(columns) >= 2:
            name = columns[1].text.strip()
            this_week = columns[2].text.strip()
            leaderboard_data.append({'rank': rank, 'name': name, 'this_week': this_week})
            rank += 1

        # Embed
    embed = discord.Embed(title="Top 25 Weekly Cp Leaderboard", color=discord.Color.random(),description='honor for eternity')
    embed.set_footer(text="Earn CP by performing kills whilst being deployed")
    embed.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/x7LmPtFsMlQVQznP_t8_ufGt6r-HxnaoYbBinLbd_Y4/https/cdn.ety.gg/ety/img/disc/embed.png")

    for player in leaderboard_data:
        rank = player['rank']
        name = player['name']
        cp = player['this_week']
        embed.add_field(name=f"#{rank} - **{name}** (CP: {cp})", value='', inline=False)  # '\u200b'  bosluk birakiyor 2 satir guzel gozukmedi ama

    await ctx.respond(embed=embed)





user_data_list = []

#keep he old message or embed here
old_message = None

#updating the embed (30 sec or 1min is okay i think idk)
@tasks.loop(seconds=30)
async def update_nft_info():
    await bot.wait_until_ready()


    global old_message
    if old_message:
        await old_message.delete()  # Eski mesajı sil

    #create new updated embed
    embed = discord.Embed(title='NFT DASHBOARD', description="honor for eternity", color=discord.Color.random())
    embed.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/x7LmPtFsMlQVQznP_t8_ufGt6r-HxnaoYbBinLbd_Y4/https/cdn.ety.gg/ety/img/disc/embed.png")

    for index, user_info in enumerate(user_data_list):
        nft_name = user_info['nft_name']
        tier = user_info['tier']
        owner = user_info['owner']
        price = user_info['price']

        embed.add_field(
            name=f"NFT {index + 1}",
            value=f"**NFT:** {nft_name}\n**Tier:** {tier}\n**Price:** {price}\n**Owner:** {owner}",
            inline=True
        )

    channel = bot.get_channel(1151904433635078274)  #send the discord channel id
    new_message = await channel.send(embed=embed)
    old_message = new_message  #keep the new message here



#add nft(
@bot.command()
async def add_nft(ctx, nft, tier, price, owner):
    user_info = {
        'nft_name': nft,
        'tier': tier,
        'price': price,
        'owner': owner
    }

    user_data_list.append(user_info)  #append the arr

    response = f"{ctx.author.mention}, bilgiler başarıyla kaydedildi."
    await ctx.respond(response)

@bot.command()
async def nfts(ctx):
    global old_message
    if old_message:
        await old_message.delete()  #delete old message

    #create new embed and send the embed
    embed = discord.Embed(title='NFT DASHBOARD', description="honor for eternity", color=discord.Color.random())
    embed.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/x7LmPtFsMlQVQznP_t8_ufGt6r-HxnaoYbBinLbd_Y4/https/cdn.ety.gg/ety/img/disc/embed.png")

    for index, user_info in enumerate(user_data_list):
        nft_name = user_info['nft_name']
        tier = user_info['tier']
        owner = user_info['owner']
        price = user_info['price']

        embed.add_field(
            name=f"NFT {index + 1}",
            value=f"**NFT:** {nft_name}\n**Tier:** {tier}\n**Price:** {price}\n**Owner:** {owner}",
            inline=True
        )

    new_message = await ctx.send(embed=embed)
    old_message = new_message

@bot.command()
async def remove_nft(ctx, nft_index: int):
    try:
        index = int(nft_index) - 1  #change the index for users baecuse indexs starts with 0 then people can confused when theusing the command do not forget
        if 0 <= index < len(user_data_list):
            removed_nft = user_data_list.pop(index)  # remove the nft
            await ctx.send(f"NFT {nft_index} Successfully removed.")
        else:
            await ctx.respond("Invalid Index.")
    except ValueError:
        await ctx.respond("Please enter valid index.") #maybe we can change with embed embeds are looks cool


@bot.command()
async def weather(ctx,city):
    """Weather Information Current"""
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}'
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)

        #target datas
        name = data.get('name')
        weather =data['weather'][0]['description']
        get_temp = data['main']['temp']
        temp = int(get_temp) - 273
        #embed config
        embed = discord.Embed(title=f'Weather information for|{name}', description="weather information", color=discord.Color.random())
        embed.add_field(name='City Name',value=name,inline=True)
        embed.add_field(name='Weather', value=f'{weather}', inline=True)
        embed.add_field(name='Temp', value=f'Temp: {temp}℃  ', inline=True)

        await ctx.respond(embed=embed)

@bot.command()
async def get_balance(ctx,wallet):

    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': 'solana',
        'vs_currencies': 'usd'
    }

    response = requests.get(url, params=params)

    data = response.json()

    sol_price_usd = data['solana']['usd']

    rpc_url = 'https://api.mainnet-beta.solana.com/'  #mainnet is ideal rpc for the req if you want you can request for other rpcs like dev.net


    #rpc req
    rpc_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [wallet], #wallet adress
    }

    # RPC req send
    response = requests.post(rpc_url, json=rpc_request)

    #response and target data
    if response.status_code == 200:
        data = response.json()
        b = data['result']['value']
        balance = b / (10 ** 9)
        sol_usd=balance*sol_price_usd


        round_balance=round(balance,3)
        round_sol_usd=round(sol_usd,2)
        round_sol_price_usd =(sol_price_usd)


        embed = discord.Embed(title='Solana Balance',description='Enter your wallet adress and see your balance',colour=discord.Color.blue())
        embed.set_thumbnail(
            url="https://cryptologos.cc/logos/solana-sol-logo.png?v=026")
        embed.add_field(name='Balance',value=f'Balance:{round_balance}sol',inline=False)
        embed.add_field(name='SOL/USD balance',value=round_sol_usd,inline=False)
        embed.add_field(name='Current Sol Price',value=f'{round_sol_price_usd}$',inline=False)
        await ctx.respond(embed=embed)


@bot.command()
async def deploy(ctx, username):
    """Deploy yourself to earn cp"""
    url = f'https://ev.io/jsonapi/user/user?filter[name]={username}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if 'data' in data and len(data['data']) > 0:
            drupal_internal__uid = data['data'][0]['attributes']['drupal_internal__uid']
            id = data['data'][0]['id']
        else:
            await ctx.respond("User not found.")
            return


        clan_url = "https://ev.io/group/11751?_format=json"  # Clan's API URL


        response1 = requests.get(clan_url)

        if response1.status_code == 200:
            clan_data = response1.json()

            # Check if the same user has been added before
            if "field_deployed" in clan_data:
                existing_users = clan_data["field_deployed"]
                user_exists = any(user.get("target_id") == drupal_internal__uid for user in existing_users)
                if not user_exists:
                    # Create data for the new user to be added
                    new_user = {
                        "target_id": drupal_internal__uid,  # Unique ID of the new user
                        "target_type": "user",
                        "target_uuid": id,  # UUID of the new user
                        "url": f"/user/{drupal_internal__uid}"  # URL of the new user
                    }
                    clan_data["field_deployed"].append(new_user)
                else:
                    await ctx.respond("This user is already deployed.")
                    return
            else:
                clan_data["field_deployed"] = [{
                    "target_id": drupal_internal__uid,
                    "target_type": "user",
                    "target_uuid": id,
                    "url": f"/user/{drupal_internal__uid}"
                }]

            # Create a PATCH request to send the updated clan data back to the server
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Basic emVnYXNlZ2E6Z29rYmVya0Fua2FyYTIwMDg=",
            }
            response2 = requests.patch(clan_url, headers=headers, data=json.dumps(clan_data))


            if response2.status_code == 200:
                await ctx.respond(f'{username} Has been Succesfly Deployed')
            else:
                await ctx.respond(f"Error code: {response1.status_code}, Error message: {response2.text}")
        else:
            await ctx.respond(f"Error code: {response1.status_code}, Error message: {response1.text}")
    else:
        await ctx.respond(f"Error code: {response.status_code}, Error message: {response.text}")



@tasks.loop(minutes=30)
async def reset_clan_data():
    clan_url = "https://ev.io/group/11751?_format=json"


    response = requests.get(clan_url)
    if response.status_code == 200:
        clan_data = response.json()

        # Reset the field_deployed list
        clan_data["field_deployed"] = []


        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic emVnYXNlZ2E6Z29rYmVya0Fua2FyYTIwMDg",
        }
        response = requests.patch(clan_url, headers=headers, data=json.dumps(clan_data))

        if response.status_code == 200:
            print("field_deployed reset successfully.")
        else:
            print(f"Error resetting field_deployed: {response.status_code}, {response.text}")
    else:
        print(f"Error fetching clan data: {response.status_code}, {response.text}")


# Start the loop
reset_clan_data.start()



@bot.slash_command(
    name="list_deployed",
    description="List deployed users."
)
async def list_deployed(ctx):
    # Uygulama yanıtını beklemek için ack (acknowledgment) gönder
    await ctx.defer()

    # API URL'si
    api_url = "https://ev.io/group/11257?_format=json"

    try:
        # API'ye istek gönder
        response = await asyncio.to_thread(requests.get, api_url)

        # İstek başarılı mı kontrol et
        if response.status_code == 200:
            # API yanıtını JSON olarak ayrıştır
            api_data = response.json()

            # "field_deployed" dizisi içindeki "target_id" değerlerini al
            target_ids = [item["target_id"] for item in api_data.get("field_deployed", [])]

            # Kullanıcı adlarını içerecek bir liste oluştur
            user_names = []

            # Kullanıcı adlarını arka planda topla
            async def fetch_user_names(target_id):
                user_api_url = f"https://ev.io/user/{target_id}?_format=json"
                user_response = await asyncio.to_thread(requests.get, user_api_url)

                # İstek başarılı mı kontrol et
                if user_response.status_code == 200:
                    # Kullanıcı API yanıtını JSON olarak ayrıştır
                    user_data = user_response.json()

                    # "name" değerini al (bu değer bir liste içinde olabilir)
                    user_name_list = user_data.get("name", [])

                    # İlk öğeyi al (eğer mevcutsa) ve kullanıcı adlarını listeye ekle
                    if user_name_list:
                        user_name = user_name_list[0].get("value", "Bilinmeyen")
                        user_names.append(user_name)

            tasks = [fetch_user_names(target_id) for target_id in target_ids]
            await asyncio.gather(*tasks)

            user_list = "\n".join([f"**{name}**" for name in user_names])

            # Embed oluştur ve kullanıcı adlarını ekleyin
            embed = discord.Embed(title="Deployed Users", description=user_list, color=0x00ff00)
            embed.set_footer(text="Deploy yourself to earn cp\nDeploy reset time:30 min")
            embed.set_thumbnail(
                url="https://ev.io/sites/default/files/insignias/out-OIG__6_-removebg-preview.png")

            # Embed'i gönder
            await ctx.respond(embed=embed)
        else:
            # İstek başarısızsa hata mesajı gönder
            await ctx.send("Api Error Contact Dev.:" + str(response.status_code))

    except Exception as e:
        # Hata durumunda mesaj gönder
        await ctx.send("Error: " + str(e))


bot.run(TOKEN)