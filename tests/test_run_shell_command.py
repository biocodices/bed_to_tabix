import subprocess
from unittest.mock import Mock

from bed_to_tabix.lib import run_shell_command


def test_run_shell_command(monkeypatch):
    check_output_mock = Mock()
    monkeypatch.setattr(subprocess, 'check_output', check_output_mock)
    run_shell_command('some command')

    assert check_output_mock.call_count == 1
    assert check_output_mock.call_args[0][0] == 'some command'
    assert check_output_mock.call_args[1]['shell'] == True
