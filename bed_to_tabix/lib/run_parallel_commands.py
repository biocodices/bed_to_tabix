from concurrent.futures import ThreadPoolExecutor

from more_itertools import chunked

from bed_to_tabix.lib import run_shell_command


def run_parallel_commands(commands_to_run, threads):
    """
    Expects a list of dicts with the commands to run:

        [{'cmd': command_1}, {'cmd': command_2}, ... ]

    Will run the commands in N threads and return a new list with the same
    entries and a 'success' key:

        [{'cmd': command_1, 'success': True}, ... ]

    """
    threads = min(threads, len(commands_to_run))
    for group_of_commands in chunked(commands_to_run, n=threads):
        # I have to group the commands in groups of size=threads before using
        # ThreadPoolExecutor because otherwise the extra commands can't be
        # easily stopped with CTRL-C or whenever an Exception is raised.
        group_of_commands = [cmd for cmd in group_of_commands if cmd]
        with ThreadPoolExecutor(len(group_of_commands)) as executor:
            results = executor.map(run_shell_command, group_of_commands)
            list(results)  # raises Exception from any of the threads
