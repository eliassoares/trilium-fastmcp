# trilium-fastmcp

[![CI](https://github.com/eliassoares/trilium-fastmcp/actions/workflows/ci.yml/badge.svg)](https://github.com/eliassoares/trilium-fastmcp/actions/workflows/ci.yml)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

[Trilium Notes](https://github.com/TriliumNext/Trilium) is a hierarchical note-taking application focused on building large personal knowledge bases. Notes are organized as a tree (with support for cloning nodes into multiple locations), and the app supports rich text, code blocks, relations between notes, scripting, and a journaling system based on day/week/month/year notes.

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server for Trilium Notes, built with [FastMCP](https://github.com/PrefectHQ/fastmcp).

This project exposes Trilium's [ETAPI](https://docs.triliumnotes.org/user-guide/advanced-usage/etapi/) as MCP tools, enabling LLMs and AI agents to interact with your Trilium instance.

> Developed and tested against **Trilium `0.102.1-test-260331-111701`**. Other versions may work but are not guaranteed.

## Available Tools

### General

| Tool | Description |
|------|-------------|
| `get_application_information` | Returns information about the running Trilium instance |

### Notes

| Tool | Description |
|------|-------------|
| `search_notes` | Search notes using a query string as described in the [Trilium search docs](https://triliumnext.github.io/Docs/Wiki/search.html) |
| `get_note` | Returns a note identified by its ID |
| `get_note_content` | Returns note content identified by its ID |
| `export_note` | Exports a ZIP file of a given note subtree. Use `root` as noteId to export the whole document |
| `get_note_attachments` | Returns all attachments for a note identified by its ID |
| `get_note_history` | Returns recent changes including note creations, modifications, and deletions |
| `get_note_revisions` | Returns all revisions for a note identified by its ID |
| `get_inbox_note` | Returns the inbox note for a given date. Uses a fixed note (via `#inbox` label) or a journal day note |
| `get_day_note` | Returns a day note for a given date. Created if it doesn't exist |
| `get_week_note` | Returns a week note for a given ISO week (format `YYYY-Www`). Created if it doesn't exist |
| `get_month_note` | Returns a month note for a given month. Created if it doesn't exist |
| `get_year_note` | Returns a year note for a given year. Created if it doesn't exist |
| `create_note` | Create a note and place it into the note tree |
| `update_note_metadata` | Update a note's metadata (title, type, mime, etc.) identified by its ID |
| `update_note_content` | Updates note content identified by its ID |
| `create_note_revision` | Create a note revision for the given note |
| `delete_note` | Deletes a single note based on its ID |
| `undelete_note` | Restore a deleted note. The note must be deleted and have at least one undeleted parent |

### Branches

| Tool | Description |
|------|-------------|
| `get_branch` | Returns a branch identified by its ID |
| `create_branch` | Create a branch (clone a note to a different location in the tree). Updates an existing branch if one already exists between the same parent and child |
| `update_branch` | Update prefix and notePosition on a branch identified by its ID |
| `refresh_note_order` | Trigger a re-ordering push to all connected clients for a given parent note. Call this after updating notePosition on branches to make the new order visible immediately |
| `delete_branch` | Deletes a branch by its ID. If this is the last branch of the child note, the note itself is deleted too |

### Attributes

| Tool | Description |
|------|-------------|
| `get_attribute` | Returns an attribute identified by its ID |
| `create_attribute` | Create a label or relation attribute for a note |
| `update_attribute` | Update an attribute identified by its ID |
| `delete_attribute` | Delete an attribute identified by its ID |

### Attachments

| Tool | Description |
|------|-------------|
| `create_attachment` | Create a text-like attachment for a note. Binary attachments are not supported |
| `get_attachment` | Returns an attachment identified by its ID |
| `get_attachment_content` | Returns attachment content identified by its ID |
| `update_attachment_metadata` | Update role, mime, title, or position of an attachment identified by its ID |
| `update_attachment_content` | Updates attachment content identified by its ID |
| `delete_attachment` | Deletes an attachment by its ID |

### Backup

| Tool | Description |
|------|-------------|
| `create_backup` | Create a database backup under a given name (e.g. `"now"` → `backup-now.db`) |

### Revisions

| Tool | Description |
|------|-------------|
| `get_revision` | Returns a revision identified by its ID |
| `get_revision_content` | Returns revision content identified by its ID |

### Web Clipper

| Tool | Description |
|------|-------------|
| `clip_url` | Clip a web page and save it as a Trilium note. Fetches the URL, extracts readable content, and creates a note with metadata labels. Saved under a `Web Clipper` note in root by default |

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

| Variable            | Default     | Description                                                       |
| ------------------- | ----------- | ----------------------------------------------------------------- |
| `TRILIUM_URL`       | —           | Base URL of your Trilium instance                                 |
| `TRILIUM_TOKEN`     | —           | ETAPI authentication token                                        |
| `HOST`              | `127.0.0.1` | Server bind address                                               |
| `PORT`              | `6969`      | Server port                                                       |
| `UPDATING_DISABLED` | `true`      | When `true`, disables all write tools at startup                  |
| `DELETING_DISABLED` | `true`      | When `true`, disables all delete tools at startup                 |
| `MCP_AUTH_TOKEN`    | —           | Optional. Static bearer token to protect the MCP server           |
| `MCP_CLIENT_ID`     | —           | Optional. Client identifier (required if `MCP_AUTH_TOKEN` is set) |

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

## Web Clipper

The web clipper logic in this project was implemented using AI and was based on the ideas and behavior from [`zadam/trilium-web-clipper`](https://github.com/zadam/trilium-web-clipper).

### Current design

The `clip_url` tool no longer tries to persist clipped images through raw ETAPI attachment uploads. In practice, `POST /etapi/attachments` plus `PUT /etapi/attachments/:attachmentId/content` did not provide a reliable binary upload path for clipped images in Trilium, and produced either corrupted files or server-side `500` errors depending on the payload format.

Because of that, the implementation now follows Trilium's native clipper flow instead of forcing image persistence through ETAPI:

- fetch the page HTML
- extract the readable article content
- find `<img>` tags in the extracted HTML
- download each image with the external web client
- convert each downloaded image to a `data:` URL
- replace each image `src` with a temporary clipper image ID
- send the clip to Trilium through the native clipper endpoint
- let Trilium create the final note and image attachments internally

This matches the design of the original Trilium web clipper more closely and is what allows the final note HTML to use Trilium-native image references such as:

```html
<img src="api/attachments/<attachmentId>/image/<filename>" />
```

These references are recognized by Trilium as real embedded note images, so the created attachments are not marked for automatic erasure.

### Why this does not use ETAPI attachments directly

This project is primarily an ETAPI-based MCP wrapper, but web clipping is the main exception.

During implementation and live validation against Trilium:

- `POST /etapi/attachments` with inline base64 created attachments whose content was base64 text, not image bytes
- `PUT /etapi/attachments/:attachmentId/content` with raw binary returned server errors or corrupted binary content
- even when the attachment record existed, the note HTML still did not use the native image reference format expected by the Trilium UI

So the final decision was:

- use the native clipper API for note creation with images
- use ETAPI only for post-processing around note placement and metadata

### Parent note behavior

The native Trilium clipper saves notes according to Trilium's own clipper inbox rules. By default this is usually the day note, or another note configured in Trilium with the `clipperInbox` label.

This project adds a second step after the native clipper creates the note:

- if `parent_note_id` is provided, the server creates a branch for the clipped note under that parent
- if the note was initially created under the clipper inbox/day note, the server removes the original branch so the note ends up only under the requested parent

When no `parent_note_id` is provided, the server looks for a note named `Web Clipper` directly under `root`. If it does not exist, the server creates that note automatically, and then moves the clipped note there.

In other words:

- `parent_note_id` provided: clip natively, then move under that note
- `parent_note_id` omitted: clip natively, then move under `root/Web Clipper`

### Image failure behavior

If an image cannot be downloaded or validated during clipping:

- the clip still succeeds
- a warning is returned in `ClipResult.warnings`
- that image keeps its original external URL in the clipped HTML

This means the note is still created even if some images cannot be internalized.

### Labels and metadata

The native clipper payload carries the main clipping metadata, and this project also adds a small ETAPI post-processing step for labels:

- `iconClass = "bx bx-globe"`
- `siteName`, when available
- `clipDate`, using the server date

The `publishedDate` label, when available from the extracted page metadata, is sent in the native clipper payload so Trilium can persist it as part of the clipping flow.

### Use case example

Example instruction to an MCP client:

```text
save this page https://eliassoares.com/2019/mova-se on KfLcNMe8YAMg note
```

That should call the clipping flow with:

- `url = "https://eliassoares.com/2019/mova-se"`
- `parent_note_id = "KfLcNMe8YAMg"`

If you omit the destination note, the clip will be saved under the `Web Clipper` note instead.

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
        "-y",
        "mcp-remote",
        "http://<your-server-ip>:6969/mcp",
        "--allow-http",
        "--header",
        "Authorization: Bearer <your-mcp-auth-token>"
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
      "args": [
        "-y",
        "mcp-remote",
        "http://<your-server-ip>:6969/mcp",
        "--allow-http"
      ]
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
        "-y",
        "mcp-remote",
        "http://<your-server-ip>:6969/mcp",
        "--allow-http",
        "--header",
        "Authorization: Bearer <your-mcp-auth-token>"
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
