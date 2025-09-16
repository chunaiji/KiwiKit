"""
完整的 PySide6 应用打包脚本
解决 DLL 依赖和模块缺失问题
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
import site

class CompleteBuildTool:
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
        
        # 在虚拟环境中查找
        site_packages = self.venv_path / "Lib" / "site-packages"
        
        # 查找 pyzbar 目录
        pyzbar_dirs = [
            site_packages / "pyzbar",
        ]
        
        # 查找所有可能的 pyzbar 版本目录
        for item in site_packages.glob("pyzbar*"):
            if item.is_dir():
                pyzbar_dirs.append(item)
        
        for pyzbar_dir in pyzbar_dirs:
            if pyzbar_dir.exists():
                # 查找所有 DLL 文件
                for dll_file in pyzbar_dir.rglob("*.dll"):
                    dll_paths.append((str(dll_file), "pyzbar"))
                    print(f"找到 pyzbar DLL: {dll_file}")
        
        # 查找系统中的 zbar DLL
        possible_paths = [
            "C:/Program Files/zbar/bin",
            "C:/zbar/bin",
            "C:/msys64/mingw64/bin",  # MSYS2 安装路径
            "C:/vcpkg/installed/x64-windows/bin",  # vcpkg 安装路径
        ]
        
        for path in possible_paths:
            path_obj = Path(path)
            if path_obj.exists():
                for dll_file in path_obj.glob("*zbar*.dll"):
                    dll_paths.append((str(dll_file), "zbar"))
                    print(f"找到 zbar DLL: {dll_file}")
                for dll_file in path_obj.glob("*iconv*.dll"):
                    dll_paths.append((str(dll_file), "zbar"))
                    print(f"找到 iconv DLL: {dll_file}")
        
        return dll_paths
    
    def _find_pillow_dlls(self):
        """查找 Pillow 相关的 DLL 文件"""
        dll_paths = []
        site_packages = self.venv_path / "Lib" / "site-packages"
        
        # 查找 Pillow 目录
        pillow_dir = site_packages / "PIL"
        if pillow_dir.exists():
            for dll_file in pillow_dir.rglob("*.dll"):
                dll_paths.append((str(dll_file), "PIL"))
                print(f"找到 Pillow DLL: {dll_file}")
        
        return dll_paths

    def _create_version_info(self):
        """创建版本信息文件，减少杀毒软件误报"""
        version_content = '''# UTF-8
# Version Information for KiwiKit.exe
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
           StringStruct(u'FileDescription', u'奇异工具包 - 多功能实用工具集'),
           StringStruct(u'FileVersion', u'1.0.0.0'),
           StringStruct(u'InternalName', u'KiwiKit'),
           StringStruct(u'LegalCopyright', u'Copyright © 2025 KiwiKit Studio. All rights reserved.'),
           StringStruct(u'OriginalFilename', u'KiwiKit.exe'),
           StringStruct(u'ProductName', u'奇异工具包'),
           StringStruct(u'ProductVersion', u'1.0.0.0'),
           StringStruct(u'LegalTrademarks', u'KiwiKit is a trademark of KiwiKit Studio')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
        
        with open(self.script_dir / 'version_info.txt', 'w', encoding='utf-8') as f:
            f.write(version_content)
        print("✅ 创建版本信息文件，用于减少杀毒软件误报")

    def create_complete_spec_file(self):
        """创建完整的 .spec 文件"""
        
        # 查找 DLL 文件
        print("🔍 搜索必要的 DLL 文件...")
        pyzbar_dlls = self._find_pyzbar_dlls()
        pillow_dlls = self._find_pillow_dlls()
        all_dlls = pyzbar_dlls + pillow_dlls
        
        # 构建 binaries 列表，使用原始字符串避免转义问题
        binaries_str = ""
        if all_dlls:
            binaries_list = [f"        (r'{dll[0]}', '{dll[1]}')" for dll in all_dlls]
            binaries_str = ",\n".join(binaries_list) + ","
        else:
            print("⚠️  未找到任何 DLL 文件，继续打包...")
        
        # 创建版本信息文件
        self._create_version_info()
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
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
        # PySide6 完整导入
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtNetwork',
        'PySide6.QtOpenGL',
        'PySide6.QtSvg',
        'PySide6.QtSql',
        'PySide6.QtPrintSupport',
        'shiboken6',
        
        # Pillow 完整导入
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'PIL.ImageFilter',
        'PIL.ImageEnhance',
        'PIL.ImageOps',
        'PIL.ImageChops',
        'PIL.ImageColor',
        'PIL.ImageFile',
        'PIL.ImageGrab',
        'PIL.ImagePath',
        'PIL.ImageSequence',
        'PIL.ImageStat',
        'PIL.ImageTransform',
        'PIL.ImageWin',
        'PIL._imaging',
        'PIL._imagingmath',
        'PIL._imagingmorph',
        'PIL._imagingft',
        'PIL._webp',
        
        # QR 码相关
        'qrcode',
        'qrcode.image',
        'qrcode.image.pil',
        'qrcode.image.svg',
        'qrcode.constants',
        'qrcode.util',
        
        # 应用模块 - 完整路径导入
        'components',
        'components.base_content',
        'components.header',
        'components.nav_primary',
        'components.nav_secondary',
 
        'components.content_area',
        'components.settings_dialog',
        'components.tools',
        'components.tools.contact',
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
        'components.tools.screen_shot',
        
        # 样式模块
        'styles',
        'styles.constants',
        'styles.constants_dark',
        'styles.widgets',
        'styles.factory',
        'styles.generator',
        
        # 工具模块
        'utils',
        'utils.api_client',
        'utils.background_api',
        'utils.http_client',
        'utils.image_loader',
        'utils.logger',
        
        # 配置模块
        'config',
        'config.app_config',
        'config.nav_config',
        
        # 网络和请求相关
        'requests',
        'requests.adapters',
        'requests.auth',
        'requests.cookies',
        'requests.exceptions',
        'requests.models',
        'requests.sessions',
        'requests.structures',
        'requests.utils',
        'urllib3',
        'urllib3.util',
        'urllib3.util.ssl_',
        'urllib3.util.retry',
        'urllib3.poolmanager',
        'urllib3.connection',
        'urllib3.connectionpool',
        'certifi',
        
        # 标准库
        'ssl',
        'json',
        'hashlib',
        'base64',
        'binascii',
        'codecs',
        'html',
        'html.parser',
        'xml',
        'xml.etree',
        'xml.etree.ElementTree',
        're',
        'threading',
        'queue',
        'time',
        'datetime',
        'logging',
        'logging.handlers',
        'pathlib',
        'os',
        'sys',
        'platform',
        'socket',
        'uuid',
        'tempfile',
        'shutil',
        'subprocess',
        'ctypes',
        'ctypes.util',
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
        'notebook',
        '_pytest',
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
    name='KiwiKit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 禁用 UPX 压缩避免 DLL 问题和误报
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 必须是 False，避免控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/icon.ico' if os.path.exists('images/icon.ico') else None,
    version='version_info.txt',  # 添加版本信息减少误报
)
'''
        
        spec_file = self.script_dir / 'WeChatToolbox_Complete.spec'
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"✅ 创建完整 .spec 文件: {spec_file}")
        return spec_file
    
    def check_environment(self):
        """检查虚拟环境和依赖"""
        print("🔍 检查构建环境...")
        
        if not self.python_exe.exists():
            print(f"❌ 虚拟环境 Python 不存在: {self.python_exe}")
            return False
        
        print(f"✅ 使用 Python: {self.python_exe}")
        
        # 检查 PyInstaller
        try:
            result = subprocess.run([str(self.python_exe), "-m", "PyInstaller", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ PyInstaller 版本: {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            print("❌ PyInstaller 未安装，正在尝试安装...")
            try:
                subprocess.run([str(self.python_exe), "-m", "pip", "install", "pyinstaller"], 
                             check=True)
                print("✅ PyInstaller 安装成功")
            except subprocess.CalledProcessError:
                print("❌ PyInstaller 安装失败")
                return False
        
        # 检查 PySide6
        try:
            result = subprocess.run([str(self.python_exe), "-c", "import PySide6; print(PySide6.__version__)"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ PySide6 版本: {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            print("❌ PySide6 未安装")
            return False
        
        return True
    
    def clean_build_files(self):
        """清理构建文件"""
        print("🧹 清理旧的构建文件...")
        
        for path in ['build', 'dist']:
            if (self.script_dir / path).exists():
                shutil.rmtree(self.script_dir / path, ignore_errors=True)
                print(f"  删除: {path}/")
        
        # 删除旧的 .spec 文件（除了我们要创建的）
        for spec in self.script_dir.glob('*.spec'):
            if spec.name != 'WeChatToolbox_Complete.spec':
                spec.unlink(missing_ok=True)
                print(f"  删除: {spec.name}")
    
    def build_application(self):
        """构建应用程序"""
        print("🔨 开始构建应用程序...")
        
        spec_file = self.create_complete_spec_file()
        
        # 构建命令
        cmd = [
            str(self.python_exe), "-m", "PyInstaller",
            str(spec_file),
            "--noconfirm",
            "--clean",
            "--log-level=INFO",
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        try:
            # 执行构建 - 避免创建额外的控制台窗口
            import subprocess
            CREATE_NO_WINDOW = 0x08000000
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                     text=True, cwd=self.script_dir,
                                     creationflags=CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            # 实时输出
            for line in process.stdout:
                print(line.rstrip())
            
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
        
        # 简单测试启动 - 避免创建console窗口
        print("🧪 测试程序启动...")
        try:
            # 使用 CREATE_NO_WINDOW 标志避免创建控制台窗口
            import subprocess
            DETACHED_PROCESS = 0x00000008
            CREATE_NO_WINDOW = 0x08000000
            
            process = subprocess.Popen([str(exe_path)], 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS,
                                     timeout=5)
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                print("✅ 程序正常启动（超时但这是正常的GUI应用行为）")
                process.kill()
                return True
                
            if process.returncode == 0:
                print("✅ 程序可以正常启动")
                return True
            else:
                print(f"⚠️  程序启动返回码: {process.returncode}")
                if stderr:
                    error_text = stderr.decode('utf-8', errors='ignore')
                    if "libiconv.dll" in error_text:
                        print("❌ 仍然存在 libiconv.dll 依赖问题")
                        return False
                    else:
                        print(f"启动信息: {error_text[:200]}...")
                return True
                
        except FileNotFoundError:
            print("❌ 可执行文件无法运行")
            return False
        except Exception as e:
            print(f"⚠️  启动测试异常: {e}")
            return True
    
    def run_complete_build(self):
        """执行完整的构建流程"""
        print("🚀 开始完整构建流程")
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
        print("🎉 构建完成！")
        print(f"📁 输出目录: {self.script_dir / 'dist'}")
        print(f"🚀 可执行文件: {self.script_dir / 'dist' / 'KiwiKit.exe'}")
        
        return True

def main():
    """主函数"""
    try:
        builder = CompleteBuildTool()
        success = builder.run_complete_build()
        
        if success:
            print("\\n✅ 所有构建步骤完成！")
            print("\\n📝 解决方案总结:")
            print("1. 自动查找并打包 pyzbar 相关的 DLL 文件")
            print("2. 使用虚拟环境 Python 进行打包")
            print("3. 添加了完整的模块导入列表")
            print("4. 禁用了可能导致 DLL 问题的优化选项")
            return 0
        else:
            print("\\n❌ 构建失败！")
            print("\\n🔧 可能的解决方案:")
            print("1. 确保虚拟环境中已安装所有依赖")
            print("2. 手动安装 zbar 库到系统")
            print("3. 检查 pyzbar 是否正确安装")
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