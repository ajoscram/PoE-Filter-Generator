import os, subprocess, console, utils
from core import ExpectedError

NAME = "path"

_REMOVE_ARG = "remove"
_WINDOWS_OS_NAME = "nt"
_GET_PATH_SCRIPT = "echo $([Environment]::GetEnvironmentVariable('PATH', [EnvironmentVariableTarget]::User))"
_SET_PATH_SCRIPT = "$NEW_PATH='{0}';[Environment]::SetEnvironmentVariable('PATH', $NEW_PATH, [EnvironmentVariableTarget]::User)"
_GENERIC_POWERSHELL_SCRIPT = "powershell -command \"{0}\""

_TAKE_A_WHILE_MESSAGE = "This might take a while..."
_ADDING_TO_PATH_MESSAGE = "Adding '{0}' to the user's PATH." 
_REMOVING_FROM_PATH_MESSAGE = "Removing '{0}' from the user's PATH." 
_PATH_SET_COMPLETE_MESSAGE = "Restart your console for changes to take effect."
_PATH_ALREADY_SET_MESSAGE = "The current directory is already a part of the user's PATH. No need to add it again!"
_PATH_ALREADY_REMOVED_MESSAGE = "The current directory could not be found as a part of the user's PATH. No need to remove it!"

_ARGS_ERROR = "The :path command only accepts 'remove' as a possible argument. You've provided: {0}"
_NOT_ON_WINDOWS_ERROR = "This command is only available on Windows systems."
_POWERSHELL_NOT_FOUND_ERROR = "Could not find PowerShell, which is required for this command. Please ensure PowerShell is installed on your computer."
_COMMAND_EXECUTION_ERROR = """An error occurred while executing a PowerShell command. Debug information:
\tcommand: {0}
\terror_code: {1}
\tstderr: {2}
\tstdout: {3}
"""

def execute(args: list[str]):
    """Adds the path where the current script / executable is placed to the system's environment variables.
    If the `remove` option is received, the path will be removed instead. 
    Only available on Windows."""
    if os.name != _WINDOWS_OS_NAME:
        raise ExpectedError(_NOT_ON_WINDOWS_ERROR)
    
    if len(args) > 1 or len(args) == 1 and args[0].lower() != _REMOVE_ARG:
        raise ExpectedError(_ARGS_ERROR.format(" ".join(args)))

    should_remove = len(args) == 1 # it must be _REMOVE_ARG because of previous if statement
    paths = _get_env_paths()
    curr_dir = utils.get_execution_dir()

    if curr_dir in paths and not should_remove:
        return console.write(_PATH_ALREADY_SET_MESSAGE)

    if curr_dir not in paths and should_remove:
        return console.write(_PATH_ALREADY_REMOVED_MESSAGE)

    if should_remove:
        setting_path_message = _REMOVING_FROM_PATH_MESSAGE
        paths = [ path for path in paths if not os.path.samefile(curr_dir, path) ]
    else:
        setting_path_message = _ADDING_TO_PATH_MESSAGE
        paths = paths + [ curr_dir ]

    console.write(setting_path_message.format(curr_dir), _TAKE_A_WHILE_MESSAGE)
    _set_env_paths(paths)
    console.write(_PATH_SET_COMPLETE_MESSAGE, done=True)

def _get_env_paths():
    env_paths_str = _execute_powershell(_GET_PATH_SCRIPT).rstrip()
    return [ os.path.abspath(env_path)
        for env_path in env_paths_str.split(os.pathsep)
        if env_path != "" ]

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