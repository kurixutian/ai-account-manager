# AI Manager

This local tool creates configuration for multiple AI agent profiles. It can share all skills, selected skills, or keep skills separate. It records provider-reported quota status and reset timestamps, then skips profiles marked exhausted when selecting a launch target.

## Installation by environment

Replace `YOUR_USERNAME` with the GitHub account that owns the repository.

### Debian, Ubuntu, and WSL

For a global `ai-manager` command, use `pipx`:

```bash
sudo apt update
sudo apt install pipx
pipx ensurepath
pipx install git+https://github.com/YOUR_USERNAME/ai-account-manager.git
```

Open a new terminal after `pipx ensurepath`, then run:

```bash
ai-manager setup
```

If `pipx` is unavailable, use the virtual-environment method below.

### Fedora

```bash
sudo dnf install python3-pip python3-virtualenv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install git+https://github.com/YOUR_USERNAME/ai-account-manager.git
ai-manager setup
```

### Arch Linux

```bash
sudo pacman -S python python-pip
python -m venv .venv
source .venv/bin/activate
python -m pip install git+https://github.com/YOUR_USERNAME/ai-account-manager.git
ai-manager setup
```

### macOS with Homebrew

```bash
brew install python pipx
pipx ensurepath
pipx install git+https://github.com/YOUR_USERNAME/ai-account-manager.git
```

Open a new terminal, then run:

```bash
ai-manager setup
```

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install git+https://github.com/YOUR_USERNAME/ai-account-manager.git
ai-manager setup
```

If PowerShell blocks activation, run this once for the current user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Cloned repository on any operating system

```bash
cd ai-account-manager
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
ai-manager setup
```

On Windows PowerShell, replace the activation line with:

```powershell
.\.venv\Scripts\Activate.ps1
```

Do not use `--break-system-packages` unless you deliberately accept the risk of modifying the OS-managed Python installation. Do not copy credentials into this repository.

Use `setup --dry-run` to preview changes. Add profiles with `add NAME`; remove them with `remove NAME`; and change sharing with `policy all`, `policy selected --path PATH --skills NAME`, or `policy separate`.

Quota checks may be supplied as a provider adapter or an explicit local command that prints JSON such as `{"status":"available","remaining":5,"reset_at":"2026-12-02T09:00:00+08:00"}`. Unknown data is reported as unknown. Configure launch commands manually in the JSON file as argument arrays.

The tool does not create online accounts, log in, bypass authentication, or handle credentials. Configure secrets through the AI provider's own supported mechanism.
