from concurrent.futures import ThreadPoolExecutor, as_completed

from more_itertools import chunked

from ..lib import run_shell_command


def run_parallel_commands(commands_to_run, threads):
    """
    Expects a list commands to run:

        ['command1 --foo FOO --bar BAR', 'command2 --baz BAZ', ...]

    Yields the same commands as they are completed. (It's a generator.)
    """
    threads = min(threads, len(commands_to_run))
    for group_of_commands in chunked(commands_to_run, n=threads):
        # I have to group the commands in groups of size=threads before using
        # ThreadPoolExecutor because otherwise the extra commands can't be
        # easily stopped with CTRL-C or whenever an Exception is raised.
        group_of_commands = [cmd for cmd in group_of_commands if cmd]

        with ThreadPoolExecutor(len(group_of_commands)) as executor:
            future_to_command = {executor.submit(run_shell_command, cmd): cmd
                                for cmd in group_of_commands}

            for future in as_completed(future_to_command):
                command = future_to_command[future]
                future.result()  # raises Exception from any of the threads
                yield command
