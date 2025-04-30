# install required libraries if needed (e.g., in GitHub Actions)
# pip install telethon pycountry ip2geotools

import asyncio
import os
import re
import subprocess
import time
from telethon import TelegramClient
import pycountry
from ip2geotools.databases.noncommercial import DbIpCity
import urllib.parse

api_id = 21294482
api_hash = '990ec4db2f39b94eb696f2058369b931'
phone_number = '+989226562298'
github_token = os.getenv('GITHUB_TOKEN') 

channels = [
    "https://t.me/s/sinavm"
    
]

allowed_countries = [
    'United States', 'Russia', 'Australia', 'United Kingdom', 'Germany',
    'Sweden', 'Finland', 'Estonia', 'Denmark', 'Luxembourg', 'Japan',
    'Singapore', 'Mexico', 'Brazil', 
    'Canada', 'Netherlands', 'Ukraine' 
]

forbidden_ports = ['80', '8080', '8181', '3128']

SESSION_FILE = 'telegram_session' 

def contains_persian(text):
    persian_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(persian_pattern.search(text))

def extract_ip_port(config):
    try:
        parsed = urllib.parse.urlparse(config)
        ip_port = parsed.netloc.split(':')
        if parsed.scheme == 'hysteria2':
             host_port = parsed.netloc
             if '[' in host_port and ']' in host_port: 
                 match = re.match(r'\[([0-9a-fA-F:]+)\](?::(\d+))?', host_port)
                 if match:
                     ip = match.group(1)
                     port = match.group(2)
                 else:
                     ip = None
                     port = None
             else: 
                 parts = host_port.split(':')
                 ip = parts[0]
                 port = parts[1] if len(parts) > 1 else None
        else: 
            ip_port = parsed.netloc.split(':')
            ip = ip_port[0]
            port = ip_port[1] if len(ip_port) > 1 else None
        return ip, port
    except Exception as e:
        print(f"Error parsing config {config}: {e}")
        return None, None

def get_country(ip):
    if not ip or not re.match(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|\[?([0-9a-fA-F:]+)\]?)$', str(ip)):
        return None 

    try:
        response = DbIpCity.get(str(ip), api_key='free')
        country = response.country
        if country == 'ZZ':
            return 'Unknown' 

        try:
             country_name = pycountry.countries.get(alpha_2=country).name
             return country_name
        except AttributeError:
             print(f"pycountry could not resolve country code: {country}")
             return country 
    except Exception as e:
        return None

async def collect_vless_hysteria2_configs():
    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    
    try:
        await client.start(phone=phone_number) 
        print("Telethon client started.")
    except Exception as e:
        print(f"Error starting Telethon client: {str(e)}")
        return [] 
    
    valid_configs = []
    
    for channel in channels:
        channel_identifier = channel.split('/')[-1] 
        if channel_identifier.startswith('s/'): 
            channel_identifier = channel_identifier[2:]

        try:
            print(f"Fetching messages from channel: {channel_identifier}")
            async for message in client.iter_messages(channel_identifier, limit=200, reverse=True): 
                if not message or not message.text:
                    continue
                    
                configs = re.findall(r'(vless://[^\s]+|hysteria2://[^\s]+)', message.text)
                if configs:
                    for config in configs:
                        if contains_persian(config):
                            continue
                            
                        ip, port = extract_ip_port(config)
                        if port and port in forbidden_ports: 
                            continue
                        
                        if not ip:
                             continue

                        country = get_country(ip)
                        
                        if country is None or country == 'Unknown' or country in allowed_countries:
                             valid_configs.append(config)

                await asyncio.sleep(0.05) 

        except Exception as e:
            print(f"Error processing channel {channel_identifier}: {str(e)}")
            
    try:
        await client.disconnect()
        print("Disconnected from Telegram.")
    except Exception as e:
        print(f"Error disconnecting from Telegram: {str(e)}")

    return valid_configs

async def main():
    print("Starting main execution...")
    try:
        configs = await collect_vless_hysteria2_configs()
        
        unique_configs = list(dict.fromkeys(configs)) 

        if unique_configs: 
            output_filename = 'V2ray_configs.txt'
            
            try:
                with open(output_filename, 'r') as f:
                    existing_configs = f.read().splitlines()
            except FileNotFoundError:
                existing_configs = []

            if sorted(unique_configs) != sorted(existing_configs): 
                print(f"Writing {len(unique_configs)} valid configurations to {output_filename}.")
                with open(output_filename, 'w') as f:
                    for config in unique_configs:
                        f.write(config + '\n')
                
                try:
                    subprocess.run(['git', 'config', '--global', 'user.name', 'GitHub Actions Bot'], check=True)
                    subprocess.run(['git', 'config', '--global', 'user.email', 'github-actions@github.com'], check=True)
                    
                    if os.path.exists(output_filename):
                        add_result = subprocess.run(['git', 'add', output_filename])
                        if add_result.returncode != 0:
                             print(f"Error adding {output_filename} to git index.")

                        result_status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, check=True)
                        if output_filename in result_status.stdout: 
                            print("Changes detected. Committing...")
                            commit_result = subprocess.run(['git', 'commit', '-m', 'Update VLESS and Hysteria2 configs via GitHub Actions'], check=True)
                            if commit_result.returncode == 0:
                                print("Pushing changes to GitHub...")
                                try:
                                    current_branch_result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True, check=True)
                                    current_branch = current_branch_result.stdout.strip()
                                    
                                    push_result = subprocess.run(['git', 'push', 'origin', current_branch], timeout=180, check=True) 
                                    if push_result.returncode == 0:
                                         print("GitHub push complete.")
                                    else:
                                        print(f"Git push failed with return code {push_result.returncode}.")

                                except subprocess.TimeoutExpired:
                                    print("Git push timed out after 180 seconds.")
                                except subprocess.CalledProcessError as e:
                                    print(f"Git push failed: {e}")
                                    print(f"Stderr: {e.stderr}")
                                    print(f"Stdout: {e.stdout}")
                                except Exception as e:
                                     print(f"An unexpected error during git push: {str(e)}")
                            else:
                                print("Git commit failed. No changes pushed.")
                        else:
                            print("No staged changes to commit/push.")
                    
                except subprocess.CalledProcessError as e:
                    print(f"A Git subprocess command failed: {e}")
                    print(f"Stderr: {e.stderr}")
                    print(f"Stdout: {e.stdout}")
                except Exception as e:
                    print(f"An unexpected error in Git operations: {str(e)}")

            else:
                 print("Configuration file content is the same. No write or push needed.")

        else:
            print("No valid configurations found after collection. No file write or push performed.")
        
    except Exception as e:
        print(f"An unexpected error occurred during the main execution: {str(e)}")

if __name__ == "__main__":
    try:
        print("Starting the script...")
        asyncio.run(main())
        print("Script finished.")
    except Exception as e:
        print(f"An error occurred during script execution: {str(e)}")
