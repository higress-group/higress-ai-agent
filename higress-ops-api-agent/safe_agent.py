import json
from qwen_agent.agents import Assistant
from qwen_agent.llm.schema import Message, ASSISTANT


class SafeAssistant(Assistant):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pending_tool = None  # Pending tool invocation awaiting confirmation

        # Whitelist of safe read-only tools (Higress API MCP Server)
        self._whitelist_tools = {
            'get-ai-provider',
            'get-ai-route',
            'get-mcp-server',
            'get-plugin',
            'get-route',
            'get-service-source',
            'list-ai-providers',
            'list-ai-routes',
            'list-mcp-server-consumers',
            'list-mcp-servers',
            'list-routes',
            'list-service-sources'
        }

        # Safe tool name prefixes (automatically considered safe)
        self._safe_tool_prefixes = {
            'higress-ops-mcp-server-get',  # All Higress Ops read operations
        }

        # Whitelist of read-only kubectl subcommands
        self._kubectl_readonly_commands = {
            'get', 'describe', 'logs', 'top', 'explain', 'version',
            'cluster-info', 'config', 'api-resources', 'api-versions'
        }

    def _is_safe_tool(self, tool_name: str) -> bool:
        """Check whether the tool is in the read-only whitelist or matches a safe prefix"""
        # Check exact match in whitelist
        if tool_name in self._whitelist_tools:
            return True
        
        # Check if tool name starts with any safe prefix
        return any(tool_name.startswith(prefix) for prefix in self._safe_tool_prefixes)

    def _is_safe_kubectl_command(self, tool_args) -> bool:
        """Check whether a kubectl command is safe (read-only)"""
        # If tool_args is a string, try to parse it as JSON
        if isinstance(tool_args, str):
            try:
                tool_args = json.loads(tool_args)
            except json.JSONDecodeError:
                return False

        # Ensure tool_args is a dict
        if not isinstance(tool_args, dict):
            return False

        # Ensure 'command' field exists
        if 'command' not in tool_args:
            return False

        command = tool_args.get('command', '')

        # If 'modifies_resource' exists and equals "no", treat as safe
        if 'modifies_resource' in tool_args:
            return tool_args.get('modifies_resource', '').lower() == 'no'

        # If no 'modifies_resource', check whether kubectl subcommand is read-only
        if command.startswith('kubectl '):
            # Extract kubectl subcommand
            cmd_parts = command.split()
            if len(cmd_parts) >= 2:
                kubectl_subcommand = cmd_parts[1]
                return kubectl_subcommand in self._kubectl_readonly_commands

        return False

    def _call_tool(self, tool_name: str, tool_args: dict, **kwargs) -> str:
        # Directly execute read-only whitelisted tools
        if self._is_safe_tool(tool_name):
            return super()._call_tool(tool_name, tool_args, **kwargs)

        # Allow safe kubectl commands
        if self._is_safe_kubectl_command(tool_args):
            return super()._call_tool(tool_name, tool_args, **kwargs)

        # Non-whitelisted operations require user confirmation
        print(f"Sensitive tool invocation detected: {tool_name}, args: {tool_args}")
        user_input = input("Allow invoking this tool? Enter y or n+reason (e.g., y or n+why): ").strip()

        if user_input.lower() == 'y':
            return super()._call_tool(tool_name, tool_args, **kwargs)
        else:
            reason = user_input[1:].strip(" +") if len(user_input) > 1 else "No reason provided"
            return f"User denied tool invocation. Reason: {reason}"