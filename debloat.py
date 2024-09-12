#This is the code for debloat.py


#Side note:
#All the code here is a WIP. I'm a first year software developer, so expect some bugs. I'm happy to hear any tips/tricks!

import subprocess
import os
import sys
import ctypes


def run_powershell_command(command, timeout=60):

    print(f"Running command: {command}")
    try:
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        else:
            print(result.stdout)
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {command}")
    
        
def is_admin():

    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():

    if not is_admin():
        print("This script requires elevated privileges. Relaunching as administrator...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
        
        
def remove_installed_apps():
    
    apps_to_remove = [
        "Microsoft.People", 
        "Microsoft.News", 
        "Microsoft.Todos",
        "Microsoft.Clipchamp",
        "MicrosoftWindows.Client.CBS_cw5n1h2txyewy"
    ]
    
    for app in apps_to_remove:
        
        print(f"Attempting to remove {app}...")
        run_powershell_command(f"Get-AppxPackage *{app}* | Remove-AppxPackage -AllUsers")
        run_powershell_command(f"Get-AppxProvisionedPackage -Online | Where-Object DisplayName -like '*{app}*' | Remove-AppxProvisionedPackage -Online")
        result = subprocess.run (["powershell", "-Command", f"Get-AppxPackage *{app}*"], capture_output=True, text=True)
        if result.stdout:
            print(f"Failed to remove {app}...")
        else:
            print(f"Successfully removed {app}.")

def disable_telemetry():
    
    commands = [
        'Set-ItemProperty -Path HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection -Name AllowTelemetry -Type DWord -Value 0',
        'Stop-Service DiagTrack',
        'Set-Service DiagTrack -StartupType Disabled',
    ]
    
    for command in commands:
        run_powershell_command(command)

def disable_ai_features():
    
    commands = [
        
        'Set-ItemProperty -Path HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced -Name ShowCopilotButton -Type DWord -Value 0', 
        'reg add HKCU\\Software\\Policies\\Microsoft\\Windows\\Windows Copilot /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f',

        # "Stop-Service -Name 'WindowsCopilot' -Force", 
        # "Set-Service -Name 'WindowsCopilot' -StartupType Disabled",
    ]
    
    for command in commands:
        run_powershell_command(command)

def remove_edge():
    
    commands = [
        'reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge /v AutoLaunchProtocolsFromOrigins /t REG_SZ /d "" /f',
        'reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge /v BrowserSignin /t REG_DWORD /d 0 /f',
        'reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge /v HideFirstRunExperience /t REG_DWORD /d 1 /f',
        'reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge /v DoNotUpdateToEdgeWithChromium /t REG_DWORD /d 1 /f'
    ]
    
    for command in commands:
        run_powershell_command(f'cmd /C "{command}"')

def restart_prompt():
    
    response = input("Debloating complete. Would you like to restart your computer now? (y/n): ").strip().lower()
    if response == 'y':
        print("Restarting your computer...")
        run_powershell_command("Restart-Computer -Force")
    else:
        print("Please restart your computer manually to apply all changes.")

def main():
    print("Debloating Windows 11, please wait...")
    run_as_admin()
    remove_installed_apps()
    disable_telemetry()
    disable_ai_features()
    remove_edge()
    restart_prompt()

if __name__ == "__main__":
    main()
