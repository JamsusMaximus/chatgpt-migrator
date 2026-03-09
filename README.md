# Switch from ChatGPT to Claude

Migrate your entire ChatGPT conversation history to Claude. You get back personalised memories, a custom system prompt, a user profile, skill suggestions, and integration recommendations - all ready to import.

| File | What you get |
|---|---|
| `claude-profile.md` | Comprehensive "about you" context document for Claude Projects |
| `claude-memories.md` | 30-100+ discrete facts to add to Claude's memory |
| `claude-system-prompt.md` | Ready-to-use custom instructions tailored to you |
| `claude-skills.md` | 3-5 skill suggestions based on your usage patterns |
| `claude-integrations.md` | Recommended MCP servers and integrations to set up |
| `topic-index.md` | Your conversation archive organised by theme |
| `migration-summary.md` | Overview of everything that was processed and found |

---

## Quick start (3 steps)

### 1. Export your ChatGPT data

1. Go to [chatgpt.com](https://chatgpt.com) > profile icon (top-right) > **Settings**
2. Click **Data controls** > **Export data** > **Confirm export**
3. Wait for the email from OpenAI (usually under an hour, can take up to 24h)
4. Download the zip and unzip it

### 2. Install the skill in Cowork

You need [Claude Cowork](https://claude.ai/cowork) (Pro/Team/Enterprise). No terminal or coding knowledge required.

**Download this file:** **[chatgpt-migrator.skill](https://github.com/JamsusMaximus/chatgpt-migrator/raw/main/chatgpt-migrator.skill)**

Then upload it:

1. Open [claude.ai/cowork](https://claude.ai/cowork)
2. Click **Skills** in the left sidebar
3. Click **Upload skill**
4. Drag the `chatgpt-migrator.skill` file you just downloaded into the upload box
5. It appears in your skill list - you're done

That's it. No git, no terminal, no npm. One file, one upload.

> [!TIP]
> You can also download the repo as a zip from the green "Code" button on GitHub - just upload the extracted folder in Cowork. The `.skill` file above is simpler though: one file, no unzipping.

### 3. Run the migration

1. In Cowork, open your unzipped ChatGPT export folder
2. Say **"migrate my ChatGPT data"**
3. The skill takes over from here, with progress updates throughout

---

## Don't have your export yet?

While you wait, you can do an instant partial migration: paste the prompt from [STANDALONE-PROMPT.md](STANDALONE-PROMPT.md) into ChatGPT to extract its stored memories, then import the result into Claude via [claude.com/import-memory](https://claude.com/import-memory). The skill will cross-reference these with your full export later.

---

## Using Claude Code instead of Cowork?

<details>
<summary>Click to expand Claude Code instructions</summary>

```bash
git clone https://github.com/JamsusMaximus/chatgpt-migrator.git
cd chatgpt-migrator
```

Then open your ChatGPT export folder and say "migrate my ChatGPT data". The skill is automatically available.

**macOS note:** If you see a popup asking to install Command Line Tools, click **Install**, wait a few minutes, then run the commands above again.

</details>

---

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

---

## Troubleshooting

| Error / problem | Fix |
|---|---|
| "SKILL.md must be in the top-level folder, not nested deeper" | You uploaded a zip or folder where `SKILL.md` isn't at the root level. Try uploading the [chatgpt-migrator.skill](https://github.com/JamsusMaximus/chatgpt-migrator/raw/main/chatgpt-migrator.skill) file instead, or re-extract the repo zip and upload the inner folder. |
| "SKILL.md must start with YAML frontmatter" | You uploaded the wrong file (probably the README). Upload the `.skill` file instead. |
| `npx skills add` doesn't work | That command isn't supported. Upload the `.skill` file in Cowork instead. |
| "The git command requires the command line developer tools" | Click **Install**, wait a few minutes, try again. Or skip the terminal and use the Cowork upload method. |
| Can't find the skill in Cowork's search | This skill isn't in the registry. Upload the `.skill` file manually. |

## Requirements

- A ChatGPT data export ([how to get one](#1-export-your-chatgpt-data))
- Python 3.8+ (for the preprocessor script - already installed on most Macs)
- Claude Cowork or Claude Code (file system access and subagent support required)

## Repo structure

```
chatgpt-migrator.skill      # Upload this to Cowork (self-contained package)
SKILL.md                    # Skill instructions and YAML frontmatter
scripts/
  preprocessor.py           # Compresses the raw export into batches
references/
  batch-analysis-prompt.md
  synthesis-prompt.md
evals/
  evals.json
STANDALONE-PROMPT.md        # Copy-paste prompt for quick partial migration
LICENSE                     # Apache 2.0
README.md                   # This file
```

## License

Apache 2.0. See [LICENSE](LICENSE).
