#!/usr/bin/env python3
"""One isolated runtime attempt; raw logs/results remain private until sanitized."""
from pathlib import Path
import json, subprocess, time, sys
ROOT = Path(__file__).resolve().parent
COMPOSE = ["/usr/bin/podman", "compose", "-f", str(ROOT / "compose.yml"), "--project-name", "artcraft-wopi-gridcraft"]

def run(args, **kwargs):
    return subprocess.run(args, cwd=ROOT, check=True, timeout=900, **kwargs)

def main():
    images = json.loads(subprocess.check_output(["/usr/bin/podman", "image", "inspect", *ROOT.joinpath("images.txt").read_text().splitlines()]))
    ROOT.joinpath("image-digests.json").write_text(json.dumps([{k: image.get(k) for k in ["Id", "RepoDigests", "RepoTags"]} for image in images], indent=2) + "\n")
    try:
        run(COMPOSE + ["up", "-d", "db", "redis", "seafile", "onlyoffice", "bridge"])
        config = "/shared/seafile/conf/seahub_settings.py"
        for _ in range(120):
            ready = subprocess.run(["/usr/bin/podman", "exec", "artcraft-wopi-gridcraft-seafile", "test", "-f", config], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
            if ready.returncode == 0:
                break
            time.sleep(5)
        else:
            raise RuntimeError("isolated Seahub settings did not appear")
        env = dict(line.split("=", 1) for line in ROOT.joinpath(".env").read_text().splitlines() if "=" in line)
        block = ROOT.joinpath("app/lab/real-seafile/seahub_settings.extra.py").read_text().replace("__ONLYOFFICE_JWT_SECRET__", env["ONLYOFFICE_JWT_SECRET"])
        run(["/usr/bin/podman", "exec", "artcraft-wopi-gridcraft-seafile", "cp", config, config + ".pre-artcraft"])
        run(["/usr/bin/podman", "exec", "artcraft-wopi-gridcraft-seafile", "sed", "-i", "/^# >>> artcraft-lab/,/^# <<< artcraft-lab/d", config])
        run(["/usr/bin/podman", "exec", "-i", "artcraft-wopi-gridcraft-seafile", "sh", "-c", "cat >> /shared/seafile/conf/seahub_settings.py"], input=(chr(10) + block).encode())
        run(COMPOSE + ["restart", "seafile"])
        for stage in ["slice", "browser"]:
            with ROOT.joinpath("results", stage + "-run.log").open("wb") as log:
                run(COMPOSE + ["--profile", "test", "run", "--rm", stage], stdout=log, stderr=subprocess.STDOUT)
            print(stage + " process passed", flush=True)
    finally:
        try:
            with ROOT.joinpath("results", "services-final.log").open("wb") as log:
                subprocess.run(COMPOSE + ["logs", "--tail", "100"], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=30)
        finally:
            subprocess.run(COMPOSE + ["--profile", "test", "down", "--remove-orphans"], cwd=ROOT, timeout=120)
    return 0

if __name__ == "__main__":
    sys.exit(main())
