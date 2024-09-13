import subprocess
import os
import sys
import ctypes
import tkinter as tk 
from tkinter import scrolledtext


def interface():
    #Starting GUI
    root = tk.Tk()
    root.geometry("800x600")
    root.title("Windows 11 Debloat Tool")
    
    
    #Main header
    label = tk.Label(root, text="Windows 11 Debloat", font=('Arial', 18))
    label.pack(padx= 20, pady= 20)
    
    #Area to display text
    log_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15, font=('Arial', 10))
    log_area.pack(padx=10, pady=10)
    
    #Button to start
    button = tk.Button(root, text= "Debloat!", font= ('Arial', 16), command= lambda: start_process(log_area))
    button.pack(padx = 20, pady = 60)

    root.mainloop()

def run_powershell_command(command, log_area, timeout=20):

    log_area.insert(tk.END, f"Running command: {command}\n")
    log_area.see(tk.END)
    log_area.update()
    
    
    try:
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            log_area.insert(tk.END, f"Error: {result.stderr}")
        else:
            log_area.insert(tk.END, result.stdout)
    except subprocess.TimeoutExpired:
       log_area.insert(tk.END, f"Command timed out: {command}")
    
    log_area.see(tk.END)
    log_area.update()
        
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
        
        
def remove_installed_apps(log_area):
    
    apps_to_remove = [
        "Microsoft.People", 
        "Microsoft.News", 
        "Microsoft.Todos",
        "Microsoft.Clipchamp",
        "MicrosoftWindows.Client.CBS_cw5n1h2txyewy"
    ]
    
    for app in apps_to_remove:
        
        log_area.insert(tk.END, f"Attempting to remove {app}...")
        log_area.see(tk.END)
        run_powershell_command(f"Get-AppxPackage *{app}* | Remove-AppxPackage -AllUsers", log_area)
        run_powershell_command(f"Get-AppxProvisionedPackage -Online | Where-Object DisplayName -like '*{app}*' | Remove-AppxProvisionedPackage -Online", log_area)
        result = subprocess.run (["powershell", "-Command", f"Get-AppxPackage *{app}*"], capture_output=True, text=True)
        if result.stdout:
            log_area.insert(tk.END, f"Failed to remove {app}...")
        else:
            log_area.insert(tk.END, f"Successfully removed {app}.")
        log_area.see(tk.END)
        log_area.update()
        

def disable_telemetry(log_area):
    
    commands = [
        'Set-ItemProperty -Path HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection -Name AllowTelemetry -Type DWord -Value 0',
        'Stop-Service DiagTrack',
        'Set-Service DiagTrack -StartupType Disabled',
    ]
    
    for command in commands:
        run_powershell_command(command, log_area)

def disable_ai_features(log_area, timeout=10):
    
    commands = [
        #10 second timeout set, will revisit this and fix the registry key. For now, it will just return an error. If it doesn't close, x out of powershell and it will continue
        'Set-ItemProperty -Path HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced -Name ShowCopilotButton -Type DWord -Value 0', 
        'reg add HKCU\\Software\\Policies\\Microsoft\\Windows\\Windows Copilot /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f',
    ]
    
    for command in commands:
        run_powershell_command(f'cmd /c "{command}"', log_area)

def remove_edge(log_area):
    
    commands = [
        'reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge /v AutoLaunchProtocolsFromOrigins /t REG_SZ /d "" /f',
        'reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge /v BrowserSignin /t REG_DWORD /d 0 /f',
        'reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge /v HideFirstRunExperience /t REG_DWORD /d 1 /f',
        'reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge /v DoNotUpdateToEdgeWithChromium /t REG_DWORD /d 1 /f'
    ]
    
    for command in commands:
        run_powershell_command(f'cmd /C "{command}"', log_area)

def restart_prompt(log_area):
    
    log_area.insert(tk.END, "Please restart your computer manually to apply all changes.")
    log_area.see(tk.END)
    log_area.update()
    
    

def start_process(log_area):
    log_area.insert(tk.END, "Starting debloating process...\n")
    log_area.see(tk.END)
    log_area.update()
    
    remove_installed_apps(log_area)
    disable_telemetry(log_area)
    disable_ai_features(log_area)
    remove_edge(log_area)

    restart_prompt(log_area)

def main():
    if is_admin():
        interface()
    else:
        run_as_admin()

if __name__ == "__main__":


    main()
