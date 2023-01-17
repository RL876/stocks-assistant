import os
import sys
import argparse
import subprocess
from pkgutil import iter_modules


def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--codes", action="store_true", help="update codes")
    parser.add_argument("--price", action="store_true", help="update price")
    parser.add_argument("--alert", action="store_true", help="run alert")
    parser.add_argument("--chart", action="store_true", help="plot chart")
    parser.add_argument("--news", action="store_true", help="update news")
    parser.add_argument("--strategy", action="store_true", help="strategy")
    parser.add_argument("--data_path", type=str, default="data", help="path")
    args = parser.parse_args()
    return args


def installPkgs(packages):
    pip_list = [p.name for p in iter_modules()]
    for pkg in packages:
        if pkg in pip_list:
            print(f"Installed:\t{pkg}")
            continue
        print(f"Installing:\t{pkg}")
        if pkg == "TA-Lib" and sys.platform == "linux":
            if not (os.path.exists("libta.deb") or os.path.exists("ta.deb")):
                url = "https://launchpad.net/~mario-mariomedina/+archive/ubuntu/talib/+files"
                os.system(
                    f"wget {url}/libta-lib0_0.4.0-oneiric1_amd64.deb -qO libta.deb")
                os.system(
                    f"wget {url}/ta-lib0-dev_0.4.0-oneiric1_amd64.deb -qO ta.deb")
            os.system("dpkg -i libta.deb ta.deb")
            os.system("pip install ta-lib")
            continue
        else:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pkg])


def setDataPath(path: str):
    if not os.path.exists(path):
        os.mkdir(path)
