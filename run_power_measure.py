import subprocess
import time
from experiment.settings import compression_dict

IMAGE_TAG = "power_consumption"


def main():
    for compression in compression_dict.keys():
        subprocess.Popen(["docker", "stop", f"json_{compression}"])
        subprocess.Popen(["docker", "stop", f"proto_{compression}"])
        subprocess.Popen(["docker", "rm", f"json_{compression}"])
        subprocess.Popen(["docker", "rm", f"proto_{compression}"])
    try:
        for compression in compression_dict.keys():
            subprocess.Popen(
                [
                    "docker",
                    "run",
                    "--name",
                    f"json_{compression}",
                    "-e",
                    f"COMPRESSION={compression}",
                    "-e",
                    "FORMAT=json",
                    "-v",
                    "./src/:/app",
                    IMAGE_TAG,
                ],
                stdout=None,
            )
            subprocess.Popen(
                [
                    "docker",
                    "run",
                    "--name",
                    f"proto_{compression}",
                    "-e",
                    f"COMPRESSION={compression}",
                    "-e",
                    "FORMAT=proto",
                    "-v",
                    "./src/:/app",
                    IMAGE_TAG,
                ],
                stdout=None,
            )
            time.sleep(60 * 10)  # сколько секунд измерять потребление
            subprocess.run(["docker", "stop", f"json_{compression}"])
            subprocess.run(["docker", "stop", f"proto_{compression}"])
            subprocess.run(["docker", "rm", f"json_{compression}"])
            subprocess.run(["docker", "rm", f"proto_{compression}"])
    except Exception:
        for compression in compression_dict.keys():
            subprocess.Popen(["docker", "stop", f"json_{compression}"])
            subprocess.Popen(["docker", "stop", f"proto_{compression}"])
            subprocess.Popen(["docker", "rm", f"json_{compression}"])
            subprocess.Popen(["docker", "rm", f"proto_{compression}"])


if __name__ == "__main__":
    main()
