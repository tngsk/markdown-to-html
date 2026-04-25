# Editor Setup for Mono

Mono provides custom snippets to enhance your editing experience in editors like VS Code and Zed. These snippets provide auto-completion for Mono components and extensions.

## Generating Snippets

The snippet files are not tracked in Git. You can generate the latest snippets for Mono components and extensions by running the following script from the root of the repository:

```bash
python scripts/generate_snippets.py
```

This script will generate two files:
- `.zed/snippets/markdown.json`
- `.vscode/mono.code-snippets`

## Setup Instructions

### For Zed

Zed supports loading snippets from its configuration directory.

1. Ensure you have run the generation script above.
2. Copy the generated `.zed/snippets/markdown.json` to your Zed user snippets directory:
   - **macOS/Linux**: `~/.config/zed/snippets/markdown.json`

Once copied, the snippets will be automatically available when editing Markdown files in Zed. Type `@[` to see components or `[` for attr_list extensions.

### For VS Code

VS Code can load workspace-specific snippets.

1. Ensure you have run the generation script above.
2. The script creates `.vscode/mono.code-snippets` inside the repository. VS Code will automatically detect and load these snippets whenever you open the Mono workspace.
3. (Optional) If you want these snippets available globally for any Markdown file you edit in VS Code, copy `.vscode/mono.code-snippets` to your user snippets folder:
   - **macOS**: `~/Library/Application Support/Code/User/snippets/`
   - **Linux**: `~/.config/Code/User/snippets/`
   - **Windows**: `%APPDATA%\Code\User\snippets\`

Once loaded, type `@[` to see components or `[` for attr_list extensions when editing Markdown files.
