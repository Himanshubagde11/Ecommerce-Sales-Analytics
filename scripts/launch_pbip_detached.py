import subprocess
import time
import psutil

pbip_path = r"D:\Portfolio Projects\E-commers sales analytics\powerbi\Veyra_Ecommerce_Analytics.pbip"
pbi_exe = r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe"

print(f"Launching Power BI Desktop with DETACHED_PROCESS: {pbip_path}")
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

proc = subprocess.Popen(
    [pbi_exe, pbip_path],
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
    close_fds=True
)

print(f"Launched PBIDesktop with PID: {proc.pid}")

# Monitor for 10 seconds to verify it starts and stays alive
for i in range(1, 11):
    time.sleep(1)
    if proc.poll() is not None:
        print(f"Process exited early with return code {proc.returncode}")
        break
    try:
        p = psutil.Process(proc.pid)
        children = [c.name() for c in p.children(recursive=True)]
        print(f"[{i}s] PID {proc.pid} is {p.status()}, children: {children}")
    except Exception as e:
        print(f"[{i}s] Process check: {e}")

print("Launch confirmed successful!")
