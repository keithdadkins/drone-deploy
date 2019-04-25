import sys
import subprocess
from pathlib import Path


def build_ami(profile_name=None):
    '''
    Runs the build-drone-server-ami.sh script to build the AMI.
    '''
    # script_path = Path(__file__).parents[2].resolve()
    script_path = Path.cwd()
    try:
        command = f"./build-drone-server-ami.sh -p {profile_name}"
        p = subprocess.Popen(command, stderr=subprocess.PIPE, shell=True, text=True,
                             cwd=script_path)
        while True:
            out = p.stderr.read(1)
            if out == '' and p.poll() is not None:
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()
    except Exception:
        pass
