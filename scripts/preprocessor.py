#!/usr/bin/env python3
"""
ChatGPT Export Preprocessor for Claude Migration
=================================================
Reads a ChatGPT data export and produces structured batch files
that Claude can process within its context window.

Applies recency weighting: recent conversations are promoted to
higher tiers and processed first, since a user's current context
matters far more than years-old conversations.

Usage:
    python3 preprocessor.py /path/to/chatgpt-export /path/to/output

The export folder should contain:
    - conversations-*.json files
    - user.json
    - user_settings.json
    - (optional) chat.html, export_manifest.json, shared_conversations.json
"""

import json
import os
import sys
import re
import time
from datetime import datetime
from collections import Counter, defaultdict
from pathlib import Path


# Recency eras: how old a conversation is relative to the most recent one
# These thresholds define the boundaries between eras
RECENCY_ERAS = {
    "recent": 180,     # Last 6 months
    "mid": 365,        # 6-12 months ago
    "older": 730,      # 1-2 years ago
    "historical": None, # 2+ years ago
}

# Tier promotion: recent medium conversations get promoted to deep
# because a 100-word recent conversation about your current job is
# more valuable than a 500-word conversation from 3 years ago
PROMOTE_MEDIUM_THRESHOLD_DAYS = 365  # Promote medium->deep if < 1 year old


def load_conversations(export_dir):
    """Load all conversations from the export directory."""
    conversations = []
    i = 0
    while True:
        fname = os.path.join(export_dir, f"conversations-{i:03d}.json")
        if not os.path.exists(fname):
            break
        with open(fname, "r", encoding="utf-8") as f:
            data = json.load(f)
        conversations.extend(data)
        i += 1
    return conversations


def extract_messages(conversation):
    """
    Walk the message tree and extract an ordered list of messages.
    Returns list of dicts with role, text, content_type, timestamp.
    """
    mapping = conversation.get("mapping", {})

    # Find root node (no parent)
    root_id = None
    for node_id, node in mapping.items():
        if node.get("parent") is None:
            root_id = node_id
            break

    if not root_id:
        return []

    # Walk the tree depth-first
    messages = []
    visited = set()

    def walk(node_id):
        if node_id in visited:
            return
        visited.add(node_id)
        node = mapping.get(node_id, {})
        msg = node.get("message")
        if msg:
            role = msg.get("author", {}).get("role", "unknown")
            content = msg.get("content", {})
            content_type = content.get("content_type", "unknown")

            # Extract text from parts
            text_parts = []
            for part in content.get("parts", []):
                if isinstance(part, str):
                    text_parts.append(part)
                elif isinstance(part, dict):
                    # Image or file reference - note it but skip content
                    asset = part.get("content_type", part.get("asset_pointer", "attachment"))
                    text_parts.append(f"[{asset}]")

            text = "\n".join(text_parts).strip()

            if text and role in ("user", "assistant"):
                messages.append({
                    "role": role,
                    "text": text,
                    "content_type": content_type,
                    "timestamp": msg.get("create_time"),
                })

        # Follow children
        children = node.get("children", [])
        for child_id in children:
            walk(child_id)

    walk(root_id)
    return messages


def assign_recency_era(create_time, latest_time):
    """
    Assign a recency era based on how old the conversation is
    relative to the newest conversation in the export.
    """
    if not create_time or not latest_time:
        return "historical"

    age_days = (latest_time - create_time) / 86400  # seconds to days

    if age_days <= RECENCY_ERAS["recent"]:
        return "recent"
    elif age_days <= RECENCY_ERAS["mid"]:
        return "mid"
    elif age_days <= RECENCY_ERAS["older"]:
        return "older"
    else:
        return "historical"


def process_conversation(conv, latest_time):
    """Process a single conversation into a structured summary."""
    messages = extract_messages(conv)

    user_messages = [m for m in messages if m["role"] == "user"]
    assistant_messages = [m for m in messages if m["role"] == "assistant"]

    user_text = "\n\n".join(m["text"] for m in user_messages)
    user_word_count = len(user_text.split()) if user_text else 0

    assistant_text = "\n\n".join(m["text"] for m in assistant_messages)
    assistant_word_count = len(assistant_text.split()) if assistant_text else 0

    create_time = conv.get("create_time", 0)
    era = assign_recency_era(create_time, latest_time)

    return {
        "id": conv.get("id", conv.get("conversation_id", "")),
        "title": conv.get("title", "Untitled"),
        "create_time": create_time,
        "date": datetime.fromtimestamp(create_time).strftime("%Y-%m-%d") if create_time else "unknown",
        "model": conv.get("default_model_slug", "unknown"),
        "is_archived": conv.get("is_archived", False),
        "gizmo_id": conv.get("gizmo_id"),
        "user_word_count": user_word_count,
        "assistant_word_count": assistant_word_count,
        "turn_count": len(messages),
        "recency_era": era,
        "user_text": user_text,
        "assistant_text": assistant_text,
        "messages": messages,
    }


def estimate_tokens(text):
    """Rough token estimate (1 token ~ 4 chars for English)."""
    return len(text) // 4


def categorise_by_depth(processed, latest_time):
    """
    Split conversations into tiers based on substance AND recency.

    Recency-aware tier promotion:
    - Recent/mid medium conversations (50-200 words) get promoted to deep
      because current context is more valuable than old deep conversations
    - Recent light conversations with >20 words also get promoted to medium

    Base tiers (by word count):
      - deep: >200 user words
      - medium: 50-200 user words
      - light: <50 user words
    """
    deep = []
    medium = []
    light = []

    promoted_to_deep = 0
    promoted_to_medium = 0

    for c in processed:
        wc = c["user_word_count"]
        age_days = (latest_time - c["create_time"]) / 86400 if c["create_time"] else 9999

        if wc > 200:
            deep.append(c)
        elif wc > 50:
            # Promote recent medium conversations to deep
            if age_days < PROMOTE_MEDIUM_THRESHOLD_DAYS:
                deep.append(c)
                promoted_to_deep += 1
            else:
                medium.append(c)
        elif wc > 20:
            # Promote recent light conversations to medium
            if age_days < PROMOTE_MEDIUM_THRESHOLD_DAYS:
                medium.append(c)
                promoted_to_medium += 1
            else:
                light.append(c)
        else:
            light.append(c)

    # Sort each tier: recent first (descending by create_time)
    for tier in [deep, medium, light]:
        tier.sort(key=lambda c: c["create_time"], reverse=True)

    if promoted_to_deep > 0:
        print(f"  Promoted {promoted_to_deep} recent medium conversations to deep tier")
    if promoted_to_medium > 0:
        print(f"  Promoted {promoted_to_medium} recent light conversations to medium tier")

    return deep, medium, light


def create_batch(conversations, tier, batch_num, max_tokens=60000):
    """
    Create a batch file from a list of conversations.
    Respects a rough token budget. Includes recency_era for each entry.
    """
    batch = {
        "batch_number": batch_num,
        "tier": tier,
        "conversation_count": 0,
        "conversations": [],
    }

    current_tokens = 0

    for conv in conversations:
        if tier == "deep":
            # Include full conversation
            entry = {
                "title": conv["title"],
                "date": conv["date"],
                "recency_era": conv["recency_era"],
                "model": conv["model"],
                "user_word_count": conv["user_word_count"],
                "messages": [],
            }
            for msg in conv["messages"]:
                entry["messages"].append({
                    "role": msg["role"],
                    "text": msg["text"][:8000],  # Cap individual messages
                })
            entry_tokens = estimate_tokens(json.dumps(entry))

        elif tier == "medium":
            # User messages only
            entry = {
                "title": conv["title"],
                "date": conv["date"],
                "recency_era": conv["recency_era"],
                "model": conv["model"],
                "user_word_count": conv["user_word_count"],
                "user_text": conv["user_text"][:4000],
            }
            entry_tokens = estimate_tokens(json.dumps(entry))

        else:  # light
            entry = {
                "title": conv["title"],
                "date": conv["date"],
                "recency_era": conv["recency_era"],
                "model": conv["model"],
                "user_word_count": conv["user_word_count"],
            }
            entry_tokens = estimate_tokens(json.dumps(entry))

        if current_tokens + entry_tokens > max_tokens and batch["conversations"]:
            # This batch is full, signal to caller
            break

        batch["conversations"].append(entry)
        batch["conversation_count"] += 1
        current_tokens += entry_tokens

    return batch, batch["conversation_count"]


def generate_batches(deep, medium, light, max_tokens=60000):
    """Generate all batches across all tiers."""
    batches = []
    batch_num = 1

    # Deep conversations first (already sorted recent-first)
    remaining = list(deep)
    while remaining:
        batch, consumed = create_batch(remaining, "deep", batch_num, max_tokens)
        if consumed == 0:
            # Single conversation too large - force include with truncation
            conv = remaining[0]
            batch = {
                "batch_number": batch_num,
                "tier": "deep",
                "conversation_count": 1,
                "conversations": [{
                    "title": conv["title"],
                    "date": conv["date"],
                    "recency_era": conv["recency_era"],
                    "model": conv["model"],
                    "user_word_count": conv["user_word_count"],
                    "user_text": conv["user_text"][:20000],
                    "note": "Truncated due to length",
                }],
            }
            consumed = 1
        batches.append(batch)
        remaining = remaining[consumed:]
        batch_num += 1

    # Medium conversations
    remaining = list(medium)
    while remaining:
        batch, consumed = create_batch(remaining, "medium", batch_num, max_tokens)
        if consumed == 0:
            consumed = 1  # Force progress
        batches.append(batch)
        remaining = remaining[consumed:]
        batch_num += 1

    # Light conversations (metadata only, can fit many)
    remaining = list(light)
    while remaining:
        batch, consumed = create_batch(remaining, "light", batch_num, max_tokens=80000)
        if consumed == 0:
            consumed = 1
        batches.append(batch)
        remaining = remaining[consumed:]
        batch_num += 1

    return batches


def generate_overview(processed, deep, medium, light, latest_time):
    """Generate a high-level overview/index of the entire export."""

    # Topic frequency from titles
    title_words = Counter()
    for conv in processed:
        words = re.findall(r'[A-Za-z]{3,}', conv["title"].lower())
        for w in words:
            if w not in {"the", "and", "for", "with", "from", "that", "this", "are", "was", "has", "have", "been", "new", "chat"}:
                title_words[w] += 1

    # Monthly activity
    monthly = Counter()
    for conv in processed:
        if conv["create_time"]:
            month = datetime.fromtimestamp(conv["create_time"]).strftime("%Y-%m")
            monthly[month] += 1

    # Model usage
    models = Counter(conv["model"] for conv in processed)

    # Recency era distribution
    era_counts = Counter(conv["recency_era"] for conv in processed)
    era_word_counts = defaultdict(int)
    for conv in processed:
        era_word_counts[conv["recency_era"]] += conv["user_word_count"]

    # Recent title keywords (last 12 months only)
    recent_title_words = Counter()
    for conv in processed:
        if conv["recency_era"] in ("recent", "mid"):
            words = re.findall(r'[A-Za-z]{3,}', conv["title"].lower())
            for w in words:
                if w not in {"the", "and", "for", "with", "from", "that", "this", "are", "was", "has", "have", "been", "new", "chat"}:
                    recent_title_words[w] += 1

    overview = {
        "total_conversations": len(processed),
        "date_range": {
            "earliest": min(c["date"] for c in processed if c["date"] != "unknown"),
            "latest": max(c["date"] for c in processed if c["date"] != "unknown"),
        },
        "total_user_words": sum(c["user_word_count"] for c in processed),
        "tier_counts": {
            "deep": len(deep),
            "medium": len(medium),
            "light": len(light),
        },
        "recency_distribution": {
            era: {"conversations": era_counts.get(era, 0), "user_words": era_word_counts.get(era, 0)}
            for era in ["recent", "mid", "older", "historical"]
        },
        "recency_era_definitions": {
            "recent": "Last 6 months",
            "mid": "6-12 months ago",
            "older": "1-2 years ago",
            "historical": "2+ years ago",
        },
        "model_usage": dict(models.most_common()),
        "monthly_activity": dict(sorted(monthly.items())),
        "top_title_keywords_all_time": dict(title_words.most_common(30)),
        "top_title_keywords_recent": dict(recent_title_words.most_common(30)),
        "conversations_using_gpts": sum(1 for c in processed if c["gizmo_id"]),
    }

    return overview


def generate_title_index(processed):
    """Generate a complete title index sorted by date (recent first)."""
    index = []
    for conv in sorted(processed, key=lambda c: c["create_time"], reverse=True):
        index.append({
            "date": conv["date"],
            "title": conv["title"],
            "words": conv["user_word_count"],
            "model": conv["model"],
            "recency_era": conv["recency_era"],
            "tier": "deep" if conv["user_word_count"] > 200 else ("medium" if conv["user_word_count"] > 50 else "light"),
        })
    return index


def load_user_profile(export_dir):
    """Load user.json and user_settings.json if available."""
    profile = {}

    user_file = os.path.join(export_dir, "user.json")
    if os.path.exists(user_file):
        with open(user_file, "r", encoding="utf-8") as f:
            profile["user"] = json.load(f)

    settings_file = os.path.join(export_dir, "user_settings.json")
    if os.path.exists(settings_file):
        with open(settings_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
            # Extract useful settings, skip noise
            if isinstance(raw, list) and raw:
                settings = raw[0].get("settings", {})
                profile["settings"] = {
                    k: v for k, v in settings.items()
                    if k in ("voice_name", "training_allowed", "developer_mode")
                }

    return profile


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 preprocessor.py <export_dir> <output_dir>")
        sys.exit(1)

    export_dir = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    print("Loading conversations...")
    conversations = load_conversations(export_dir)
    print(f"  Loaded {len(conversations)} conversations")

    # Find the latest conversation timestamp for recency calculations
    latest_time = max(
        (c.get("create_time", 0) for c in conversations),
        default=time.time()
    )
    print(f"  Latest conversation: {datetime.fromtimestamp(latest_time).strftime('%Y-%m-%d')}")

    print("Processing conversations...")
    processed = []
    for conv in conversations:
        try:
            p = process_conversation(conv, latest_time)
            processed.append(p)
        except Exception as e:
            title = conv.get("title", "unknown")
            print(f"  Warning: Failed to process '{title}': {e}")

    print(f"  Processed {len(processed)} conversations successfully")

    # Recency distribution
    era_counts = Counter(c["recency_era"] for c in processed)
    print(f"  Recency: recent={era_counts.get('recent',0)}, mid={era_counts.get('mid',0)}, older={era_counts.get('older',0)}, historical={era_counts.get('historical',0)}")

    print("Categorising by depth (with recency promotion)...")
    deep, medium, light = categorise_by_depth(processed, latest_time)
    print(f"  Deep: {len(deep)}")
    print(f"  Medium: {len(medium)}")
    print(f"  Light: {len(light)}")

    print("Generating overview...")
    overview = generate_overview(processed, deep, medium, light, latest_time)
    with open(os.path.join(output_dir, "00-overview.json"), "w", encoding="utf-8") as f:
        json.dump(overview, f, indent=2)

    print("Generating title index...")
    title_index = generate_title_index(processed)
    with open(os.path.join(output_dir, "01-title-index.json"), "w", encoding="utf-8") as f:
        json.dump(title_index, f, indent=2)

    print("Loading user profile...")
    profile = load_user_profile(export_dir)
    with open(os.path.join(output_dir, "02-user-profile.json"), "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

    print("Generating batches (recent conversations first)...")
    batches = generate_batches(deep, medium, light)
    for batch in batches:
        fname = f"batch-{batch['batch_number']:03d}-{batch['tier']}.json"
        with open(os.path.join(output_dir, fname), "w", encoding="utf-8") as f:
            json.dump(batch, f, indent=2)
    print(f"  Generated {len(batches)} batch files")

    # Summary
    print("\n=== Preprocessing Complete ===")
    print(f"Output directory: {output_dir}")
    print(f"Files generated: {len(batches) + 3}")
    print(f"  - 00-overview.json (high-level stats with recency breakdown)")
    print(f"  - 01-title-index.json (all titles, recent first)")
    print(f"  - 02-user-profile.json (account info)")
    print(f"  - {len(batches)} batch files for Claude to process")

    total_batch_size = sum(
        os.path.getsize(os.path.join(output_dir, f"batch-{b['batch_number']:03d}-{b['tier']}.json"))
        for b in batches
    )
    print(f"  Total batch data: {total_batch_size / 1024 / 1024:.1f}MB")
    print(f"\n  NOTE: Batches are ordered recent-first. The first deep batches")
    print(f"  contain the most current conversations and should be weighted")
    print(f"  most heavily during synthesis.")


if __name__ == "__main__":
    main()
