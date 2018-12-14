from subprocess import check_output, STDOUT
from concurrent.futures import ThreadPoolExecutor

from more_itertools import chunked

from .logger import logger


def run_parallel_commands(commands_to_run, threads):
    """
    Expects a list of dicts with the commands to run:

        [{'cmd': command_1}, {'cmd': command_2}, ... ]

    Will run the commands in N threads and return a new list with the same
    entries and a 'success' key:

        [{'cmd': command_1, 'success': True}, ... ]

    """
    def syscall(command):
        ix = id(command['cmd'])
        logger.debug('Running command {}: {}'.format(ix, command['cmd']))
        output = check_output(command['cmd'], shell=True, stderr=STDOUT)
        logger.debug('Output {}: {}'.format(ix, output.decode('utf-8')))

    threads = min(threads, len(commands_to_run))
    for group_of_commands in chunked(commands_to_run, n=threads):
        # I have to group the commands in groups of size=threads before using
        # ThreadPoolExecutor because otherwise the extra commands can't be
        # easily stopped with CTRL-C or whenever an Exception is raised.
        group_of_commands = [cmd for cmd in group_of_commands if cmd]
        with ThreadPoolExecutor(len(group_of_commands)) as executor:
            results = executor.map(syscall, group_of_commands)
            list(results)  # raises Exception from any of the threads
