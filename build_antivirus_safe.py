"""
解决杀毒软件误报和Console窗口问题的优化构建脚本
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def create_antivirus_friendly_spec():
    """创建对杀毒软件友好的spec文件"""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
# 反病毒优化配置

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 收集数据文件
datas = [
    ('components', 'components'),
    ('styles', 'styles'),
    ('utils', 'utils'),
    ('config', 'config'),
    ('images', 'images'),
    ('docs', 'docs'),
]

# 收集隐藏导入
hiddenimports = [
    # PySide6 核心
    'PySide6.QtCore',
    'PySide6.QtGui', 
    'PySide6.QtWidgets',
    'PySide6.QtNetwork',
    'shiboken6',
    
    # PIL 核心
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'PIL._imaging',
    
    # 应用模块
    'components.header',
    'components.nav_primary',
    'components.nav_secondary',
    'components.content_area',
    'components.settings_dialog',
    
    # 工具模块
    'components.tools.json_formatter',
    'components.tools.encode_decode',
    'components.tools.file_search',
    'components.tools.image_conver',
    'components.tools.regex_formatter',
    'components.tools.file_diff',
    'components.tools.code_formatter',
    'components.tools.base_converter',
    'components.tools.color_picker',
    'components.tools.media_download',
    'components.tools.qr_tool',
    
    # 样式和配置
    'styles.constants',
    'styles.widgets',
    'styles.factory',
    'utils.logger',
    'utils.api_client',
    'config.app_config',
    
    # 标准库
    'json', 'ssl', 'hashlib', 'base64', 'logging',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块减少体积和误报
        'tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy',
        'IPython', 'jupyter', 'notebook', '_pytest', 'pytest',
        'pycryptodome', 'crypto', 'cryptography',  # 避免加密库误报
        'pywin32', 'win32api', 'win32con',  # 避免系统API误报
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KiwiKit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 禁用UPX压缩，减少误报
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 关键：禁用控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/icon.ico' if os.path.exists('images/icon.ico') else None,
    version='version_info.txt',  # 添加版本信息
    uac_admin=False,  # 不请求管理员权限，减少误报
    uac_uiaccess=False,  # 禁用UI访问权限
)
'''
    
    with open('KiwiKit_AntiVirus.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✅ 创建反病毒友好的spec文件")

def create_version_info():
    """创建详细的版本信息"""
    version_content = '''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'KiwiKit Studio'),
           StringStruct(u'FileDescription', u'KiwiKit - Multi-Purpose Utility Toolkit'),
           StringStruct(u'FileVersion', u'1.0.0.0'),
           StringStruct(u'InternalName', u'KiwiKit'),
           StringStruct(u'LegalCopyright', u'Copyright © 2025 KiwiKit Studio. All rights reserved.'),
           StringStruct(u'OriginalFilename', u'KiwiKit.exe'),
           StringStruct(u'ProductName', u'KiwiKit Toolkit'),
           StringStruct(u'ProductVersion', u'1.0.0.0'),
           StringStruct(u'Comments', u'A legitimate utility application for developers and power users'),
           StringStruct(u'LegalTrademarks', u'KiwiKit is a trademark of KiwiKit Studio')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_content)
    print("✅ 创建详细版本信息")

def build_antivirus_friendly():
    """构建对杀毒软件友好的版本"""
    print("🛡️ 开始构建反病毒优化版本")
    print("=" * 60)
    
    # 检查虚拟环境
    venv_python = Path("venv/Scripts/python.exe")
    if not venv_python.exists():
        print("❌ 未找到虚拟环境")
        return False
    
    # 清理旧文件
    for path in ['build', 'dist']:
        if Path(path).exists():
            shutil.rmtree(path, ignore_errors=True)
            print(f"🧹 清理: {path}")
    
    # 创建文件
    create_antivirus_friendly_spec()
    create_version_info()
    
    # 构建命令
    cmd = [
        str(venv_python), "-m", "PyInstaller",
        "KiwiKit_AntiVirus.spec",
        "--noconfirm",
        "--clean",
        "--log-level=WARN",  # 减少输出
    ]
    
    print("🔨 开始构建...")
    print(f"执行: {' '.join(cmd)}")
    
    try:
        # 使用 CREATE_NO_WINDOW 避免创建控制台
        CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0
        
        result = subprocess.run(cmd, 
                               capture_output=True, 
                               text=True,
                               creationflags=CREATE_NO_WINDOW,
                               cwd=Path.cwd())
        
        if result.returncode == 0:
            exe_path = Path("dist/KiwiKit.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"✅ 构建成功!")
                print(f"📦 文件: {exe_path}")
                print(f"📏 大小: {size_mb:.1f} MB")
                
                # 创建说明文件
                create_readme()
                return True
        
        print("❌ 构建失败")
        print("错误输出:", result.stderr)
        return False
        
    except Exception as e:
        print(f"❌ 构建异常: {e}")
        return False

def create_readme():
    """创建说明文件"""
    readme_content = '''# KiwiKit 工具包

## 关于杀毒软件误报

KiwiKit是一个合法的开源工具包，但可能被某些杀毒软件误报为病毒。这是因为：

1. **PyInstaller打包**: 使用PyInstaller打包的程序经常被误报
2. **文件压缩**: 可执行文件内包含压缩的Python代码
3. **动态加载**: 程序运行时动态加载模块

## 如何处理误报

### Avast用户
1. 打开Avast安全软件
2. 转到"防护" > "病毒胸部"
3. 找到KiwiKit.exe并选择"恢复并添加例外"
4. 或者在"设置" > "例外"中添加文件路径

### Windows Defender用户
1. 打开Windows安全中心
2. 转到"病毒和威胁防护"
3. 点击"管理设置"
4. 添加或删除排除项 > 添加排除项 > 文件
5. 选择KiwiKit.exe

### 通用解决方案
1. 将KiwiKit.exe添加到杀毒软件的白名单
2. 临时禁用实时保护进行安装
3. 从官方渠道下载确保文件完整性

## 安全声明

- ✅ 本软件是开源项目
- ✅ 不包含恶意代码
- ✅ 不会收集个人信息
- ✅ 不会连接可疑服务器
- ✅ 源代码可供审查

如果您仍有疑虑，建议从源代码自行编译。

## 联系方式

如有问题，请联系: support@kiwikit.studio
'''
    
    with open('dist/README_防病毒误报说明.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✅ 创建防误报说明文件")

if __name__ == "__main__":
    success = build_antivirus_friendly()
    
    if success:
        print("\n🎉 构建完成!")
        print("\n📋 反病毒优化措施:")
        print("1. ✅ 禁用了控制台窗口 (console=False)")
        print("2. ✅ 添加了详细版本信息")
        print("3. ✅ 排除了可疑模块")
        print("4. ✅ 禁用了UPX压缩")
        print("5. ✅ 不请求管理员权限")
        print("6. ✅ 创建了防误报说明文件")
        
        print("\n🛡️ 如果仍被误报:")
        print("- 将程序添加到杀毒软件白名单")
        print("- 检查dist/README_防病毒误报说明.txt")
        
    input("\n按回车键退出...")