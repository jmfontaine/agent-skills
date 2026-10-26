# Agent Skills

The [Agent Skills](https://agentskills.io) I use every day for software development,
product management, and running AI agents. I built them for my own use, so they are
opinionated: they encode my tools, conventions, and workflow. They are not a
general-purpose framework, and I don't plan to accommodate other tools, conventions, or
workflows. They are also a snapshot of a process I keep refining, so expect any skill to
change, including in ways that break how you use it.

I share them so you can adopt the skills whose assumptions fit, adapt them to your own
tools and workflow, or study them as inspiration for your own skills.

## Compatibility

These skills target, in order of priority, [omp](https://omp.sh), Claude, ChatGPT,
Claude Code, and Codex. They follow the
[Agent Skills specification](https://agentskills.io/specification), so other agents
that implement it might run them, but I neither target nor test those. Not every skill
suits every target: `python-codebase-review` and `parallel-issues` are written for omp.

Some skills need more than basic skill support: tools on the machine, a configured
environment, or agent features such as subagents.
[Local setup](docs/workflow.md#local-setup) lists the tools each skill needs, and a
skill that needs a particular agent or environment says so in the `compatibility` field
of its `SKILL.md` frontmatter.

## Available Skills

You can install one skill without the others. The workflow skills refer to each other
for the steps each one owns, so check what a skill relies on before you adopt it alone.
[docs/workflow.md](docs/workflow.md) shows how they fit together, defines the terms they
use, and lists what to set up.

### Standalone

Each works on its own.

- [`project-review`](skills/project-review/SKILL.md): Review project files for
  consistency, completeness, correctness, and simplicity.
- [`python-codebase-review`](skills/python-codebase-review/SKILL.md): Review a whole
  Python codebase with parallel reviewers on a ruff, type checker, and pytest baseline,
  and write a verified, prioritized list of fixes and improvements to `REVIEW.md`.
- [`retro`](skills/retro/SKILL.md): Review recent coding-agent sessions for friction
  and mistakes, trace each to the skill or instruction that allowed it, and propose
  evidence-backed changes for approval.
- [`review-verification`](skills/review-verification/SKILL.md): Check every finding in
  an existing review file against the code or a dependency version, mark each with a
  verdict and evidence, and add what the review missed.
- [`uv`](skills/uv/SKILL.md): Python package management with uv.

### Shared workflow

How I plan products and deliver changes on GitHub. These skills refer to each other and
expect the repository setup the workflow describes.

- [`git-branch`](skills/git-branch/SKILL.md): Git branch naming guidelines:
  `<type>/issue-<N>-<slug>` for issue work and `<type>/<slug>` otherwise, with the
  Conventional Commits type of the change, in every repository.
- [`git-commit`](skills/git-commit/SKILL.md): Git commit guidelines: which branch a
  commit goes on, the first commit, the split check, and GitHub stacked pull requests.
- [`github-workflow`](skills/github-workflow/SKILL.md): Track work in GitHub issues and
  deliver it through pull requests, with agent reviews alongside AI review bots.
- [`product-development-system`](skills/product-development-system/SKILL.md): Guide
  product vision, mapping, briefs, and release review through focused references and
  templates.

### Unattended agents

Builds on the workflow skills and needs the most preparation. Read its
[Before the first run](skills/parallel-issues/SKILL.md#before-the-first-run) section
before installing it.

- [`parallel-issues`](skills/parallel-issues/SKILL.md): Run unattended agents on several
  GitHub issues at once, one Herdr worktree per group, each group delivered as a stack
  of signed, reviewed pull requests.

## Installation

Installing a skill copies its files; it installs none of the tools the skill uses.
Check a skill's prerequisites (see [Compatibility](#compatibility)) before you use it,
and start with the skills you need.

### Coding Agents

Install with the [skills CLI](https://github.com/vercel-labs/skills), which supports
Claude Code, Codex, and
[many other agents](https://github.com/vercel-labs/skills#supported-agents):

```shell
# Choose skills and agents interactively
npx skills add jmfontaine/agent-skills

# Install every skill globally for Claude Code, Codex, and omp (through -a codex)
npx skills add jmfontaine/agent-skills --skill '*' -a claude-code -a codex -g -y

# Update installed skills (asks which scope)
npx skills update

# Update the global install without the prompt
npx skills update -g
```

omp is not an `npx skills` agent target. It loads skills from `~/.agents/skills` and
`.agents/skills`, so include `-a codex`, which writes there for both project and global
installs.

### Claude and ChatGPT

Claude and ChatGPT install skills from uploaded files. Each skill's ZIP must have the
skill folder as its top-level entry. To package every skill into `dist/`, one ZIP per
skill, run [just](https://just.systems):

```shell
git clone https://github.com/jmfontaine/agent-skills.git
cd agent-skills
just package
```

To package a single skill without just:

```shell
cd agent-skills/skills
zip -r ~/Downloads/git-commit.zip git-commit
```

- **Claude:** Go to **Customize → Skills**, click **+**, choose
  **Create skill → Upload a skill**, and select the ZIP. Requires
  **Code execution and file creation** in **Settings → Capabilities**.
- **ChatGPT:** Go to **Plugins → Skills**, click **Create**, choose
  **Upload from your computer**, and select the ZIP or the skill folder. Available on
  Business, Enterprise, Healthcare, and Edu plans.

## Usage

Agents load a skill when a task matches its description. Most agents also let you invoke
a skill by name, such as `/git-commit` in Claude Code.

## Contributing

I share these skills as a look at how I work, not as a project to contribute to.
Questions and ideas are welcome in
[Discussions](https://github.com/jmfontaine/agent-skills/discussions/categories/ideas).
I don't expect pull requests: fork the repository and adapt the skills to your own
workflow instead.

## License

Agent Skills is licensed under the [Apache License 2.0](LICENSE.txt).
