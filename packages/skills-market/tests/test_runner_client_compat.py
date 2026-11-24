import os
from pathlib import Path
import subprocess
import sys

import pytest


SKILLS = Path(__file__).resolve().parents[3] / "skills"
SHELL_CLIENTS = ("claude", "codex", "gemini", "kimi", "opencode", "qwen")
HELPER = SKILLS / "codex-cli-runner/scripts/client_compat.py"


def test_standalone_runners_ship_the_same_diagnostic():
    for client in SHELL_CLIENTS:
        script = SKILLS / f"{client}-cli-runner/scripts/client_compat.py"
        assert script.read_bytes() == HELPER.read_bytes()


@pytest.mark.parametrize("diagnostic", [
    "401 unauthorized",
    "Invalid argument: token expired",
    "Unknown model: not-configured",
    "The answer quoted 'unknown option --custom'",
])
def test_non_interface_errors_do_not_advise_an_update(tmp_path, diagnostic):
    log = tmp_path / "stderr"
    log.write_text(diagnostic)
    probe = subprocess.run([sys.executable, HELPER, "options", "missing-client", log], capture_output=True)
    assert probe.returncode == 1 and not probe.stderr


def test_check_client_uses_command_help_and_accepts_other_versions(tmp_path):
    if sys.platform == "win32":
        executable = tmp_path / "codex.cmd"
        executable.write_text(
            '@echo off\n'
            'if "%~1"=="--version" (\n'
            '  echo codex-cli 9.8.7\n'
            '  exit /b 0\n'
            ')\n'
            'if not "%~1 %~2"=="exec --help" exit /b 9\n'
            'echo   --sandbox MODE\n'
            'echo   -o, --output-last-message FILE\n'
            'echo   --skip-git-repo-check\n'
            'echo   -c, --config VAL\n',
            encoding="ascii",
        )
    else:
        executable = tmp_path / "codex"
        executable.write_text("#!/bin/sh\n"
                              'if [ "$1" = --version ]; then echo "codex-cli 9.8.7"; exit; fi\n'
                              '[ "$1 $2" = "exec --help" ] || exit 9\n'
                              "printf '%s\\n' '  --sandbox MODE' '  -o, --output-last-message FILE' "
                              "'  --skip-git-repo-check' '  -c, --config VAL'\n", encoding="ascii")
        executable.chmod(0o755)
    cmd = ["bash", SKILLS / "codex-cli-runner/scripts/run_codex.sh", "--check-client"]
    env = dict(os.environ, PATH=str(tmp_path) + os.pathsep + os.environ["PATH"])
    passed = subprocess.run(cmd, env=env, capture_output=True, text=True)
    assert passed.returncode == 0 and "9.8.7" in passed.stdout
    assert os.path.normcase(str(executable)) in os.path.normcase(passed.stdout)
    executable.write_text(executable.read_text().replace("--sandbox MODE", "--sandbox-mode MODE"))
    refused = subprocess.run(cmd, env=env, capture_output=True, text=True)
    assert refused.returncode == 1 and "--sandbox" in refused.stderr and "9.8.7" in refused.stderr
