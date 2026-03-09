# Switch from ChatGPT to Claude

Migrate your entire ChatGPT conversation history to Claude. The skill analyses everything you've discussed with ChatGPT and creates:

- A **personal profile** so Claude knows who you are from day one
- **Memories** pulled from your conversations (30-100+ facts about you)
- **Custom instructions** tailored to how you like to work
- A **topic index** of everything you've talked about, organised by theme
- **Skill and integration suggestions** based on what you actually use AI for

Everything is ready to import into Claude when it's done.

---

## What you get

| Output | What's in it |
|---|---|
| **Personal profile** | A comprehensive "about you" document covering who you are, what you do, your interests, communication style, and key life context. Add it to a Claude Project or keep it in a folder Cowork can access, and Claude has your full context from the first message. |
| **Memories** | 30-100+ discrete facts extracted from your conversations, ready to add to Claude's memory. Job title, location, preferences, current projects, personal details - each one a single, specific, useful fact. |
| **Custom instructions** | A tailored system prompt you can paste straight into Claude's settings. Encodes your communication preferences, key context, and specific instructions so Claude works the way you like from day one. |
| **Skill suggestions** | 3-5 custom Cowork skills based on how you actually used ChatGPT. Each includes a name, what it would do, why it suits you, and enough detail to build it. Weekly reporting, data analysis, content drafting - your patterns become purpose-built skills. |
| **Integrations & MCP servers** | Personalised recommendations for official MCP servers and Claude connectors based on the tools in your ChatGPT history. Google Workspace, GitHub, Slack, Notion, Figma, Todoist, databases, and more - but only the ones that match your actual usage. Each recommendation explains what it is, why it's relevant to you, and what it enables. |
| **Topic index** | Your entire conversation archive organised by theme. For each topic: a brief description, how many conversations touched on it, the date range, and the most notable conversation titles. |
| **Migration summary** | Overview of what was processed, what was found, and suggestions for next steps. The first thing you'll read when the migration finishes. |

---

## Get started

### Step 1: Request your ChatGPT export

1. Go to [chatgpt.com](https://chatgpt.com) and click your profile icon (top-right corner)
2. Click **Settings**
3. Click **Data controls**, then **Export data**, then **Confirm export**
4. OpenAI will email you a download link (usually within an hour, sometimes up to 24 hours)
5. When the email arrives, download the zip file and unzip it somewhere you can find it

> [!TIP]
> While you wait for the export, you can do a quick partial migration right now. See [Don't have your export yet?](#dont-have-your-export-yet) below.

### Step 2: Install the skill

You need a Claude Pro, Team, or Enterprise plan.

1. **[Click here to download the skill file](https://github.com/JamsusMaximus/chatgpt-migrator/raw/main/chatgpt-migrator.skill)** - your browser will save a file called `chatgpt-migrator.skill`
2. Open the Claude desktop app
3. Go to **Settings** > **Customize** > **Skills**
4. Click **Upload skill**
5. Drag the `chatgpt-migrator.skill` file from your Downloads folder into the upload area
6. You'll see it appear in your skills list - that's it, it's installed

### Step 3: Run the migration

1. In Cowork, start a new session
2. Add your unzipped ChatGPT export folder to the session (drag the folder in, or use the attachment button)
3. Type **"migrate my ChatGPT data"** and press enter
4. The skill walks you through everything from here, with progress updates along the way

It will ask you a few questions about what you want to focus on, then process your conversations. When it's done, it helps you import everything into Claude.

---

## Don't have your export yet?

You can do a quick partial migration while you wait:

1. Open [STANDALONE-PROMPT.md](STANDALONE-PROMPT.md) and copy the entire prompt
2. Paste it into a new ChatGPT conversation and send it
3. ChatGPT will output a block of memories - copy the whole response
4. Go to [claude.com/import-memory](https://claude.com/import-memory) and paste it in

This grabs what ChatGPT has memorised about you so far. When your full export arrives, the skill will cross-reference and build on these.

---

## How long does it take?

| Export size | Estimated time |
|---|---|
| Under 200 conversations | 10-15 minutes |
| 200-800 conversations | 20-30 minutes |
| 800-1500 conversations | 30-45 minutes |
| 1500+ conversations | 45-60 minutes |

You get progress updates throughout. If a session runs out of context, start a new one and say **"continue"** - it picks up where it left off.

## Privacy

Your files stay on your machine. Conversation content is sent to Claude for processing, subject to [Anthropic's privacy policy](https://www.anthropic.com/legal/privacy). Nothing is sent to any third-party services.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| The skill file opened in my browser instead of downloading | Right-click the [download link](https://github.com/JamsusMaximus/chatgpt-migrator/raw/main/chatgpt-migrator.skill) and choose **Save link as...** or **Download linked file** |
| Cowork says the skill file is invalid or can't read it | Make sure you're uploading the `.skill` file, not the README or a zip of this page. Re-download it from the [link in Step 2](#step-2-install-the-skill) |
| The session ran out before finishing | Start a new Cowork session, add the same export folder, and say **"continue"** |
| Can't find the skill in Cowork's search | This skill isn't in the public registry. Install it by uploading the file as described in [Step 2](#step-2-install-the-skill) |

---

<details>
<summary>Using Claude Code instead of Cowork?</summary>

```bash
git clone https://github.com/JamsusMaximus/chatgpt-migrator.git
cd chatgpt-migrator
```

Then open your ChatGPT export folder and say "migrate my ChatGPT data". The skill is automatically available.

**macOS note:** If you see a popup asking to install Command Line Tools, click **Install**, wait a few minutes, then run the commands above again.

</details>

<details>
<summary>Developer information</summary>

### Requirements

- A ChatGPT data export ([how to get one](#step-1-request-your-chatgpt-export))
- Python 3.8+ (for the preprocessor script - install via [python.org](https://www.python.org/downloads/) if you don't have it)
- Claude Cowork or Claude Code

### Repo structure

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

### How the pipeline works

1. **Identify** the export and check for any previous progress
2. **Interview** you about scope, priorities, and target platform
3. **Preprocess** the raw export into batches (a Python script handles this in under a minute)
4. **Analyse** each batch in parallel using subagents (waves of 3-5 at a time)
5. **Synthesise** all analyses into the final output files
6. **Fact-check** up to 10 key facts with you, then walk you through importing into Claude

Progress is saved to `progress.json` after every step.

</details>

## Licence

Apache 2.0. See [LICENSE](LICENSE).
