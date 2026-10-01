# Austin shared agent workflows

Ten skills: Drive evidence, Drive maintenance, transaction deadlines, appraisal workfiles, reZEN document preparation, automation repair, daily operations, agent handoff, PLAUD intake, and Gemini Workspace integration.

Canonical library: docs/austin-agent-workflows/. Native discovery copies: .agents/skills/ for Codex and .github/skills/ for Copilot. Root instructions route to the appropriate copy. Resolve referenced integration documents from integrations/austin-skills/ and the reZEN helper from scripts/austin-skills/rezen_organizer.py. ChatGPT uses CHATGPT_KNOWLEDGE.md with CHATGPT_INSTRUCTIONS.md. Roman uses ROMAN_INSTRUCTIONS.md; its runtime discovery remains unverified. Gemini uses the integration adapter; saving it does not configure a Gem.

Repository scope and existing instructions govern. Apply business skills only to matching business requests; they do not replace project coding conventions. In appraisal-only projects, professional restrictions in the project README also govern. No reusable skill grants permission to send, sign, publish, delete, or change sharing.

Check: python docs/austin-agent-workflows/validate.py; python docs/austin-agent-workflows/test_install.py; node integrations/austin-skills/test_workspace_bridge.cjs. Live model evaluations and runtime installation remain separate. See EVALUATION.md and per-skill evals.json (60 authored cases, not executed model evaluations).

Public-ready package: no live folder IDs, client transcripts, credentials, or signed audio URLs. Configure the actual private destinations in Apps Script properties. The provided script performs source preparation with readback and duplicate prevention, and does not install an automatic schedule.
