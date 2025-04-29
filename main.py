from bs4 import BeautifulSoup
import requests
import urllib.parse
import re # Importing the regular expression module

# Define a pattern to match common Persian/Arabic characters
# This pattern includes most letters and digits used in Persian, plus common punctuation that might appear in remarks.
# You might need to adjust this pattern based on what specifically you want to exclude.
# This pattern looks for the Unicode range of Arabic/Persian characters, plus common numbers and some symbols.
PERSIAN_CHARS_PATTERN = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\u0030-\u0039\u0660-\u0669\s.,!?:;-]')


def contains_persian_chars(text):
    """
    Checks if a string contains characters commonly used in Persian or Arabic.

    Args:
        text (str): The string to check.

    Returns:
        bool: True if Persian/Arabic characters are found, False otherwise.
    """
    if not text:
        return False
    # Search for the pattern in the text
    return bool(PERSIAN_CHARS_PATTERN.search(text))


def get_filtered_vless_links(url):
    """
    Fetches content from a Telegram channel URL and extracts VLESS configuration links
    excluding those with ports 80 or 8080, and those with Persian remarks.

    Args:
        url (str): The URL of the Telegram channel.

    Returns:
        list: A list of extracted and filtered VLESS configuration strings, or None if fetching fails.
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
    # Adding a more general search for span and div
    possible_tags.extend(soup.find_all('span'))
    possible_tags.extend(soup.find_all('div'))

    filtered_vless_configs = []
    for tag in possible_tags:
        text = tag.get_text().strip()

        if text.startswith('vless://'):
            try:
                # Decode the URL
                decoded_text = urllib.parse.unquote(text)

                # Parse the VLESS URL to extract its components
                parsed_url = urllib.parse.urlparse(decoded_text)

                # Extract the port
                port = parsed_url.port

                # *** Check if the port is 80 or 8080 ***
                if port is not None and (port == 80 or port == 8080):
                    # print(f"Skipping VLESS config with filtered port: {text}") # Optional: print skipped links
                    continue # Skip this config because its port is 80 or 8080

                # *** Check if the remark (fragment) contains Persian characters ***
                remark = parsed_url.fragment # The part after '#' is usually the remark
                if contains_persian_chars(remark):
                    # print(f"Skipping VLESS config with Persian remark: {remark} in {text}") # Optional: print skipped links
                    continue # Skip this config because its remark contains Persian characters

                # If both filters pass, add the config
                filtered_vless_configs.append(decoded_text)

            except Exception as e:
                # If parsing or decoding fails, skip or handle appropriately
                print(f"Error parsing or decoding VLESS URL: {e} - {text}")
                # Skipping configs that fail to parse/decode
                continue


    return filtered_vless_configs


def save_all_configs(configs, filename="Subs_VLESS_No8080_NoPersianRemark.txt"):
    """
    Saves a list of configuration strings to a file.

    Args:
        configs (list): A list of configuration strings.
        filename (str): The name of the file to save the configurations to.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(configs))
        print(f"Saved { len(configs) } unique filtered VLESS configs to {filename}")
    except IOError as e:
        print(f"Error saving configs to file {filename}: {e}")

if __name__ == "__main__":
    telegram_urls = [
        "https://t.me/s/v2line",
        "https://t.me/s/forwardv2ray",
        "https://t.me/s/inikotesla",
        "https://t.me/s/PrivateVPNs",
        "https://t.me/s/VlessConfig",
        "https://t.me/s/V2pedia",
        "https://t.me/s/v2rayNG_Matsuri",
        "https://t.me/s/PrivateVPNs",
        "https://t.me/s/proxystore11",
        "https://t.me/s/DirectVPN",
        "https://t.me/s/VmessProtocol",
        "https://t.me/s/OutlineVpnOfficial",
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
        "https://t.me/s/v2_vmess",
        "https://t.me/s/FreeVlessVpn",
        "https://t.me/s/vmess_vless_v2rayng",
        "https://tme.cat/s/PrivateVPNs",
        "https://t.me/s/freeland8",
        "https://t.me/s/vmessiran",
        "https://t.me/s/Outline_Vpn",
        "https://t.me/s/vmessq",
        "https://t.me/s/WeePeeN",
        "https://tme.cat/s/V2rayNG3",
        "https://tme.cat/s/ShadowsocksM",
        "https://tme.cat/s/shadowsocksshop",
        "https://t.me/s/v2rayan",
        "https://tme.cat/s/ShadowSocks_s",
        "https://t.me/s/VmessProtocol",
        "https://t.me/s/napsternetv_config",
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

    all_filtered_vless_configs = []
    for url in telegram_urls:
        configs = get_filtered_vless_links(url)
        if configs:
            all_filtered_vless_configs.extend(configs)

    if all_filtered_vless_configs:
        # Remove duplicates
        unique_configs = list(set(all_filtered_vless_configs))
        # Save to a file
        save_all_configs(unique_configs, filename="Subs_VLESS_No8080_NoPersianRemark.txt")
    else:
        print("No filtered VLESS configs found.")
