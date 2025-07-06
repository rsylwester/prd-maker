# Claude Code Instructions

This file contains specific instructions for Claude Code when working on this project.

## Commit Message Guidelines

- Commit messages should not include a Claude attribution footer
- Don't write: 🤖 Generated with [Claude Code](https://claude.ai/code)
- Don't write: Co-Authored-By: Claude <noreply@anthropic.com>
- But still include the 🤖 emoji as the very first character.

## Example Good Commit Message

```
🤖 Add Tech Stack Analysis as 7th step in PRD creation process

- Added TECH_STACK_ANALYSIS as new ProjectStep enum value
- Enhanced Project model with tech_stack_proposal and tech_stack_analysis fields
- Implemented analyze_tech_stack() method in LLMManager
- Created render_tech_stack_analysis_step() UI component
- Updated navigation logic and progress bar to support 7-step process
```

## Example Bad Commit Message

```
Add Tech Stack Analysis as 7th step in PRD creation process

- Added TECH_STACK_ANALYSIS as new ProjectStep enum value
- Enhanced Project model with tech_stack_proposal and tech_stack_analysis fields

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```