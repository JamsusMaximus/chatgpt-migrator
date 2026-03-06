# ChatGPT to Claude Migration Skill

An [Agent Skill](https://agentskills.io) that migrates your entire ChatGPT conversation history into Claude-ready context files, memories, system prompts, and skill suggestions.

It processes thousands of conversations, applies recency weighting (so your profile reflects who you are *now*, not a blurred composite of all time periods), and walks you through importing everything into Claude step by step - including which MCP servers and integrations to set up based on the tools you actually use.

## Get started

### Step 1: Export your ChatGPT data

1. Go to [chatgpt.com](https://chatgpt.com) > profile icon (top-right) > **Settings**
2. Click **Data controls** > **Export data** > **Confirm export**
3. Wait for the email from OpenAI with a download link
4. Download the zip and unzip it

**The export can take anywhere from a few minutes to 24 hours.** Most arrive within an hour, but plan ahead in case yours takes longer.

### Step 2: Run the migration

#### Option A: Cowork or Claude Code (recommended)

Install the skill:

```bash
git clone https://github.com/JamsusMaximus/chatgpt-migrator.git
cp -r chatgpt-migrator/chatgpt-migrator ~/.claude/skills/
```

Then open Cowork or Claude Code, select the unzipped export folder, and say "migrate my ChatGPT data". The skill triggers automatically and handles the rest, with progress updates throughout.

This is the recommended path because Cowork and Claude Code can use subagents for parallel processing and have direct file system access, which makes large exports much smoother.

#### Option B: Claude Chat (standalone prompt)

If you're using Claude Chat (claude.ai), no skill installation needed:

1. Open [STANDALONE-PROMPT.md](STANDALONE-PROMPT.md) and copy the prompt between the `---` lines
2. Start a new Claude conversation with the export folder added as context
3. Paste the prompt

This gives Claude the same instructions as the skill. It works well for smaller exports.

#### Don't have your export yet?

While you wait, you can do an instant partial migration: paste the ChatGPT memory extraction prompt (included in [STANDALONE-PROMPT.md](STANDALONE-PROMPT.md)) into ChatGPT to extract its stored memories, then import the result into Claude via [claude.com/import-memory](https://claude.com/import-memory). The skill will cross-reference these with your full export later.

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

- A ChatGPT data export ([how to get one](#step-1-export-your-chatgpt-data))
- Python 3.8+ (for the preprocessor script)
- Claude Cowork or Claude Code (recommended), or Claude Chat for the standalone prompt

## License

Apache 2.0. See [LICENSE](LICENSE).
