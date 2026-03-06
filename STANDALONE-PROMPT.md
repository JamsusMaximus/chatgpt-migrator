# ChatGPT to Claude Migration Guide

## Two Ways to Migrate

There are two paths here, depending on how much time you have and how thorough you want to be. You can do either one, or both in sequence.

### Path 1: Quick Start (5 minutes)

This gets your core context into Claude immediately. No data export needed.

1. **Copy the prompt below** and paste it into a ChatGPT conversation.
2. **Copy ChatGPT's response** (it will be a structured list of everything it knows about you).
3. **Go to [claude.com/import-memory](https://claude.com/import-memory)** and paste the response there, or manually add the items to Claude's memory in Settings.

**The prompt to give ChatGPT:**

```
I'm moving to another service and need to export my data. List every memory you have stored about me, as well as any context you've learned about me from past conversations. Output everything in a single code block so I can easily copy it. Format each entry as: [date saved, if available] - memory content. Make sure to cover all of the following — preserve my words verbatim where possible: Instructions I've given you about how to respond (tone, format, style, 'always do X', 'never do Y'). Personal details: name, location, job, family, interests. Projects, goals, and recurring topics. Tools, languages, and frameworks I use. Preferences and corrections I've made to your behavior. Any other stored context not covered above. Do not summarize, group, or omit any entries. After the code block, confirm whether that is the complete set or if any remain.
```

This gives you a solid starting point. ChatGPT's stored memories are a curated set of the facts it decided were important enough to keep. But it misses a lot: topics you discussed once but that still matter, patterns in how you work, professional context that wasn't explicitly memorised, and anything from conversations where memory was turned off.

### Path 2: Deep Migration (20-60 minutes depending on export size)

This processes your entire ChatGPT conversation history, not just what ChatGPT chose to remember. It produces a full user profile, comprehensive memories list, tailored system prompt, skill suggestions, topic index, and migration summary.

**How long will it take?**

| Export size | Rough time |
|---|---|
| Under 200 conversations | 10-15 minutes |
| 200-800 conversations | 20-30 minutes |
| 800-1500 conversations | 30-45 minutes |
| 1500+ conversations | 45-60 minutes |

Most of the time is spent in the batch analysis phase. You'll get regular progress updates throughout.

**If you already did Path 1**, the deep migration will cross-reference your new Claude memories with what it finds in the full history, identifying confirmed facts, potentially outdated entries, and new discoveries.

**To get started:**

1. **Export your ChatGPT data**: Go to ChatGPT > Settings > Data controls > Export data. You'll receive an email with a download link (can take up to 24 hours). Download and unzip the folder.

2. **Open Cowork** (or Claude Code, or any Claude environment with file system access) and select the unzipped export folder as your workspace, or drop it in.

3. **Paste the prompt below** to start the migration.

## The Prompt (for Path 2)

Copy everything between the `---` lines and paste it as your first message:

---

I've dropped my ChatGPT data export into this folder. I'd like you to help me migrate to Claude by analysing my conversation history and producing useful context files, system prompts, and memories.

Here's how I'd like you to approach this:

**Step 0: Check for existing progress.** Before doing anything else, check if `migration-workspace/progress.json` exists in this folder. If it does, read it and resume from wherever the pipeline left off (skip completed stages, don't re-ask interview questions, don't re-process completed batches). This file is your checkpoint. If I say "continue" or "keep going", this is what I mean.

**Step 1: Verify the export.** Check this folder for `conversations-*.json` files, `user.json`, and `chat.html`. If you find them, confirm you can see them and tell me the rough stats (how many conversations, date range, etc.). If you DON'T find them, don't just stop. Ask me where I'm at: maybe I haven't exported yet (walk me through it step by step), maybe my export is in a different folder, or maybe I just want to do the quick migration (Path 1) for now. Whatever the situation, help me get to something useful.

**Step 2: Interview me.** Before processing, ask me a few questions:
- What do I want to extract? (Everything, mostly work stuff, mostly personal, a specific topic)
- What matters most? (Claude understanding who I am, carrying over professional context, preserving reference material, or getting set up with good prompts/skills)
- Where will I primarily use Claude? (Claude.ai, Cowork, Claude Code, or all of them)
- What's my Claude experience so far? (Completely new / a few weeks / a few months / 6+ months). This shapes how much guidance to give during the import walkthrough.
- Do I have existing Claude memories we should cross-reference with my ChatGPT history?

**Step 3: Preprocess.** The raw export is too large to read directly. Write and run a Python script that:
- Reads all `conversations-*.json` files
- Tags each conversation with a recency era based on age: recent (last 6 months), mid (6-12 months), older (1-2 years), historical (2+ years)
- Categorises conversations into three tiers by substance, with recency-aware promotion:
  - **Deep** (200+ user words, OR recent conversations with 50+ words): Include full message content
  - **Medium** (50-200 user words, OR recent conversations with 20+ words): Include user messages only
  - **Light** (everything else): Include metadata only (title, date, word count)
- Sorts all batches recent-first so the most current conversations are processed with highest priority
- Splits the output into batch files, each under 60,000 estimated tokens (~240KB)
- Produces an overview file with stats (including a recency breakdown and separate recent vs all-time keyword analysis) and a title index

Save all preprocessed files to a `migration-workspace` subfolder.

After preprocessing, **tell me how long the rest will take** based on the batch count. Roughly 1.5-2 minutes per batch (processed in waves of 3-5), plus 5-10 minutes for synthesis and review at the end.

**Progress tracking:** Maintain a `progress.json` file in the migration-workspace that records: the current stage, my interview answers, which batches have been processed, and which output files have been produced. Update this file after every meaningful step (interview complete, preprocessing complete, each wave of batches analysed, each output file written). This way, if the session hits its context limit, the next session can read this file and pick up exactly where things left off. The structure should be:
```json
{
  "current_stage": 3,
  "stage_name": "batch_analysis",
  "interview": { "scope": "...", "priority": "...", "target": "...", "existing_claude_user": false },
  "preprocessing": { "completed": true, "total_batches": 22, "batch_files": ["..."] },
  "batch_analysis": { "completed_batches": ["..."], "pending_batches": ["..."] },
  "synthesis": { "completed": false, "files_produced": [] },
  "fact_check": { "completed": false, "facts_presented": [], "facts_kept": [], "facts_discarded": [], "corrections": [] },
  "last_updated": "ISO-timestamp"
}
```

**Step 4: Analyse batches.** Process each batch file using subagents (the Task tool), in **waves of 3-5 at a time** (not more, to avoid long waits). For each batch, extract:
- Personal facts about me (name, location, job, relationships, etc.) with the recency era noted
- Communication preferences and style patterns
- Professional context (role, company, expertise, tools) noting which era each fact comes from
- Recurring topics and themes
- Notable conversations worth flagging (prioritise recent ones)
- Tools and workflows I use
- Values and priorities
- Patterns in how I use AI (what types of tasks I bring)
- **Temporal shifts**: Any clear changes over time (changed job, moved city, new interests)

After each wave completes, give me a brief update: how many batches are done, what's emerging, and roughly how much time remains.

This is critical: my history spans years and multiple jobs/life stages. Facts from years ago may be completely wrong for who I am today. Always tag facts with their era and flag contradictions across time periods.

Save each batch analysis as a structured JSON file in the migration-workspace.

**Step 5: Synthesise.** Read all batch analyses and combine them with my interview answers to produce:

1. **claude-profile.md** - A comprehensive "about me" context document, written like a close colleague introducing me. 500-1000 words covering who I am *now*, what I do, how I work, and what I care about. Historical context should be background, not the lead.

2. **claude-memories.md** - 30-100 discrete facts and preferences for Claude to remember. Only include things that are current (from recent/mid eras, or consistent across all eras). Drop anything that's likely outdated.

3. **claude-system-prompt.md** - A ready-to-use system prompt encoding my communication preferences, key context, and strongest preferences. Under 1000 words.

4. **claude-skills.md** - 3-5 suggested Cowork skills based on my *recent* usage patterns. For each: name, purpose, why it suits me, and a rough outline.

5. **claude-integrations.md** - Recommended MCP servers, Claude connectors, and integrations based on the tools and services that appear in my history. For each: what it is, why it's relevant to me (with evidence from my usage patterns), and what it enables. Map tools and services I used with ChatGPT to their Claude equivalents (e.g., Google Workspace -> Google MCP servers, GitHub -> GitHub MCP server, Notion -> Notion connector, Slack -> Slack MCP server, databases -> database MCP servers, etc.). Only include integrations where there's clear evidence in my history - don't pad with generic suggestions. Only recommend official MCP servers (published by the service provider) and first-party Claude connectors - never unofficial or community-built ones. If no official integration exists for a service I use, note it as a gap.

6. **topic-index.md** - My conversation history organised by theme, with counts and representative titles. Sort by a combination of frequency and recency (recent themes first).

7. **migration-summary.md** - A brief overview of what was processed, key findings, recency breakdown, and next steps.

8. **memory-crossref.md** (only if I provided existing Claude memories) - A cross-reference showing: confirmed facts (in both), potentially outdated Claude memories (contradicted by recent ChatGPT data), new discoveries (from ChatGPT, not in Claude memory), and Claude-only memories (left as-is).

**Step 6: Fact-check with me.** Before finalising, pick up to 10 key facts from the synthesis that are most likely to be wrong or outdated (current job, location, relationships, active projects, etc.) and ask me to confirm, correct, or discard each one. Then update the output files based on my answers. This is important because the analysis is working from conversation fragments and can easily get things wrong.

**Step 7: Walk me through importing into Claude.** Don't just hand me the files. Show me exactly where to go and what to paste for my specific setup (Claude.ai, Cowork, or Claude Code). Step by step, with specific menu paths and instructions.

**Important guidelines:**
- Only include facts clearly stated in my conversations. Never infer or assume.
- Be factual about sensitive topics without editorialising.
- **Recency wins.** Always prioritise recent information over old. My history likely spans multiple jobs, life stages, and contexts. Build my profile from who I am now, not a blurred composite of all time periods.
- Keep the tone warm and useful, not clinical.
- **Tell me how long things will take** throughout. Give me time estimates before long operations and progress updates during them.

---

## What You'll Get

After the migration, you'll have these files ready to use:

| File | What It's For | How to Use It |
|------|--------------|---------------|
| `claude-profile.md` | Comprehensive context about you | Add as a Project in Claude.ai, or as context in Cowork |
| `claude-memories.md` | Discrete facts Claude should know | Add to Claude's memory (manually or via conversation) |
| `claude-system-prompt.md` | Customised instructions for Claude | Set as custom instructions in Claude.ai settings, or as CLAUDE.md for Claude Code |
| `claude-skills.md` | Suggested automation skills | Build these as Cowork skills |
| `claude-integrations.md` | MCP servers and connectors to install | Set up the ones that match your workflow |
| `topic-index.md` | Archive of your ChatGPT history | Personal reference |
| `migration-summary.md` | Overview of the migration | Read this first |
| `memory-crossref.md` | Cross-reference with existing Claude memories | Review and update your Claude memories |

## Tips

- **Large exports (1000+ conversations)**: The process works fine but takes longer. Expect 30-60 minutes. The preprocessor handles the heavy lifting. You'll get progress updates after every wave of batches.
- **Session limits**: If the session runs out of context mid-migration, just start a new session, drop the same folder in, and say "continue the migration". The tool saves its progress to `progress.json` and will pick up where it left off.
- **Privacy**: Everything runs locally. Your data stays on your machine and is processed by Claude in your session. Nothing is uploaded or stored elsewhere.
- **Iterating**: After the initial migration, you can ask Claude to go deeper on specific topics, refine the system prompt, or build out any of the suggested skills.
- **Multiple exports**: If you have exports from other AI tools too, you can run this process for each and then ask Claude to merge the results.
- **Already using Claude?** If you have existing Claude memories, paste them when asked during the interview. The tool will cross-reference them with your ChatGPT history to find outdated entries and new facts.
