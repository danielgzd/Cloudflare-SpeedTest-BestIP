#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def check_ip_range(ip: str):
    """检查IP属于哪个Cloudflare IP段"""
    ip_parts = ip.split('.')
    if len(ip_parts) < 2:
        return "Unknown"
    
    first = int(ip_parts[0])
    second = int(ip_parts[1])
    
    # Cloudflare官方IP段：https://www.cloudflare.com/ips/
    # IPv4 ranges
    
    # 检查是否在已知的Cloudflare IP段中
    if first == 173 and second == 245:
        return "173.245.48.0/20 (US)"
    elif first == 188 and second == 114:
        return "188.114.96.0/20 (US)"
    elif first == 162 and second == 158:
        return "162.158.0.0/15 (US)"
    elif first == 162 and second == 159:
        return "162.159.0.0/16 (US)"
    elif first == 104 and 16 <= second <= 31:
        return f"104.{second}.0.0/16 (US)"
    elif first == 172 and 64 <= second <= 71:
        return f"172.{second}.0.0/16 (US)"
    elif first == 198 and second == 41:
        return "198.41.128.0/17 (US)"
    elif first == 108 and second == 162:
        return "108.162.192.0/18 (US)"
    elif first == 141 and second == 101:
        return "141.101.64.0/18 (EU)"
    elif first == 190 and second == 93:
        return "190.93.240.0/20 (HK)"
    elif first == 103 and second == 21:
        return "103.21.244.0/22 (JP)"
    elif first == 103 and second == 22:
        return "103.22.200.0/22 (KR)"
    elif first == 103 and second == 31:
        return "103.31.4.0/22 (SG)"
    elif first == 197 and second == 234:
        return "197.234.240.0/22 (IN)"
    else:
        return "Unknown/Other"

# 测试 best_ip.txt 中被分类为 "Other" 的IP
other_ips = [
    "173.245.59.249",
    "188.114.97.52", 
    "173.245.58.24",
    "188.114.98.180",
    "188.114.99.12",
    "188.114.96.128",
    "173.245.49.220"
]

print("Checking IPs classified as 'Other' in best_ip.txt:")
print("=" * 60)
for ip in other_ips:
    ip_range = check_ip_range(ip)
    print(f"{ip}: {ip_range}")

# 检查一些美国IP
print("\n\nChecking some US IPs from best_ip.txt:")
print("=" * 60)
us_ips = [
    "172.65.95.96",
    "172.65.205.98",
    "162.159.13.51",
    "172.66.207.200",
    "172.67.217.70"
]

for ip in us_ips:
    ip_range = check_ip_range(ip)
    print(f"{ip}: {ip_range}")

# 检查其他地区的IP
print("\n\nChecking other region IPs from best_ip.txt:")
print("=" * 60)
other_region_ips = [
    "190.93.246.50",  # HK
    "141.101.115.156", # GB
    "103.31.4.13"     # SG
]

for ip in other_region_ips:
    ip_range = check_ip_range(ip)
    print(f"{ip}: {ip_range}")