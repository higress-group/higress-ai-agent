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

        # Build MCP server configuration
        mcp_servers = {}

        # Check if higress-ops-mcp-server is enabled
        ops_mcp_url = os.getenv("HIGRESS_OPS_MCP_SERVER_URL")
        if ops_mcp_url:
            mcp_servers["higress-ops-mcp-server"] = {
                "type": "sse",
                "url": ops_mcp_url,
                "sse_read_timeout": 3000
            }
            print(f"Enable higress-ops-mcp-server: {ops_mcp_url}")

        # Check if higress-api-mcp-server is enabled
        api_mcp_url = os.getenv("HIGRESS_API_MCP_SERVER_URL")
        if api_mcp_url:
            mcp_servers["higress-api-mcp-server"] = {
                "type": "sse",
                "url": api_mcp_url,
                "sse_read_timeout": 3000
            }
            print(f"Enable higress-api-mcp-server: {api_mcp_url}")

        # Check if kubectl-ai-mcp-server is enabled
        enable_kubectl = os.getenv("ENABLE_KUBECTL_MCP_SERVER", "false").lower() == "true"
        if enable_kubectl:
            mcp_servers["kubectl-ai-mcp-server"] = {
                "command": "kubectl-ai",
                "args": ["--mcp-server"],
                "sse_read_timeout": 3000
            }
            print("Enable kubectl-ai-mcp-server")

        # If no MCP servers are enabled, use empty tool list
        tools = [{"mcpServers": mcp_servers}] if mcp_servers else []

        system_prompt = """
        You are an operations and API management assistant for the Higress community. You should leverage available tools to help the user solve problems end-to-end.
        
        Your Ops capabilities:
            - You can use the higress-api MCP server for Higress operations and API management; you can also use k8s tools to check Higress logs.
            - You can use the kubectl-ai MCP server for Kubernetes operations and management. Run kubectl yourself for analysis; do not ask the user to run commands.
            - You can use kubectl exec + curl to access envoy/istio debug endpoints when needed.
        
        Debugging tips:
            - /debug/configz (from higress-controller) can fetch and analyze gateway configs.
            - Check logs from higress-controller and higress-gateway containers.
            - You can use kubectl to enter the container and curl to adjust the log level of the higress for easier analysis
        
        Communication guidelines:
            - Before invoking any tool, briefly state the purpose of the call. If an error occurs, print the error details to aid diagnosis.
            - If tool parameters require user-provided details to be precise, proactively ask for them. Do NOT assume values the user did not specify (e.g., do not assume domain is example.com).
        
        Critical notes when calling the api-mcp-server (must follow):
            - Before creating an MCP server (API: higress-api-mcp-server-add-or-update-mcp-server), ensure there is an existing service source. If the user did not specify one, create it first.
            - For higress-api, domain must be in the form ip:port (e.g., 127.0.0.1:3306). Do not use bare IP.
            - When creating backend services, a concrete existing service source is required; create one if missing.
            - When calling add-or-update-mcp-server and type is not "database", do NOT include database-only parameters such as dbType.
        """

        memory_file_path = os.getenv('MEMORY_FILE_PATH')
        if not memory_file_path:
            memory_file_path = os.path.join(os.path.dirname(__file__), 'memory')
        try:
            with open(memory_file_path, 'r', encoding='utf-8') as f:
                memory_prompt = f.read()
        except FileNotFoundError:
            print("memory file does not exist")
            memory_prompt = ""

        bot = SafeAssistant(
            llm=llm_cfg,
            name='higress-report-agent',
            function_list=tools,
            description="I am Higress-ops-api-agent, I can help you with operations and API management",
            system_message=system_prompt + memory_prompt
        )
        return bot

    def _read_multiline_input(self):
        """
        Read multiline input, supports pasting multiline text
        - Input empty line (press Enter directly) to end input
        - Input 'exit' or 'quit' to exit program
        """
        print('\nuser query (enter empty line to finish, exit/quit to exit):')
        lines = []

        while True:
            try:
                line = input('... ' if lines else '')

                # Check if it's an exit command
                if not lines and line.lower() in ['exit', 'quit']:
                    return None

                # Empty line indicates end of input
                if not line:
                    break

                lines.append(line)
            except EOFError:
                # Ctrl+D also ends input
                break

        return '\n'.join(lines)

    def interactive_mode(self):
        bot = self.llm_assistant
        # Stores the chat history
        messages = []

        print("=" * 60)
        print("Higress Operations & API Management Agent")
        print("=" * 60)
        print("Tip: Supports multiline input, enter empty line to end current message")
        print("     Enter 'exit' or 'quit' to exit program")
        print("=" * 60)

        while True:
            query = self._read_multiline_input()

            # User chooses to exit
            if query is None:
                print("Exiting")
                break

            # Skip empty or whitespace-only input
            if not query.strip():
                continue

            # Append the user query to the chat history
            messages.append({'role': 'user', 'content': query})
            response = []
            response_plain_text = ''
            print('\nbot response:')
            for response in bot.run(messages=messages):
                # Streaming output
                response_plain_text = typewriter_print(response, response_plain_text)
            # Append the bot responses to the chat history
            messages.extend(response)


def main():
    load_dotenv()

    agent = Agent()

    # agent.web_mode()

    agent.interactive_mode()


if __name__ == '__main__':
    main()
