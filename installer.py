import platform
import subprocess
from tqdm import tqdm

try:
    os_name = platform.system()
    with tqdm(desc="Installing pipx", unit="step") as progress_bar:
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
        progress_bar.update(1)

    with tqdm(desc="Installing poetry", unit="step") as progress_bar:
        subprocess.run(['pipx', 'install', 'poetry'], check=True)
        progress_bar.update(1)

    with tqdm(desc="Running poetry install", unit="step") as progress_bar:
        subprocess.run(['poetry', 'install'], check=True)
        progress_bar.update(1)

except subprocess.CalledProcessError as e:
    print(f"Unable to install the package. Error: {e}")
finally:
    print("""
    Installation process is completed. Please check above for any errors.
    """)


