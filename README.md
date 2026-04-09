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
| `MCP_AUTH_TOKEN` | — | Optional. Static bearer token to protect the MCP server |
| `MCP_CLIENT_ID` | — | Optional. Client identifier (required if `MCP_AUTH_TOKEN` is set) |

## Running

```bash
# With Docker (recommended)
make build
make run
```

The MCP Inspector is available at `http://localhost:6274`. Use `http://trilium-fastmcp:6969/mcp` as the server URL inside the inspector.

## Safety Defaults

By default, both update and delete tools are **disabled** at startup. This prevents accidental modifications to your Trilium notes. To enable them, set the following environment variables:

```bash
UPDATING_DISABLED=false  # Enable update tools (update note metadata, content, etc.)
DELETING_DISABLED=false  # Enable delete tools (delete notes)
```

Only enable these if you trust the LLM and have reviewed how the tools work.

## Authentication

Since Trilium's own ETAPI uses a simple token-based authentication, we chose to keep the MCP server authentication equally simple — no OAuth, no JWT infrastructure required. The server uses a static bearer token via FastMCP's `StaticTokenVerifier`.

When `MCP_AUTH_TOKEN` and `MCP_CLIENT_ID` are both set, the server requires an `Authorization: Bearer <token>` header on all requests. When unset, the server runs without authentication.

**We recommend enabling authentication if your MCP server is accessible externally** (i.e., not just `localhost`).

### Generating tokens

You can generate secure tokens with Python:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Or with OpenSSL:

```bash
openssl rand -base64 32
```

Then add them to your `.env` file:

```bash
MCP_AUTH_TOKEN=<generated-token>
MCP_CLIENT_ID=<generated-client-id>
```

## Client Configuration

### Claude Code

Add to `.mcp.json` (project-level) or `~/.claude/settings.json` (global):

**Without authentication:**

```json
{
  "mcpServers": {
    "trilium": {
      "type": "http",
      "url": "http://<your-server-ip>:6969/mcp"
    }
  }
}
```

**With authentication** (requires [mcp-remote](https://www.npmjs.com/package/mcp-remote) + Node.js):

```json
{
  "mcpServers": {
    "trilium": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "http://<your-server-ip>:6969/mcp",
        "--allow-http",
        "--header", "Authorization: Bearer <your-mcp-auth-token>"
      ]
    }
  }
}
```

> **Note:** Claude Code currently has a [known issue](https://github.com/anthropics/claude-code/issues/7290) where it ignores `Authorization` headers on HTTP transport and forces OAuth discovery. Using `mcp-remote` as a stdio bridge is the recommended workaround.

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

**Without authentication:**

```json
{
  "mcpServers": {
    "trilium": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://<your-server-ip>:6969/mcp", "--allow-http"]
    }
  }
}
```

**With authentication:**

```json
{
  "mcpServers": {
    "trilium": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "http://<your-server-ip>:6969/mcp",
        "--allow-http",
        "--header", "Authorization: Bearer <your-mcp-auth-token>"
      ]
    }
  }
}
```

> **Note:** Both clients require [mcp-remote](https://www.npmjs.com/package/mcp-remote) for authenticated connections (needs Node.js). The `--allow-http` flag is required for non-HTTPS URLs.

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
