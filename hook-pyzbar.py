from PyInstaller.utils.hooks import collect_dynamic_libs

def hook(hook_api):
    # 获取 pyzbar 相关的动态库
    binaries = collect_dynamic_libs('pyzbar')
    
    # 添加所需的 DLL 文件
    binaries.extend([
        ('libiconv.dll', '.'),
        ('libzbar-64.dll', '.'),
        ('zbar.dll', '.'),
    ])
    
    hook_api.add_binaries(binaries)