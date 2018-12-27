import subprocess
from unittest.mock import Mock

from bed_to_tabix.lib import run_parallel_commands


def test_run_parallel_commands(monkeypatch):
    check_output_mock = Mock()
    monkeypatch.setattr(subprocess, 'check_output', check_output_mock)

    result = run_parallel_commands(commands_to_run=['cmd1', 'cmd2'], threads=2)
    result = list(result)

    assert check_output_mock.call_count == 2
    call1, call2 = check_output_mock.call_args_list
    assert call1[0][0] == 'cmd1'
    assert call1[1]['shell'] is True
    assert call2[0][0] == 'cmd2'
    assert call2[1]['shell'] is True
