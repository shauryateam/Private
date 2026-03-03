from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import PeerChannel
from telethon import functions
from telethon.sessions import StringSession
from colorama import Fore, init
import asyncio
import argparse
import os

init(autoreset=True)

api_id = 28805072
api_hash = 'f73ffcf96637c268997b24a029d76cb3'

parser = argparse.ArgumentParser(description="Private Channel Reporter - Multi Account")
parser.add_argument('-an', '--add-number', help='Add a new account (phone with +91)', type=str)
parser.add_argument('-r', '--run', type=int, help="Number of reports per account")
parser.add_argument('-t', '--target', type=str, help="Channel ID (-100xxxxxxxxxx) or username")
parser.add_argument('-m', '--mode', choices=['spam', 'violence', 'fake_account', 'hacking', 'illegal'], default='spam')
args = parser.parse_args()

# Account add karne ka logic
if args.add_number:
    session_name = f"account_{args.add_number.replace('+', '')}"
    client = TelegramClient(session_name, api_id, api_hash)
    try:
        client.start(phone=args.add_number)
        print(f"[{Fore.GREEN}✅{Fore.RESET}] Account added: {args.add_number} (Session: {session_name})")
    except Exception as e:
        print(f"[{Fore.RED}!{Fore.RESET}] Error adding account: {e}")
    client.disconnect()
    exit(0)

# Agar add nahi to reporting mode
if not args.run or not args.target:
    parser.print_help()
    exit(1)

reason_map = {
    'spam': b'spam',
    'violence': b'violence',
    'fake_account': b'fake',
    'hacking': b'spam',
    'illegal': b'spam'
}

async def report_channel(client, target, mode, count):
    try:
        if str(target).startswith('-100'):
            channel_id = int(str(target)[4:])
            peer = PeerChannel(channel_id)
            entity = await client.get_entity(peer)
        else:
            entity = await client.get_entity(target)
            if not entity.username:
                await client(JoinChannelRequest(entity))
            peer = entity

        print(f"{Fore.CYAN}Reporting from {await client.get_me().username}: {entity.title or target}{Fore.RESET}")
        print(f"Mode: {mode} | Per account: {count}\n")

        for i in range(count):
            try:
                await client(functions.messages.ReportRequest(
                    peer=peer,
                    id=[0],
                    option=reason_map.get(mode, b'spam'),
                    message="Channel selling hacking tools, cheats, loaders - Illegal goods and services / Hacking tools and malware"
                ))
                print(f"[{Fore.GREEN}✅{Fore.RESET}] Reported | Count: {i+1}")
            except Exception as e:
                print(f"[{Fore.RED}!{Fore.RESET}] Error: {e}")
                break
            await asyncio.sleep(3)  # anti-flood delay

    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Fore.RESET}")

async def main():
    # Sab sessions folder se load karo
    sessions = [f for f in os.listdir('.') if f.endswith('.session')]
    if not sessions:
        print(f"{Fore.RED}No accounts added! Use -an to add numbers first.{Fore.RESET}")
        exit(1)

    print(f"{Fore.YELLOW}Found {len(sessions)} accounts!{Fore.RESET}\n")

    tasks = []
    for session in sessions:
        client = TelegramClient(session, api_id, api_hash)
        tasks.append(report_channel(client, args.target, args.mode, args.run))

    await asyncio.gather(*tasks)

asyncio.run(main())
