# ChatGPT to Claude Migration Skill

An [Agent Skill](https://agentskills.io) that migrates your entire ChatGPT conversation history into Claude-ready context files, memories, system prompts, and skill suggestions.

It:

1. Processes thousands of conversations in batches using subagents
2. Applies recency weighting so your profile reflects who you are *now*, not a blurred composite of all time periods
3. Fact-checks key findings with you before finalising
4. Recommends MCP servers and integrations based on the tools you actually use
5. Walks you through importing everything into Claude step by step

| File | What you get |
|---|---|
| `claude-profile.md` | Comprehensive "about you" context document for Claude Projects |
| `claude-memories.md` | 30-100+ discrete facts to add to Claude's memory |
| `claude-system-prompt.md` | Ready-to-use custom instructions tailored to you |
| `claude-skills.md` | 3-5 skill suggestions based on your usage patterns |
| `claude-integrations.md` | Recommended MCP servers and integrations to set up |
| `topic-index.md` | Your conversation archive organised by theme |
| `migration-summary.md` | Overview of everything that was processed and found |

## Get started

### Step 1: Export your ChatGPT data

1. Go to [chatgpt.com](https://chatgpt.com) > profile icon (top-right) > **Settings**
2. Click **Data controls** > **Export data** > **Confirm export**
3. Wait for the email from OpenAI with a download link
4. Download the zip and unzip it

**The export can take anywhere from a few minutes to 24 hours.** Most arrive within an hour, but plan ahead in case yours takes longer.

### Step 2: Run the migration

Install the skill (works in both Cowork and Claude Code):

```
npx skills add JamsusMaximus/chatgpt-migrator
```

Then open your unzipped ChatGPT export folder and say "migrate my ChatGPT data". The skill triggers automatically and handles the rest, with progress updates throughout.

This skill requires [Cowork](https://claude.ai/cowork) or [Claude Code](https://claude.ai/code) because it needs file system access to read your export and subagent support to process batches in parallel.

#### Don't have your export yet?

While you wait, you can do an instant partial migration: paste the ChatGPT memory extraction prompt (included in [STANDALONE-PROMPT.md](STANDALONE-PROMPT.md)) into ChatGPT to extract its stored memories, then import the result into Claude via [claude.com/import-memory](https://claude.com/import-memory). The skill will cross-reference these with your full export later.

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

Your export files stay on your machine. Conversation content is sent to Claude for processing, subject to [Anthropic's standard usage policy](https://www.anthropic.com/policies/privacy). No data is sent to any third-party services.

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
- Claude Cowork or Claude Code (file system access and subagent support required)

## License

Apache 2.0. See [LICENSE](LICENSE).
