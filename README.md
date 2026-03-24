# trilium-fastmcp

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server for [Trilium Notes](https://github.com/TriliumNext/Trilium), built with [FastMCP](https://github.com/PrefectHQ/fastmcp).

This project exposes Trilium's [ETAPI](https://docs.triliumnotes.org/user-guide/advanced-usage/etapi/) as MCP tools, enabling LLMs and AI agents to interact with your Trilium instance.

## ETAPI Endpoints TODO

### App Info

- [ ] `GET /etapi/app-info` — get server version and info

### Notes

- [ ] `GET /etapi/notes` — search notes
- [ ] `GET /etapi/notes/:noteId` — get note by ID
- [ ] `POST /etapi/create-note` — create a new note
- [ ] `PATCH /etapi/notes/:noteId` — update note metadata
- [ ] `DELETE /etapi/notes/:noteId` — delete a note
- [ ] `GET /etapi/notes/:noteId/content` — get note content
- [ ] `PUT /etapi/notes/:noteId/content` — update note content
- [ ] `GET /etapi/notes/:noteId/export` — export a note
- [ ] `POST /etapi/notes/:noteId/import` — import into a note
- [ ] `POST /etapi/notes/:noteId/revision` — create a note revision
- [ ] `GET /etapi/notes/:noteId/attachments` — list note attachments

### Branches

- [ ] `GET /etapi/branches/:branchId` — get branch by ID
- [ ] `POST /etapi/branches` — create a branch
- [ ] `PATCH /etapi/branches/:branchId` — update a branch
- [ ] `DELETE /etapi/branches/:branchId` — delete a branch
- [ ] `POST /etapi/refresh-note-ordering/:parentNoteId` — refresh child note ordering

### Attributes

- [ ] `GET /etapi/attributes/:attributeId` — get attribute by ID
- [ ] `POST /etapi/attributes` — create an attribute
- [ ] `PATCH /etapi/attributes/:attributeId` — update an attribute
- [ ] `DELETE /etapi/attributes/:attributeId` — delete an attribute

### Attachments

- [ ] `POST /etapi/attachments` — create an attachment
- [ ] `GET /etapi/attachments/:attachmentId` — get attachment by ID
- [ ] `PATCH /etapi/attachments/:attachmentId` — update attachment metadata
- [ ] `GET /etapi/attachments/:attachmentId/content` — get attachment content
- [ ] `PUT /etapi/attachments/:attachmentId/content` — update attachment content
- [ ] `DELETE /etapi/attachments/:attachmentId` — delete an attachment

### Auth

- [ ] `POST /etapi/auth/logout` — logout / invalidate token

### Backup

- [ ] `PUT /etapi/backup/:backupName` — create a backup

### Special Notes

- [ ] `GET /etapi/inbox/:date` — get inbox note for a date
- [ ] `GET /etapi/calendar/days/:date` — get day note
- [ ] `GET /etapi/calendar/week-first-day/:date` — get first day of week note
- [ ] `GET /etapi/calendar/weeks/:week` — get week note
- [ ] `GET /etapi/calendar/months/:month` — get month note
- [ ] `GET /etapi/calendar/years/:year` — get year note

## Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/trilium-fastmcp.git
cd trilium-fastmcp

# Create virtual environment and install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

## Configuration

The server requires a Trilium ETAPI token. You can obtain one from **Trilium → Options → ETAPI**.

## Development

```bash
# Run linter
uv run ruff check .

# Run formatter
uv run ruff format .

# Run type checker
uv run mypy .
```
