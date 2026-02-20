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
    # 173.245.48.0 - 173.245.63.255
    elif first_octet == 173 and second_octet == 245:
        return "US"
    # 188.114.96.0 - 188.114.111.255
    elif first_octet == 188 and second_octet == 114:
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

# 模拟新的配置
priority_regions = ["US", "GB", "IN", "JP", "KR", "SG", "HK"]
max_per_region = 50  # 增加到50
max_total = 100

print("Simulating new configuration with MAX_PER_REGION=50")
print("=" * 60)

# 读取CSV文件
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

print(f"Total IPs in result.csv: {len(ip_data)}")

# 统计地区分布
region_counts = {}
for ip, latency, region in ip_data:
    region_counts[region] = region_counts.get(region, 0) + 1

print("\nRegion distribution in entire result.csv:")
for region, count in sorted(region_counts.items()):
    print(f"{region}: {count}")

# 模拟 parse_top_ips_by_region 函数
selected_ips = []
region_counts_sim = {}

# 优先处理指定的地区
for region in priority_regions:
    region_counts_sim[region] = 0

# 首先选择指定地区的IP
for ip, latency, region in ip_data:
    if region in priority_regions and region_counts_sim.get(region, 0) < max_per_region:
        selected_ips.append(ip)
        region_counts_sim[region] = region_counts_sim.get(region, 0) + 1
    
    # 如果达到总数限制，停止
    if len(selected_ips) >= max_total:
        break

print(f"\nAfter first loop (priority regions): {len(selected_ips)} IPs selected")

# 如果还有空位，选择其他地区的IP
if len(selected_ips) < max_total:
    for ip, latency, region in ip_data:
        if ip in selected_ips:  # 跳过已选择的IP
            continue
                
        if region not in priority_regions:  # 只选择非优先地区的IP
            selected_ips.append(ip)
        
        # 如果达到总数限制，停止
        if len(selected_ips) >= max_total:
            break

print(f"After second loop (other regions): {len(selected_ips)} IPs selected")

# 统计最终选择的地区分布
final_region_counts = {}
for ip in selected_ips:
    region = get_region_for_ip(ip)
    final_region_counts[region] = final_region_counts.get(region, 0) + 1

print("\nFinal selection by region:")
for region, count in sorted(final_region_counts.items()):
    print(f"{region}: {count}")

print(f"\nTotal IPs selected: {len(selected_ips)}")

# 显示前20个被选中的IP及其延迟
print("\nFirst 20 selected IPs (by latency):")
for i, ip in enumerate(selected_ips[:20]):
    # 查找延迟
    for ip2, latency, region in ip_data:
        if ip2 == ip:
            print(f"{i+1:3}. {ip:20} - {latency:.2f}ms ({region})")
            break

# 检查是否达到了100个IP的限制
if len(selected_ips) < max_total:
    print(f"\n⚠️  Warning: Only {len(selected_ips)} IPs selected out of {max_total} maximum.")
    print("   This is because there aren't enough IPs in priority regions.")
    
    # 检查还有多少IP可用
    available_in_priority = 0
    for region in priority_regions:
        available = min(region_counts.get(region, 0), max_per_region)
        available_in_priority += available
    
    print(f"   Available IPs in priority regions: {available_in_priority}")
    print(f"   Available IPs in other regions: {region_counts.get('Other', 0)}")
else:
    print(f"\n✅ Successfully selected {len(selected_ips)} IPs (maximum: {max_total})")