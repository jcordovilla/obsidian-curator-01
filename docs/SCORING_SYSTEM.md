# Simplified Scoring System

## Overview

The scoring system has been completely redesigned for clarity and effectiveness. It now uses a **single-pass LLM assessment** with clear context about input types.

## How It Works

### 1. Single LLM Call
- **One comprehensive assessment** returns a usefulness score (0-1)
- No complex blending of multiple scores
- Clear rubric with specific examples

### 2. Input Context
The LLM is explicitly told it will receive:
- Personal work logs, timesheets, meeting notes
- Web-clipped articles (with residual boilerplate)
- Conference/event emails
- Technical guides and research papers
- User's own notes and reflections
- PDFs, images (OCR), transcribed audio

### 3. Scoring Rubric

| Score Range | Category | Description | Examples |
|-------------|----------|-------------|----------|
| **0.70-1.00** | 🟢 HIGH VALUE | Reusable knowledge about sectors/markets/policy | Spain toll revenue, Indonesia credit rating, energy access strategies |
| **0.45-0.69** | 🟡 MEDIUM VALUE | Background knowledge, context, frameworks | PPP model overviews, infrastructure finance intro |
| **0.25-0.44** | 🟠 LOW VALUE | Minimal reusable knowledge | Generic tips, promotional material |
| **0.00-0.24** | 🔴 NO VALUE | Not reusable, discard | Timesheets, receipts, to-do lists, corrupted content |

### 4. Decision Thresholds

```
keep_threshold: 0.45    # Keep anything with medium+ value
gray_margin: 0.20       # Creates triage zone 0.25-0.45
```

**Decisions:**
- **KEEP**: score ≥ 0.45 (medium to high value)
- **TRIAGE**: 0.25 ≤ score < 0.45 (low value, needs review)
- **DISCARD**: score < 0.25 (no reusable value)

### 5. Safety Net
A minimal heuristic richness check caps obviously corrupted/empty content at 0.25 max score, even if the LLM is overly generous.

## Key Improvements

### ✅ Removed Complexity
- **Eliminated**: 3-stage assessment (fast classifier + deep LLM + heuristics)
- **Eliminated**: Score blending (70% LLM + 30% classifier)
- **Eliminated**: Separate relevance/credibility/depth dimensions
- **Result**: One clear usefulness score

### ✅ Better Context
The LLM now understands:
- **What types of content it will see** (timesheets vs. articles vs. guides)
- **The purpose** (reusability as knowledge for writing/analysis)
- **Specific examples** of what to keep vs. discard

### ✅ Clear Rubric
- Explicit examples in each score range
- Focus on "reusable knowledge" not abstract "relevance"
- Clear distinction: administrative tracking ❌ vs. professional insights ✅

## Example Evaluations

| Content | Old System | New System | Correct? |
|---------|------------|------------|----------|
| "April 3rd: Met with Pak Jusuf, reviewed memo" | 0.39 (triage) | ~0.15 (discard) | ✅ |
| "Spain toll revenue impact article" | 0.478 (triage) | ~0.75 (keep) | ✅ |
| "Energy access in Sub-Saharan Africa" | 0.331 (discard) | ~0.70 (keep) | ✅ |
| "WEDC Water & Sanitation Guides" | 0.400 (triage) | ~0.65 (keep) | ✅ |

## Technical Details

### Code Changes
- `analyze.py`: New `get_llm_usefulness_score()` function replaces `get_llm_relevance_score()`
- `analyze.py`: Simplified `analyze_features()` - no relevance_score parameter
- `analyze.py`: Simplified `score_usefulness()` - returns LLM score directly
- `main.py`: Removed publication_readiness blending
- `config.py`: Updated thresholds (0.45/0.20 vs. 0.48/0.10)

### Models Used
- **Main scoring**: `llama3.1:8b` (temp=0.15 for consistency)
- **Classification**: `llama3.1:8b` (still used for categories/tags/entities)
- **Embeddings**: `nomic-embed-text` (for FAISS index)

### Prompt Engineering
The new prompt:
1. Explains input diversity upfront
2. Defines evaluation purpose clearly
3. Uses emoji + concrete examples for each tier
4. Emphasizes "reusable knowledge" not "professional relevance"
5. Includes anti-hallucination instructions
6. Asks for 2-3 sentence reasoning

## Next Steps

1. Test on the same 10 notes to validate improvements
2. Monitor triage ratio (should drop from 50% to ~20%)
3. Verify timesheets are discarded, sector content is kept
4. Adjust thresholds if needed based on real-world performance

