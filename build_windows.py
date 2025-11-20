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
        """必要なパッケージがインストールされているか確認"""
        print("=" * 60)
        print("必要なパッケージを確認中...")
        print("=" * 60)
        
        required = ['PySide6', 'numpy', 'matplotlib', 'pyinstaller']
        missing = []
        
        for package in required:
            try:
                __import__(package.lower().replace('-', '_'))
                print(f"✓ {package} - インストール済み")
            except ImportError:
                print(f"✗ {package} - 未インストール")
                missing.append(package)
        
        if missing:
            print("\n以下のパッケージをインストールしてください:")
            print(f"pip install {' '.join(missing)}")
            return False
        
        print("\n全ての必要なパッケージがインストールされています！")
        return True
    
    def clean_build(self):
        """以前のビルドファイルを削除"""
        print("\n" + "=" * 60)
        print("クリーンアップ中...")
        print("=" * 60)
        
        dirs_to_remove = [self.build_dir, self.dist_dir, "__pycache__"]
        files_to_remove = [self.spec_file]
        
        for dir_path in dirs_to_remove:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"✓ {dir_path} を削除しました")
        
        for file_path in files_to_remove:
            if Path(file_path).exists():
                os.remove(file_path)
                print(f"✓ {file_path} を削除しました")
    
    def create_spec_file(self):
        """PyInstallerの.specファイルを作成"""
        print("\n" + "=" * 60)
        print(".specファイルを作成中...")
        print("=" * 60)
        
        spec_content = f"""# -*- mode: python ; coding: utf-8 -*- block_cipher = None a = Analysis( ['{self.main_script}'], pathex=[], binaries=[], datas=[], hiddenimports=[ 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'PySide6.QtSvgWidgets', 'matplotlib.backends.backend_qt5agg', 'matplotlib.backends.backend_agg', 'numpy', 'PIL', 'PIL._imaging', ], hookspath=[], hooksconfig={{}}, runtime_hooks=[], excludes=[ 'tkinter', 'PyQt5', 'PyQt6', ], win_no_prefer_redirects=False, win_private_assemblies=False, cipher=block_cipher, noarchive=False, ) pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher) exe = EXE( pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [], name='{self.project_name}', debug=False, bootloader_ignore_signals=False, strip=False, upx=True, upx_exclude=[], runtime_tmpdir=None, console=False, # GUIアプリケーションなのでコンソールを非表示 disable_windowed_traceback=False, argv_emulation=False, target_arch=None, codesign_identity=None, entitlements_file=None, icon='icon.ico' if Path('icon.ico').exists() else None, ) """
        
        with open(self.spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"✓ {self.spec_file} を作成しました")
    
    def build_exe(self):
        """PyInstallerでビルド実行"""
        print("\n" + "=" * 60)
        print("ビルドを開始します...")
        print("=" * 60)
        print("※ この処理には数分かかる場合があります")
        
        try:
            # PyInstallerを実行
            subprocess.run(
                ['pyinstaller', '--clean', self.spec_file],
                check=True
            )
            
            print("\n" + "=" * 60)
            print("ビルド完了！")
            print("=" * 60)
            
            exe_path = self.dist_dir / f"{self.project_name}.exe"
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"\n実行ファイル: {exe_path}")
                print(f"ファイルサイズ: {size_mb:.2f} MB")
                print(f"\n{exe_path} をダブルクリックして実行してください！")
                return True
            else:
                print("エラー: 実行ファイルが見つかりません")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"\nビルドエラー: {e}")
            return False
    
    def create_readme(self):
        """READMEファイルを作成"""
        readme_content = """# トロコイド系曲線ビューアー ## 実行方法 `TrochoidViewer.exe` をダブルクリックして起動してください。 ## 機能 1. **曲線ビューアー**: 様々なトロコイド系曲線を描画・アニメーション表示 2. **分類図**: 曲線の分類体系を表示 3. **練習問題**: 数学Ⅲレベルの練習問題と解答・解説 ## 動作環境 - Windows 10/11 (64bit) ## トラブルシューティング ### 起動しない場合 1. Windows Defenderやウイルス対策ソフトでブロックされている可能性があります 2. ファイルを右クリック → プロパティ → 「ブロックの解除」をチェック ### 動作が重い場合 - 描画速度スライダーを調整してください - 補助円の表示をオフにすると軽くなります ## 問い合わせ 問題が発生した場合は、エラーメッセージのスクリーンショットと共にお知らせください。 """
        
        readme_path = self.dist_dir / "README.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"\n✓ {readme_path} を作成しました")
    
    def run(self):
        """ビルドプロセス全体を実行"""
        print("\n" + "=" * 60)
        print("Windows用ビルドを開始します")
        print("=" * 60)
        
        # ステップ1: 要件チェック
        if not self.check_requirements():
            print("\n必要なパッケージをインストールしてから再実行してください")
            print("コマンド: pip install -r requirements.txt")
            return False
        
        # ステップ2: クリーンアップ
        self.clean_build()
        
        # ステップ3: .specファイル作成
        self.create_spec_file()
        
        # ステップ4: ビルド実行
        if not self.build_exe():
            return False
        
        # ステップ5: README作成
        self.create_readme()
        
        print("\n" + "=" * 60)
        print("全ての処理が完了しました！")
        print("=" * 60)
        print(f"\ndist/{self.project_name}.exe を実行してください")
        
        return True

def main():
    """メイン処理"""
    builder = WindowsBuilder()
    
    # メインスクリプトの存在確認
    if not Path(builder.main_script).exists():
        print(f"エラー: {builder.main_script} が見つかりません")
        print("このスクリプトとtrochoid_viewer.pyを同じフォルダに配置してください")
        return
    
    # ビルド実行
    success = builder.run()
    
    if success:
        print("\n配布する場合は、distフォルダ内の全てのファイルを配布してください")
    else:
        print("\nビルドに失敗しました。エラーメッセージを確認してください")

if __name__ == "__main__":
    main()