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

def parse_top_ips_by_region(csv_path: str, regions: list[str], max_per_region: int = 10, max_total: int = 100) -> list[str]:
    """
    解析CSV文件，按地区选择最快的前N个IP
    
    Args:
        csv_path: CSV文件路径
        regions: 优先处理的地区列表
        max_per_region: 每个地区最多选择的IP数量
        max_total: 总共最多选择的IP数量
    
    Returns:
        按地区分组选择的IP列表
    """
    
    # 读取CSV文件
    ip_data = []  # 存储(ip, latency, region)元组
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            return []
        
        # 查找延迟列的索引
        latency_idx = 4 if len(header) > 4 else -1  # 平均延迟在第5列
        
        for row in reader:
            if not row or len(row) <= latency_idx:
                continue
            
            ip = row[0].strip()
            if not ip:
                continue
            
            # 解析延迟
            try:
                latency = float(row[latency_idx]) if latency_idx != -1 else 0.0
            except (ValueError, IndexError):
                latency = 9999.0  # 如果解析失败，设置一个很大的延迟值
            
            # 获取地区
            region = get_region_for_ip(ip)
            
            ip_data.append((ip, latency, region))
    
    # 按延迟排序
    ip_data.sort(key=lambda x: x[1])
    
    # 按地区分组选择IP
    selected_ips = []
    region_counts = {}
    
    # 优先处理指定的地区
    for region in regions:
        region_counts[region] = 0
    
    # 首先选择指定地区的IP
    for ip, latency, region in ip_data:
        if region in regions and region_counts.get(region, 0) < max_per_region:
            selected_ips.append(ip)
            region_counts[region] = region_counts.get(region, 0) + 1
        
        # 如果达到总数限制，停止
        if len(selected_ips) >= max_total:
            break
    
    # 如果还有空位，选择其他地区的IP
    if len(selected_ips) < max_total:
        for ip, latency, region in ip_data:
            if ip in selected_ips:  # 跳过已选择的IP
                continue
                
            if region not in regions:  # 只选择非优先地区的IP
                selected_ips.append(ip)
            
            # 如果达到总数限制，停止
            if len(selected_ips) >= max_total:
                break
    
    # 如果仍然有空位（因为优先地区IP数量不足），从所有IP中选择最快的前N个
    if len(selected_ips) < max_total:
        # 重新遍历所有IP，选择最快的前N个（不考虑地区）
        for ip, latency, region in ip_data:
            if ip in selected_ips:  # 跳过已选择的IP
                continue
                
            selected_ips.append(ip)
            
            # 如果达到总数限制，停止
            if len(selected_ips) >= max_total:
                break
    
    return selected_ips

# 测试新的选择逻辑
print("Testing final selection logic with MAX_PER_REGION=50")
print("=" * 60)

priority_regions = ["US", "GB", "IN", "JP", "KR", "SG", "HK"]
max_per_region = 50
max_total = 100

selected_ips = parse_top_ips_by_region("result.csv", priority_regions, max_per_region, max_total)

print(f"Total IPs selected: {len(selected_ips)}")

# 统计地区分布
region_counts = {}
for ip in selected_ips:
    region = get_region_for_ip(ip)
    region_counts[region] = region_counts.get(region, 0) + 1

print("\nFinal selection by region:")
for region, count in sorted(region_counts.items()):
    print(f"{region}: {count}")

# 显示前30个被选中的IP及其延迟
print("\nFirst 30 selected IPs (by latency):")

# 重新读取数据以获取延迟
with open('result.csv', 'r', encoding='utf-8', newline='') as f:
    reader = csv.reader(f)
    header = next(reader, None)
    
    latency_map = {}
    for row in reader:
        if not row:
            continue
        
        ip = row[0].strip()
        if not ip:
            continue
        
        try:
            latency = float(row[4]) if len(row) > 4 else 0.0
        except (ValueError, IndexError):
            latency = 9999.0
        
        latency_map[ip] = latency

for i, ip in enumerate(selected_ips[:30]):
    latency = latency_map.get(ip, 0.0)
    region = get_region_for_ip(ip)
    print(f"{i+1:3}. {ip:20} - {latency:.2f}ms ({region})")

print(f"\n✅ Successfully selected {len(selected_ips)} IPs (maximum: {max_total})")

# 检查是否所有IP都是唯一的
if len(set(selected_ips)) == len(selected_ips):
    print("✅ All IPs are unique.")
else:
    print("⚠️  Warning: Duplicate IPs found!")

# 保存到文件测试
with open('test_best_ip.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(selected_ips) + ("\n" if selected_ips else ""))

print(f"\nTest results saved to 'test_best_ip.txt'")