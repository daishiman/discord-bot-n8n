import discord
import aiohttp
import os
from flask import Flask
from threading import Thread

# 環境変数から取得
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')

# Flask アプリ（Railway用のhealthcheck）
app = Flask('')

@app.route('/')
def home():
    return "Discord Bot is running!", 200

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_flask, daemon=True)
    t.start()
    print('✅ Healthcheck server started')

# Discord Bot設定
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(
    intents=intents,
    heartbeat_timeout=60
)

@client.event
async def on_ready():
    print(f'✅ {client.user} でログイン成功！')
    print(f'🔗 n8n Webhook URL: {N8N_WEBHOOK_URL}')
    print(f'🤖 接続済みサーバー数: {len(client.guilds)}')

@client.event
async def on_resumed():
    print('🔄 セッションが再開されました')

@client.event
async def on_disconnect():
    print('⚠️ 切断されました')

@client.event
async def on_error(event, *args, **kwargs):
    import traceback
    print(f'❌ エラーが発生: {event}')
    traceback.print_exc()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(f'📩 メッセージ受信: {message.content[:50]}...')

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
        async with aiohttp.ClientSession() as session:
            async with session.post(
                N8N_WEBHOOK_URL,
                json=data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                print(f'✅ n8nへ送信成功: {response.status}')
    except aiohttp.ClientError as e:
        print(f'❌ HTTP エラー: {e}')
    except Exception as e:
        print(f'❌ 予期しないエラー: {e}')

if __name__ == '__main__':
    if not DISCORD_TOKEN:
        print('❌ DISCORD_TOKEN が設定されていません')
        exit(1)
    if not N8N_WEBHOOK_URL:
        print('❌ N8N_WEBHOOK_URL が設定されていません')
        exit(1)

    keep_alive()

    try:
        client.run(DISCORD_TOKEN)
    except Exception as e:
        print(f'❌ Bot起動エラー: {e}')
        exit(1)