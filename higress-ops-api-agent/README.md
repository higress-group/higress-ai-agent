# 第一版
1. 采用system+memory prompt，方便用户个人把一些需要agent长期记忆的信息放到memory prompt中
2. system prompt中，会陆续加上可能有利于debug，判断的说明

## 安装 kubectl-ai
使用 https://github.com/GoogleCloudPlatform/kubectl-ai

安装教程
```mermaid
curl -sSL https://raw.githubusercontent.com/GoogleCloudPlatform/kubectl-ai/main/install.sh | bash

# 验证
kubectl-ai --help
```

## 启动higress，启动higress-api-mcp-server
higress-configmap的控制台参考配置
```mermaid
apiVersion: v1
kind: ConfigMap
metadata:
  name: higress-config
  namespace: higress-system
  resourceVersion: '3402'
data:
  higress: |-
    mcpServer:
      sse_path_suffix: /sse # SSE 连接的路径后缀
      enable: true # 启用 MCP Server
      redis:
        address: redis-stack-server.higress-system.svc.cluster.local:6379 # Redis服务地址
        username: "" # Redis用户名（可选）
        password: "" # Redis密码（可选）
        db: 0 # Redis数据库（可选）
      match_list: # MCP Server 会话保持路由规则（当匹配下面路径时，将被识别为一个 MCP 会话，通过 SSE 等机制进行会话保持）
        - match_rule_domain: "*"
          match_rule_path: /higress-api
          match_rule_type: "prefix"
      servers:
        - name: higress-api-mcp-server # MCP Server 名称
          path: /higress-api # 访问路径，需要与 match_list 中的配置匹配
          type: higress-api # 类型和 RegisterServer 一致
          config:
            higressURL: http://higress-console.higress-system.svc.cluster.local:8080
            username: admin
            password: admin
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