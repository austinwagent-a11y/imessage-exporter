# PLAUD and Gemini Workspace setup

Use the actual supported PLAUD app/MCP in the intended host. Select an observed recording ID and fetch raw transcript pages with speaker/timestamp provenance; notes are AI-generated context. Empty transcripts may be pending. Recording-name searches are not transcript searches.

Create or select a private Transcript Inbox and Gemini Source Documents folder. Configure their verified IDs in Apps Script Project Settings > Script Properties as PLAUD_INBOX_ID and GEMINI_SOURCES_ID. Install plaud_gemini_workspace.gs under the intended account, authorize Drive/Docs access, and manually run prepareGeminiSources. It examines at most 100 input entries and prepares at most 10 source Docs per run. It accepts TXT/MD/JSON exports, retains source links, records hash receipts, verifies writes, and refuses automatic retries of incomplete checkpoints. Inspect execution reports and any incomplete documents before retrying.

Attach source Docs and GEMINI_WORKSPACE_INSTRUCTIONS.md to the intended Gemini app or Gem. No Spark API endpoint is assumed. This script prepares documents, not AI summaries; Gemini configuration is a separate step. No recurring trigger, live AI job, client outreach, or private data transmission is installed by these source files.

Integration code is verified with mocks, not a production Apps Script run. Each host's authorization and data access must be tested separately. Keep client transcripts and live configuration outside reusable skills and Git history.
