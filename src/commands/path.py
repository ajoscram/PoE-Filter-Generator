import os, subprocess, console
from core import ExpectedError

NAME = "path"

_WINDOWS_OS_NAME = "nt"
_GET_PATH_SCRIPT = "echo $([Environment]::GetEnvironmentVariable('PATH', [EnvironmentVariableTarget]::User))"
_SET_PATH_SCRIPT = "$NEW_PATH='{0}';[Environment]::SetEnvironmentVariable('PATH', $NEW_PATH, [EnvironmentVariableTarget]::User)"
_GENERIC_POWERSHELL_SCRIPT = "powershell -command \"{0}\""

_SETTING_PATH_MESSAGE = "Adding '{0}' to the user's PATH. This might take a while..."
_PATH_SET_COMPLETE_MESSAGE = "Restart your console for changes to take effect."
_PATH_ALREADY_SET_MESSAGE = "The current directory is already a part of the user's PATH. No need to add it again!"

_NOT_ON_WINDOWS_ERROR = "This command is only available on Windows systems."
_POWERSHELL_NOT_FOUND_ERROR = "Could not find PowerShell, which is required for this command. Please ensure PowerShell is installed on your computer."
_COMMAND_EXECUTION_ERROR = """An error occurred while executing a PowerShell command. Debug information:
\tcommand: {0}
\terror_code: {1}
\tstderr: {2}
\tstdout: {3}
"""

def execute(curr_dir: str, _):
    if os.name != _WINDOWS_OS_NAME:
        raise ExpectedError(_NOT_ON_WINDOWS_ERROR)

    paths = _get_env_paths()
    if _is_path_in_env_paths(curr_dir, paths):
        return console.write(_PATH_ALREADY_SET_MESSAGE)

    console.write(_SETTING_PATH_MESSAGE.format(curr_dir))
    _set_env_paths(paths + [ curr_dir ])
    console.write(_PATH_SET_COMPLETE_MESSAGE, done=True)

def _get_env_paths():
    env_paths_str = _execute_powershell(_GET_PATH_SCRIPT).rstrip()
    return [ env_path
        for env_path in env_paths_str.split(os.pathsep)
        if env_path != "" ]

def _is_path_in_env_paths(path: str, env_paths: list[str]):
    env_paths = [ os.path.abspath(env_path) for env_path in env_paths ]
    print("path: ", path)
    print("env_paths: ", env_paths)
    return path in env_paths

def _set_env_paths(paths: list[str]):
    env_path = os.pathsep.join(paths)
    _execute_powershell(_SET_PATH_SCRIPT.format(env_path))

def _execute_powershell(command: str):
    command = command.replace('"', '\\"')
    command = _GENERIC_POWERSHELL_SCRIPT.format(command)

    completed_process = _run_subprocess(command)
    if completed_process.returncode != 0:
        error = _COMMAND_EXECUTION_ERROR.format(
            command,
            completed_process.returncode,
            completed_process.stderr,
            completed_process.stdout)
        raise ExpectedError(error)

    return completed_process.stdout
    
def _run_subprocess(command: str):
    try:
        return subprocess.run(command, capture_output=True, text=True)
    except FileNotFoundError:
        raise ExpectedError(_POWERSHELL_NOT_FOUND_ERROR)