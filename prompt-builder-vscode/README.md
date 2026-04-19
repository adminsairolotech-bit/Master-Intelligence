# Prompt Builder Chat - VS Code Extension

Simple prompt builder with ON/OFF chatbot toggle for VS Code.

## Features

- **Prompt Builder**: Create structured prompts with Role, Task, Topic, Style, Constraints
- **Chatbot Toggle**: ON/OFF switch to enable/disable chat
- **Dark Theme**: Matches VS Code dark theme
- **Quick Replies**: Interactive response buttons

## Installation

1. Copy this folder to your VS Code extensions folder:
   ```
   Windows: %USERPROFILE%\.vscode\extensions\
   ```

2. Or use VS Code's "Install from VSIX" option

## Usage

1. Open Command Palette (`Ctrl+Shift+P`)
2. Type: `Prompt Builder`
3. Select: `Open Prompt Builder`
4. Toggle the chatbot ON/OFF using the switch
5. Fill in prompt fields and click "Generate Prompt"
6. Click "Send to Chat" to chat

## Files

- `package.json` - Extension manifest
- `extension.js` - Extension entry point with embedded webview
