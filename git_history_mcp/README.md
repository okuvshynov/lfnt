# Git History MCP Server

## Overview

This MCP server provides a tool for Claude and other LLMs to analyze git repository history. It helps with codebase understanding by identifying the most relevant commits for a given query.

## Features

- Analyzes git repository history
- Takes a repository path and query as input
- Returns relevant commit IDs and references to help understand the codebase
- Integrates with Claude Code via MCP protocol

## Installation

```bash
# Install with uv
uv pip install .

# Register the MCP server with Claude Code
claude mcp add history_lookup -s user -- uv "--directory" /Absolute/path/to/git_history_mcp run history_lookup.py
```

## Usage

From Claude Code, you can use the following to analyze a git repository:

```
/mcp history_lookup.history_lookup --repo_path="/path/to/git/repo" --query="What commits are relevant to the authentication feature?"
```

This will analyze the repository's history and return the most relevant commits for the given query.