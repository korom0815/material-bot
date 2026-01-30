import discord
from discord.ext import commands
import json
import os
import re

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    pattern = r"(.+?)×(-?\d+)"
    match = re.match(pattern, message.content)

    if match:
        item = match.group(1).strip()
        count = int(match.group(2))
        user = message.author.display_name

        if item not in data:
            data[item] = {}

        if user not in data[item]:
            data[item][user] = 0

        data[item][user] += count

        if data[item][user] <= 0:
            del data[item][user]

        if not data[item]:
            del data[item]

        save_data(data)

        await message.channel.send(
            f"📦 {item} を {count} 個反映しました"
        )

    # 👇 これが無いとコマンドが死ぬ
    await bot.process_commands(message)


@bot.command()
async def item(ctx, *, item_name):
    if item_name not in data:
        await ctx.send("未登録のアイテムです")
        return

    total = 0
    lines = []

    for user_tag, count in data[item_name].items():
        total += count

        # ユーザー名だけ取り出す（名前#1234 → 名前）
        username = user_tag.split("#")[0]
        lines.append(f"{username} : {count}")

    text = f"【{item_name} 所持一覧】\n"
    text += "\n".join(lines)
    text += f"\n---\n合計 : {total}"

    await ctx.send(text)


@bot.command()
@commands.has_permissions(administrator=True)
async def reset(ctx, *, item_name):
    if item_name not in data:
        await ctx.send("そのアイテムは登録されていません")
        return

    del data[item_name]
    save_data(data)
    await ctx.send(f"🗑 {item_name} のカウントをリセットしました")



import os
bot.run(os.getenv("TOKEN"))
