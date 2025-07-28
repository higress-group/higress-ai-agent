import os
from dotenv import load_dotenv
from safe_agent import SafeAssistant
from qwen_agent.utils.output_beautify import typewriter_print
from qwen_agent.gui import WebUI

class Agent:
    def __init__(self):
        self.llm_assistant = self._init_agent_service()

    def _init_agent_service(self):
        llm_cfg = {
            'model': os.getenv('MODEL_NAME'),
            'model_server': os.getenv('MODEL_SERVER'),
            'api_key': os.getenv('DASHSCOPE_API_KEY'),
            'generate_cfg': {
                'extra_body': {
                    'enable_thinking': False
                },
            },
        }

        if os.getenv('DASHSCOPE_API_KEY') == None:
            raise ValueError("Please set environment variable DASHSCOPE_API_KEY")

        api_mcp_url = os.getenv("HIGRESS_API_MCP_SERVER_URL")
        if api_mcp_url == None:
            raise ValueError("Please set environment variable HIGRESS_API_MCP_SERVER_URL")

        tools = [{
            "mcpServers": {
                "higress-api-mcp-server": {
                    "type": "sse",
                    "url": api_mcp_url
                },
                "kubectl-ai-mcp-server": {
                    "command": "kubectl-ai",
                    "args": ["--mcp-server"]
                },
            }
        }]

        system_prompt="""
        你是一个Higress社区的运维和API管理助手，
        你可以调用higress-ai-mcp-server进行higress相关的运维和API管理，
        
        你可以调用kubectl-ai-mcp-server进行Kubernetes集群的运维和管理。
        
        你可以调用 kubectl exec + curl 工具进行 envoy/istio 相关 debug 接口的请求
        对于debug可能很有用的工具
        /debug/configz 接口可以获取网关配置并分析（higress-controller中）
        higress-controller和higress-gateway的容器日志
        """

        memory_file_path = os.getenv('MEMORY_FILE_PATH')
        if not memory_file_path:
            memory_file_path = os.path.join(os.path.dirname(__file__), 'memory')
        try:
            with open(memory_file_path, 'r', encoding='utf-8') as f:
                memory_prompt = f.read()
        except FileNotFoundError:
            print("memory文件不存在")
            memory_prompt = ""

        bot = SafeAssistant(
            llm=llm_cfg,
            name='higress-report-agent',
            function_list=tools,
            description="I am Higress-ops-api-agent, I can help you with operations and API management",
            system_message=system_prompt+memory_prompt
        )
        return bot

    def interactive_mode(self):
        bot = self.llm_assistant
        # This stores the chat history.
        messages = []
        while True:
            query = input('\nuser query: ')
            if query.lower() in ['exit', 'quit']:
                print("Exiting")
                break
            # Append the user query to the chat history.
            messages.append({'role': 'user', 'content': query})
            response = []
            response_plain_text = ''
            print('bot response:')
            for response in bot.run(messages=messages):
                # Streaming output.
                response_plain_text = typewriter_print(response, response_plain_text)
            # Append the bot responses to the chat history.
            messages.extend(response)


    def web_mode(self):
        WebUI(self.llm_assistant).run()

def main():
    load_dotenv()

    agent = Agent()

    # agent.web_mode()

    agent.interactive_mode()


if __name__ == '__main__':
    main()
