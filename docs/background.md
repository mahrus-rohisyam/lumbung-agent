# Background: why I built Lumbung

## How I work

Most of my development happens on one VM. My laptop and my PC usually connect to it, and the actual work runs there. I like it that way: one place, one set of tools, everything in sync without thinking about it.

The VM does not cover everything, though:

1. **Its resources are limited.** Some jobs are too heavy for it, so I run them locally.
2. **My main day-to-day work is on the laptop:** reports and marketing.
3. **I build Windows apps on the PC,** and that has to happen on Windows.

So I end up using Claude Code on three machines, not one.

## What kept going wrong

**The good agent was always on the other machine.** I would sit at the PC and remember there was an agent that did exactly what I needed, but it lived on the VM. Or I would be on the VM and the one I wanted was on the laptop. "Ah, the good agent is on the VM" became a small, regular annoyance. Every agent I wrote made one machine better and left the other two as they were.

**Every new repo wanted its own agents.** A new project, or an old one that needed help with something new, tended to get its own `.claude/agents/`, even when another repo already had an agent that did the same job. The shared reviewers were already copied into several repos by a sync script. One more repo meant one more copy, and one more copy to keep up to date. It was getting redundant, and it would only get worse with each project.

**I could not see what was actually used.** I had no record of which agents ran, how often, or where. I could not tell a useful agent from one I wrote once and forgot, so I had no basis for deciding what to keep, merge or delete.

## What I wanted

- The same agents and skills on every machine, without copying files around by hand.
- One place to look before making a new agent, and something that stops me, or Claude, from writing a near copy of one that already exists.
- A record of which agent ran on which machine and in which repo.
- A way to try a new agent on one machine before it shows up everywhere.

## How the design got here

The first idea was to make the VM the hub: everything lives there, and the laptop and PC pull from it over SSH. That matched how I already work. It also meant that the moment I was away from the VM, or the VM was down, syncing stopped.

Then the obvious question: why not just put it in git? A git remote is something every machine can reach without depending on the VM. The code was changed so each machine only talks to its `origin` remote. Today that is the VM; moving to a private GitHub or GitLab repo is a one-line change per machine. Usage logs went on their own branch for the same reason: no service to run, nothing that has to be reachable.

The last question was about agents still in development. If every machine follows the repo, a half-finished agent would spread everywhere the moment I committed it. So only `master` is shared. New work happens on a branch, on one machine, and reaches the others only when I merge it.

## The name

A *lumbung* is the rice barn that an Indonesian village shares. Each family puts its harvest in and takes from it when needed. Nobody keeps a separate pile, and everyone knows where the rice is.

That is the job here. Agents and skills go into one store, every machine draws from it, and before anyone makes a new one, they look in the barn first.
