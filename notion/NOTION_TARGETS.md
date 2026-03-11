# Notion Targets (NO TOKENS)

This file stores **Notion page/database identifiers and links** used by this OpenClaw workspace.
It must **not** contain API tokens.

## Notion API token location (reference only)

- Token file: `~/.config/notion/api_key`
- Permissions: `chmod 600 ~/.config/notion/api_key`

## Primary pages

### Arthos2 page (connected to integration)

- Page URL: https://www.notion.so/31e608063a3b80f48468dd3fdc391fba
- Page ID (no dashes): `31e608063a3b80f48468dd3fdc391fba`

## Databases / Data sources

### Arthos2-Memory Store

- Type: child database
- Database URL: https://www.notion.so/31e608063a3b8164ad8dedf7b49cfb64
- Database ID (for creating pages): `31e608063a3b8164ad8dedf7b49cfb64`
- Data Source ID (for querying): `31e608063a3b81e68195000b8d1380ad`

## Notes

- Notion may return 404 for resources that are not shared with the integration.
- If you change/rotate the token, update only `~/.config/notion/api_key` (never paste tokens into this file).
