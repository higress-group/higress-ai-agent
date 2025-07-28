import json
from qwen_agent.agents import Assistant
from qwen_agent.llm.schema import Message, ASSISTANT


class SafeAssistant(Assistant):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pending_tool = None  # 记录待确认的工具调用

    def _call_tool(self, tool_name: str, tool_args: dict, **kwargs) -> str:
        print(f"检测到敏感工具调用: {tool_name}，参数: {tool_args}")
        user_input = input("是否允许调用该工具？请输入 y/n+理由（如 y 或 n+原因）：").strip()
        if user_input.lower() == 'y':
            return super()._call_tool(tool_name, tool_args, **kwargs)
        else:
            reason = user_input[0:].strip(" +")
            return f"用户拒绝调用工具，理由：{reason if reason else '未提供理由'}"

