# Background: why Lumbung exists

## The multi-machine problem

Many developers work across more than one machine — for example a remote Linux dev server or VM, a laptop for daily work, and a desktop workstation for platform-specific or heavier tasks. When Claude Code runs on multiple machines, local configurations drift fast.

## What kept going wrong

**The good agent was always on another machine.** You sit down at one machine and remember an agent that does exactly what you need, only to realize it lives on another machine. Every new agent makes one machine better and leaves the others behind.

**Every new repo wanted its own agents.** A new project, or an existing one that needs help with a recurring task, tends to get its own `.claude/agents/`, even when another repo already has an agent doing the same job. Copying shared reviewers into each repo creates multiple copies to keep in sync, and the drift gets worse with every project.

**No visibility into what was actually used.** Without a record of which agents run, how often, or in which repos, you cannot tell a useful agent from one you wrote once and forgot, so you have no basis for deciding what to keep, merge, or retire.

## What Lumbung aims to provide

- The same agents and skills on every machine, without copying files around by hand.
- One place to look before making a new agent, and a guard that stops you — or Claude — from writing a near copy of one that already exists.
- A record of which agent ran on which machine and in which repo.
- A way to try a new agent on one machine before it shows up everywhere.

## How the design got here

The first idea was to make one central machine the hub and pull from it over SSH. That breaks the moment that machine is unreachable.

Moving the shared kit to a Git remote removed the single-machine dependency: every machine can fetch from `origin`, and work-in-progress agents stay on feature branches so only `master` is shared across machines.

Even then, every machine still needed a manual clone and a Python install script. If setting up the tool that avoids manual copying is itself a chore, it gets skipped.

Claude Code already knows how to install and update plugins from a Git repository. Turning Lumbung into a plugin that is also its own marketplace reduced setup on a new machine to one command in Claude Code and one toggle for auto-update. Claude Code downloads the plugin, keeps it current, and loads its agents, skills, and rules. Python remains only behind the hooks for the duplicate guard and usage log. Trying a new agent on a branch became `claude --plugin-dir`, which affects only that session.

## The name

A *lumbung* is the rice barn that an Indonesian village shares. Each family puts its harvest in and takes from it when needed. Nobody keeps a separate pile, and everyone knows where the rice is.

That is the job here. Agents and skills go into one store, every machine draws from it, and before anyone makes a new one, they look in the barn first.
