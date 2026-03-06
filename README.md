# ChatGPT to Claude Migration Skill

An [Agent Skill](https://agentskills.io) that migrates your entire ChatGPT conversation history into Claude-ready context files, memories, system prompts, and skill suggestions.

It processes thousands of conversations, applies recency weighting (so your profile reflects who you are *now*, not a blurred composite of all time periods), and walks you through importing everything into Claude step by step - including which MCP servers and integrations to set up based on the tools you actually use.

## Before you start: export your ChatGPT data

You'll need a copy of your ChatGPT conversation history. Here's how to get it:

1. Go to [chatgpt.com](https://chatgpt.com)
2. Click your profile icon (top-right) > **Settings**
3. Click **Data controls** in the left sidebar
4. Click **Export data** > **Confirm export**
5. Wait for the email from OpenAI with a download link

**The export can take anywhere from a few minutes to 24 hours.** There's no way to speed it up. Most arrive within an hour, but plan ahead in case yours takes longer.

Once the email arrives, download the zip file and unzip it. You'll see a folder full of `conversations-*.json` files, a `chat.html` file, and various other bits. That's what the skill processes.

## What it produces

| File | Purpose |
|---|---|
| `claude-profile.md` | Comprehensive "about you" context document for Claude Projects |
| `claude-memories.md` | 30-100+ discrete facts to add to Claude's memory |
| `claude-system-prompt.md` | Ready-to-use custom instructions tailored to you |
| `claude-skills.md` | 3-5 Cowork skill suggestions based on your usage patterns |
| `claude-integrations.md` | Recommended MCP servers, connectors, and integrations based on the tools and services you actually use |
| `topic-index.md` | Your conversation archive organised by theme |
| `migration-summary.md` | Overview of everything that was processed and found |

## Two ways to migrate

### Path 1: Install the skill in Cowork or Claude Code (recommended)

This is the best experience. The skill automates the full pipeline: it interviews you about your priorities, preprocesses your export into batches, analyses everything using subagents, synthesises the results, fact-checks key findings with you, and walks you through importing into Claude.

**Install the skill:**

Download the latest `.skill` file from [Releases](../../releases) and install it, or clone and copy:

```bash
git clone https://github.com/yourusername/chatgpt-migrator.git
cp -r chatgpt-migrator/chatgpt-migrator ~/.claude/skills/
```

**Run it:**

1. Open Cowork or Claude Code and select the unzipped export folder
2. Say "migrate my ChatGPT data" (or anything similar - the skill triggers automatically)

That's it. The skill handles everything from there, with progress updates throughout. If you don't have your export yet, the skill will walk you through requesting it from ChatGPT.

### Path 2: Use the standalone prompt in Claude Chat

If you're using Claude Chat (claude.ai) rather than Cowork or Claude Code, you can use the standalone prompt instead. No skill installation needed.

1. Open [STANDALONE-PROMPT.md](STANDALONE-PROMPT.md) and copy the prompt between the `---` lines
2. Start a new Claude conversation with the export folder added as context
3. Paste the prompt

This gives Claude the same instructions as the skill. It works well, but Cowork and Claude Code handle large exports more smoothly because they can use subagents for parallel processing and have direct file system access.

### Quick start: don't have your export yet?

While you wait for your export (which can take up to 24 hours), you can do an instant partial migration. Paste this prompt into ChatGPT to extract its stored memories, then import the result into Claude via [claude.com/import-memory](https://claude.com/import-memory). This captures what ChatGPT explicitly memorised, but misses the deeper patterns the full migration finds. The skill will cross-reference these with your full export later if you've done both.

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
- **Path 1:** Claude Cowork or Claude Code (file system access and subagent support)
- **Path 2:** Claude Chat (claude.ai) with the export folder added as context
- A ChatGPT data export

## License

Apache 2.0. See [LICENSE](LICENSE).
