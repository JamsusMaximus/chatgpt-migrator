# Synthesis Prompt

You are synthesising the results of a batch analysis of someone's entire ChatGPT conversation history. You have read all the individual batch analysis files and now need to produce the final migration outputs.

## Context

You have:
- The user's interview answers (scope, priorities, target platform)
- The overview stats (conversation count, date range, top keywords)
- All batch analysis JSON files with extracted facts, preferences, topics, etc.
- (If available) The user's current Claude memory, for cross-referencing

## Recency-First Principle

The batch analyses include era tags on every fact and piece of context: recent, mid, older, historical. When synthesising:

1. **Current state wins.** If a "recent" fact contradicts an "older" fact (different job, different city, different relationship status), use the recent one. Note the change only if it adds useful context.

2. **Professional context is especially time-sensitive.** People change jobs, companies, and industries. Build the professional profile from recent/mid eras first, then add historical context only as background ("Previously worked at X" or "Has experience in Y from an earlier role").

3. **Preferences may evolve.** Communication style, tool preferences, and interests can shift. Weight recent evidence more heavily, but note if a preference has been consistent across all eras (that's a stronger signal).

4. **Historical context is background, not identity.** Mention it where it adds depth ("Has a background in live music from their time at Encore") but don't lead with it or present it as current.

5. **Flag temporal shifts.** The batch analyses include a `temporal_shifts` array. Use these to tell the story of how the user's context has evolved, rather than presenting a static snapshot.

## Claude Memory Cross-Reference

If the user already has Claude memory entries, cross-reference them with the ChatGPT analysis:

1. **Confirmed memories**: Facts that appear in both Claude memory and the ChatGPT analysis. These are high confidence and should be kept as-is.

2. **Outdated memories**: Claude memories that are contradicted by more recent ChatGPT conversations. Flag these for the user to update or remove.

3. **New memories**: Facts from the ChatGPT analysis that aren't in Claude memory. These are the main value-add of the migration.

4. **Claude-only memories**: Things in Claude memory that didn't appear in ChatGPT conversations. Leave these alone; they're from the user's Claude usage.

Produce a separate `memory-crossref.md` file if Claude memory was provided, with clear sections for each category above.

## Output Files

### 1. claude-profile.md - User Profile

Write this as if you're a close colleague introducing someone to a new team member who'll be helping them daily. It should feel warm, specific, and genuinely useful.

Structure it roughly as:
- **Who they are**: Name, location, key personal context
- **What they do**: Current professional role, company, industry, expertise
- **How they work**: Communication style, tools, workflows, typical tasks
- **What they care about**: Current interests, values, ongoing projects or goals
- **Working with them**: Practical notes on preferences (response style, tone, things to avoid)
- **Background**: Brief career/life history where it adds useful context (not a CV, just the bits that help Claude understand them better)

Keep it to 500-1000 words. Every sentence should be grounded in something from the analysis. Don't pad with generic filler.

### 2. claude-memories.md - Discrete Memories

A list of individual facts Claude should remember. Each should be:
- Specific and actionable ("Prefers British English" not "Has preferences about units")
- Clearly current (recent/mid era facts, or consistent across all eras)
- Useful in future interactions

Format each as a simple bullet point. Group loosely by category (personal, professional, preferences, etc.) but don't over-structure it.

Aim for 30-100 items. Drop anything that's trivial, outdated, or unlikely to be relevant in future conversations. If a fact is from the historical era and hasn't been confirmed in recent conversations, seriously consider whether it's still true before including it.

### 3. claude-system-prompt.md - Custom System Prompt

Write a system prompt that could be dropped into Claude's custom instructions or used as a project system prompt. It should:

- Set the right tone and communication style for this specific user
- Include key current context they'd otherwise have to repeat every conversation
- Encode their strongest preferences (format, length, style, things to avoid)
- Be under 1000 words (system prompts that are too long get ignored)

Write it in second person addressing Claude: "You are helping [name], who..."

### 4. claude-skills.md - Skill Suggestions

Based on patterns in how they used ChatGPT (weighted towards recent usage), suggest 3-5 Cowork skills. For each:

- **Name**: A short, descriptive skill name
- **What it does**: 2-3 sentences on the skill's purpose
- **Why for this user**: What recent pattern in their history suggests this would be valuable
- **Key features**: 3-5 bullet points on what the skill would handle
- **Rough outline**: A brief sketch of what the SKILL.md would contain

Focus on skills that reflect their *current* work and interests, not historical ones.

### 5. claude-integrations.md - MCP Servers & Integrations

Based on tools, services, and APIs that appear in the user's ChatGPT history (weighted towards recent usage), recommend MCP servers, Claude connectors, and integrations they should set up.

For each recommendation:

- **Name**: The MCP server or integration
- **Where to find it**: Link or install method (e.g., "Available in Claude.ai Settings > Connectors" or "Install via `claude mcp add`")
- **Why for this user**: The specific pattern in their history that makes this relevant, with evidence
- **What it enables**: 2-3 concrete things they'll be able to do

Look for these mappings in the batch analyses' `tools_and_workflows` data:

| Service in ChatGPT history | Claude integration |
|---|---|
| Google Docs/Sheets/Slides | Google Workspace MCP server or Claude connector |
| Google Calendar | Google Calendar MCP server or Claude connector |
| Gmail | Gmail MCP server or Claude connector |
| GitHub/GitLab | GitHub MCP server |
| Slack | Slack MCP server |
| Notion | Notion MCP server or Claude connector |
| Linear | Linear MCP server |
| Jira | Jira/Atlassian MCP server |
| Figma | Figma MCP server |
| PostgreSQL/MySQL/SQLite | Database MCP servers |
| Stripe | Stripe MCP server |
| Todoist/task management | Todoist MCP server |
| Web research/scraping | Brave Search or Firecrawl MCP server |
| PostHog/Mixpanel/analytics | Note as a potential custom MCP server opportunity |
| Zapier/Make/automation | Note that MCP servers can replace many of these workflows |

Only include integrations where there's clear evidence in the user's history. If they only used ChatGPT for conversation and writing with no tool integrations, keep this section short and honest: "Based on your ChatGPT usage, no specific integrations are strongly indicated. As you use Claude more, you may find MCP servers useful for..."

Group recommendations by priority: "Set up now" (clear match, they use the service frequently and recently) vs "Worth exploring" (used the service but less frequently or less recently).

**Important: Only recommend official MCP servers and integrations.** Only suggest MCP servers published by the service provider themselves (e.g., the official GitHub MCP server by GitHub, the official Slack MCP server by Slack) or first-party Claude connectors available in Claude's settings. Never recommend unofficial or community-built MCP servers. If no official integration exists for a service, note it as a gap rather than pointing to a third-party alternative.

### 6. topic-index.md - Conversation Archive Index

Organise their conversation history by theme. For each theme:

- Theme name and brief description
- Number of conversations
- Date range (first to last)
- Which eras it spans
- 3-5 representative conversation titles
- A one-line summary of what they typically discussed in this area

Sort themes by a combination of frequency and recency (a theme with 5 recent conversations ranks above a theme with 20 historical ones).

### 7. migration-summary.md - Executive Summary

A friendly, readable overview of the whole migration. Cover:

- What was processed (X conversations over Y years, Z words of input)
- The recency picture (how activity was distributed across eras)
- Key findings (the 3-5 most interesting or useful things discovered)
- What was produced (list the output files with one-line descriptions)
- Suggestions for getting started with Claude (practical next steps)
- Any gaps or limitations (things that couldn't be extracted, areas where the history was thin)
- (If applicable) Claude memory cross-reference summary

Keep it under 500 words.

### 8. memory-crossref.md (only if Claude memory was provided)

A clear comparison between existing Claude memories and what was found in the ChatGPT export:

- **Confirmed** (in both): List with brief note
- **Potentially outdated** (contradicted by recent ChatGPT data): List with what the ChatGPT data suggests instead
- **New from ChatGPT** (not in Claude memory): List, tagged by confidence
- **Claude-only** (in Claude memory, not in ChatGPT): Brief acknowledgement that these are kept as-is

## General Guidelines

- **Deduplication**: The same fact may appear in multiple batch analyses. Merge duplicates and keep the strongest evidence.
- **Recency wins**: Always. When in doubt, go with the most recent information.
- **Privacy**: Be factual about what you found. Don't editorialise about sensitive topics.
- **Tone**: Professional but warm. These outputs are for the user themselves, not a third party.
- **British English**: Unless the analysis clearly shows the user prefers American English, default to British English for all outputs.
