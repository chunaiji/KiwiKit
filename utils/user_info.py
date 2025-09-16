import platform
import hashlib
import uuid
import os

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

def get_cpu_info():
    """获取CPU信息"""
    cpu_info = platform.processor()  # 获取CPU的名称
    if not cpu_info and HAS_PSUTIL:  # 如果platform.processor()为空，尝试通过psutil获取
        try:
            cpu_freq = psutil.cpu_freq()
            cpu_info = str(cpu_freq.current) if cpu_freq else "unknown_cpu"
        except:
            cpu_info = "unknown_cpu"
    elif not cpu_info:
        cpu_info = "unknown_cpu"
    return cpu_info

def get_memory_info():
    """获取内存信息"""
    if HAS_PSUTIL:
        try:
            memory_info = psutil.virtual_memory()
            total_memory = memory_info.total  # 总内存（字节）
            available_memory = memory_info.available  # 可用内存（字节）
            return f"{total_memory}-{available_memory}"
        except:
            pass
    # 使用系统平台信息作为备选
    return f"{platform.machine()}-{platform.architecture()[0]}"

def get_disk_info():
    """获取硬盘信息"""
    try:
        if platform.system() == "Windows":
            try:
                import win32api
                drives = win32api.GetLogicalDrives()
                disk_info = [win32api.GetVolumeInformation(drive) for drive in drives]
                disk_serial_numbers = [disk[1] for disk in disk_info]
                return "-".join(map(str, disk_serial_numbers))
            except ImportError:
                # 如果没有win32api，使用其他方法
                import subprocess
                try:
                    result = subprocess.run(['wmic', 'diskdrive', 'get', 'serialnumber'], 
                                          capture_output=True, text=True, timeout=5)
                    lines = result.stdout.strip().split('\n')
                    serials = [line.strip() for line in lines[1:] if line.strip()]
                    return "-".join(serials) if serials else "unknown_disk"
                except:
                    return "unknown_disk"
        else:
            # For Linux/macOS
            if HAS_PSUTIL:
                try:
                    disk_info = psutil.disk_partitions()
                    serial_numbers = []
                    for partition in disk_info:
                        try:
                            device = partition.device
                            serial = os.popen(f"lsblk -no SERIAL {device}").read().strip()
                            if serial:
                                serial_numbers.append(serial)
                        except Exception as e:
                            pass
                    return "-".join(serial_numbers) if serial_numbers else "unknown_disk"
                except:
                    pass
            return "unknown_disk"
    except Exception as e:
        return "unknown_disk"

def get_unique_identifier():
    """生成唯一标识符"""
    try:
        # 获取硬件信息
        cpu_info = get_cpu_info()
        memory_info = get_memory_info()
        disk_info = get_disk_info()
        
        # 获取操作系统信息作为补充（避免不同系统生成相同编码）
        system_info = platform.system() + platform.version() + platform.machine()
        
        # 获取MAC地址作为补充
        try:
            mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                                  for elements in range(0,2*6,2)][::-1])
        except:
            mac_address = "unknown_mac"
        
        # 组合所有信息生成原始数据
        raw_data = f"{cpu_info}-{memory_info}-{disk_info}-{system_info}-{mac_address}"
        
        # 使用SHA-256哈希生成唯一编码
        unique_hash = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
        
        # 返回前16位作为简化的唯一码
        return unique_hash[:16].upper()
        
    except Exception as e:
        # 如果所有方法都失败，生成一个基于时间和随机数的备用码
        import time
        import random
        fallback_data = f"{time.time()}-{random.randint(1000,9999)}-{platform.system()}"
        fallback_hash = hashlib.sha256(fallback_data.encode('utf-8')).hexdigest()
        return fallback_hash[:16].upper()

