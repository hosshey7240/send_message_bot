#コードはあくまで一例
import discord
from discord import app_commands
from discord.ext import tasks
import json
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
send_movie_path = ""#動画のパスを入れる
send_movie_data = "" #付属のjsonのパスを入れる(ONとOFFの管理に必要)

def load_json():
    with open(send_movie_data, "r") as f:
        return json.load(f)

def save_json(status):
    with open(send_movie_data,"w") as f:
        json.dump(status,f,indent=4)
    
@tree.command(name="readme",description="先に読んでくれ")
async def readme(interaction: discord.Interaction):
    readme_embed = discord.Embed(title="readmeだよ",description="botの設定はお済みでしょうか\nコードにあるパスを指定しないと動かないので注意してね")
    await interaction.response.send_message(embed=readme_embed)


@tree.command(name="send_movie",description="動画を送るか送らないかの切り替えができます")
@app_commands.default_permissions(manage_messages=True)
@discord.app_commands.choices(option=[
    discord.app_commands.Choice(name="ON", value="ON"),
    discord.app_commands.Choice(name="OFF", value="OFF")
])
async def send_movie_message(interaction: discord.Interaction,option:str):
    if option == "ON":
        status = load_json()
        channel_id_kari = interaction.channel.id
        channel_id = str(channel_id_kari)
        status[channel_id] = True  
        save_json(status)
        on_send_movie_embed = discord.Embed(title="設定しました",description="動画の送信をONにしました",color=discord.Color.brand_green())
        await interaction.response.send_message(embed=on_send_movie_embed)
    elif option == "OFF":
        status = load_json()
        channel_id_kari = interaction.channel.id
        channel_id = str(channel_id_kari)
        status[channel_id] = False  # 現在のチャンネルを OFF に設定
        save_json(status)
        off_send_movie_embed = discord.Embed(title="設定しました",description="動画の送信をOFFにしました",color=discord.Color.brand_green())
        await interaction.response.send_message(embed=off_send_movie_embed)


@tasks.loop(minutes=20)  # 20分おきに実行(ここをいじったら何分に一度動くとかできるけど悪用厳禁)
async def send_video():
    status = load_json()
    for channel_id, is_on in status.items():
       if is_on:  # ON の場合のみ送信
            channel = client.get_channel(int(channel_id))
            if channel: #Noneじゃないなら
                try:
                    # 動画ファイルを送信 
                    await channel.send("",file=discord.File(send_movie_path)) #「""」にメッセージを置く
                    print(f"動画を {channel.name} に送信しました。")
                except Exception as e:
                    print(f"動画送信エラー: {e}")
            else:
                print("チャンネルが見つかりません。IDを確認してください。")

client.run(TOKEN)