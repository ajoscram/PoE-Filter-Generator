# Performs a console command every time files within the directory where this command was invoked are changed.
# The first argument must be the command to run.
# Every argument after the first will be used as a glob pattern to filter out files in the directory.

import sys
sys.path.append('./src')

import os, multiprocessing, subprocess, watcher, console

class _CLIAction:
    def __init__(self, command: str):
        self.command = command
    
    def __call__(self):
        result = subprocess.run(self.command, shell=True, text=True, check=False)
        exit(result.returncode)

def main(args: list[str]):
    
    if len(args) == 0:
        console.write("Error: Requires at least a command to run.")
        exit(1)

    if len(args) == 1:
        args.append("*.*")

    directory = os.getcwd()    
    command = args[0]
    globs = args[1:]

    console.write("\n[yellow]👁\tPYMON[/]")
    console.write(
        f"Watching directory: [green]{directory}[/]",
        f"\nFiltering files by: [green]{ "[/], [green]".join(globs) }[/]",
        f"\nExecuting: [blue]{command}[/]")
    watcher.watch(directory, globs, _CLIAction(command))

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main(sys.argv[1:])