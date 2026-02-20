#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv

def get_region_for_ip(ip: str) -> str:
    ip_parts = ip.split('.')
    if len(ip_parts) < 2:
        return "Other"
    
    first_octet = int(ip_parts[0])
    second_octet = int(ip_parts[1])
    
    # 美国IP段 (主要Cloudflare数据中心)
    # 104.16.0.0 - 104.31.255.255
    if first_octet == 104 and 16 <= second_octet <= 31:
        return "US"
    # 172.64.0.0 - 172.71.255.255
    elif first_octet == 172 and 64 <= second_octet <= 71:
        return "US"
    # 162.158.0.0 - 162.159.255.255
    elif first_octet == 162 and second_octet in [158, 159]:
        return "US"
    # 198.41.128.0 - 198.41.255.255
    elif first_octet == 198 and second_octet == 41:
        return "US"
    # 108.162.192.0 - 108.162.255.255
    elif first_octet == 108 and second_octet == 162:
        return "US"
    # 172.65.0.0 - 172.67.255.255
    elif first_octet == 172 and 65 <= second_octet <= 67:
        return "US"
    
    # 英国IP段
    # 141.101.64.0 - 141.101.127.255
    elif first_octet == 141 and second_octet == 101:
        return "GB"
    
    # 日本IP段
    # 103.21.244.0 - 103.21.247.255
    elif first_octet == 103 and second_octet == 21:
        return "JP"
    
    # 韩国IP段
    # 103.22.200.0 - 103.22.203.255
    elif first_octet == 103 and second_octet == 22:
        return "KR"
    
    # 新加坡IP段
    # 103.31.4.0 - 103.31.7.255
    elif first_octet == 103 and second_octet == 31:
        return "SG"
    
    # 香港IP段
    # 190.93.240.0 - 190.93.243.255
    elif first_octet == 190 and second_octet == 93:
        return "HK"
    
    # 印度IP段
    # 197.234.240.0 - 197.234.243.255
    elif first_octet == 197 and second_octet == 234:
        return "IN"
    
    # 其他地区
    else:
        return "Other"

# 读取CSV文件
priority_regions = ["US", "GB", "IN", "JP", "KR", "SG", "HK"]

with open('result.csv', 'r', encoding='utf-8', newline='') as f:
    reader = csv.reader(f)
    header = next(reader, None)
    
    ip_data = []
    for row in reader:
        if not row:
            continue
        
        ip = row[0].strip()
        if not ip:
            continue
        
        # 解析延迟
        try:
            latency = float(row[4]) if len(row) > 4 else 0.0
        except (ValueError, IndexError):
            latency = 9999.0
        
        # 获取地区
        region = get_region_for_ip(ip)
        
        ip_data.append((ip, latency, region))

# 按延迟排序
ip_data.sort(key=lambda x: x[1])

print("Finding positions of different regions in sorted IP list:")
print("(Position 0 is the first IP, with lowest latency)\n")

# 查找每个地区最早出现的位置
region_first_pos = {}
for i, (ip, latency, region) in enumerate(ip_data):
    if region not in region_first_pos:
        region_first_pos[region] = i

print("First occurrence of each region:")
for region in sorted(region_first_pos.keys()):
    pos = region_first_pos[region]
    ip, latency, _ = ip_data[pos]
    print(f"{region}: position {pos}, IP: {ip}, latency: {latency:.2f}ms")

print("\n\nChecking specific regions from best_ip.txt:")

# 读取 best_ip.txt 中的IP
with open('best_ip.txt', 'r') as f:
    best_ips = [line.strip() for line in f if line.strip()]

print(f"\nTotal IPs in best_ip.txt: {len(best_ips)}")

# 查找这些IP在排序列表中的位置
print("\nPositions of best_ip.txt IPs in sorted list:")
for ip in best_ips:
    # 在 ip_data 中查找这个IP
    for i, (ip2, latency, region) in enumerate(ip_data):
        if ip2 == ip:
            print(f"IP: {ip}, position: {i}, latency: {latency:.2f}ms, region: {region}")
            break

# 统计每个地区在排序列表中的分布
print("\n\nRegion distribution in entire result.csv:")
region_counts = {}
for ip, latency, region in ip_data:
    region_counts[region] = region_counts.get(region, 0) + 1

for region, count in sorted(region_counts.items()):
    print(f"{region}: {count}")

print(f"\nTotal IPs: {len(ip_data)}")