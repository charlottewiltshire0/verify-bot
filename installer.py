import platform
import subprocess

try:
    os_name = platform.system()
    match os_name:
        case "Windows":
            # If you installed python using Microsoft Store, replace `py` with `python3` in the next line.
            subprocess.run(['py', '-m', 'pip', 'install', '--user', 'pipx'], check=True)
        case "Linux":
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            subprocess.run(['sudo', 'apt', 'install', '-y', 'pipx'], check=True)
            subprocess.run(['pipx', 'ensurepath'], check=True)
        case "Darwin":
            subprocess.run(['brew', 'install', 'pipx'], check=True)
            subprocess.run(['pipx', 'ensurepath'], check=True)
        case _:
            print(f"Unable to determine the operating system: {os_name}")
            exit(1)
    subprocess.run(['pipx', 'install', 'poetry'], check=True)
    subprocess.run(['poetry', 'install'], check=True)
except subprocess.CalledProcessError as e:
    print(f"Unable to install the package. Error: {e}")
finally:
    print("""
    Installation process is completed. Please check above for any errors.
    """)
    
    
    
    """)


