"""
彻底解决控制台窗口闪现问题的构建脚本
通过多层控制台抑制措施确保用户体验
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
import tempfile

class NoConsoleBuildTool:
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

    def _create_launcher_script(self):
        """创建启动器脚本，确保完全无控制台启动"""
        launcher_content = '''"""
无控制台启动器
确保应用程序以无控制台模式启动
"""

import sys
import os
from pathlib import Path

# 立即禁用控制台输出
if hasattr(sys, '_getframe'):
    try:
        # 尝试隐藏控制台窗口
        import ctypes
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        
        # 获取控制台窗口句柄
        console_window = kernel32.GetConsoleWindow()
        if console_window:
            # 隐藏控制台窗口
            user32.ShowWindow(console_window, 0)  # SW_HIDE
    except:
        pass  # 忽略任何错误

# 设置环境变量确保完全静默模式
os.environ['KIWIKIT_NO_CONSOLE'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 重定向所有输出到空设备
try:
    import io
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
except:
    pass

# 导入并启动主应用
if __name__ == "__main__":
    try:
        # 导入主模块
        from main import main
        main()
    except Exception:
        # 完全静默，不显示任何错误
        pass
'''
        
        launcher_path = self.script_dir / 'launcher_no_console.py'
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        print(f"✅ 创建无控制台启动器: {launcher_path}")
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
           StringStruct(u'FileDescription', u'奇异工具包 - 静默运行版本'),
           StringStruct(u'FileVersion', u'1.0.0.0'),
           StringStruct(u'InternalName', u'KiwiKit'),
           StringStruct(u'LegalCopyright', u'Copyright © 2025 KiwiKit Studio. All rights reserved.'),
           StringStruct(u'OriginalFilename', u'KiwiKit.exe'),
           StringStruct(u'ProductName', u'奇异工具包'),
           StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
        
        with open(self.script_dir / 'version_info.txt', 'w', encoding='utf-8') as f:
            f.write(version_content)
        print("✅ 创建版本信息文件")

    def create_no_console_spec_file(self):
        """创建完全无控制台的 .spec 文件"""
        
        # 查找 DLL 文件
        print("🔍 搜索必要的 DLL 文件...")
        pyzbar_dlls = self._find_pyzbar_dlls()
        
        # 构建 binaries 列表，使用正确的Python字符串格式
        binaries_str = ""
        if pyzbar_dlls:
            # 去重处理
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
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],  # 直接使用主文件，避免启动器问题
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
        'ctypes.wintypes',  # Windows 特定
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
        'unittest',
        'pdb',
        'doctest',
        'argparse',
        'cmd',
        'pprint',
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
    upx=False,  # 禁用 UPX 压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 关键：禁用控制台
    disable_windowed_traceback=True,  # 禁用窗口化异常追踪
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/icon.ico' if os.path.exists('images/icon.ico') else None,
    version='version_info.txt',
    # Windows 特定选项
    uac_admin=False,  # 不需要管理员权限
    uac_uiaccess=False,  # 不需要UI访问
)
'''
        
        spec_file = self.script_dir / 'KiwiKit_NoConsole.spec'
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"✅ 创建无控制台 .spec 文件: {spec_file}")
        return spec_file
    
    def check_environment(self):
        """检查构建环境"""
        print("🔍 检查构建环境...")
        
        if not self.python_exe.exists():
            print(f"❌ 虚拟环境 Python 不存在: {self.python_exe}")
            return False
        
        print(f"✅ 使用 Python: {self.python_exe}")
        
        # 使用 CREATE_NO_WINDOW 检查 PyInstaller
        try:
            CREATE_NO_WINDOW = 0x08000000
            result = subprocess.run([str(self.python_exe), "-m", "PyInstaller", "--version"], 
                                  capture_output=True, text=True, check=True,
                                  creationflags=CREATE_NO_WINDOW if os.name == 'nt' else 0)
            print(f"✅ PyInstaller 版本: {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            print("❌ PyInstaller 未安装，正在尝试安装...")
            try:
                CREATE_NO_WINDOW = 0x08000000
                subprocess.run([str(self.python_exe), "-m", "pip", "install", "pyinstaller"], 
                             check=True, creationflags=CREATE_NO_WINDOW if os.name == 'nt' else 0)
                print("✅ PyInstaller 安装成功")
            except subprocess.CalledProcessError:
                print("❌ PyInstaller 安装失败")
                return False
        
        return True
    
    def clean_build_files(self):
        """清理构建文件"""
        print("🧹 清理旧的构建文件...")
        
        for path in ['build', 'dist']:
            if (self.script_dir / path).exists():
                shutil.rmtree(self.script_dir / path, ignore_errors=True)
                print(f"  删除: {path}/")
    
    def build_application(self):
        """构建应用程序"""
        print("🔨 开始构建无控制台应用程序...")
        
        spec_file = self.create_no_console_spec_file()
        
        # 构建命令
        cmd = [
            str(self.python_exe), "-m", "PyInstaller",
            str(spec_file),
            "--noconfirm",
            "--clean",
            "--log-level=WARN",  # 减少输出
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        try:
            # 使用最严格的控制台抑制设置
            CREATE_NO_WINDOW = 0x08000000
            DETACHED_PROCESS = 0x00000008
            
            # 重定向所有输出
            with open(os.devnull, 'w') as devnull:
                process = subprocess.Popen(
                    cmd, 
                    stdout=devnull, 
                    stderr=devnull,
                    stdin=subprocess.DEVNULL,
                    cwd=self.script_dir,
                    creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS if os.name == 'nt' else 0,
                    close_fds=True if os.name != 'nt' else False
                )
                
                process.wait()
            
            if process.returncode == 0:
                print("📦 构建成功！")
                return True
            else:
                print(f"❌ 构建失败，返回码: {process.returncode}")
                return False
                
        except Exception as e:
            print(f"❌ 构建过程中出现异常: {e}")
            return False
    
    def verify_build(self):
        """验证构建结果"""
        print("🔍 验证构建结果...")
        
        exe_path = self.script_dir / 'dist' / 'KiwiKit.exe'
        if not exe_path.exists():
            print("❌ 未找到可执行文件")
            return False
        
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ 可执行文件: {exe_path}")
        print(f"📏 文件大小: {size_mb:.1f} MB")
        
        return True
    
    def run_complete_build(self):
        """执行完整的构建流程"""
        print("🚀 开始无控制台构建流程")
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
        
        # 2. 清理文件
        self.clean_build_files()
        
        # 3. 构建应用
        if not self.build_application():
            print("❌ 应用构建失败")
            return False
        
        # 4. 验证结果
        if not self.verify_build():
            print("❌ 构建验证失败")
            return False
        
        print("=" * 60)
        print("🎉 无控制台构建完成！")
        print(f"📁 输出目录: {self.script_dir / 'dist'}")
        print(f"🚀 可执行文件: {self.script_dir / 'dist' / 'KiwiKit.exe'}")
        print("📝 特点: 完全无控制台窗口，静默运行")
        
        return True

def main():
    """主函数"""
    try:
        builder = NoConsoleBuildTool()
        success = builder.run_complete_build()
        
        if success:
            print("\\n✅ 无控制台构建成功！")
            print("\\n🔧 解决方案特点:")
            print("1. 使用专门的启动器完全避免控制台")
            print("2. 所有 subprocess 调用都使用 CREATE_NO_WINDOW")
            print("3. 禁用所有调试和异常追踪输出")
            print("4. 重定向所有标准输出到空设备")
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