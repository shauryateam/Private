from telethon.sync import TelegramClient
from colorama import Fore

api_id = 28805072  # ← yahan apna daal
api_hash = 'f73ffcf96637c268997b24a029d76cb3'  # ← yahan apna daal

client = TelegramClient('get_id_session', api_id, api_hash)

async def main():
    await client.start()
    print(f"{Fore.CYAN}Private channels jisme tu member hai:{Fore.RESET}\n")
    async for dialog in client.iter_dialogs():
        if dialog.is_channel and not dialog.entity.username:
            print(f"Title: {dialog.title}")
            print(f"Channel ID: -100{dialog.id}   ← yeh copy kar lena")
            print("-" * 50)

with client:
    client.loop.run_until_complete(main())
