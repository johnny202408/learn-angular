# Appendix A. Setting up your machine

This appendix collects the platform-specific setup Chapter 4 pointed you to. Read only the sections that apply to your operating system. Come back for troubleshooting.

## What you need, at a glance

- **Node.js 20 or later.** Angular refuses to install on older versions.
- **npm 10 or later.** Ships with Node.js.
- **The Angular CLI.** Installed globally via npm.
- **A code editor.** Visual Studio Code is recommended and free.
- **Git.** For version control; often preinstalled.
- **A terminal.** Any modern terminal application.

## macOS

**Node.js.** Two good options:

1. Download the LTS installer from `nodejs.org` and run it. This installs `node` and `npm` at `/usr/local/bin` (Intel) or `/opt/homebrew/bin` (Apple Silicon).
2. Use Homebrew: `brew install node`. Homebrew's install matches your architecture automatically.

Verify:

```bash
node --version
npm --version
```

**Angular CLI.**

```bash
npm install --global @angular/cli
ng version
```

**Editor.** Install Visual Studio Code from `code.visualstudio.com`. After install, open Terminal and run `code --version` — if it isn't found, open VS Code and use Command Palette → "Shell Command: Install 'code' command in PATH".

**Git.** `xcode-select --install` installs the Command Line Tools, which include git. Or `brew install git`.

## Windows

**Node.js.** Download the LTS `.msi` installer from `nodejs.org` and run it. Accept the default options. It installs Node.js and npm and adds them to your PATH.

Open a new PowerShell or Windows Terminal window (not one from before the install — PATH updates only affect new sessions). Verify:

```powershell
node --version
npm --version
```

**Angular CLI.**

```powershell
npm install --global @angular/cli
ng version
```

If you get an execution policy error running `ng`, run PowerShell as administrator and set:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Editor.** Install Visual Studio Code from `code.visualstudio.com`. The installer offers an "Add to PATH" checkbox — leave it checked.

**Git.** Install Git for Windows from `git-scm.com`. Accept the defaults, but on the "Adjusting your PATH environment" screen, choose "Git from the command line and also from 3rd-party software."

**A terminal.** Install Windows Terminal from the Microsoft Store if it isn't already there. It handles PowerShell, cmd, and Git Bash gracefully.

## Linux (Ubuntu / Debian / similar)

**Node.js.** The distro-packaged Node.js is often too old. Use NodeSource:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs
node --version
npm --version
```

Or use nvm (Node Version Manager):

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
# reopen your terminal
nvm install 20
nvm use 20
```

nvm is the better choice long-term because it lets you switch Node versions per project.

**Angular CLI.**

```bash
npm install --global @angular/cli
ng version
```

If you installed Node globally without nvm, you may need `sudo`:

```bash
sudo npm install --global @angular/cli
```

Better: configure npm to install globals in your home directory:

```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
# then add ~/.npm-global/bin to your PATH
```

**Editor.** VS Code has `.deb` and `.rpm` packages at `code.visualstudio.com`, or install via Snap: `sudo snap install code --classic`.

**Git.** Almost always preinstalled. If not: `sudo apt install git`.

## Recommended VS Code extensions

None are strictly required, but these make working with Angular much nicer:

- **Angular Language Service** (official Angular team) — inline errors and autocomplete in templates.
- **ESLint** — surfaces lint issues in the editor.
- **Prettier** — auto-formats code on save.
- **GitLens** — line-level git blame and history.
- **Path Intellisense** — autocompletes import paths.

Install via Extensions panel or `code --install-extension <id>`.

## Troubleshooting

**"`ng` is not recognized" / "command not found."**

npm installed the CLI but your PATH doesn't include npm's global bin directory. Reopen your terminal first. If still failing:

```bash
npm config get prefix
```

Add the returned path's `bin` subdirectory to your PATH (in `~/.zshrc`, `~/.bashrc`, or your shell's config).

**Node version too old.**

You installed Node ages ago and Angular now needs a newer one. On Windows/macOS run the LTS installer again; it upgrades. On Linux, use nvm as described above.

**Long install times.**

`ng new` downloads a lot of packages the first time. On slow connections this can take five minutes. Subsequent projects share npm's cache and are faster.

**"EACCES" errors from npm.**

You are trying to install a global package without permission. Either use `sudo` (Linux; macOS with system Node), configure npm's prefix to your home directory (better), or use nvm (best).

**Corporate proxy or firewall.**

`npm` respects the environment variables `HTTP_PROXY` and `HTTPS_PROXY`. If your workplace requires them, set them in your shell config. Some corporate firewalls block Node's certificate lookups; ask your IT team for the internal cert bundle and set `NODE_EXTRA_CA_CERTS`.

**HMR / dev server won't hot-reload.**

Some file systems (Windows shared drives, some Docker mounts) don't notify Node of changes. Try `ng serve --poll=1000` (polls every second). Slower but reliable.

**Antivirus slows every build to a crawl (Windows).**

Add your project folder and `%APPDATA%\npm-cache` to your antivirus exclusions. Do not disable antivirus.

**"Cannot find module" after `git pull`.**

Someone else added a dependency. Run `npm install` to pick it up.

**Port 4200 is already in use.**

Another `ng serve` is running, or another process took the port. `ng serve --port 4201`. Find and kill the process: on macOS/Linux `lsof -i :4200`; on Windows `netstat -ano | findstr 4200` and `taskkill /PID <id>`.

## A minimum quality-of-life setup

If you are new to shell environments, spend fifteen minutes on these once:

- Use an editor with syntax highlighting for TypeScript. (VS Code has it out of the box.)
- Turn on "format on save" so your code is uniformly indented and quoted.
- Use a terminal with pretty colors (Windows Terminal, iTerm2, GNOME Terminal). Reading long stack traces in monochrome is unpleasant.
- Learn your editor's file-navigation shortcut. In VS Code: Cmd/Ctrl+P → type a filename fragment. This alone doubles your speed in a large project.

## Node versions across projects

Once you have two Angular projects on your machine, they may target different Node versions. `nvm` is the cleanest solution: put a `.nvmrc` file in each project (`echo 20 > .nvmrc`), and `nvm use` picks up the right version automatically.

Windows has `nvm-windows`. macOS/Linux use `nvm-sh`. Both work; both integrate well with VS Code.
