# higress-ops-api-agent

English | [简体中文](./README_CN)

An AI-powered operations and API management assistant for Higress, integrating multiple MCP Servers to help you easily manage Higress gateway and Kubernetes clusters.

## Features

- 🚀 **Higress API Management**: Manage routes, services, plugins, etc. via higress-api-mcp-server
- 🔧 **Higress Operations**: Get Envoy/Istiod configuration and status via higress-ops-mcp-server
- ☸️ **Kubernetes Operations**: Manage K8s clusters via kubectl-ai
- 🔒 **Security Control**: Built-in tool invocation safety mechanism, sensitive operations require user confirmation
- 💾 **Long-term Memory**: Support configuring long-term memory content via files
- 🔌 **Flexible Configuration**: Control which MCP Servers to enable via environment variables

## Demo
agent fix route

https://private-user-images.githubusercontent.com/153273766/508026451-3c1536af-84eb-4a8d-9f49-a1cfd58e96de.mov?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjE4ODk0OTYsIm5iZiI6MTc2MTg4OTE5NiwicGF0aCI6Ii8xNTMyNzM3NjYvNTA4MDI2NDUxLTNjMTUzNmFmLTg0ZWItNGE4ZC05ZjQ5LWExY2ZkNThlOTZkZS5tb3Y_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUxMDMxJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MTAzMVQwNTM5NTZaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1jNDViZjBhODQyZTAzNTQ5YzA2Y2Y1ZmQwYmIxMDJiODE2YzFiNjNhZjU4NjQ5NTY3Mjg4N2I1NGI2NGRiYTkwJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.pvOWeJN26LorQyysQtfeg4xppztRdLnuR6fGSrzJw78

agent create ai-route

https://private-user-images.githubusercontent.com/153273766/508026004-6e1fd332-91cf-43f9-beae-df851022be82.mov?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjE4ODk0NTYsIm5iZiI6MTc2MTg4OTE1NiwicGF0aCI6Ii8xNTMyNzM3NjYvNTA4MDI2MDA0LTZlMWZkMzMyLTkxY2YtNDNmOS1iZWFlLWRmODUxMDIyYmU4Mi5tb3Y_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUxMDMxJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MTAzMVQwNTM5MTZaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1mOTlmMjU2ODcwZjc3Y2ZiZmVjZTQwNmU5YzlmNWEyMzlhOTdhMDk4YmFlNmRmODllOGRjNjcxZTEyZmNhMjk3JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.0KxEO0s_9MHxEEEjngP09dt3-ut-cec7K1d55KDYImI

## Prerequisites

### 1. Install kubectl-ai (Optional)

If you need Kubernetes operations functionality, install `kubectl-ai`.

Reference project: https://github.com/GoogleCloudPlatform/kubectl-ai

Installation command:
```bash
curl -sSL https://raw.githubusercontent.com/GoogleCloudPlatform/kubectl-ai/main/install.sh | bash

# Verify installation
kubectl-ai --help
```

### 2. Configure Higress MCP Server (Optional)

If you need Higress API management or operations functionality, enable MCP Server in Higress.

#### higress-api-mcp-server Configuration

Add the following configuration to the `higress-config` ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: higress-config
  namespace: higress-system
  resourceVersion: '107160'
data:
  higress: |
    mcpServer:
      sse_path_suffix: /sse  # SSE 连接的路径后缀
      enable: true           # 启用 MCP Server
      redis:
        address: redis-stack-server.higress-system.svc.cluster.local:6379  # Redis服务地址
        username: ""         # Redis用户名（可选）
        password: ""         # Redis密码（可选）
        db: 0                # Redis数据库（可选）
      match_list:            # MCP Server 会话保持路由规则
        - match_rule_domain: "*"
          match_rule_path: /higress-api
          match_rule_type: "prefix"
        - match_rule_domain: "*"
          match_rule_path: /higress-ops
          match_rule_type: "prefix"
        - match_rule_domain: "*"
          match_rule_path: /mysql
          match_rule_type: "prefix"
      servers:
        - name: higress-api-mcp-server     # MCP Server 名称
          path: /higress-api               # 访问路径，需要与 match_list 中的配置匹配
          type: higress-api                # 类型和 RegisterServer 一致
          config:
            higressURL: http://higress-console.higress-system.svc.cluster.local:8080
        - name: higress-ops-mcp-server
          path: /higress-ops
          type: higress-ops
          config:
            istiodURL: http://higress-controller.higress-system.svc.cluster.local:15014   # istiod url
            envoyAdminURL: http://127.0.0.1:15000 # envoy url 填127.0.0.1就行，和 gateway 于同一容器
            namespace: higress-system
            description: "Higress Ops MCP Server for Istio and Envoy debugging"


```

## Environment Variables Configuration

Create a `.env` file and configure the following environment variables:

```bash
# Higress API MCP Server URL (optional, won't be enabled if not set)
# Example: http://localhost:8080/higress-api/sse
HIGRESS_API_MCP_SERVER_URL=

# Authorization header for Higress API MCP Server (optional)
# Example: Bearer your-token-here
AUTHORIZATION=

# Higress Ops MCP Server URL (optional, won't be enabled if not set)
# Example: http://localhost:8080/higress-ops/sse
HIGRESS_OPS_MCP_SERVER_URL=

# X-Istiod-Token header for Higress Ops MCP Server (optional)
# Generate token with: kubectl create token higress-gateway -n higress-system --audience istio-ca --duration 87600h
X_ISTIOD_TOKEN=

# Whether to enable Kubectl MCP Server (optional, defaults to false)
# Requires kubectl-ai to be installed first
ENABLE_KUBECTL_MCP_SERVER=false

# Long-term memory file path (optional)
MEMORY_FILE_PATH=./memory

# Dashscope API Key (required)
DASHSCOPE_API_KEY=your-api-key

# Model name
MODEL_NAME=qwen-plus

# Model server address (optional)
MODEL_SERVER=
```

### MCP Server Configuration Guide

- **higress-api-mcp-server**: For Higress API management (routes, services, plugins, etc.)
- **higress-ops-mcp-server**: For Higress operations (get Envoy/Istiod configuration and status)
- **kubectl-ai-mcp-server**: For Kubernetes cluster management

**By default, all MCP Servers are disabled**. You can selectively enable them as needed.

## Long-term Memory

You can write the content you want the agent to remember into a file (default is `memory`), then specify the file path via the `MEMORY_FILE_PATH` environment variable. The agent will read the file content at startup as part of the system prompt.

## Installation and Running

### 1. Install Dependencies

```bash
pip install -U qwen-agent python-dotenv
```

### 2. Configure Environment Variables

Create a `.env` file, refer to the environment variable configuration guide above.

### 3. Run the Agent

```bash
python main.py
```

After the agent starts, it will display the enabled MCP Servers, for example:

```
启用 higress-api-mcp-server: http://localhost:8080/higress-api/sse
启用 kubectl-ai-mcp-server
```

## Usage Examples

### Example 1: Create MCP Service

In interactive mode, enter:

```
帮我创建一个 MCP 服务，服务类型是 openapi，指向我 127.0.0.1:5555 这个后端服务
```
(Help me create an MCP service with openapi type, pointing to my backend service at 127.0.0.1:5555)

### Example 2: View Higress Routes

```
列出所有的 Higress 路由
```
(List all Higress routes)

### Example 3: Get Envoy Configuration

```
帮我查看 Envoy 的集群配置
```
(Help me check the Envoy cluster configuration)

### Example 4: Kubernetes Operations

```
查看 higress-system 命名空间下的所有 pod
```
(View all pods in the higress-system namespace)

## Security Mechanism

The project has a built-in tool invocation safety mechanism:

- ✅ **Auto-approved**: All read-only operations like `get`, `list` are executed automatically
- ✅ **Auto-approved**: kubectl read-only commands (get, describe, logs, etc.) are executed automatically
- ⚠️ **Requires confirmation**: Write operations like create, update, delete require user confirmation

When a sensitive operation is triggered, you will see:

```
Sensitive tool invocation detected: add-route, args: {...}
Allow invoking this tool? Enter y or n+reason (e.g., y or n+why):
```

Enter `y` to allow execution, or `n+reason` to reject.

## Architecture

```
┌─────────────────────────────────────────┐
│     higress-ops-api-agent (AI Agent)    │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   SafeAssistant (Security Layer) │   │
│  └─────────────────────────────────┘   │
│              │                          │
│              ▼                          │
│  ┌─────────────────────────────────┐   │
│  │      MCP Server Integration      │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ higress-api-mcp-server  │    │   │
│  │  │ (API Management)        │    │   │
│  │  └─────────────────────────┘    │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ higress-ops-mcp-server  │    │   │
│  │  │ (Operations Monitoring) │    │   │
│  │  └─────────────────────────┘    │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ kubectl-ai-mcp-server   │    │   │
│  │  │ (K8s Management)        │    │   │
│  │  └─────────────────────────┘    │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## License

This project is licensed under the Apache 2.0 License.

