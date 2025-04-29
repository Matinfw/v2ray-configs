from bs4 import BeautifulSoup
import requests
import urllib.parse

def get_vless_links(url):
    """
    Fetches content from a Telegram channel URL and extracts VLESS configuration links.

    Args:
        url (str): The URL of the Telegram channel.

    Returns:
        list: A list of extracted VLESS configuration strings, or None if fetching fails.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Search for potential tags containing configuration
    possible_tags = soup.find_all(class_=[
        'tgme_widget_message_text',
        'tgme_widget_message_text js-message_text before_footer'
    ])
    possible_tags.extend(soup.find_all('span', class_='tgme_widget_message_text'))
    possible_tags.extend(soup.find_all('code'))
    # Adding a more general search for span and div to catch more cases,
    # but this might include noise, so we rely heavily on the startswith check.
    possible_tags.extend(soup.find_all('span'))
    possible_tags.extend(soup.find_all('div'))

    vless_configs = []
    for tag in possible_tags:
        text = tag.get_text().strip()
        # *** Changed: Only check for vless:// protocol ***
        if text.startswith('vless://'):
            # Decode the URL to handle potential encoding issues in the config string
            try:
                decoded_text = urllib.parse.unquote(text)
                vless_configs.append(decoded_text)
            except Exception as e:
                print(f"Error decoding URL: {e} - {text}")
                vless_configs.append(text) # Add the original text if decoding fails

    return vless_configs


def save_all_configs(configs, filename="Subs_VLESS.txt"):
    """
    Saves a list of configuration strings to a file.

    Args:
        configs (list): A list of configuration strings.
        filename (str): The name of the file to save the configurations to.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(configs))
        print(f"Saved { len(configs) } unique VLESS configs to {filename}")
    except IOError as e:
        print(f"Error saving configs to file {filename}: {e}")

if __name__ == "__main__":
    telegram_urls = [
        "https://t.me/s/v2line",
        "https://t.me/s/forwardv2ray",
        "https://t.me/s/inikotesla",
        "https://t.me/s/PrivateVPNs",
        "https://t.me/s/VlessConfig", # این کانال بیشتر محتوای vless خواهد داشت
        "https://t.me/s/V2pedia",
        "https://t.me/s/v2rayNG_Matsuri",
        "https://t.me/s/PrivateVPNs",
        "https://t.me/s/proxystore11",
        "https://t.me/s/DirectVPN",
        "https://t.me/s/VmessProtocol", # احتمالا کمتر VLESS داشته باشد
        "https://t.me/s/OutlineVpnOfficial", # احتمالا کمتر VLESS داشته باشد
        "https://t.me/s/networknim",
        "https://t.me/s/beiten",
        "https://t.me/s/MsV2ray",
        "https://t.me/s/foxrayiran",
        "https://t.me/s/DailyV2RY",
        "https://t.me/s/yaney_01",
        "https://tme.cat/s/FreakConfig",
        "https://t.me/s/EliV2ray",
        "https://t.me/s/ServerNett",
        "https://t.me/s/proxystore11",
        "https://t.me/s/v2rayng_fa2",
        "https://tme.cat/s/v2rayng_org",
        "https://tme.cat/s/V2rayNGvpni",
        "https://t.me/s/custom_14",
        "https://tme.cat/s/v2rayNG_VPNN",
        "https://t.me/s/v2ray_outlineir",
        "https://t.me/s/v2_vmess", # احتمالا کمتر VLESS داشته باشد
        "https://t.me/s/FreeVlessVpn", # این کانال بیشتر محتوای vless خواهد داشت
        "https://t.me/s/vmess_vless_v2rayng",
        "https://tme.cat/s/PrivateVPNs",
        "https://t.me/s/freeland8",
        "https://t.me/s/vmessiran", # احتمالا کمتر VLESS داشته باشد
        "https://t.me/s/Outline_Vpn", # احتمالا کمتر VLESS داشته باشد
        "https://t.me/s/vmessq", # احتمالا کمتر VLESS داشته باشد
        "https://t.me/s/WeePeeN",
        "https://tme.cat/s/V2rayNG3",
        "https://tme.cat/s/ShadowsocksM", # احتمالا کمتر VLESS داشته باشد
        "https://tme.cat/s/shadowsocksshop", # احتمالا کمتر VLESS داشته باشد
        "https://t.me/s/v2rayan",
        "https://tme.cat/s/ShadowSocks_s", # احتمالا کمتر VLESS داشته باشد
        "https://t.me/s/VmessProtocol", # احتمالا کمتر VLESS داشته باشد
        "https://t.me/s/napsternetv_config", # احتمالا کمتر VLESS داشته باشد
        "https://t.me/s/Easy_Free_VPN",
        "https://t.me/s/V2Ray_FreedomIran",
        "https://t.me/s/V2RAY_VMESS_free",
        "https://t.me/s/v2ray_for_free",
        "https://tme.cat/s/V2RayN_Free",
        "https://t.me/s/free4allVPN",
        "https://t.me/s/vpn_ocean",
        "https://tme.cat/s/configV2rayForFree",
        "https://t.me/s/FreeV2rays",
        "https://t.me/s/DigiV2ray",
        "https://t.me/s/v2rayNG_VPN",
        "https://tme.cat/s/freev2rayssr",
        "https://tme.cat/s/v2rayn_server",
        "https://tme.cat/s/Shadowlinkserverr",
        "https://t.me/s/iranvpnet",
        "https://tme.cat/s/vmess_iran",
        "https://tme.cat/s/mahsaamoon1",
        "https://t.me/s/V2RAY_NEW",
        "https://t.me/s/v2RayChannel",
        "https://tme.cat/s/configV2rayNG",
        "https://tme.cat/s/config_v2ray",
        "https://tme.cat/s/vpn_proxy_custom",
        "https://tme.cat/s/vpnmasi",
        "https://tme.cat/s/v2ray_custom",
        "https://tme.cat/s/VPNCUSTOMIZE",
        "https://tme.cat/s/HTTPCustomLand",
        "https://tme.cat/s/vpn_proxy_custom",
        "https://tme.cat/s/ViPVpn_v2ray",
        "https://tme.cat/s/FreeNet1500",
        "https://tme.cat/s/v2ray_ar",
        "https://tme.cat/s/beta_v2ray",
        "https://tme.cat/s/vip_vpn_2022",
        "https://tme.cat/s/FOX_VPN66",
        "https://tme.cat/s/VorTexIRN",
        "https://tme.cat/s/YtTe3la",
        "https://tme.cat/s/V2RayOxygen",
        "https://tme.cat/s/Network_442",
        "https://tme.cat/s/VPN_443",
        "https://tme.cat/s/v2rayng_v",
        "https://tme.cat/s/ultrasurf_12",
        "https://tme.cat/s/iSeqaro",
        "https://tme.cat/s/frev2rayng",
        "https://tme.cat/s/frev2ray",
        "https://tme.cat/s/FreakConfig",
        "https://tme.cat/s/Awlix_ir",
        "https://tme.cat/s/v2rayngvpn",
        "https://tme.cat/s/God_CONFIG",
        "https://tme.cat/s/Configforvpn01",
    ]

    all_vless_configs = []
    for url in telegram_urls:
        # *** Changed: Call the function that specifically gets VLESS links ***
        configs = get_vless_links(url)
        if configs:
            all_vless_configs.extend(configs)

    if all_vless_configs:
        # Remove duplicates
        unique_configs = list(set(all_vless_configs))
        # *** Changed: Save to a file with a different name to distinguish VLESS configs ***
        save_all_configs(unique_configs, filename="Subs_VLESS.txt")
    else:
        print("No VLESS configs found.")
