#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

# 测试 best_ip.txt 中的IP
with open('best_ip.txt', 'r') as f:
    ips = [line.strip() for line in f if line.strip()]

print(f"Total IPs in best_ip.txt: {len(ips)}")
print("\nRegion distribution:")

region_counts = {}
for ip in ips:
    region = get_region_for_ip(ip)
    region_counts[region] = region_counts.get(region, 0) + 1

for region, count in sorted(region_counts.items()):
    print(f"{region}: {count}")

# 检查优先地区
priority_regions = ["US", "GB", "IN", "JP", "KR", "SG", "HK"]
print(f"\nPriority regions: {priority_regions}")
print("IPs in priority regions:")
for region in priority_regions:
    count = region_counts.get(region, 0)
    print(f"{region}: {count}")

total_in_priority = sum(region_counts.get(region, 0) for region in priority_regions)
print(f"\nTotal IPs in priority regions: {total_in_priority}")
print(f"Total IPs in other regions: {len(ips) - total_in_priority}")