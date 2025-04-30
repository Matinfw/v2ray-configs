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

# GitHub Actions uses environment variables for secrets
# These should be set as secrets in your GitHub repository settings
# You can keep default values here for local testing if preferred,
# but for security, rely on GitHub Secrets in production.
api_id = int(os.getenv('TELEGRAM_API_ID', 'YOUR_DEFAULT_API_ID')) # Replace YOUR_DEFAULT_API_ID if needed
api_hash = os.getenv('TELEGRAM_API_HASH', 'YOUR_DEFAULT_API_HASH') # Replace YOUR_DEFAULT_API_HASH if needed
phone_number = os.getenv('TELEGRAM_PHONE', 'YOUR_DEFAULT_PHONE') # Replace YOUR_DEFAULT_PHONE if needed
github_token = os.getenv('GITHUB_TOKEN') # This MUST be set as a GitHub Secret

# list of Telegram channels
channels = [
    "https://t.me/s/sinavm"
    
]

# list of allowed countries
allowed_countries = [
    'United States', 'Russia', 'Australia', 'United Kingdom', 'Germany',
    'Sweden', 'Finland', 'Estonia', 'Denmark', 'Luxembourg', 'Japan',
    'Singapore', 'Mexico', 'Brazil', 
    'Canada', 'Netherlands', 'Ukraine' 
]

# forbidden ports
forbidden_ports = ['80', '8080', '8181', '3128']

# Session file name - Important for GitHub Actions to persist session
SESSION_FILE = 'telegram_session' 

# function to check for Persian text
def contains_persian(text):
    persian_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(persian_pattern.search(text))

# function to extract IP and port from VLESS or Hysteria2 config
def extract_ip_port(config):
    try:
        parsed = urllib.parse.urlparse(config)
        ip_port = parsed.netloc.split(':')
        # For hysteria2, the host might be the whole netloc before parameters
        if parsed.scheme == 'hysteria2':
             # hysteria2://hostname:port?params...
             # urlparse puts 'hostname:port' in netloc
             host_port = parsed.netloc
             if '[' in host_port and ']' in host_port: # Handle IPv6
                 match = re.match(r'\[([0-9a-fA-F:]+)\](?::(\d+))?', host_port)
                 if match:
                     ip = match.group(1)
                     port = match.group(2)
                 else:
                     ip = None
                     port = None
             else: # Handle IPv4 or hostname
                 parts = host_port.split(':')
                 ip = parts[0]
                 port = parts[1] if len(parts) > 1 else None
        else: # Assume VLESS or similar
            ip_port = parsed.netloc.split(':')
            ip = ip_port[0]
            port = ip_port[1] if len(ip_port) > 1 else None
        return ip, port
    except Exception as e:
        print(f"Error parsing config {config}: {e}")
        return None, None

# function to get server country
def get_country(ip):
    # Simple validation for IP format (basic)
    if not ip or not re.match(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|\[?([0-9a-fA-F:]+)\]?)$', str(ip)):
        # print(f"Skipping country check for invalid IP format: {ip}") # Optional: too verbose
        return None # Skip lookup for invalid formats

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
        # print(f"Error getting country for IP {ip}: {e}") # Optional: too verbose
        return None

# main function to collect configs
async def collect_vless_hysteria2_configs():
    # Use the session file name for Telethon
    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    
    try:
        # Connect and start - will handle authentication if needed
        await client.start(phone=phone_number) 
        print("Telethon client started.")
    except Exception as e:
        print(f"Error starting Telethon client: {str(e)}")
        # In GitHub Actions, failing here means the workflow fails
        return [] 
    
    valid_configs = []
    
    for channel in channels:
        channel_identifier = channel.split('/')[-1] 
        if channel_identifier.startswith('s/'): 
            channel_identifier = channel_identifier[2:]

        try:
            print(f"Fetching messages from channel: {channel_identifier}")
            # Limit to 200 messages for potentially more configs
            # Use reverse=True to get recent messages first (might be slightly faster)
            async for message in client.iter_messages(channel_identifier, limit=200, reverse=True): 
                if not message or not message.text:
                    continue
                    
                configs = re.findall(r'(vless://[^\s]+|hysteria2://[^\s]+)', message.text)
                if configs:
                    # print(f"Found {len(configs)} potential configs in a message.") # Optional: too verbose
                    for config in configs:
                        if contains_persian(config):
                            continue
                            
                        ip, port = extract_ip_port(config)
                        if port and port in forbidden_ports: 
                            continue
                        
                        if not ip:
                             continue

                        country = get_country(ip)
                        
                        # Include configs if country is allowed or unknown
                        if country is None or country == 'Unknown' or country in allowed_countries:
                             valid_configs.append(config)
                        # else:
                             # print(f"Skipping config from disallowed country {country} for IP {ip}: {config}") # Optional: too verbose

                await asyncio.sleep(0.05) # Smaller delay to fetch faster, adjust if needed

        except Exception as e:
            print(f"Error processing channel {channel_identifier}: {str(e)}")
            
    try:
        # Ensure client is disconnected before exiting
        await client.disconnect()
        print("Disconnected from Telegram.")
    except Exception as e:
        print(f"Error disconnecting from Telegram: {str(e)}")

    return valid_configs

# main function
async def main():
    print("Starting main execution...")
    try:
        configs = await collect_vless_hysteria2_configs()
        
        # Remove duplicates
        unique_configs = list(dict.fromkeys(configs)) # Faster way to remove duplicates while preserving order

        if unique_configs: 
            output_filename = 'vless_hysteria2_configs.txt'
            
            # Check if the file content has changed before writing
            try:
                with open(output_filename, 'r') as f:
                    existing_configs = f.read().splitlines()
            except FileNotFoundError:
                existing_configs = []

            # Compare unique configs with existing file content
            if sorted(unique_configs) != sorted(existing_configs): 
                print(f"Writing {len(unique_configs)} valid configurations to {output_filename}.")
                with open(output_filename, 'w') as f:
                    for config in unique_configs:
                        f.write(config + '\n')
                
                # Git operations for GitHub Actions
                try:
                    # Set Git user details - important for committing
                    subprocess.run(['git', 'config', '--global', 'user.name', 'GitHub Actions Bot'], check=True)
                    subprocess.run(['git', 'config', '--global', 'user.email', 'github-actions@github.com'], check=True)
                    
                    # Add the file
                    add_result = subprocess.run(['git', 'add', output_filename])
                    if add_result.returncode != 0:
                         print(f"Error adding {output_filename} to git index.")
                         # Decide if you want to stop here or continue

                    # Check for staged changes before committing
                    result_status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, check=True)
                    if output_filename in result_status.stdout: 
                        print("Changes detected. Committing...")
                        # Commit the changes
                        commit_result = subprocess.run(['git', 'commit', '-m', 'Update VLESS and Hysteria2 configs via GitHub Actions'], check=True)
                        if commit_result.returncode == 0:
                            print("Pushing changes to GitHub...")
                            # Push to the repository using the GITHUB_TOKEN
                            # The GITHUB_TOKEN is automatically available as an environment variable in actions
                            # We don't need GIT_ASKPASS or manual password here, the action runner handles auth
                            try:
                                # Push to the current branch (usually main or master)
                                # Get current branch name - robust way
                                current_branch_result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True, check=True)
                                current_branch = current_branch_result.stdout.strip()
                                
                                # Use --force-with-lease if you want to overwrite potential concurrent commits (use with caution)
                                # For a simple append workflow, a normal push should be fine.
                                push_result = subprocess.run(['git', 'push', 'origin', current_branch], timeout=180, check=True) 
                                if push_result.returncode == 0:
                                     print("GitHub push complete.")
                                else:
                                    print(f"Git push failed with return code {push_result.returncode}.")
                                    # This might indicate authentication issues or conflicts

                            except subprocess.TimeoutExpired:
                                print("Git push timed out after 180 seconds.")
                                # This might indicate network issues or a large history
                            except subprocess.CalledProcessError as e:
                                print(f"Git push failed: {e}")
                                print(f"Stderr: {e.stderr}")
                                print(f"Stdout: {e.stdout}")
                            except Exception as e:
                                 print(f"An unexpected error during git push: {str(e)}")
                        else:
                            print("Git commit failed. No changes pushed.")
                            # Examine commit_result.stderr for details if needed
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


# GitHub Actions typically run a script once, not periodically in a loop.
# The scheduling is handled by the GitHub Actions workflow file (.github/workflows/*.yml).
# So, we remove the periodic loop and just run the main function once.

# Use asyncio.run() for a simpler entry point in a single execution script
# asyncio.run() handles loop creation and closing.

if __name__ == "__main__":
    # In GitHub Actions, KeyboardInterrupt is not relevant as it's not interactive.
    # The script will run to completion or error.
    try:
        print("Starting the script...")
        # Use asyncio.run to run the async main function
        asyncio.run(main())
        print("Script finished.")
    except Exception as e:
        print(f"An error occurred during script execution: {str(e)}")
        # In GitHub Actions, a non-zero exit code indicates failure.
        # raise # Re-raise the exception if you want the action to fail explicitly
