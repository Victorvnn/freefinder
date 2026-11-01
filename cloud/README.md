# Public cloud state

`state.json` is created automatically by the first GitHub Actions run. It is
not supplied with example products. It retains actual observed offers,
limited change history, and sanitized run outcomes between ephemeral jobs.

This file is PUBLIC when stored in the GitHub repository or Pages snapshot.
Never add secrets, customer information, full addresses, phone notes,
favorites, marketplace credentials, cookies or private source data here.

Do not delete state.json to retry a source: it preserves source-specific
request intervals. Use the workflow manually; it respects those intervals.
