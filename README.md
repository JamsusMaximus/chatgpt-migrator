# ChatGPT to Claude Migration Skill

An [Agent Skill](https://agentskills.io) that migrates your entire ChatGPT conversation history into Claude-ready context files, memories, system prompts, and skill suggestions.

It processes thousands of conversations, applies recency weighting (so your profile reflects who you are *now*, not a blurred composite of all time periods), and walks you through importing everything into Claude step by step.

## What it produces

| File | Purpose |
|---|---|
| `claude-profile.md` | Comprehensive "about you" context document for Claude Projects |
| `claude-memories.md` | 30-100+ discrete facts to add to Claude's memory |
| `claude-system-prompt.md` | Ready-to-use custom instructions tailored to you |
| `claude-skills.md` | 3-5 Cowork skill suggestions based on your usage patterns |
| `topic-index.md` | Your conversation archive organised by theme |
| `migration-summary.md` | Overview of everything that was processed and found |

## Two migration paths

**Path 1 (Quick Start, 5 minutes):** Paste a prompt into ChatGPT to extract its stored memories, then import them into Claude via [claude.com/import-memory](https://claude.com/import-memory). No data export needed.

**Path 2 (Deep Migration, 20-60 minutes):** Process your full ChatGPT export. This is what the skill automates. It finds everything ChatGPT's memory feature missed: patterns in how you work, professional context from conversations, preferences you never explicitly stated, and the full arc of your interests over time.

You can do Path 1 immediately and Path 2 later when your export arrives. The skill handles both and will cross-reference them if you've done both.

## Install

### As a Cowork/Claude Code skill

Download the latest `.skill` file from [Releases](../../releases) and install it, or clone and copy:

```bash
git clone https://github.com/yourusername/chatgpt-migrator.git
cp -r chatgpt-migrator/chatgpt-migrator ~/.claude/skills/
```

### Without installing

If you don't want to install the skill, you can use the standalone prompt instead. See [STANDALONE-PROMPT.md](STANDALONE-PROMPT.md) for a copy-paste prompt that gives Claude the same instructions.

## Usage

### With the skill installed

1. Export your ChatGPT data: ChatGPT > Settings > Data controls > Export data
2. Download and unzip the export when the email arrives (can take up to 24 hours)
3. Open Cowork or Claude Code and select the unzipped folder
4. Say "migrate my ChatGPT data" (or anything similar; the skill triggers automatically)

The skill handles everything from there: it interviews you about your priorities, preprocesses the export, analyses it in batches, synthesises the results, fact-checks key findings with you, and walks you through importing into Claude.

### Without the skill

1. Follow the same export steps above
2. Open the [standalone prompt](STANDALONE-PROMPT.md) and copy the prompt between the `---` lines
3. Paste it into a new Claude conversation with the export folder selected

### Don't have your export yet?

The skill handles this too. If you trigger it without an export in your folder, it'll walk you through exporting from ChatGPT and offer the quick Path 1 migration while you wait.

## How it works

The pipeline has six stages:

1. **Identify** the export and check for any previous progress
2. **Interview** you about scope, priorities, and target platform
3. **Preprocess** the raw export into batches (a Python script handles this in under a minute)
4. **Analyse** each batch in parallel using subagents (waves of 3-5 at a time, with progress updates)
5. **Synthesise** all analyses into the final output files
6. **Fact-check** up to 10 key facts with you, then walk you through importing into Claude

The pipeline saves its progress to `progress.json` after every step. If the session runs out of context mid-way through, start a new session and say "continue" to pick up where it left off.

## How long does it take?

| Export size | Batches | Estimated time |
|---|---|---|
| Under 200 conversations | 3-5 | 10-15 minutes |
| 200-800 conversations | 8-15 | 20-30 minutes |
| 800-1500 conversations | 15-25 | 30-45 minutes |
| 1500+ conversations | 25-40 | 45-60 minutes |

You get regular progress updates throughout. After preprocessing, the skill gives you a precise estimate based on your actual batch count.

## Privacy

Everything runs locally. Your data stays on your machine and is processed by Claude in your session. Nothing is uploaded or stored externally.

## Repo structure

```
chatgpt-migrator/           # The skill (Agent Skills format)
  SKILL.md                  # Skill instructions and frontmatter
  scripts/
    preprocessor.py         # Python script that compresses the raw export into batches
  references/
    batch-analysis-prompt.md  # Prompt template for analysing each batch
    synthesis-prompt.md       # Prompt template for final synthesis
  evals/
    evals.json              # Test cases for the skill
STANDALONE-PROMPT.md        # Copy-paste prompt for users who don't install the skill
LICENSE                     # Apache 2.0
README.md                   # This file
```

## Requirements

- Python 3.8+ (for the preprocessor script)
- Claude with file system access and subagent support (Cowork or Claude Code)
- A ChatGPT data export (or just a ChatGPT account for Path 1)

## License

Apache 2.0. See [LICENSE](LICENSE).
