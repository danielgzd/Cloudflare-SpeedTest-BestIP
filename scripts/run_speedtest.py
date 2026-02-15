#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
import json
import shutil
import tarfile
import zipfile
import urllib.request
import subprocess
from pathlib import Path

RELEASE_URL_LINUX_AMD64_TGZ = (
    "https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.3.4/"
    "cfst_linux_amd64.tar.gz"
)

# ip.txt 的官方原始地址（master 分支）
IP_TXT_URL = "https://raw.githubusercontent.com/XIU2/CloudflareSpeedTest/master/ip.txt"  # :contentReference[oaicite:1]{index=1}

def download(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "MyAutoScript/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dst, "wb") as f:
        shutil.copyfileobj(r, f)

def extract_archive(archive: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    name = archive.name.lower()

    if name.endswith(".tar.gz") or name.endswith(".tgz"):
        with tarfile.open(archive, "r:gz") as t:
            t.extractall(out_dir)
        return

    if name.endswith(".zip"):
        with zipfile.ZipFile(archive, "r") as z:
            z.extractall(out_dir)
        return

    raise RuntimeError(f"Unsupported archive format: {archive}")

def find_cfst(bin_dir: Path) -> Path:
    for c in (bin_dir / "cfst", bin_dir / "CloudflareST", bin_dir / "cloudflareST"):
        if c.exists():
            return c
    for p in bin_dir.rglob("*"):
        if p.is_file() and p.name in ("cfst", "CloudflareST"):
            return p
    raise RuntimeError("cfst binary not found after extraction")

def run_cmd(cmd: list[str], cwd: Path | None = None) -> None:
    print(">>", " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)

def parse_top_ips_by_region(csv_path: Path, regions: list[str], max_per_region: int = 10, max_total: int = 100) -> list[str]:
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
    # 基于Cloudflare IP段的地区检测
    # 参考：https://www.cloudflare.com/ips/
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
    
    return selected_ips

def main() -> int:
    repo_root = Path(os.getenv("GITHUB_WORKSPACE", Path.cwd())).resolve()

    # 配置参数
    max_per_region = int(os.getenv("MAX_PER_REGION", "10"))
    max_total = int(os.getenv("MAX_TOTAL", "100"))
    
    # 优先处理的地区列表（美国、英国、印度、日本、韩国、新加坡、香港）
    # 使用ISO 3166-1 alpha-2国家代码
    priority_regions = os.getenv("PRIORITY_REGIONS", "US,GB,IN,JP,KR,SG,HK")
    regions = [region.strip() for region in priority_regions.split(",") if region.strip()]
    
    cfst_args = os.getenv("CFST_ARGS", "-n 200 -t 4 -dn 100 -dt 8 -p 0 -o result.csv").strip()

    # ✅ 确保 ip.txt 存在（cfst 默认读取 ip.txt）
    ip_txt = repo_root / "ip.txt"
    if not ip_txt.exists():
        print(f"ip.txt not found, downloading from: {IP_TXT_URL}")
        download(IP_TXT_URL, ip_txt)

    work_dir = repo_root / ".tmp_cfst"
    work_dir.mkdir(parents=True, exist_ok=True)

    archive = work_dir / "cfst_linux_amd64.tar.gz"
    bin_dir = work_dir / "bin"

    if not archive.exists():
        print(f"Downloading cfst from {RELEASE_URL_LINUX_AMD64_TGZ}")
        download(RELEASE_URL_LINUX_AMD64_TGZ, archive)

    if bin_dir.exists():
        shutil.rmtree(bin_dir)
    extract_archive(archive, bin_dir)

    cfst_bin = find_cfst(bin_dir)
    cfst_bin.chmod(0o755)

    # 在 repo_root 下跑，确保 result.csv 输出到仓库根目录
    cmd = [str(cfst_bin)] + cfst_args.split()
    run_cmd(cmd, cwd=repo_root)

    csv_path = repo_root / "result.csv"
    if not csv_path.exists():
        print("ERROR: result.csv not found. Check CFST_ARGS.")
        return 2

    # 使用新的按地区选择IP的函数
    ips = parse_top_ips_by_region(csv_path, regions, max_per_region, max_total)
    best_path = repo_root / "best_ip.txt"
    best_path.write_text("\n".join(ips) + ("\n" if ips else ""), encoding="utf-8")

    print("Done:", json.dumps({
        "priority_regions": regions,
        "max_per_region": max_per_region,
        "max_total": max_total,
        "cfst_args": cfst_args,
        "count": len(ips),
        "best_ip_txt": str(best_path),
        "result_csv": str(csv_path),
        "ip_txt": str(ip_txt),
    }, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
