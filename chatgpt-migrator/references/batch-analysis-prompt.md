# Batch Analysis Prompt

You are analysing a batch of conversations from a ChatGPT export as part of a migration to Claude. Your job is to extract structured insights from these conversations.

## Recency Matters

Each conversation in the batch has a `recency_era` field:
- **recent** (last 6 months): Highest priority. This is who the user is *now*.
- **mid** (6-12 months): High priority. Still very relevant.
- **older** (1-2 years): Medium priority. May reflect past roles, projects, or interests.
- **historical** (2+ years): Low priority. Useful for background but may be outdated.

When extracting facts, always note the era. If a conversation from 2023 says "I work at CompanyX" but a conversation from 2025 says "I work at CompanyY", the recent one is the current truth. Flag these temporal shifts explicitly so the synthesis stage can resolve them.

Batches are sorted recent-first. The first conversations in each batch are the most current.

## Your Task

Read the batch file provided and extract the following information. Be thorough but concise. Only include things that are clearly evidenced in the conversations.

## What to Extract

### 1. Personal Facts
Concrete facts about the user: name, location, age, job title, company, relationships, pets, health conditions, languages spoken, etc. Only things explicitly stated or very clearly implied.

Format: A list of facts, each with a confidence level (stated/implied), the source conversation title, and the recency era.

### 2. Preferences & Style
How the user communicates and what they prefer: formality level, response length preferences, whether they like bullet points or prose, technical level, language preferences (British/American English), emoji usage, etc.

### 3. Professional Context
What the user does for work, their expertise areas, tools they use, projects they've worked on, professional goals, industry context.

**Important**: If this batch spans multiple time periods, note the era for each piece of professional context. People change jobs, roles, and companies. A fact tagged "historical" about their employer might be completely wrong for who they are today.

### 4. Recurring Topics
Themes that come up repeatedly. For each: the topic, how many conversations touch on it, and a brief note on what angle the user typically approaches it from.

### 5. Notable Conversations
The 3-5 most substantive or revealing conversations in this batch. Prioritise recent conversations, but include older ones if they're especially rich. For each: the title, date, era, and a one-sentence summary of why it's notable.

### 6. Tools & Workflows
Specific tools, software, frameworks, or workflows the user mentions using. Include version numbers or specifics if mentioned. Note the era, since tool preferences change over time.

### 7. Values & Priorities
What the user seems to care about, based on what they ask about and how they react. This is the most interpretive category - keep it grounded in evidence.

### 8. Skills Patterns
Recurring types of tasks the user brings to ChatGPT. Examples: "Frequently asks for code review", "Often drafts professional emails", "Regularly analyses spreadsheet data". These inform what Cowork skills would be useful.

### 9. Temporal Shifts
If you notice any clear changes over time in this batch (changed job, moved city, new interests, different tools), note them explicitly. This is critical for producing an accurate current profile rather than a blurred composite of all time periods.

## Output Format

Return a JSON object with this structure:

```json
{
  "batch_number": <number>,
  "tier": "<deep|medium|light>",
  "conversations_analysed": <count>,
  "era_breakdown": {"recent": <n>, "mid": <n>, "older": <n>, "historical": <n>},
  "personal_facts": [
    {"fact": "...", "confidence": "stated|implied", "source": "conversation title", "era": "recent|mid|older|historical"}
  ],
  "preferences_and_style": [
    {"preference": "...", "evidence": "brief note on where this was observed", "era": "recent|mid|older|historical"}
  ],
  "professional_context": [
    {"era": "recent|mid|older|historical", "role": "...", "company": "...", "industry": "...", "expertise_areas": [], "tools": [], "projects": []}
  ],
  "recurring_topics": [
    {"topic": "...", "frequency": <count>, "typical_angle": "...", "era_span": "recent only|recent+mid|all eras|historical only"}
  ],
  "notable_conversations": [
    {"title": "...", "date": "...", "era": "...", "why_notable": "..."}
  ],
  "tools_and_workflows": [
    {"tool": "...", "context": "how they use it", "era": "recent|mid|older|historical"}
  ],
  "values_and_priorities": [
    {"value": "...", "evidence": "..."}
  ],
  "skills_patterns": [
    {"pattern": "...", "frequency": "often|sometimes|once", "description": "...", "era_span": "recent|all|historical"}
  ],
  "temporal_shifts": [
    {"what_changed": "...", "from": "...", "to": "...", "approximate_date": "...", "evidence": "..."}
  ]
}
```

Note that `professional_context` is now an array, because a single batch might span multiple roles or companies across time.

## Tier-Specific Guidance

### For Deep Batches
You have full conversation content (both user and assistant messages). Pay close attention to:
- How the user phrases requests (this reveals communication style)
- What follow-up questions they ask (this reveals what matters to them)
- Where they push back on responses (this reveals preferences and values)
- The progression of topics over time
- Changes in professional context or personal circumstances across conversations

### For Medium Batches
You have user messages only. Focus on:
- What they ask about (topics and recurring needs)
- How they ask (style and preferences)
- Professional context clues in their requests

### For Light Batches
You only have titles, dates, and word counts. Focus on:
- Topic distribution across titles
- Usage patterns over time
- Breadth of interests
- Any titles that suggest important life events or projects

For light batches, the output will naturally be sparser. That's fine.
