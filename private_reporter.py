from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import PeerChannel
from telethon import functions
from colorama import Fore, init
import asyncio
import argparse
import glob
import os

init(autoreset=True)

api_id = '28805072'          # ← apna daal
api_hash = 'f73ffcf96637c268997b24a029d76cb3'  # ← apna daal

parser = argparse.ArgumentParser(description="Private Channel Reporter - Final Fixed Version")
parser.add_argument('-an', '--add-number', help='Add new account (+91 number)', type=str)
parser.add_argument('-r', '--run', type=int, default=30, help="Reports per account")
parser.add_argument('-t', '--target', type=str, required=True, help="Channel ID (-100xxxxxxxxxx) or username")
parser.add_argument('-m', '--mode', choices=['spam', 'violence', 'fake_account', 'hacking', 'illegal'], default='hacking')
args = parser.parse_args()

# ===================== ACCOUNT ADD =====================
if args.add_number:
    session_name = f"account_{args.add_number.replace('+', '')}"
    client = TelegramClient(session_name, api_id, api_hash)
    try:
        client.start(phone=args.add_number)
        print(f"[{Fore.GREEN}✅{Fore.RESET}] Account added: {args.add_number}")
    except Exception as e:
        print(f"[{Fore.RED}!{Fore.RESET}] Error: {e}")
    client.disconnect()
    exit(0)

# ===================== REPORTING MODE =====================
sessions = glob.glob("*.session")
if not sessions:
    print(f"{Fore.RED}No accounts found! Use -an first.{Fore.RESET}")
    exit(1)

print(f"{Fore.YELLOW}Found {len(sessions)} accounts → Total reports: {len(sessions) * args.run}{Fore.RESET}\n")

reason_map = {
    'spam': b'spam',
    'violence': b'violence',
    'fake_account': b'fake',
    'hacking': b'spam',
    'illegal': b'spam'
}

async def report_from_session(session_file, target, mode, count):
    client = TelegramClient(session_file, api_id, api_hash)
    try:
        await client.start()
        me = await client.get_me()
        username = me.username or me.first_name or "Unknown"

        # Resolve target (private ID or username)
        if str(target).startswith('-100'):
            peer = PeerChannel(int(str(target)[4:]))
            entity = await client.get_entity(peer)
        else:
            entity = await client.get_entity(target)
            if not entity.username:
                await client(JoinChannelRequest(entity))
            peer = entity

        print(f"{Fore.CYAN}[{username}] Reporting: {entity.title or target}{Fore.RESET}")

        for i in range(count):
            for attempt in range(3):  # retry on disconnect
                try:
                    await client(functions.messages.ReportRequest(
                        peer=peer,
                        id=[0],
                        option=reason_map.get(mode, b'spam'),
                        message="Channel selling hacking tools, cheats, loaders, mods - Illegal goods and services / Hacking tools and malware"
                    ))
                    print(f"  [{Fore.GREEN}✅{Fore.RESET}] {username} | Report {i+1}")
                    break
                except Exception as e:
                    if "disconnected" in str(e).lower() or "connection" in str(e).lower():
                        print(f"  [{Fore.YELLOW}Retry{Fore.RESET}] Disconnected, waiting 10s... ({attempt+1}/3)")
                        await asyncio.sleep(10)
                    else:
                        print(f"  [{Fore.RED}!{Fore.RESET}] {username} Error: {e}")
                        break
            await asyncio.sleep(6)  # safe delay

    except Exception as e:
        print(f"{Fore.RED}{username} failed: {e}{Fore.RESET}")
    finally:
        await client.disconnect()

async def main():
    tasks = []
    for session in sessions:
        tasks.append(report_from_session(session, args.target, args.mode, args.run))
    await asyncio.gather(*tasks)

asyncio.run(main())
