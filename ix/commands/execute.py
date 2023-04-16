import subprocess

from ix.commands import command as registry_command
from ix.commands.filesystem import WORKDIR


@registry_command(description="execute a python file", name="execute_python_file")
def execute_python_file(filename: str):
    """Execute a python file"""
    full_path = WORKDIR / filename
    return subprocess.run(["python", full_path])


def execute_bash_command(command: str) -> str:
    # XXX: turn on once dockerfile users are setup
    # command = f"sudo -u {user} {command}"

    try:
        output = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT, text=True, cwd=WORKDIR
        )
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.strip()}"
