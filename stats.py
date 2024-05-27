import requests
import json
from better_proxy import Proxy
from pyuseragents import random as randomaf
import re

n = 40
class NFTCopilotClient:
    def __init__(self, proxy):
        self.base_url = "https://nftcopilot.com/p-api/layer-zero-rank/check"
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": "Bearer null",
            "Content-Type": "application/json",
            "Origin": "https://nftcopilot.com",
            "Referer": "",
            "Sec-Ch-Ua": '"Opera";v="109", "Not:A-Brand";v="8", "Chromium";v="123"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": randomaf()
        }
        self.proxy = proxy

    def create_referer(self, addresses):
        base_referer = "https://nftcopilot.com/layer-zero-rank-check?address="
        address_str = "%0A".join(addresses)
        self.headers["Referer"] = f"{base_referer}{address_str}"

    def post_request(self, address, addresses):
        payload = {
            "address": address,
            "addresses": addresses,
            "c": "check"
        }
        self.create_referer(addresses)
        response = requests.post(self.base_url, headers=self.headers, data=json.dumps(payload),
                                 proxies=self.proxy.as_proxies_dict)
        if response.status_code == 429:
            raise Exception("Rate limited")
        return response.json()


def read_proxies(file_path):
    proxies = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                proxies.append(Proxy.from_str(f"http://{line}"))
    return proxies


def extract_addresses(address_file):
    addresses = []
    with open(address_file, 'r') as file:
        for line in file:
            match = re.search(r'https://debank\.com/profile/(0x[a-fA-F0-9]{40})', line)
            if match:
                addresses.append(match.group(1))
    return addresses


def format_as_markdown_table(results):
    headers = ["Address", "Rank", "Top", "Txn", "Volume", "Contracts", "Months", "Source Chains", "Destination Chains"]
    rows = []
    for result in results:
        rows.append([
            result["address"],
            result["rank"],
            f"{result['topFinal']}%",
            result["txsCount"],
            result["volume"],
            result["contracts"],
            result["distinctMonths"],
            result["networks"],
            result["destChains"]
        ])

    # Find the maximum length of each column
    col_widths = [max(len(str(row[i])) for row in rows + [headers]) for i in range(len(headers))]

    # Create the Markdown table
    table = "| " + " | ".join(f"{header:<{col_widths[i]}}" for i, header in enumerate(headers)) + " |\n"
    table += "|-" + "-|-".join('-' * col_width for col_width in col_widths) + "-|\n"
    for row in rows:
        table += "| " + " | ".join(f"{str(row[i]):<{col_widths[i]}}" for i in range(len(row))) + " |\n"

    return table


def main():
    # Extract addresses from file
    address_file = 'report.md'
    addresses = extract_addresses(address_file)

    # Read and parse proxies
    proxies = read_proxies('proxy.txt')
    proxy_index = 0
    total_proxies = len(proxies)

    results = []

    for i in range(0, len(addresses), n):
        address_chunk = addresses[i:i + n]

        while True:
            try:
                proxy = proxies[proxy_index]
                client = NFTCopilotClient(proxy)
                result = client.post_request(address_chunk[0], address_chunk)
                results.extend(result)
                proxy_index = (proxy_index + 1) % total_proxies  # Circular rotation of proxies
                break
            except Exception as e:
                if "Rate limited" in str(e):
                    print("Rate limited")
                    proxy_index = (proxy_index + 1) % total_proxies  # Circular rotation of proxies
                else:
                    print(f"Error: {e}")
                    break

    # Print results as a Markdown table
    markdown_table = format_as_markdown_table(results)
    print(markdown_table)

    # Save the Markdown table to output.md
    with open('output.md', 'w') as f:
        f.write(markdown_table)

if __name__ == "__main__":
    main()