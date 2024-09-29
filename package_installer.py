import subprocess

packages=[
    "rich",
]

for package in packages:
    subprocess.run(f"pip install {package}")