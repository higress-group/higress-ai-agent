import json
from qwen_agent.agents import Assistant
from qwen_agent.llm.schema import Message, ASSISTANT


class SafeAssistant(Assistant):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pending_tool = None  # 记录待确认的工具调用

        # 定义白名单，包含所有只读操作
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

        # 定义 kubectl 只读命令白名单
        self._kubectl_readonly_commands = {
            'get', 'describe', 'logs', 'top', 'explain', 'version',
            'cluster-info', 'config', 'api-resources', 'api-versions'
        }

    def _is_safe_tool(self, tool_name: str) -> bool:
        """检查工具是否在白名单中（只读操作）"""
        return tool_name in self._whitelist_tools

    def _is_safe_kubectl_command(self, tool_args) -> bool:
        """检查 kubectl 命令是否安全（只读操作）"""
        # 如果 tool_args 是字符串，尝试解析为 JSON
        if isinstance(tool_args, str):
            try:
                tool_args = json.loads(tool_args)
            except json.JSONDecodeError:
                return False

        # 确保 tool_args 是字典
        if not isinstance(tool_args, dict):
            return False

        # 检查是否存在 command 参数
        if 'command' not in tool_args:
            return False

        command = tool_args.get('command', '')

        # 如果存在 modifies_resource 参数且为 "no"，则认为是安全的
        if 'modifies_resource' in tool_args:
            return tool_args.get('modifies_resource', '').lower() == 'no'

        # 如果没有 modifies_resource 参数，检查是否是只读 kubectl 命令
        if command.startswith('kubectl '):
            # 提取 kubectl 子命令
            cmd_parts = command.split()
            if len(cmd_parts) >= 2:
                kubectl_subcommand = cmd_parts[1]
                return kubectl_subcommand in self._kubectl_readonly_commands

        return False

    def _call_tool(self, tool_name: str, tool_args: dict, **kwargs) -> str:
        # 如果是白名单中的只读操作，直接执行
        if self._is_safe_tool(tool_name):
            return super()._call_tool(tool_name, tool_args, **kwargs)

        # 检查是否是安全的 kubectl 命令
        if self._is_safe_kubectl_command(tool_args):
            return super()._call_tool(tool_name, tool_args, **kwargs)

        # 非白名单操作需要用户确认
        print(f"检测到敏感工具调用: {tool_name}，参数: {tool_args}")
        user_input = input("是否允许调用该工具？请输入 y/n+理由（如 y 或 n+原因）：").strip()

        if user_input.lower() == 'y':
            return super()._call_tool(tool_name, tool_args, **kwargs)
        else:
            reason = user_input[1:].strip(" +") if len(user_input) > 1 else "未提供理由"
            return f"用户拒绝调用工具，理由：{reason}"