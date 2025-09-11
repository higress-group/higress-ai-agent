import os
from dotenv import load_dotenv
from safe_agent import SafeAssistant
from qwen_agent.utils.output_beautify import typewriter_print
from qwen_agent.gui import WebUI

# todo: change to english
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

        # todo：找出api-mcp-server断联的原因
        tools = [{
            "mcpServers": {
                "higress-api-mcp-server": {
                    "type": "sse",
                    "url": api_mcp_url,
                    "sse_read_timeout": 3000
                },
                "kubectl-ai-mcp-server": {
                    "command": "kubectl-ai",
                    "args": ["--mcp-server"],
                    "sse_read_timeout": 3000
                },
            }
        }]

        system_prompt="""
        你是一个Higress社区的运维和API管理助手，你需要调用各种工具帮用户解决问题
        你的ops能力：
            你可以调用higress-ai-mcp-server进行higress相关的运维和API管理，可以调用k8s工具查看higress的日志
            你可以调用kubectl-ai-mcp-server进行Kubernetes集群的运维和管理，调用 kubectl 进行分析（不要叫用户去执行）
            你可以调用 kubectl exec + curl 工具进行 envoy/istio 相关 debug 接口的请求
        
        一些能帮助你debug的技巧：
            对于debug可能很有用的工具
            /debug/configz 接口可以获取网关配置并分析（higress-controller中）
            higress-controller和higress-gateway的容器日志
            
        一些你和用户沟通的技巧
            调用工具前，一定要跟用户说你的调用目的。遇到报错时，一定要把报错信息输出方便用户诊断
            如果有些工具参数需要用户表明才能精确调用，请务必让用户提供更多信息，比如不要做下面的事
            1. 用户没提及，不要默认域名是example.com
            
        你调用api-mcp-server需要注意的细节（一定要遵守），如果报错，请一一核对这些细节:
            创建mcp服务之前（对应接口是higress-api-mcp-server-add-or-update-mcp-server），如果用户没有指定服务来源，一定要先创建一个服务来源！
             调用 higress-api 时的 domain 形式是 ip+port比如 127.0.0.1:3306，不能只填 ip
             调用 higress-api 时，注意服务来源的形式类似 service-name.service-type，必须要加上 servicetype(比如 static)
             创建后端服务时，必须有明确存在的服务来源，如果没有需要创建一个
             add-or-update-mcp-server接口时，type 不是 database，不要带 dbtype 等 database 才有的参数请求
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

            # 跳过空输入或只包含空白字符的输入
            if not query.strip():
                continue

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


def main():
    load_dotenv()

    agent = Agent()

    # agent.web_mode()

    agent.interactive_mode()


if __name__ == '__main__':
    main()

