---
name: chatgpt-migrator
description: "Migrate from ChatGPT to Claude by analysing a ChatGPT data export. Use this skill whenever a user mentions ChatGPT export, ChatGPT history, ChatGPT migration, switching from ChatGPT, importing ChatGPT data, or drops a folder containing conversations-*.json files. Also trigger if the user has a folder with chat.html and conversations JSON files, even if they don't explicitly say 'ChatGPT'. This skill handles the full pipeline: interviewing the user about their priorities, preprocessing the massive export into manageable batches, analysing conversation themes and patterns, and producing Claude-ready context files, system prompts, memories, and skills."
license: Apache-2.0
compatibility: "Requires Python 3.8+. Works with Claude Code, Cowork, or any Claude environment with file system access and subagent support."
metadata:
  author: jddmcaulay
  version: "1.0.0"
---

# ChatGPT to Claude Migration Tool

You are running a migration pipeline that turns a user's ChatGPT conversation history into useful Claude artefacts. The export can be enormous (hundreds of megabytes, thousands of conversations), so the process is designed to work within context window limits through a multi-stage pipeline.

This skill is fully self-contained. It walks the user through every step from start to finish, including verifying the output with them and showing them exactly how to import everything into Claude.

## Two Migration Paths

Users may arrive via two different routes:

**Path 1 (Quick Start)**: They pasted a prompt into ChatGPT to extract its stored memories, then imported those into Claude via claude.com/import-memory or by manually adding them. This is fast but only captures what ChatGPT explicitly memorised, which is typically a small, biased subset.

**Path 2 (Deep Migration)**: They exported their full ChatGPT data and want you to process it. This is what the rest of this skill handles.

Many users will do Path 1 first and then come to Path 2 later when their data export arrives (it can take up to 24 hours). In this case, they already have Claude memories from Path 1. The interview stage (Question 5) will detect this and the synthesis stage will cross-reference the Path 1 memories with the deep analysis results, enriching rather than duplicating.

## Before You Begin

Read the reference files in this skill's directory to understand the batch analysis prompts and output formats:
- `references/batch-analysis-prompt.md` - The prompt used to analyse each batch
- `references/synthesis-prompt.md` - The prompt used for final synthesis
- `scripts/preprocessor.py` - The Python preprocessor that compresses the raw export

## Time Estimates

Processing time depends on the size of the export. Share these estimates with the user early and give regular updates throughout:

| Export size | Batches | Estimated time |
|---|---|---|
| Small (under 200 conversations) | 3-5 batches | 10-15 minutes |
| Medium (200-800 conversations) | 8-15 batches | 20-30 minutes |
| Large (800-1500 conversations) | 15-25 batches | 30-45 minutes |
| Very large (1500+ conversations) | 25-40 batches | 45-60 minutes |

These estimates assume batch analysis is the bottleneck (it is). Preprocessing takes under a minute regardless of size. Synthesis takes 2-5 minutes. The fact-checking interview and import walkthrough add another 5-10 minutes at the end.

After preprocessing, you'll know the exact batch count. Recalculate and share a more precise estimate at that point: roughly **1.5-2 minutes per batch** when processing in waves of 3-5.

## Progress Tracking (Compaction Resilience)

Large exports can take a long time to process, and sessions may hit context limits mid-run. To handle this, the pipeline maintains a `progress.json` file in the migration-workspace that tracks exactly where things stand. This is the first file you should check when starting work.

**At the very start of every session**, look for `<export-folder-path>/migration-workspace/progress.json`. If it exists, read it and resume from wherever the pipeline left off. If it doesn't exist, start from Stage 0.

The progress file has this structure:

```json
{
  "current_stage": 3,
  "stage_name": "batch_analysis",
  "export_path": "/path/to/export",
  "skill_path": "/path/to/skill",
  "interview": {
    "scope": "everything",
    "priority": "understand_me",
    "target": "all_platforms",
    "claude_experience": "few_months",
    "claude_memories_provided": true
  },
  "preprocessing": {
    "completed": true,
    "total_batches": 22,
    "batch_files": ["batch-001-deep.json", "batch-002-deep.json", "..."]
  },
  "batch_analysis": {
    "completed_batches": ["batch-001-deep.json", "batch-002-deep.json"],
    "pending_batches": ["batch-003-deep.json", "batch-004-medium.json", "..."],
    "failed_batches": []
  },
  "synthesis": {
    "completed": false,
    "files_produced": []
  },
  "fact_check": {
    "completed": false,
    "facts_presented": [],
    "facts_kept": [],
    "facts_discarded": [],
    "corrections": []
  },
  "last_updated": "2026-03-06T14:30:00Z"
}
```

**Update this file after every meaningful step**: after the interview, after preprocessing, after each wave of batch analysis completes, after synthesis, after the fact-check interview. Write it with `json.dumps(..., indent=2)` so it's human-readable.

When resuming:
- **Stage 0-1 complete**: Skip straight to preprocessing or batch analysis
- **Mid batch analysis**: Check which `analysis-NNN.json` files already exist in the migration-workspace. Any batch with a corresponding analysis file is done. Process only the remaining batches.
- **All batches done**: Jump to synthesis
- **Synthesis done**: Jump to fact-checking interview
- **Fact-check done**: Jump to delivery and import walkthrough

This means the user can hit compaction, start a new session, say "continue the migration", and the skill will pick up right where it left off without re-processing anything or re-asking interview questions.

## Stage 0: Check for Existing Progress, Then Identify the Export

First, check if `migration-workspace/progress.json` exists in the workspace. If it does, read it and skip to whatever stage is indicated. If the user says something like "continue", "keep going", or "pick up where we left off", this is your cue to look for the progress file.

If no progress file exists, look in the user's workspace folder for signs of a ChatGPT export. The telltale files are:
- `conversations-000.json`, `conversations-001.json`, etc. (the actual conversation data)
- `chat.html` (an HTML rendering of all conversations, not needed for processing)
- `user.json` (basic account info)
- `user_settings.json` (settings and preferences)
- `export_manifest.json` (file listing)
- Various UUID-named folders (conversation attachments)

If you find these files, confirm with the user that this is their ChatGPT export and move to Stage 1.

### If the export files aren't found

The user might not have their export yet, or they might have selected the wrong folder. Handle this warmly and practically. Use AskUserQuestion to ask:

**"I can't see a ChatGPT export in this folder. Where are you in the process?"**
- I haven't exported my data yet (show me how)
- I've exported it but it's in a different folder
- I'm waiting for the export email from ChatGPT
- I just want to do the quick migration (no export needed)

**If they haven't exported yet**, walk them through it step by step:

1. Open ChatGPT (chatgpt.com)
2. Click your profile icon in the top-right corner
3. Go to **Settings**
4. Click **Data controls** in the left sidebar
5. Click **Export data** then **Confirm export**
6. ChatGPT will email you a download link. This can take anywhere from a few minutes to 24 hours, though it's usually under an hour.
7. When the email arrives, click the download link, download the zip file, and unzip it.
8. Then come back here and either select the unzipped folder, or drop it into your current workspace.

Then offer Path 1 as something they can do right now while they wait: "While you're waiting for the export, you can do the quick migration. This takes 5 minutes and gets your core ChatGPT context into Claude immediately." Explain Path 1 (the ChatGPT memory extraction prompt from the Two Migration Paths section above) and walk them through it.

**If they've exported but it's in a different folder**, ask them to select the correct folder or tell you the path. If the tool supports directory selection (e.g., Cowork's request_cowork_directory), use that.

**If they're waiting for the email**, offer Path 1 as above. Also let them know they can come back to this conversation (or start a new one) once the export arrives.

**If they just want the quick migration**, walk them through Path 1 entirely:
1. Give them the ChatGPT memory extraction prompt to paste into ChatGPT
2. Tell them to copy ChatGPT's response
3. Direct them to claude.com/import-memory to paste it, or show them how to add memories manually in Claude's settings
4. Let them know that if they want to do the deep migration later, they can export their data and come back.

The key principle: never leave the user stuck. Every path should lead somewhere useful, even if they don't have their export data yet.

## Stage 1: Interview

Before processing anything, have a brief conversation with the user to understand what they want. Use the AskUserQuestion tool for this. Ask about:

**Question 1: Scope** - "What would you like to extract from your ChatGPT history?"
- Everything (work, personal, creative, all of it)
- Mostly work/professional stuff
- Mostly personal/creative stuff
- A specific topic or project (ask them what)

**Question 2: Priority** - "What matters most to you in the migration?"
- Having Claude understand who I am (personality, preferences, communication style)
- Carrying over my professional context (projects, expertise, workflows)
- Preserving useful reference material (research, decisions, analysis)
- Getting set up with good system prompts and skills for how I actually use AI

**Question 3: Target** - "Where will you primarily use Claude?"
- Claude.ai (web/app)
- Cowork (desktop automation)
- Claude Code (developer tool)
- Multiple / all of the above

**Question 4: Claude experience** - "What's your Claude experience so far?"
- I'm completely new to Claude (just switched from ChatGPT)
- I've been using Claude for a few weeks
- I've been using Claude for a few months
- I've been using Claude for 6+ months

This shapes the tone and depth of the import walkthrough. New users need more guidance on Claude's features, memory, and projects. Experienced users mainly need their ChatGPT context ported over efficiently.

**Question 5: Existing Claude memories** - "Do you have memories saved in Claude that we should cross-reference with your ChatGPT history?"
- Yes, I have Claude memories (ask them to paste or export their memories)
- No / not sure

If they have existing Claude memories, save them to the migration-workspace as `existing-claude-memories.txt`. These will be cross-referenced during synthesis to identify confirmed facts, outdated information, and new discoveries.

After the interview, write (or update) `progress.json` in the migration-workspace with the interview answers and set `current_stage` to 2. This way, if the session is interrupted, the next session won't re-ask all the questions.

## Stage 2: Preprocess

Run the preprocessor script to compress the raw export into manageable batches:

```bash
python3 <skill-path>/scripts/preprocessor.py "<export-folder-path>" "<export-folder-path>/migration-workspace"
```

The preprocessor applies recency weighting automatically:
- Conversations are tagged with recency eras (recent/mid/older/historical)
- Recent medium conversations (50-200 words, less than 1 year old) are promoted to deep tier
- Recent light conversations (20-50 words, less than 1 year old) are promoted to medium tier
- All batches are sorted recent-first so Claude sees the most current picture first

This produces:
- `00-overview.json` - High-level stats with recency breakdown and separate recent vs all-time keyword analysis
- `01-title-index.json` - Every conversation title with date, word count, recency era, and tier
- `02-user-profile.json` - Account info from user.json
- `batch-NNN-{deep|medium|light}.json` - Conversation content in context-window-sized batches, sorted recent-first

Read `00-overview.json` first and share the key stats with the user. This helps them understand the scope and sets expectations.

**After sharing the stats, give the user a time estimate.** Now that you know the exact batch count, calculate: roughly 1.5-2 minutes per batch in waves of 3-5, plus 2-5 minutes for synthesis, plus 5-10 minutes for fact-checking and import walkthrough. Tell the user something like: "You've got 22 batches, so the analysis phase will take roughly 35-45 minutes. I'll give you updates as each wave finishes."

After preprocessing completes, update `progress.json`: set `current_stage` to 3, `preprocessing.completed` to true, and list all batch files. This is critical because preprocessing is deterministic and never needs to be re-run.

## Stage 3: Batch Analysis

This is the core processing stage and the longest part of the pipeline. For each batch file, you need to extract structured insights. The batches come in three tiers:

**Deep batches** (conversations with 200+ user words): Full message content included. These are the richest source of personal context, preferences, and patterns. Process these carefully.

**Medium batches** (50-200 user words): User messages only. Good for identifying topics, recurring needs, and professional context.

**Light batches** (under 50 words): Metadata only (title, date, model). Useful for understanding breadth of usage and topic distribution, but not much else.

### Processing approach: waves of 3-5 subagents

Use subagents (the Task tool) to process batches in parallel, but **limit each wave to 3-5 subagents at a time**. This keeps wait times manageable (each wave takes roughly 1.5-2 minutes) and gives the user regular progress updates rather than one long silence.

For each batch, spawn a subagent with the batch analysis prompt from `references/batch-analysis-prompt.md`, adapted for the batch tier.

The subagent should read the batch file and produce a structured analysis saved to the migration-workspace. Name the output files `analysis-NNN.json` to match their batch numbers.

Process deep batches first (they take longest and contain the most value), then medium, then light.

**Important**: Don't try to read the batch files directly into your own context. They're 150-240KB each. Use subagents so each batch gets a fresh context window.

### Wave processing loop

1. Launch 3-5 subagents for the next wave of batches
2. Wait for them to complete
3. Update `progress.json` with the newly completed batches
4. Tell the user: "Wave complete: [X] of [Y] batches done. [brief note on what's emerging]. Next wave starting now, roughly [Z] minutes remaining."
5. Launch the next wave
6. Repeat until all batches are processed

The progress update after each wave is important. Keep it brief but informative: mention a finding or two so the user knows the analysis is substantive, and always include the updated time estimate.

### Progress tracking during batch analysis

After each wave of subagents completes, update `progress.json`: move those batches from `pending_batches` to `completed_batches` and update `last_updated`. This way, if the session hits compaction mid-way through batch analysis, the next session can see exactly which batches are done (it can also verify by checking which `analysis-NNN.json` files exist on disk).

When resuming mid-batch-analysis: list the `analysis-*.json` files in the migration-workspace, compare against the full batch list from preprocessing, and only process the missing ones.

## Stage 4: Synthesis

Once all batch analyses are complete, update `progress.json` with `current_stage` set to 4.

Tell the user: "All batches analysed. Now synthesising everything into your migration files. This takes 2-5 minutes."

Read all the `analysis-NNN.json` files. These are much smaller than the raw batches (typically 2-5KB each). Combine the insights with the user's interview answers (from `progress.json` if resuming) to produce the final outputs.

Use the synthesis prompt from `references/synthesis-prompt.md` as your guide. The outputs are:

### 1. User Profile (`claude-profile.md`)
A comprehensive "about me" context document. This covers: who they are, what they do professionally, their interests and hobbies, their communication style, their values and priorities, key life context (location, relationships, etc. - only what they've naturally shared in conversations, never inferred or assumed).

This should read like a friend describing them to someone who's about to help them, not like a clinical dossier.

### 2. Memories (`claude-memories.md`)
Discrete facts and preferences extracted from conversations, formatted as a list. These are things Claude should remember across conversations. Examples: "Prefers British English", "Works at [company] as [role]", "Training for a marathon", "Allergic to [thing]", "Prefers concise responses".

Aim for 30-100 memories depending on how much is in the history. Quality over quantity. Each memory should be a single, specific, useful fact.

### 3. System Prompt (`claude-system-prompt.md`)
A ready-to-use system prompt for claude.ai, Cowork, Claude Code, or the API, tailored to this specific user. It should encode their communication preferences, key context, and any specific instructions that would make Claude more useful to them from the first message.

### 4. Cowork Skills Suggestions (`claude-skills.md`)
Based on patterns in how they used ChatGPT, suggest 3-5 Cowork skills that would be valuable. For each: a name, what it would do, why it would help them specifically, and a rough outline of what the SKILL.md would contain. Don't build the full skills, just give enough detail that the user (or Claude) could build them later.

### 5. Integrations & MCP Servers (`claude-integrations.md`)
Based on the tools, services, and APIs that appear in their ChatGPT history (weighted towards recent usage), recommend MCP servers, Claude connectors, and integrations they should set up. For each recommendation:

- **What it is**: The MCP server or integration name and where to find it
- **Why for this user**: What pattern in their history makes this relevant (e.g., "You frequently worked with Google Sheets data in ChatGPT" -> Google Sheets MCP server)
- **What it enables**: 2-3 concrete things they'll be able to do with Claude that they were doing with ChatGPT

Common mappings to look for:
- **Google Workspace** (Docs, Sheets, Calendar, Gmail) -> Google MCP servers or Claude connectors
- **GitHub/GitLab** -> GitHub MCP server
- **Slack** -> Slack MCP server
- **Notion** -> Notion MCP server or Claude connector
- **Linear/Jira** -> Linear MCP server
- **Figma** -> Figma MCP server
- **Databases** (PostgreSQL, MySQL, etc.) -> Database MCP servers
- **Web scraping/research** -> Firecrawl, Brave Search, or web search MCP servers
- **File management** -> Filesystem MCP server
- **Todoist/task management** -> Todoist MCP server
- **Stripe/billing** -> Stripe MCP server
- **Analytics** (PostHog, Mixpanel, GA) -> relevant MCP servers if available, or note that a custom integration would be valuable

Only recommend integrations where there's clear evidence in their history. Don't pad with generic suggestions. If they only used ChatGPT for conversation and writing, it's fine to have a short list or even say "No specific integrations recommended based on your usage patterns."

**Important: Only recommend official MCP servers and integrations.** Only suggest MCP servers published by the service provider themselves (e.g., the official GitHub MCP server by GitHub, the official Slack MCP server by Slack) or first-party Claude connectors available in Claude's settings. Never recommend unofficial or community-built MCP servers. If no official integration exists for a service the user relies on, note it as a gap rather than pointing to a third-party alternative.

### 6. Topic Index (`topic-index.md`)
A curated index of their conversation history organised by theme/topic. For each topic: a brief description, how many conversations touched on it, the date range, and the 3-5 most notable conversation titles. This serves as a reference so they know what's in their archive.

### 7. Migration Summary (`migration-summary.md`)
A brief, readable summary of the whole migration: what was processed, what was found, what was produced, and suggestions for next steps. This is the document they'll read first.

### 8. Memory Cross-Reference (`memory-crossref.md`, only if user provided Claude memories)
If the user already has Claude memories, produce a cross-reference showing:
- **Confirmed**: Facts that appear in both Claude memory and ChatGPT analysis
- **Potentially outdated**: Claude memories contradicted by recent ChatGPT conversations
- **New discoveries**: Facts from ChatGPT that aren't in Claude memory
- **Claude-only**: Things in Claude memory not found in ChatGPT (left as-is)

## Stage 5: Fact-Checking Interview

This stage is critical. Before delivering anything, present the user with up to 10 key facts from the synthesis and ask them to confirm, correct, or discard each one.

### Why this matters

The analysis is working from conversation fragments spanning years. It's easy to get things wrong: outdated job titles, misunderstood relationships, incorrect locations, confused project details. The user is the only person who can verify whether the synthesis got things right.

### How to do it

1. **Select up to 10 facts to verify.** Choose the ones that are:
   - Most prominent in the outputs (things that appear in the profile, system prompt, AND memories)
   - Most likely to be wrong (facts from older eras, implied rather than stated, or where conflicting signals appeared across batches)
   - Most consequential if wrong (current job title, location, key relationships, professional identity)

2. **Present them using AskUserQuestion**, grouping into 2-3 rounds of questions. For each fact, give the user the option to:
   - **Keep** - This is correct
   - **Discard** - This is wrong or outdated, remove it
   - **Correct** - This is close but needs fixing (use the "Other" option for them to type the correction)

   Example: "The analysis found you're currently the founder of Jack & Jill AI, an AI-powered recruitment platform. Is this correct?"

3. **Apply the corrections.** After the fact-check interview, update all affected output files (profile, memories, system prompt) to reflect what the user confirmed, corrected, or discarded. This may mean rewriting sections of the profile or removing memories.

4. **Update progress.json** with the fact-check results: which facts were presented, which were kept, discarded, or corrected.

### What to check

Prioritise these categories:
- Current job title and company
- Location and living situation
- Key relationships mentioned
- Active projects (are they still active?)
- Technical skills and tools (still using them?)
- Health or personal details that may have changed
- Any facts that appeared contradictory across different batches

If the synthesis only found a handful of substantive facts (small export, narrow scope), you can do fewer than 10. The point is verification, not bureaucracy.

## Stage 6: Deliver and Import Walkthrough

Save all output files to the migration-workspace folder and present them to the user with links.

### File delivery

Present each file with a one-line description of what it is. Don't give lengthy explanations; the user can read the files themselves.

### Import walkthrough

This is the most important part. Walk the user through exactly how to get their migration data into Claude, step by step. Tailor the walkthrough to whatever they said in the interview (Question 3) about where they use Claude.

**For Claude.ai users:**

1. **System prompt / custom instructions:**
   - Go to claude.ai > Settings (bottom left) > Profile
   - In the "How would you like Claude to respond?" box, paste the contents of `claude-system-prompt.md`
   - Click Save
   - Note: this has a character limit. If the system prompt is too long, prioritise the communication preferences and key context sections, and trim the background/topics sections.

2. **Memories:**
   - Go to claude.ai > Settings > Profile
   - Under "What would you like Claude to remember about you?", you can add memories manually
   - Alternatively, open a new conversation and say: "I'd like you to memorise the following facts about me" then paste the contents of `claude-memories.md`. Claude will add them to its memory over the course of the conversation.
   - Note: Claude's memory feature adds items gradually. If you have 100+ memories, it may take a few conversations for them all to be absorbed. You can also add the most important ones manually in Settings.

3. **Profile as a Project:**
   - In Claude.ai, click "Projects" in the left sidebar
   - Create a new project (e.g., "About Me" or "My Context")
   - Add `claude-profile.md` as a file in the project
   - Any conversation started within this project will have your full profile as context
   - This is the most powerful way to use the profile, as it persists across conversations within the project without using up memory slots

**For Cowork users:**

1. **System prompt:**
   - The contents of `claude-system-prompt.md` can be added to your Cowork preferences
   - Or create a skill that includes it as context

2. **Profile:**
   - Keep `claude-profile.md` in a folder that Cowork has access to
   - Reference it in conversations: "Read my profile from claude-profile.md"
   - Or build a skill that automatically loads it

3. **Skills:**
   - Review `claude-skills.md` for suggested skills to build
   - Each suggestion includes enough detail to create the skill in Cowork

**For Claude Code users:**

1. **System prompt as CLAUDE.md:**
   - Save `claude-system-prompt.md` as `CLAUDE.md` in your home directory or project root
   - Claude Code reads this file automatically at the start of each session

2. **Memories:**
   - Claude Code doesn't have a built-in memory feature, but you can add key facts to your `CLAUDE.md` file
   - Or keep `claude-profile.md` somewhere accessible and reference it when needed

3. **Skills:**
   - The skill suggestions in `claude-skills.md` can be built as Claude Code slash commands or skills

**For all users:**

- `claude-integrations.md` lists MCP servers and Claude connectors to install based on the tools and services in your history. Review the list and install any that look useful.
- `topic-index.md` is for your reference. Keep it somewhere handy if you want to look back at what you discussed with ChatGPT.
- `migration-summary.md` is a one-time read. It summarises what was processed and found.
- If a `memory-crossref.md` was produced, review the "potentially outdated" section and update or remove those Claude memories.

### Final check

After walking through the import steps, ask the user if they'd like to:
- Adjust any of the output files
- Go deeper on a specific topic
- Build out any of the suggested skills
- See specific conversations from their archive in more detail

After delivery, update `progress.json` with `current_stage` set to 6 and `synthesis.completed` set to true, with the list of files produced. This marks the migration as complete.

## Important Notes

- **Privacy**: This is deeply personal data. Don't make assumptions about sensitive topics. Report what you find factually without judgment.
- **Accuracy**: Only include facts that are clearly stated in conversations. Don't infer or hallucinate details. If something is ambiguous, note it as such.
- **Tone**: The outputs should feel warm and useful, not clinical. The user is trusting you with their entire AI conversation history.
- **Scale**: A typical export might have 500-2000 conversations. The preprocessor handles the compression, but synthesis still requires careful attention to not miss important threads.
- **Batching**: Never try to load raw conversation JSON files directly. Always use the preprocessed batches. The raw files can be 5-10MB each.
- **Recency**: Always prioritise recent information. A user's ChatGPT history might span years and multiple jobs, relationships, cities. What matters is who they are now, with historical context adding depth rather than defining the picture.
- **Time communication**: Always tell the user how long things will take. Silence during processing is the worst user experience. Brief updates after every wave of batches keep them informed and confident the process is working.
