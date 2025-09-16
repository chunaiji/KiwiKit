"""
调试版本的无控制台构建脚本
保留错误输出用于调试界面问题
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

class DebugNoConsoleBuildTool:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.venv_path = self.script_dir / "venv"
        self.python_exe = self._get_python_executable()
        
    def _get_python_executable(self):
        """获取虚拟环境的 Python 可执行文件路径"""
        if platform.system() == "Windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
    
    def _find_pyzbar_dlls(self):
        """查找 pyzbar 相关的 DLL 文件"""
        dll_paths = []
        site_packages = self.venv_path / "Lib" / "site-packages"
        
        # 查找 pyzbar 目录
        pyzbar_dirs = [site_packages / "pyzbar"]
        
        for item in site_packages.glob("pyzbar*"):
            if item.is_dir():
                pyzbar_dirs.append(item)
        
        for pyzbar_dir in pyzbar_dirs:
            if pyzbar_dir.exists():
                for dll_file in pyzbar_dir.rglob("*.dll"):
                    dll_paths.append((str(dll_file), "pyzbar"))
                    print(f"找到 pyzbar DLL: {dll_file}")
        
        return dll_paths

    def _create_debug_launcher(self):
        """创建调试启动器，保留错误输出"""
        launcher_content = '''"""
调试启动器 - 保留错误输出
"""

import sys
import os
from pathlib import Path

# 设置环境变量但不完全静默
os.environ['KIWIKIT_NO_CONSOLE'] = 'false'  # 允许错误输出
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 导入并启动主应用
if __name__ == "__main__":
    try:
        # 导入主模块
        from main import main
        main()
    except Exception as e:
        # 显示错误信息用于调试
        import traceback
        print(f"启动失败: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        input("按回车键退出...")
'''
        
        launcher_path = self.script_dir / 'debug_launcher.py'
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        print(f"✅ 创建调试启动器: {launcher_path}")
        return launcher_path

    def _create_version_info(self):
        """创建版本信息文件"""
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
           StringStruct(u'FileDescription', u'奇异工具包 - 调试版本'),
           StringStruct(u'FileVersion', u'1.0.0.0'),
           StringStruct(u'InternalName', u'KiwiKit_Debug'),
           StringStruct(u'LegalCopyright', u'Copyright © 2025 KiwiKit Studio. All rights reserved.'),
           StringStruct(u'OriginalFilename', u'KiwiKit_Debug.exe'),
           StringStruct(u'ProductName', u'奇异工具包调试版'),
           StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
        
        with open(self.script_dir / 'version_info_debug.txt', 'w', encoding='utf-8') as f:
            f.write(version_content)
        print("✅ 创建调试版本信息文件")

    def create_debug_spec_file(self):
        """创建调试版本的 .spec 文件"""
        
        # 查找 DLL 文件
        print("🔍 搜索必要的 DLL 文件...")
        pyzbar_dlls = self._find_pyzbar_dlls()
        
        # 构建 binaries 列表，去重处理
        binaries_str = ""
        if pyzbar_dlls:
            unique_dlls = []
            seen_paths = set()
            for dll_path, dll_dir in pyzbar_dlls:
                if dll_path not in seen_paths:
                    seen_paths.add(dll_path)
                    unique_dlls.append((dll_path, dll_dir))
            
            # 使用正确的路径格式
            binaries_list = []
            for dll_path, dll_dir in unique_dlls:
                # 将反斜杠替换为正斜杠以避免转义问题
                clean_path = dll_path.replace('\\', '/')
                binaries_list.append(f'        ("{clean_path}", "{dll_dir}")')
            binaries_str = ",\n".join(binaries_list) + ","
        
        # 创建版本信息文件
        self._create_version_info()
        
        # 创建调试启动器
        launcher_path = self._create_debug_launcher()
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['debug_launcher.py'],  # 使用调试启动器
    pathex=[],
    binaries=[
{binaries_str}
    ],
    datas=[
        ('components', 'components'),
        ('styles', 'styles'), 
        ('utils', 'utils'),
        ('config', 'config'),
        ('images', 'images'),
        ('docs', 'docs'),
        ('main.py', '.'),  # 确保主模块被包含
    ],
    hiddenimports=[
        # 核心模块
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'PySide6.QtNetwork',
        'shiboken6',
        
        # 图像处理
        'PIL',
        'PIL.Image',
        'PIL._imaging',
        
        # QR码
        'qrcode',
        'qrcode.image.pil',
        
        # 应用模块
        'main',
        'components',
        'components.content_area',
        'components.header',
        'components.nav_primary',
        'components.nav_secondary',
        'components.settings_dialog',
        'components.tools',
        'components.tools.encode_decode',
        'components.tools.json_formatter',
        'components.tools.base_converter',
        'components.tools.color_picker',
        
        # 样式模块
        'styles',
        'styles.constants',
        'styles.widgets',
        'styles.factory',
        'styles.generator',
        
        # 工具模块
        'utils',
        'utils.http_client',
        'utils.image_loader',
        'utils.logger',
        
        # 配置模块
        'config',
        'config.app_config',
        'config.nav_config',
        
        # 网络相关
        'requests',
        'urllib3',
        'certifi',
        
        # 标准库
        'json',
        'base64',
        'hashlib',
        'logging',
        'pathlib',
        'ctypes',
        'io',
        'threading',
        'queue',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
        'pytest',
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
    name='KiwiKit_Debug',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 禁用 UPX 压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 调试版本允许控制台输出
    disable_windowed_traceback=False,  # 允许异常追踪
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/icon.ico' if os.path.exists('images/icon.ico') else None,
    version='version_info_debug.txt',
)
'''
        
        spec_file = self.script_dir / 'KiwiKit_Debug.spec'
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"✅ 创建调试 .spec 文件: {spec_file}")
        return spec_file
    
    def check_environment(self):
        """检查构建环境"""
        print("🔍 检查构建环境...")
        
        if not self.python_exe.exists():
            print(f"❌ 虚拟环境 Python 不存在: {self.python_exe}")
            return False
        
        print(f"✅ 使用 Python: {self.python_exe}")
        return True
    
    def clean_debug_files(self):
        """清理调试构建文件"""
        print("🧹 清理调试构建文件...")
        
        # 只删除调试相关的文件
        debug_files = ['KiwiKit_Debug.exe']
        for filename in debug_files:
            filepath = self.script_dir / 'dist' / filename
            if filepath.exists():
                filepath.unlink()
                print(f"  删除: {filename}")
    
    def build_debug_application(self):
        """构建调试版应用程序"""
        print("🔨 开始构建调试版应用程序...")
        
        spec_file = self.create_debug_spec_file()
        
        # 构建命令
        cmd = [
            str(self.python_exe), "-m", "PyInstaller",
            str(spec_file),
            "--noconfirm",
            "--clean",
            "--log-level=INFO",  # 显示详细日志用于调试
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        try:
            # 正常执行，显示输出用于调试
            result = subprocess.run(cmd, cwd=self.script_dir)
            
            if result.returncode == 0:
                print("📦 调试版构建成功！")
                return True
            else:
                print(f"❌ 构建失败，返回码: {result.returncode}")
                return False
                
        except Exception as e:
            print(f"❌ 构建过程中出现异常: {e}")
            return False
    
    def run_debug_build(self):
        """执行调试构建流程"""
        print("🚀 开始调试版构建流程")
        print("=" * 60)
        
        # 切换到脚本目录
        os.chdir(self.script_dir)
        
        # 检查主文件
        if not (self.script_dir / 'main.py').exists():
            print("❌ 未找到 main.py 文件")
            return False
        
        # 1. 检查环境
        if not self.check_environment():
            print("❌ 环境检查失败")
            return False
        
        # 2. 清理调试文件
        self.clean_debug_files()
        
        # 3. 构建应用
        if not self.build_debug_application():
            print("❌ 应用构建失败")
            return False
        
        # 4. 检查结果
        exe_path = self.script_dir / 'dist' / 'KiwiKit_Debug.exe'
        if not exe_path.exists():
            print("❌ 未找到调试可执行文件")
            return False
        
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ 调试可执行文件: {exe_path}")
        print(f"📏 文件大小: {size_mb:.1f} MB")
        
        print("=" * 60)
        print("🎉 调试版构建完成！")
        print(f"📁 输出目录: {self.script_dir / 'dist'}")
        print(f"🚀 可执行文件: {exe_path}")
        print("📝 特点: 保留控制台输出，便于调试")
        
        return True

def main():
    """主函数"""
    try:
        builder = DebugNoConsoleBuildTool()
        success = builder.run_debug_build()
        
        if success:
            print("\\n✅ 调试版构建成功！")
            print("\\n🔧 使用说明:")
            print("1. 运行 KiwiKit_Debug.exe 查看启动错误")
            print("2. 检查控制台输出中的错误信息")
            print("3. 根据错误信息修复问题")
            return 0
        else:
            print("\\n❌ 构建失败！")
            return 1
            
    except KeyboardInterrupt:
        print("\\n\\n⏹️  用户取消构建")
        return 1
    except Exception as e:
        print(f"\\n❌ 构建过程中发生异常: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    input(f"\\n按回车键退出... (退出码: {exit_code})")
    sys.exit(exit_code)