import discord
import requests
import os

# 環境変数から取得
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ {client.user} でログイン成功！')
    print(f'🔗 n8n Webhook URL: {N8N_WEBHOOK_URL}')

@client.event
async def on_message(message):
    # Bot自身のメッセージは無視
    if message.author == client.user:
        return

    print(f'📩 メッセージ受信: {message.content}')

    # n8nに送信するデータ
    data = {
        "content": message.content,
        "author": str(message.author),
        "author_id": str(message.author.id),
        "channel": str(message.channel.name) if hasattr(message.channel, 'name') else 'DM',
        "channel_id": str(message.channel.id),
        "guild": str(message.guild.name) if message.guild else None,
        "guild_id": str(message.guild.id) if message.guild else None,
        "timestamp": message.created_at.isoformat()
    }

    try:
        response = requests.post(N8N_WEBHOOK_URL, json=data, timeout=10)
        print(f'✅ n8nへ送信成功: {response.status_code}')
    except Exception as e:
        print(f'❌ エラー: {e}')

# Botを起動
if __name__ == '__main__':
    if not DISCORD_TOKEN:
        print('❌ DISCORD_TOKEN が設定されていません')
        exit(1)
    if not N8N_WEBHOOK_URL:
        print('❌ N8N_WEBHOOK_URL が設定されていません')
        exit(1)

    client.run(DISCORD_TOKEN)