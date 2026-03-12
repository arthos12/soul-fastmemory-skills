# fast-memory bootstrap

Install target: immediate use after installation.

After installation, the agent should treat this skill as the default memory workflow for:
- new-session restore
- session save / handoff
- recent full-session fallback
- old-session transfer / downgrade / cleanup

Default behavior:
1. On new session, restore using the retrieval rules in SKILL.md.
2. On save / handoff, classify and store using the storage rules in SKILL.md.
3. Keep recent full sessions as the hot buffer.
4. Transfer sessions older than 3 days into extracted storage.
5. Downgrade colder extracted content when storage becomes too large.

This skill is meant to be used automatically when memory behavior is needed, not only when explicitly requested.
