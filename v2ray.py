import asyncio
import os
import re
import subprocess
import time
from telethon import TelegramClient
import pycountry
from ip2geotools.databases.noncommercial import DbIpCity
import urllib.parse

# بررسی متغیرهای محیطی
def check_env_vars():
    required_vars = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 'TELEGRAM_PHONE', 'GITHUB_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"متغیرهای محیطی زیر تنظیم نشده‌اند: {', '.join(missing_vars)}")

check_env_vars()

# متغیرهای محیطی
api_id = int(os.getenv('TELEGRAM_API_ID'))
api_hash = os.getenv('TELEGRAM_API_HASH')
phone_number = os.getenv('TELEGRAM_PHONE')

# لیست کانال‌های تلگرامی
channels = [
    "https://t.me/s/V2rayNG_VPN",
    "https://t.me/s/configs_v2ray",
    "https://t.me/s/ConfigKamaprox",
    "https://t.me/s/iranian_vpn_free",
    "https://t.me/s/vmess_iran",
    "https://t.me/s/outline_vpn",
    "https://t.me/s/v2ray_outline",
    "https://t.me/s/vpn_ocean",
    "https://t.me/s/iranvpntunnel",
    "https://t.me/s/pr0xy_mix",
    "https://t.me/s/Vless_Pro",
    "https://t.me/s/VMESS_SERVER",
    "https://t.me/s/SERVER_VLESS",
    "https://t.me/s/Server_iran",
    "https://t.me/s/vmess_vless_trojan",
    "https://t.me/s/hashmakvpn",
    "https://t.me/s/proxy_server",
    "https://t.me/s/V2rayConfig",
    "https://t.me/s/MsV2ray",
    "https://t.me/s/freconnect",
    "https://t.me/s/server_digi",
    "https://t.me/s/fox_vpn_free",
    "https://t.me/s/Pars_vpn",
    "https://t.me/s/iran_vpn_v2ray",
    "https://t.me/s/ok_vpn",
    "https://t.me/s/vpn_black",
    "https://t.me/s/shahanshan_vpn",
    "https://t.me/s/king_vpn",
    "https://t.me/s/day_vpn",
    "https://t.me/s/ConfigsV2ray_Plus",
    "https://t.me/s/SHADOWSOCKS_VPN",
    "https://t.me/s/VPNCLEAKS",
    "https://t.me/s/aparat_vpn",
    "https://t.me/s/Helix_Configs",
    "https://t.me/s/ircfconfig",
    "https://t.me/s/MTConfig",
    "https://t.me/s/MehradHydel_VPN",
    "https://t.me/s/Internet4Iranians",
    "https://t.me/s/server_amireu",
    "https://t.me/s/TeamSecureTunnel",
    "https://t.me/s/Configs_Vpn_bali",
    "https://t.me/s/FreeVmessVlessV2ray",
    "https://t.me/s/EasyConfigs",
    "https://t.me/s/Vpn_Fast",
    "https://t.me/s/Pro_Max_Config",
    "https://t.me/s/UnlimitedFreeConfigs",
    "https://t.me/s/OutlineVpnOfficial",
    "https://t.me/s/Power_Vpn",
    "https://t.me/s/VPNIRANORG",
    "https://t.me/s/Outline_conf",
    "https://t.me/s/V2ray_Collector",
    "https://t.me/s/FreakConfig",
    "https://t.me/s/Custom_Config",
    "https://t.me/s/VPNMODIFY",
    "https://t.me/s/NapsternetV_VPN",
    "https://t.me/s/Proxy_chnnel",
    "https://t.me/s/GephConnector",
    "https://t.me/s/iranfreeby",
    "https://t.me/s/Azadi_az_net",
    "https://t.me/s/VPNCUSTOMIZE",
    "https://t.me/s/iran_azadi_vpn",
    "https://t.me/s/Parsian_vpn",
    "https://t.me/s/AzadNetiran",
    "https://t.me/s/Net_Proxy_V2ray",
    "https://t.me/s/ShadowrocketChannel",
    "https://t.me/s/ServiceSocks",
    "https://t.me/s/Outline_Free_Iran",
    "https://t.me/s/proxyiranvpn",
    "https://t.me/s/NetFaz",
    "https://t.me/s/ProxyMTprotoTest",
    "https://t.me/s/Proxyha_channel",
    "https://t.me/s/irproxy_tci",
    "https://t.me/s/iFoox",
    "https://t.me/s/freeproxy",
    "https://t.me/s/VpnShah",
    "https://t.me/s/TelNET",
    "https://t.me/s/DailyV2ray",
    "https://t.me/s/Network_source",
    "https://t.me/s/FreakProxy",
    "https://t.me/s/DigiVPN",
    "https://t.me/s/SocinConfigs",
    "https://t.me/s/InternetGV",
    "https://t.me/s/SpeedPlus_Config",
    "https://t.me/s/Oneclickvpnfree",
    "https://t.me/s/Config_for_All",
    "https://t.me/s/FreeVpnForIran2022",
    "https://t.me/s/NateTeam",
    "https://t.me/s/PandoVPN",
    "https://t.me/s/VPN_Exp",
    "https://t.me/s/SafeNet_Server",
    "https://t.me/s/Directvpn",
    "https://t.me/s/NetBoxConfig",
    "https://t.me/s/free_vpn_iran2023",
    "https://t.me/s/AvvalTeam",
    "https://t.me/s/iranv2ray",
    "https://t.me/s/Daily_Free_VPN",
    "https://t.me/s/Server_shah",
    "https://t.me/s/v2line",
    "https://t.me/s/forwardv2ray",
    "https://t.me/s/inikotesla",
    "https://t.me/s/PrivateVPNs",
    "https://t.me/s/VlessConfig",
    "https://t.me/s/V2pedia",
    "https://t.me/s/v2rayNG_Matsuri",
    "https://t.me/s/proxystore11",
    "https://t.me/s/DirectVPN",
    "https://t.me/s/VmessProtocol",
    "https://t.me/s/networknim",
    "https://t.me/s/beiten",
    "https://t.me/s/foxrayiran",
    "https://t.me/s/DailyV2RY",
    "https://t.me/s/yaney_01",
    "https://t.me/s/EliV2ray",
    "https://t.me/s/ServerNett",
    "https://t.me/s/v2rayng_fa2",
    "https://t.me/s/v2rayng_org",
    "https://t.me/s/V2rayNGvpni",
    "https://t.me/s/custom_14",
    "https://t.me/s/v2rayNG_VPNN",
    "https://t.me/s/v2ray_outlineir",
    "https://t.me/s/v2_vmess",
    "https://t.me/s/FreeVlessVpn",
    "https://t.me/s/vmess_vless_v2rayng",
    "https://t.me/s/freeland8",
    "https://t.me/s/vmessiran",
    "https://t.me/s/Outline_Vpn",
    "https://t.me/s/vmessq",
    "https://t.me/s/WeePeeN",
    "https://t.me/s/V2rayNG3",
    "https://t.me/s/ShadowsocksM",
    "https://t.me/s/shadowsocksshop",
    "https://t.me/s/v2rayan",
    "https://t.me/s/ShadowSocks_s",
    "https://t.me/s/napsternetv_config",
    "https://t.me/s/Easy_Free_VPN",
    "https://t.me/s/V2Ray_FreedomIran",
    "https://t.me/s/V2RAY_VMESS_free",
    "https://t.me/s/v2ray_for_free",
    "https://t.me/s/V2rayN_Free",
    "https://t.me/s/free4allVPN",
    "https://t.me/s/configV2rayForFree",
    "https://t.me/s/FreeV2rays",
    "https://t.me/s/DigiV2ray",
    "https://t.me/s/freev2rayssr",
    "https://t.me/s/v2rayn_server",
    "https://t.me/s/Shadowlinkserverr",
    "https://t.me/s/iranvpnet",
    "https://t.me/s/mahsaamoon1",
    "https://t.me/s/V2RAY_NEW",
    "https://t.me/s/v2RayChannel",
    "https “‘https://t.me/s/configV2rayNG",
    "https://t.me/s/config_v2ray",
    "https://t.me/s/vpnmasi",
    "https://t.me/s/v2ray_custom",
    "https://t.me/s/HTTPCustomLand",
    "https://t.me/s/ViPVpn_v2ray",
    "https://t.me/s/FreeNet1500",
    "https://t.me/s/v2ray_ar",
    "https://t.me/s/beta_v2ray",
    "https://t.me/s/vip_vpn_2022",
    "https://t.me/s/FOX_VPN66",
    "https://t.me/s/VorTexIRN",
    "https://t.me/s/YtTe3la",
    "https://t.me/s/V2RayOxygen",
    "https://t.me/s/Network_442",
    "https://t.me/s/VPN_443",
    "https://t.me/s/v2rayng_v",
    "https://t.me/s/ultrasurf_12",
    "https://t.me/s/iSeqaro",
    "https://t.me/s/frev2rayng",
    "https://t.me/s/frev2ray",
    "https://t.me/s/Awlix_ir",
    "https://t.me/s/v2rayngvpn",
    "https://t.me/s/God_CONFIG",
    "https://t.me/s/Configforvpn01"
]

# لیست کشورهای مجاز
allowed_countries = [
    'United States', 'Russia', 'Australia', 'United Kingdom', 'Germany',
    'Sweden', 'Finland', 'Estonia', 'Denmark', 'Luxembourg', 'Japan',
    'Singapore', 'Mexico', 'Brazil'
]

# پورت‌های غیرمجاز
forbidden_ports = ['80', '8080', '8181', '3128']

# تابع بررسی متن فارسی
def contains_persian(text):
    persian_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(persian_pattern.search(text))

# تابع استخراج IP و پورت از کانفیگ VLESS
def extract_ip_port(config):
    try:
        parsed = urllib.parse.urlparse(config)
        ip_port = parsed.netloc.split(':')
        ip = ip_port[0]
        port = ip_port[1] if len(ip_port) > 1 else None
        return ip, port
    except:
        return None, None

# تابع بررسی کشور سرور
def get_country(ip):
    try:
        response = DbIpCity.get(ip, api_key='free')
        country = response.country
        country_name = pycountry.countries.get(alpha_2=country).name
        return country_name
    except:
        return None

# تابع اصلی جمع‌آوری کانفیگ‌ها
async def collect_vless_configs():
    client = TelegramClient('session_name', api_id, api_hash)
    await client.start(phone=phone_number)
    
    valid_configs = []
    
    for channel in channels:
        channel_name = channel.split('/')[-1]
        try:
            async for message in client.iter_messages(channel_name, limit=100):
                if not message.text:
                    continue
                    
                if 'vless://' in message.text:
                    configs = re.findall(r'(vless://[^\s]+)', message.text)
                    for config in configs:
                        if contains_persian(config):
                            continue
                            
                        ip, port = extract_ip_port(config)
                        if port in forbidden_ports:
                            continue
                            
                        if ip:
                            country = get_country(ip)
                            if country in allowed_countries:
                                valid_configs.append(config)
        except Exception as e:
            print(f"خطا در پردازش کانال {channel_name}: {str(e)}")
    
    await client.disconnect()
    return valid_configs

# تابع اصلی
async def main():
    configs = await collect_vless_configs()
    with open('vless_configs.txt', 'w') as f:
        for config in configs:
            f.write(config + '\n')
    print(f"تعداد کانفیگ‌های معتبر: {len(configs)}")
    
    # Push به GitHub
    try:
        subprocess.run(['git', 'config', '--global', 'user.name', 'Railway Bot'])
        subprocess.run(['git', 'config', '--global', 'user.email', 'bot@railway.app'])
        subprocess.run(['git', 'add', 'vless_configs.txt'])
        subprocess.run(['git', 'commit', '-m', 'Update VLESS configs'])
        subprocess.run(['git', 'push', 'origin', 'main'], env={'GIT_ASKPASS': 'echo', 'GIT_USERNAME': 'x-oauth-basic', 'GIT_PASSWORD': os.getenv('GITHUB_TOKEN')})
    except Exception as e:
        print(f"خطا در push به GitHub: {str(e)}")

# اجرای دوره‌ای
async def run_periodically():
    while True:
        await main()
        print("در انتظار اجرای بعدی (6 ساعت)...")
        await asyncio.sleep(6 * 60 * 60)  # هر 6 ساعت

if __name__ == '__main__':
    asyncio.run(run_periodically())
