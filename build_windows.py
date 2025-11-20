"""
Windows Build Script
Build Trochoid Viewer to .exe file
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class WindowsBuilder:
    def __init__(self):
        self.project_name = "TrochoidViewer"
        self.main_script = "trochoid_viewer.py"
        self.build_dir = Path("build")
        self.dist_dir = Path("dist")
        self.spec_file = f"{self.project_name}.spec"
        
    def check_requirements(self):
        """Check if required packages are installed"""
        print("=" * 60)
        print("Checking required packages...")
        print("=" * 60)
        
        required = ['PySide6', 'numpy', 'matplotlib', 'pyinstaller']
        missing = []
        
        for package in required:
            try:
                __import__(package.lower().replace('-', '_'))
                print(f"OK {package} - installed")
            except ImportError:
                print(f"NG {package} - not installed")
                missing.append(package)
        
        if missing:
            print("\nPlease install the following packages:")
            print(f"pip install {' '.join(missing)}")
            return False
        
        print("\nAll required packages are installed!")
        return True
    
    def clean_build(self):
        """Remove previous build files"""
        print("\n" + "=" * 60)
        print("Cleaning up...")
        print("=" * 60)
        
        dirs_to_remove = [self.build_dir, self.dist_dir, "__pycache__"]
        files_to_remove = [self.spec_file]
        
        for dir_path in dirs_to_remove:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"OK Removed {dir_path}")
        
        for file_path in files_to_remove:
            if Path(file_path).exists():
                os.remove(file_path)
                print(f"OK Removed {file_path}")
    
    def create_spec_file(self):
        """Create PyInstaller .spec file"""
        print("\n" + "=" * 60)
        print("Creating .spec file...")
        print("=" * 60)
        
        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{self.main_script}'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtSvgWidgets',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.backends.backend_agg',
        'numpy',
        'PIL',
        'PIL._imaging',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'PyQt5',
        'PyQt6',
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
    name='{self.project_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
        
        with open(self.spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"OK Created {self.spec_file}")
    
    def build_exe(self):
        """Build with PyInstaller"""
        print("\n" + "=" * 60)
        print("Starting build...")
        print("=" * 60)
        print("This may take several minutes...")
        
        try:
            subprocess.run(
                ['pyinstaller', '--clean', self.spec_file],
                check=True
            )
            
            print("\n" + "=" * 60)
            print("Build completed!")
            print("=" * 60)
            
            exe_path = self.dist_dir / f"{self.project_name}.exe"
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"\nExecutable: {exe_path}")
                print(f"File size: {size_mb:.2f} MB")
                print(f"\nDouble-click {exe_path} to run!")
                return True
            else:
                print("Error: Executable not found")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"\nBuild error: {e}")
            return False
    
    def create_readme(self):
        """Create README file"""
        readme_content = """# Trochoid Viewer

## How to Run

Double-click `TrochoidViewer.exe` to start.

## Features

1. **Curve Viewer**: Draw and animate various trochoid curves
2. **Classification Chart**: Display curve classification system
3. **Practice Problems**: Math III level practice problems with solutions

## System Requirements

- Windows 10/11 (64bit)

## Troubleshooting

### Won't start

1. May be blocked by Windows Defender or antivirus software
2. Right-click file -> Properties -> Check "Unblock"

### Slow performance

- Adjust drawing speed slider
- Turn off auxiliary circle display

## Contact

If you encounter problems, please provide a screenshot of the error message.
"""
        
        readme_path = self.dist_dir / "README.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"\nOK Created {readme_path}")
    
    def run(self):
        """Run entire build process"""
        print("\n" + "=" * 60)
        print("Starting Windows build")
        print("=" * 60)
        
        if not self.check_requirements():
            print("\nPlease install required packages and try again")
            print("Command: pip install -r requirements.txt")
            return False
        
        self.clean_build()
        self.create_spec_file()
        
        if not self.build_exe():
            return False
        
        self.create_readme()
        
        print("\n" + "=" * 60)
        print("All processes completed!")
        print("=" * 60)
        print(f"\nRun dist/{self.project_name}.exe")
        
        return True

def main():
    """Main process"""
    builder = WindowsBuilder()
    
    if not Path(builder.main_script).exists():
        print(f"Error: {builder.main_script} not found")
        print("Place this script and trochoid_viewer.py in the same folder")
        return
    
    success = builder.run()
    
    if success:
        print("\nTo distribute, share all files in the dist folder")
    else:
        print("\nBuild failed. Check error messages")

if __name__ == "__main__":
    main()
