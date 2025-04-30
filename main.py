# install required libraries if needed (e.g., in GitHub Actions)
# pip install telethon pycountry ip2geotools

import asyncio
import os
import re
import subprocess
import time
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest # اضافه شده
import pycountry
from ip2geotools.databases.noncommercial import DbIpCity
import urllib.parse

# اطلاعات API تلگرام و شماره تلفن
# بهتر است از محیط (Environment) برای این اطلاعات استفاده کنید
api_id = 21294482 # example_api_id - Replace with your actual api_id
api_hash = '990ec4db2f39b94eb696f2058369b931' # example_api_hash - Replace with your actual api_hash
phone_number = '+989226562298' # Replace with your actual phone number

# توکن گیت‌هاب برای احراز هویت در عملیات Git Push
github_token = os.getenv('GITHUB_TOKEN')

# لیست کانال‌هایی که می‌خواهید کانفیگ‌ها را از آن‌ها جمع‌آوری کنید
# مطمئن شوید که این لینک‌ها صحیح و قابل دسترسی هستند (کانال‌های عمومی یا لینک دعوت معتبر)
channels = [
    "https://t.me/s/sinavm",
    # می توانید کانال های دیگر را اینجا اضافه کنید
    # "https://t.me/s/another_channel",
    # "https://t.me/some_public_channel"
]

# لیست کشورهایی که کانفیگ‌های مربوط به آن‌ها مجاز هستند
allowed_countries = [
    'United States', 'Russia', 'Australia', 'United Kingdom', 'Germany',
    'Sweden', 'Finland', 'Estonia', 'Denmark', 'Luxembourg', 'Japan',
    'Singapore', 'Mexico', 'Brazil',
    'Canada', 'Netherlands', 'Ukraine'
]

# لیست پورت‌هایی که استفاده از آن‌ها در کانفیگ مجاز نیست
forbidden_ports = ['80', '8080', '8181', '3128']

# نام فایل برای ذخیره اطلاعات جلسه تلگرام
SESSION_FILE = 'telegram_session'

# تابع برای بررسی وجود کاراکترهای فارسی در متن
def contains_persian(text):
    persian_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(persian_pattern.search(text))

# تابع برای استخراج آدرس IP و پورت از لینک کانفیگ
def extract_ip_port(config):
    try:
        parsed = urllib.parse.urlparse(config)
        # بررسیscheme برای Hysteria2 که فرمت netloc متفاوتی دارد
        if parsed.scheme == 'hysteria2':
             host_port = parsed.netloc
             # هندل کردن آدرس های IPv6 داخل براکت
             if '[' in host_port and ']' in host_port:
                 match = re.match(r'\[([0-9a-fA-F:]+)\](?::(\d+))?', host_port)
                 if match:
                     ip = match.group(1)
                     port = match.group(2)
                 else:
                     ip = None
                     port = None # یا می توانید پورت پیش فرض Hysteria2 را در نظر بگیرید
             else: # هندل کردن آدرس های IPv4 یا نام دامنه
                 parts = host_port.split(':')
                 ip = parts[0]
                 port = parts[1] if len(parts) > 1 else None
        else: # برای سایر schemes مانند vless
            ip_port = parsed.netloc.split(':')
            ip = ip_port[0]
            port = ip_port[1] if len(ip_port) > 1 else None
        return ip, port
    except Exception as e:
        print(f"Error parsing config {config}: {e}")
        return None, None

# تابع برای دریافت نام کشور بر اساس آدرس IP
def get_country(ip):
    # اعتبار سنجی اولیه آدرس IP (IPv4 و IPv6)
    if not ip or not re.match(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|\[?([0-9a-fA-F:]+)\]?)$', str(ip)):
        # print(f"Invalid IP format: {ip}") # می توانید برای دیباگ فعال کنید
        return None

    try:
        # استفاده از DbIpCity برای دریافت اطلاعات جغرافیایی
        response = DbIpCity.get(str(ip), api_key='free')
        country_code = response.country
        if country_code == 'ZZ': # ZZ معمولا برای آدرس های ناشناخته استفاده می شود
            return 'Unknown'

        try:
            # تبدیل کد کشور (alpha_2) به نام کامل کشور
            country_name = pycountry.countries.get(alpha_2=country_code).name
            return country_name
        except AttributeError:
            # اگر pycountry نتوانست کد کشور را تشخیص دهد
            print(f"pycountry could not resolve country code: {country_code}")
            return country_code # کد کشور خام را برمی گرداند
    except Exception as e:
        # خطاهای احتمالی در هنگام فراخوانی DbIpCity یا network issues
        # print(f"Error getting country for IP {ip}: {e}") # می توانید برای دیباگ فعال کنید
        return None

# تابع برای عضویت خودکار در کانال های مشخص شده
async def join_channels(client, channels_list):
    print("Trying to join specified channels...")
    for channel_url in channels_list:
        try:
            # استخراج نام کاربری کانال از لینک
            channel_identifier = channel_url.split('/')[-1]
            if channel_identifier.startswith('s/'):
                channel_identifier = channel_identifier[2:]

            print(f"Attempting to join channel: {channel_identifier}")

            # ارسال درخواست عضویت به تلگرام
            await client(JoinChannelRequest(channel_identifier))
            print(f"Successfully joined or already a member of channel: {channel_identifier}")
            await asyncio.sleep(1) # مکث کوتاه برای جلوگیری از محدودیت API

        except Exception as e:
            print(f"Could not join channel {channel_identifier}: {str(e)}")
            # می توانید منطق مدیریت خطا را در اینجا اضافه کنید، مثلاً اگر کانال خصوصی است و نیاز به لینک دعوت دارد

# تابع برای جمع آوری کانفیگ های VLESS و Hysteria2 از کانال ها
async def collect_vless_hysteria2_configs(client, channels_list):
    valid_configs = []

    for channel in channels_list:
        channel_identifier = channel.split('/')[-1]
        if channel_identifier.startswith('s/'):
            channel_identifier = channel_identifier[2:]

        try:
            print(f"Fetching messages from channel: {channel_identifier}")
            # پیمایش در پیام‌های کانال (محدود به 200 پیام آخر)
            async for message in client.iter_messages(channel_identifier, limit=200, reverse=True):
                if not message or not message.text:
                    continue

                # پیدا کردن الگوهای VLESS و Hysteria2 در متن پیام
                configs = re.findall(r'(vless://[^\s]+|hysteria2://[^\s]+)', message.text)
                if configs:
                    for config in configs:
                        # فیلتر کردن کانفیگ‌هایی که حاوی کاراکتر فارسی هستند
                        if contains_persian(config):
                            continue

                        # استخراج IP و پورت
                        ip, port = extract_ip_port(config)
                        if not ip: # اگر استخراج IP با مشکل مواجه شد، از این کانفیگ صرف نظر کنید
                             continue

                        # فیلتر کردن پورت‌های ممنوعه
                        if port and port in forbidden_ports:
                            # print(f"Skipping config due to forbidden port {port}: {config}") # می توانید برای دیباگ فعال کنید
                            continue

                        # دریافت کشور مربوط به IP
                        country = get_country(ip)

                        # فیلتر بر اساس کشور (اگر کشور ناشناخته است یا در لیست کشورهای مجاز است)
                        if country is None or country == 'Unknown' or country in allowed_countries:
                            valid_configs.append(config)
                            # print(f"Found valid config from {country}: {config}") # می توانید برای دیباگ فعال کنید
                        # else:
                            # print(f"Skipping config from forbidden country {country}: {config}") # می توانید برای دیباگ فعال کنید

                # مکث کوتاه برای جلوگیری از محدودیت API هنگام پردازش پیام‌ها
                await asyncio.sleep(0.05)

        except Exception as e:
            print(f"Error processing channel {channel_identifier}: {str(e)}")

    return valid_configs

# تابع اصلی برای اجرای فرآیند
async def main():
    print("Starting script execution...")
    # ایجاد کلاینت تلگرام
    client = TelegramClient(SESSION_FILE, api_id, api_hash)

    try:
        # شروع اتصال به تلگرام
        await client.start(phone=phone_number)
        print("Telethon client started successfully.")

        # مرحله اول: عضویت در کانال‌های مشخص شده
        await join_channels(client, channels)

        # مرحله دوم: جمع‌آوری کانفیگ‌ها از کانال‌ها
        configs = await collect_vless_hysteria2_configs(client, channels)

        # حذف کانفیگ‌های تکراری
        unique_configs = list(dict.fromkeys(configs))
        print(f"Found {len(unique_configs)} unique valid configurations.")

        # نام فایل خروجی
        output_filename = 'V2ray_configs.txt'

        # خواندن کانفیگ‌های موجود در فایل (اگر وجود دارد)
        existing_configs = []
        try:
            if os.path.exists(output_filename):
                with open(output_filename, 'r') as f:
                    existing_configs = f.read().splitlines()
        except Exception as e:
            print(f"Error reading existing configs file {output_filename}: {str(e)}")

        # مقایسه کانفیگ‌های جدید با کانفیگ‌های موجود
        # اگر لیست کانفیگ‌های جدید با لیست موجود تفاوت داشته باشد
        if sorted(unique_configs) != sorted(existing_configs):
            print(f"Changes detected. Writing {len(unique_configs)} valid configurations to {output_filename}.")
            try:
                # نوشتن کانفیگ‌های جدید در فایل
                with open(output_filename, 'w') as f:
                    for config in unique_configs:
                        f.write(config + '\n')

                # شروع عملیات Git برای Commit و Push تغییرات
                try:
                    # تنظیم اطلاعات کاربری Git برای GitHub Actions
                    subprocess.run(['git', 'config', '--global', 'user.name', 'GitHub Actions Bot'], check=True)
                    subprocess.run(['git', 'config', '--global', 'user.email', 'github-actions@github.com'], check=True)

                    # افزودن فایل تغییر یافته به Git Index
                    add_result = subprocess.run(['git', 'add', output_filename])
                    if add_result.returncode != 0:
                         print(f"Error adding {output_filename} to git index. Return code: {add_result.returncode}")
                         # می توانید stderr و stdout را برای اطلاعات بیشتر چاپ کنید

                    # بررسی وضعیت Git برای اطمینان از وجود تغییرات Staged شده
                    result_status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, check=True)
                    if output_filename in result_status.stdout:
                        print("Changes staged. Committing...")
                        # کامیت کردن تغییرات
                        commit_result = subprocess.run(['git', 'commit', '-m', 'Update VLESS and Hysteria2 configs via GitHub Actions'], check=True)

                        if commit_result.returncode == 0:
                            print("Git commit successful. Pushing changes to GitHub...")
                            try:
                                # دریافت نام شاخه فعلی
                                current_branch_result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True, check=True)
                                current_branch = current_branch_result.stdout.strip()

                                # Push تغییرات به مخزن GitHub
                                # timeout برای جلوگیری از هنگ کردن بی نهایت
                                push_result = subprocess.run(['git', 'push', 'origin', current_branch], timeout=180, check=True)

                                if push_result.returncode == 0:
                                     print("GitHub push complete.")
                                else:
                                    print(f"Git push failed with return code {push_result.returncode}.")
                                    # می توانید stderr و stdout را برای اطلاعات بیشتر چاپ کنید

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
                            # می توانید stderr و stdout را برای اطلاعات بیشتر چاپ کنید
                    else:
                        print("No staged changes to commit/push.")

                except subprocess.CalledProcessError as e:
                    print(f"A Git subprocess command failed: {e}")
                    print(f"Stderr: {e.stderr}")
                    print(f"Stdout: {e.stdout}")
                except Exception as e:
                    print(f"An unexpected error in Git operations: {str(e)}")

            except Exception as e:
                 print(f"Error writing configurations to file {output_filename}: {str(e)}")

        else:
             print("Configuration file content is the same. No write or push needed.")

    except Exception as e:
        print(f"An unexpected error occurred during the main execution: {str(e)}")
    finally:
        # اطمینان از قطع اتصال کلاینت تلگرام در نهایت
        if client and client.is_connected():
            try:
                await client.disconnect()
                print("Disconnected from Telegram.")
            except Exception as e:
                print(f"Error disconnecting from Telegram: {str(e)}")

# نقطه شروع اجرای اسکریپت
if __name__ == "__main__":
    try:
        print("Script started.")
        asyncio.run(main())
        print("Script finished.")
    except Exception as e:
        print(f"An error occurred during script execution: {str(e)}")
