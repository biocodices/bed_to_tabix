import subprocess

from bed_to_tabix.lib import logger


def run_shell_command(command, ix=None):
    """Run a *command* (string) in the shell. Return the output."""
    if not ix:
        ix = id(command)

    logger.info(f'[{ix}] Running: {command}')

    try:
        out = subprocess.check_output(command, shell=True,
                                      stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        error = e.stdout.decode('utf-8')
        message = (f'Command:\n\n[{ix}] {command}\n\nFailed with message:' +
                   f'\n\n{error}')
        logger.error(message)
        raise subprocess.CalledProcessError(message)

    out = out.decode('utf-8')
    logger.debug(f'[{ix}] Output: {out}')

    return out
