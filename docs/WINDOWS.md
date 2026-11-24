# Native Windows

Use PowerShell with Node 22, pnpm 9.0.0, Python 3.11 and Git for Windows.
Git Bash runs the checked-in shell scripts. Keep research projects outside
the checkout.

## Install from source

From the checkout, select Node 22 and run:

```powershell
py -3.11 -m venv "$env:LOCALAPPDATA\Nullius\python"
$env:NULLIUS_PYTHON = "$env:LOCALAPPDATA\Nullius\python\Scripts\python.exe"
& $env:NULLIUS_PYTHON --version
corepack pnpm install --frozen-lockfile
& $env:NULLIUS_PYTHON -m pip install -r meta/scripts/codegen-requirements.txt pytest pyyaml pydantic uv
corepack pnpm -r build
.\scripts\install-windows-runtime.ps1 -PythonPath $env:NULLIUS_PYTHON -Persist
nullius --help
nullius runtime path
```

The installer backs up and replaces existing `nullius.ps1` and `nullius.cmd`
entries in `~/.local/bin` and adds a Git Bash `python3` bridge. `-Persist` saves
the Python path and appends the required directories to the user PATH. Restart
GUI agent clients to pick up the user environment. Use `-BinDir` without
`-Persist` to test in a separate bin directory.

Use `nullius` or the `.ps1` launcher in PowerShell and `.cmd` in cmd.exe.
For raw byte streams, run the built CLI or the project-local `nullius.cjs`
directly with Node. MCP hosts can launch the built CLI with an absolute Node
path and the arguments `runtime mcp <server>`.

Memory-graph execution requires `sqlite3.exe`. Install Graphviz for SVG or PNG
graph rendering. Project MCP PDF reading requires Poppler (`pdfinfo.exe` and
`pdftotext.exe`, plus `pdftoppm.exe` for page images).

## Initialize or reconnect a project

```powershell
$project = Join-Path $env:LOCALAPPDATA 'Nullius\example-project'
nullius init --project-root $project --mode engine
& "$project\.nullius\bin\nullius.ps1" status --json
nullius init --project-root $project --runtime-only
& "$project\.nullius\bin\nullius.ps1" status --json
```

Use `--mode file` for a file-mode project. Runtime-only refresh repairs the
handshake and launchers while preserving authored files and historical runs.

## Install or refresh skills

The installer bundles Windows helpers with the skills that use them. Preview
the Codex install from the checkout:

```powershell
$skillRoot = Join-Path $env:USERPROFILE '.agents\skills'
& $env:NULLIUS_PYTHON .\packages\skills-market\scripts\install_skill.py --platform codex --source-root (Get-Location).Path --target-root $skillRoot --package research-harness --dry-run
```

Remove `--dry-run` to install. For Claude Code, use `--platform claude_code`
and omit `--target-root`. Compare and back up customized copies before using
`--force`. Check the host's skill list for existing copies with the same names.

## Platform limits

Atomic writes on local NTFS flush file contents before replacement. Parent
directory fsync durability applies to POSIX. Protected contract writes
validate file identity and preserve ACLs. Windows Job Objects
control transient process lifetimes and give durable deliveries separate
ownership across transport disconnects.

Independent reproduction uses Git for Windows `sh.exe`. Worktree inputs with
committed symbolic links require Windows symlink support. Scratch cleanup with
`run_storage.py closeout` requires POSIX.

Run `corepack pnpm codegen:check` with Git Bash and the selected Python Scripts
directory on PATH. The Windows CI job covers the native runtime.
