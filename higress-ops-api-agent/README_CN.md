# higress-ops-api-agent

[English](./README) | 简体中文

一个基于 AI 的 Higress 运维和 API 管理助手，集成多个 MCP Server，帮助您轻松管理 Higress 网关和 Kubernetes 集群。

## 功能特性

- 🚀 **Higress API 管理**: 通过 higress-api-mcp-server 管理路由、服务、插件等
- 🔧 **Higress 运维**: 通过 higress-ops-mcp-server 获取 Envoy/Istiod 配置和状态
- ☸️ **Kubernetes 运维**: 通过 kubectl-ai 进行 K8s 集群管理
- 🔒 **安全控制**: 内置工具调用安全机制，敏感操作需要用户确认
- 💾 **长期记忆**: 支持通过文件配置长期记忆内容
- 🔌 **灵活配置**: 通过环境变量控制启用哪些 MCP Server

## Demo
agent fix route

https://private-user-images.githubusercontent.com/153273766/508026451-3c1536af-84eb-4a8d-9f49-a1cfd58e96de.mov?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjE4ODk0OTYsIm5iZiI6MTc2MTg4OTE5NiwicGF0aCI6Ii8xNTMyNzM3NjYvNTA4MDI2NDUxLTNjMTUzNmFmLTg0ZWItNGE4ZC05ZjQ5LWExY2ZkNThlOTZkZS5tb3Y_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUxMDMxJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MTAzMVQwNTM5NTZaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1jNDViZjBhODQyZTAzNTQ5YzA2Y2Y1ZmQwYmIxMDJiODE2YzFiNjNhZjU4NjQ5NTY3Mjg4N2I1NGI2NGRiYTkwJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.pvOWeJN26LorQyysQtfeg4xppztRdLnuR6fGSrzJw78

agent create ai-route

https://private-user-images.githubusercontent.com/153273766/508026004-6e1fd332-91cf-43f9-beae-df851022be82.mov?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjE4ODk0NTYsIm5iZiI6MTc2MTg4OTE1NiwicGF0aCI6Ii8xNTMyNzM3NjYvNTA4MDI2MDA0LTZlMWZkMzMyLTkxY2YtNDNmOS1iZWFlLWRmODUxMDIyYmU4Mi5tb3Y_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUxMDMxJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MTAzMVQwNTM5MTZaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1mOTlmMjU2ODcwZjc3Y2ZiZmVjZTQwNmU5YzlmNWEyMzlhOTdhMDk4YmFlNmRmODllOGRjNjcxZTEyZmNhMjk3JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.0KxEO0s_9MHxEEEjngP09dt3-ut-cec7K1d55KDYImI

## 前置依赖

### 1. 安装 kubectl-ai (可选)

如果需要使用 Kubernetes 运维功能，需要安装 `kubectl-ai`。

参考项目：https://github.com/GoogleCloudPlatform/kubectl-ai

安装命令：
```bash
curl -sSL https://raw.githubusercontent.com/GoogleCloudPlatform/kubectl-ai/main/install.sh | bash

# 验证安装
kubectl-ai --help
```

### 2. 配置 Higress MCP Server (可选)

如果需要使用 Higress API 管理或运维功能，需要在 Higress 中启用 MCP Server。

#### higress-api-mcp-server 配置

在 `higress-config` ConfigMap 中添加以下配置：

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
            envoyAdminURL: http://127.0.0.1:15000 # envoy url 填127.0.0.1就行，和 gateway 于同一容器
            namespace: higress-system
            description: "Higress Ops MCP Server for Istio and Envoy debugging"


```

## 环境变量配置

创建 `.env` 文件并配置以下环境变量：

```bash
# Higress API MCP Server URL (可选，不设置则不启用)
# 示例: http://localhost:8080/higress-api/sse
HIGRESS_API_MCP_SERVER_URL=

# Higress API MCP Server 的 Authorization 请求头 (可选)
# 示例: Bearer your-token-here
AUTHORIZATION=

# Higress Ops MCP Server URL (可选，不设置则不启用)
# 示例: http://localhost:8080/higress-ops/sse
HIGRESS_OPS_MCP_SERVER_URL=

# Higress Ops MCP Server 的 X-Istiod-Token 请求头 (可选)
# 生成方式: kubectl create token higress-gateway -n higress-system --audience istio-ca --duration 87600h
X_ISTIOD_TOKEN=

# 是否启用 Kubectl MCP Server (可选，默认为 false)
# 需要先安装 kubectl-ai
ENABLE_KUBECTL_MCP_SERVER=false

# 长期记忆文件路径 (可选)
MEMORY_FILE_PATH=./memory

# Dashscope API Key (必需)
DASHSCOPE_API_KEY=your-api-key

# 模型名称
MODEL_NAME=qwen-plus

# 模型服务地址 (可选)
MODEL_SERVER=
```

### MCP Server 配置说明

- **higress-api-mcp-server**: 用于 Higress API 管理（路由、服务、插件等）
- **higress-ops-mcp-server**: 用于 Higress 运维（获取 Envoy/Istiod 配置和状态）
- **kubectl-ai-mcp-server**: 用于 Kubernetes 集群管理

**默认情况下所有 MCP Server 都不启用**，您可以根据需要选择性启用。

## 长期记忆

您可以将想要 agent 记忆的内容写入一个文件（默认为 `memory`），然后通过环境变量 `MEMORY_FILE_PATH` 指定文件路径。Agent 会在启动时读取该文件内容作为系统提示的一部分。

## 安装和运行

### 1. 安装依赖

```bash
pip install -U qwen-agent python-dotenv
```

### 2. 配置环境变量

创建 `.env` 文件，参考上面的环境变量配置说明。

### 3. 运行 Agent

```bash
python main.py
```

Agent 启动后会显示已启用的 MCP Server，例如：

```
启用 higress-api-mcp-server: http://localhost:8080/higress-api/sse
启用 kubectl-ai-mcp-server
```

## 使用示例

### 示例 1: 创建 MCP 服务

在交互模式中输入：

```
帮我创建一个 MCP 服务，服务类型是 openapi，指向我 127.0.0.1:5555 这个后端服务
```

### 示例 2: 查看 Higress 路由

```
列出所有的 Higress 路由
```

### 示例 3: 获取 Envoy 配置

```
帮我查看 Envoy 的集群配置
```

### 示例 4: Kubernetes 运维

```
查看 higress-system 命名空间下的所有 pod
```

## 安全机制

项目内置了工具调用安全机制：

- ✅ **自动放行**: 所有 `get`、`list` 等只读操作自动执行
- ✅ **自动放行**: kubectl 的只读命令（get、describe、logs 等）自动执行
- ⚠️ **需要确认**: 创建、更新、删除等写操作需要用户确认

当触发敏感操作时，会提示：

```
Sensitive tool invocation detected: add-route, args: {...}
Allow invoking this tool? Enter y or n+reason (e.g., y or n+why):
```

输入 `y` 允许执行，输入 `n+原因` 拒绝执行。

## 架构说明

```
┌─────────────────────────────────────────┐
│     higress-ops-api-agent (AI Agent)    │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   SafeAssistant (安全控制层)     │   │
│  └─────────────────────────────────┘   │
│              │                          │
│              ▼                          │
│  ┌─────────────────────────────────┐   │
│  │      MCP Server 集成             │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ higress-api-mcp-server  │    │   │
│  │  │ (API 管理)              │    │   │
│  │  └─────────────────────────┘    │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ higress-ops-mcp-server  │    │   │
│  │  │ (运维监控)              │    │   │
│  │  └─────────────────────────┘    │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ kubectl-ai-mcp-server   │    │   │
│  │  │ (K8s 管理)              │    │   │
│  │  └─────────────────────────┘    │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## 许可证

本项目采用 Apache 2.0 许可证。

