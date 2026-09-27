# Agent Skills

A collection of [Agent Skills](https://agentskills.io) for Claude Code, Claude, ChatGPT, Codex, omp, and any other agent that supports the format. I built these for my own use, but they might help you, either to use directly or as inspiration for your own skills.

## Available Skills

- [git-branch](skills/git-branch/SKILL.md): Git branch naming guidelines based on Conventional Branch.
- [git-commit](skills/git-commit/SKILL.md): Git commit guidelines based on Conventional Commits.
- [project-review](skills/project-review/SKILL.md): Review project files for consistency, completeness, and correctness.
- [uv](skills/uv/SKILL.md): Python package management with uv.

## Installation

### Coding Agents

Install with the [skills CLI](https://github.com/vercel-labs/skills), which supports Claude Code, Codex, and [many other agents](https://github.com/vercel-labs/skills#supported-agents):

```shell
# Choose skills and agents interactively
npx skills add jmfontaine/agent-skills

# Install all skills globally for Claude Code and Codex
npx skills add jmfontaine/agent-skills --skill '*' -a claude-code -a codex -g -y

# Update installed skills
npx skills update
```

omp is not an `npx skills` agent target. It loads skills from `~/.agents/skills` and `.agents/skills`, so include `-a codex`, which writes there for both project and global installs.

### Claude and ChatGPT

Claude and ChatGPT install skills from uploaded files. Zip the skill folder so that it is the top-level entry of the archive:

```shell
git clone https://github.com/jmfontaine/agent-skills.git
cd agent-skills/skills
zip -r ~/Downloads/git-commit.zip git-commit
```

- **Claude:** Go to **Customize → Skills**, click **+**, choose **Create skill → Upload a skill**, and select the ZIP. Requires **Code execution and file creation** in **Settings → Capabilities**.
- **ChatGPT:** Go to **Plugins → Skills**, click **Create**, choose **Upload from your computer**, and select the ZIP or the skill folder. Available on Business, Enterprise, Healthcare, and Edu plans.

## Usage

Agents load a skill when a task matches its description. Most agents also let you invoke a skill by name, such as `/git-commit` in Claude Code.

## License

Agent Skills is licensed under the [Apache License 2.0](LICENSE.txt).
