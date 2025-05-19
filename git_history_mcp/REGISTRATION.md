# Registering the Git History MCP Server with Claude Code

This guide explains how to register the Git History MCP server with Claude Code, allowing Claude to look up and analyze git repository history.

## Prerequisites

1. [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code/overview) installed
2. Python 3.10+ installed
3. [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Installation Steps

### 1. Install the MCP Server Package

First, navigate to the git_history_mcp directory and install the package:

```bash
cd /Users/oleksandr/projects/lfnt/git_history_mcp

# Using uv (recommended)
uv pip install .

# Or using pip
pip install .
```

### 2. Register the MCP Server with Claude Code

Use the Claude Code CLI to register the MCP server:

```bash
# For user-wide registration (available in all projects)
claude mcp add history_lookup -s user -- uv "--directory" /Users/oleksandr/projects/lfnt/git_history_mcp run history_lookup.py

# OR for project-specific registration (only available in current project)
claude mcp add history_lookup -- uv "--directory" /Users/oleksandr/projects/lfnt/git_history_mcp run history_lookup.py
```

### 3. Verify Registration

Check that the MCP server is registered correctly:

```bash
claude mcp list
```

You should see `history_lookup` in the list of available MCP servers.

## Usage

Once registered, you can use the git history lookup tool in Claude Code with:

```
/mcp history_lookup.history_lookup --repo_path="/path/to/git/repo" --query="Your query about the repository"
```

### Optional: Add a Custom Command

To make it easier to use the tool, you can add a custom command to your project:

1. Create a `.claude/commands` directory in your project (if it doesn't exist):
   ```bash
   mkdir -p /path/to/your/project/.claude/commands
   ```

2. Copy the get_history.md command:
   ```bash
   cp /Users/oleksandr/projects/lfnt/git_history_mcp/commands/get_history.md /path/to/your/project/.claude/commands/
   ```

3. Now you can use the command in Claude Code:
   ```
   /get_history
   ```

## Troubleshooting

If you encounter issues:

1. Make sure the main FastAPI app is running:
   ```bash
   python /Users/oleksandr/projects/lfnt/run.py
   ```

2. Check that your MCP server can communicate with the FastAPI app:
   ```bash
   python /Users/oleksandr/projects/lfnt/git_history_mcp/history_lookup.py --test --test-repo=/path/to/git/repo
   ```

3. Verify that the git repository is valid:
   ```bash
   git -C /path/to/git/repo rev-parse --is-inside-work-tree
   ```