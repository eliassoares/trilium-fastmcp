# trilium-fastmcp

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server for [Trilium Notes](https://github.com/TriliumNext/Trilium), built with [FastMCP](https://github.com/PrefectHQ/fastmcp).

This project exposes Trilium's [ETAPI](https://docs.triliumnotes.org/user-guide/advanced-usage/etapi/) as MCP tools, enabling LLMs and AI agents to interact with your Trilium instance.

## ETAPI Endpoints TODO

### App Info

- [x] `GET /etapi/app-info` — get server version and info

### Notes

- [x] `GET /etapi/notes` — search notes
- [x] `GET /etapi/notes/:noteId` — get note by ID
- [x] `POST /etapi/create-note` — create a new note
- [x] `PATCH /etapi/notes/:noteId` — update note metadata
- [x] `DELETE /etapi/notes/:noteId` — delete a note
- [x] `GET /etapi/notes/:noteId/content` — get note content
- [x] `PUT /etapi/notes/:noteId/content` — update note content
- [x] `GET /etapi/notes/:noteId/export` — export a note
- [x] `POST /etapi/notes/:noteId/revision` — create a note revision
- [x] `GET /etapi/notes/:noteId/attachments` — list note attachments
- [x] `GET /etapi/notes/history` — get note history
- [x] `GET /etapi/notes/:noteId/revisions` — list note revisions
- [x] `POST /etapi/notes/:noteId/undelete` — undelete a note

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

- [ ] `POST /etapi/auth/login` — login
- [ ] `POST /etapi/auth/logout` — logout / invalidate token

### Backup

- [ ] `PUT /etapi/backup/:backupName` — create a backup

### Special Notes

- [ ] `GET /etapi/inbox/:date` — get inbox note for a date
- [ ] `GET /etapi/calendar/days/:date` — get day note
- [ ] `GET /etapi/calendar/weeks/:week` — get week note
- [ ] `GET /etapi/calendar/months/:month` — get month note
- [ ] `GET /etapi/calendar/years/:year` — get year note

### Revisions

- [x] `GET /etapi/revisions/:revisionId` — get revision by ID
- [x] `GET /etapi/revisions/:revisionId/content` — get revision content

## Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/trilium-fastmcp.git
cd trilium-fastmcp

# Install dependencies and pre-commit hooks
make install
```

## Configuration

The server requires a Trilium ETAPI token. You can obtain one from **Trilium → Options → ETAPI**.

Set the following environment variables (or create a `.env` file):

| Variable | Default | Description |
|---|---|---|
| `TRILIUM_URL` | — | Base URL of your Trilium instance |
| `TRILIUM_TOKEN` | — | ETAPI authentication token |
| `HOST` | `127.0.0.1` | Server bind address |
| `PORT` | `6969` | Server port |
| `UPDATING_DISABLED` | `true` | When `true`, disables all write tools at startup |
| `DELETING_DISABLED` | `true` | When `true`, disables all delete tools at startup |

## Running

```bash
# With Docker (recommended)
make build
make run
```

The MCP Inspector is available at `http://localhost:6274`. Use `http://trilium-fastmcp:6969/mcp` as the server URL inside the inspector.

## Development

```bash
make lint        # Run linter
make fix         # Run linter with auto-fix
make format      # Run formatter
make typecheck   # Run type checker (strict)
make security    # Run bandit security scan
make audit       # Run dependency vulnerability check
make check       # Run all checks
make test        # Run tests
```
