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
            username: admin
            password: admin
        - name: higress-ops-mcp-server
          path: /higress-ops
          type: higress-ops
          config:
            istiodURL: http://higress-controller.higress-system.svc.cluster.local:15014   # istiod url
            istiodToken: "your token"  # 生成方式：kubectl create token higress-gateway -n higress-system --audience istio-ca --duration 87600h
            envoyAdminURL: http://127.0.0.1:15000 # envoy url 填127.0.0.1就行，和 gateway 于同一容器
            namespace: higress-system
            description: "Higress Ops MCP Server for Istio and Envoy debugging"
  mesh: |-
    accessLogEncoding: TEXT
    accessLogFile: /dev/stdout
    accessLogFormat: '{"ai_log":"%FILTER_STATE(wasm.ai_log:PLAIN)%","authority":"%REQ(X-ENVOY-ORIGINAL-HOST?:AUTHORITY)%","bytes_received":"%BYTES_RECEIVED%","bytes_sent":"%BYTES_SENT%","downstream_local_address":"%DOWNSTREAM_LOCAL_ADDRESS%","downstream_remote_address":"%DOWNSTREAM_REMOTE_ADDRESS%","duration":"%DURATION%","istio_policy_status":"%DYNAMIC_METADATA(istio.mixer:status)%","method":"%REQ(:METHOD)%","path":"%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%","protocol":"%PROTOCOL%","request_id":"%REQ(X-REQUEST-ID)%","requested_server_name":"%REQUESTED_SERVER_NAME%","response_code":"%RESPONSE_CODE%","response_flags":"%RESPONSE_FLAGS%","route_name":"%ROUTE_NAME%","start_time":"%START_TIME%","trace_id":"%REQ(X-B3-TRACEID)%","upstream_cluster":"%UPSTREAM_CLUSTER%","upstream_host":"%UPSTREAM_HOST%","upstream_local_address":"%UPSTREAM_LOCAL_ADDRESS%","upstream_service_time":"%RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)%","upstream_transport_failure_reason":"%UPSTREAM_TRANSPORT_FAILURE_REASON%","user_agent":"%REQ(USER-AGENT)%","x_forwarded_for":"%REQ(X-FORWARDED-FOR)%","response_code_details":"%RESPONSE_CODE_DETAILS%"}'
    configSources:
    - address: xds://127.0.0.1:15051
    - address: k8s://
    defaultConfig:
      discoveryAddress: higress-controller.higress-system.svc:15012
      proxyStatsMatcher:
        inclusionRegexps:
        - .*
      tracing: {}
    dnsRefreshRate: 200s
    enableAutoMtls: false
    enablePrometheusMerge: true
    ingressControllerMode: "OFF"
    mseIngressGlobalConfig:
      enableH3: false
      enableProxyProtocol: false
    protocolDetectionTimeout: 100ms
    rootNamespace: higress-system
    trustDomain: cluster.local
  meshNetworks: 'networks: {}'


```

## 环境变量配置

创建 `.env` 文件并配置以下环境变量：

```bash
# Higress API MCP Server URL (可选，不设置则不启用)
# 示例: http://localhost:8080/higress-api/sse
HIGRESS_API_MCP_SERVER_URL=

# Higress Ops MCP Server URL (可选，不设置则不启用)
# 示例: http://localhost:8080/higress-ops/sse
HIGRESS_OPS_MCP_SERVER_URL=

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

