import os
from pathlib import Path

def create_inno_script():
    """Inno Setup用のスクリプトを生成"""
    
    script_content = """ ; Inno Setup Script for Trochoid Viewer #define MyAppName "トロコイド系曲線ビューアー" #define MyAppVersion "1.0.0" #define MyAppPublisher "Your Name" #define MyAppExeName "TrochoidViewer.exe" [Setup] AppId={{YOUR-GUID-HERE}} AppName={#MyAppName} AppVersion={#MyAppVersion} AppPublisher={#MyAppPublisher} DefaultDirName={autopf}\\TrochoidViewer DefaultGroupName={#MyAppName} OutputDir=installer OutputBaseFilename=TrochoidViewer_Setup Compression=lzma SolidCompression=yes WizardStyle=modern [Languages] Name: "japanese"; MessagesFile: "compiler:Languages\\Japanese.isl" [Tasks] Name: "desktopicon"; Description: "デスクトップにショートカットを作成"; GroupDescription: "追加のアイコン:" [Files] Source: "dist\\TrochoidViewer.exe"; DestDir: "{app}"; Flags: ignoreversion Source: "dist\\README.txt"; DestDir: "{app}"; Flags: ignoreversion [Icons] Name: "{group}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}" Name: "{group}\\README"; Filename: "{app}\\README.txt" Name: "{autodesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon [Run] Filename: "{app}\\{#MyAppExeName}"; Description: "アプリケーションを起動"; Flags: nowait postinstall skipifsilent """
    
    with open("installer_script.iss", 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✓ installer_script.iss を作成しました")
    print("\nInno Setup Compilerでこのファイルを開いてインストーラーを作成できます")
    print("ダウンロード: https://jrsoftware.org/isdl.php")

if __name__ == "__main__":
    create_inno_script()