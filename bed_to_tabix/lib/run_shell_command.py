import subprocess

from ..lib import logger


def run_shell_command(command, ix=None):
    """Run a *command* (string) in the shell. Return the output."""
    if not ix:
        ix = id(command)

    logger.debug(f'[{ix}] Running: {command}')

    # The exception will be caught and logged by run_pipeline:
    try:
        out = subprocess.check_output(command, shell=True,
                                    stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        error = e.stdout.decode('utf-8')
        message = ('Command:\n\n' +
                   f'\t[{ix}] {command}\n\n' +
                   'Failed with message:\n\n' +
                   f'\t"{error.strip()}"')
        e.args = (message, ) + e.args
        raise

    out = out.decode('utf-8')
    logger.debug(f'[{ix}] Output: {out}')

    return out
