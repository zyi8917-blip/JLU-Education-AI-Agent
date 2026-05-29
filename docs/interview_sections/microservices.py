"""微服务架构面试题与参考答案。"""

MICROSERVICES_QUESTIONS = [
    (
        '什么是微服务架构？与单体架构有何区别？',
        '- 微服务将应用拆分为一组小型、独立部署的服务，每个服务围绕业务能力构建，拥有独立数据存储与生命周期。\n- 单体架构所有模块在同一进程内，部署简单但扩展与迭代耦合；微服务可按服务独立扩缩容与技术选型。\n- 微服务强调去中心化治理、轻量通信（HTTP/gRPC）、自动化运维（CI/CD、容器编排）。\n- 代价是分布式复杂度上升：网络延迟、一致性、链路追踪、运维成本需配套能力支撑。',
    ),
    (
        '微服务拆分的原则有哪些？',
        '- 按业务能力（DDD 限界上下文）拆分，而非简单按技术层（Controller/Service）拆分。\n- 高内聚低耦合：服务内部变化不应频繁影响其它服务；接口稳定、实现可替换。\n- 单一职责：一个服务聚焦一个业务域，避免“上帝服务”。\n- 数据独立：每个服务拥有自己的数据库，避免共享表导致紧耦合。\n- 团队对齐：Conway 定律——架构应匹配组织沟通结构，一个团队可独立负责一个或多个服务。',
    ),
    (
        '微服务有哪些优点和缺点？',
        '- 优点：独立部署与发布、技术栈异构、故障隔离、按服务弹性伸缩、团队自治。\n- 缺点：分布式事务难、运维复杂、服务间调用延迟、测试与调试成本、数据一致性挑战。\n- 需要配套：服务注册发现、配置中心、网关、链路追踪、熔断限流、统一日志监控。\n- 并非银弹：小团队或业务早期盲目微服务化可能得不偿失，应渐进演进。',
    ),
    (
        '什么是领域驱动设计（DDD）？与微服务的关系？',
        '- DDD 强调以业务领域为核心建模，通过实体、值对象、聚合根、限界上下文划分复杂系统。\n- 限界上下文（Bounded Context）是微服务边界的天然依据，上下文内模型统一，上下文间通过防腐层交互。\n- 聚合根保证业务不变量，是事务一致性边界；跨聚合/跨服务需最终一致性。\n- DDD 提供“拆什么”的方法论，微服务提供“怎么拆、怎么跑”的工程实践。',
    ),
    (
        '微服务间通信方式有哪些？',
        '- 同步：REST/HTTP（通用、易调试）、gRPC（Protobuf、高性能、强类型契约）。\n- 异步：消息队列（Kafka/RabbitMQ/RocketMQ），解耦、削峰、支持事件驱动架构。\n- 选择依据：实时性要求、调用方是否需立即结果、流量模式、一致性语义。\n- 避免服务间过度同步调用链导致级联故障，读多写少场景可优先事件驱动。',
    ),
    (
        'REST 与 gRPC 在微服务中如何选型？',
        '- REST 基于 HTTP+JSON，浏览器友好、生态成熟，适合对外 API 与异构系统集成。\n- gRPC 基于 HTTP/2+Protobuf，二进制序列化、支持流式、代码生成，适合内部高性能 RPC。\n- gRPC 需处理负载均衡、网关转 REST 等对外暴露问题；REST 在弱类型契约下需注意版本兼容。\n- 实践中内外分层：内部 gRPC，边缘 API Gateway 转 REST/GraphQL。',
    ),
    (
        '什么是 API 网关？有哪些职责？',
        '- API Gateway 是微服务架构的统一入口，对外屏蔽内部服务拓扑。\n- 职责：路由转发、认证鉴权、限流熔断、协议转换、请求聚合、灰度发布、日志监控。\n- 常见实现：Spring Cloud Gateway、Kong、Nginx+Lua、APISIX、Envoy。\n- 避免网关过于“胖”，业务逻辑应下沉到 BFF 或领域服务，网关聚焦横切关注点。',
    ),
    (
        '什么是 BFF（Backend for Frontend）模式？',
        '- BFF 为不同客户端（Web/App/小程序）提供定制化后端聚合层，避免单一通用 API 勉强适配所有端。\n- 各 BFF 按前端需求组合多个微服务调用，裁剪字段、适配协议，降低客户端复杂度。\n- BFF 仍属后端，可独立部署；与 API Gateway 配合：Gateway 做横切，BFF 做聚合编排。\n- 注意避免 BFF 膨胀成新单体，保持薄编排层定位。',
    ),
    (
        '什么是服务注册与发现？',
        '- 微服务实例动态扩缩，IP/端口不固定，需注册中心维护服务实例列表。\n- 服务启动时注册（Service Registration），消费者从注册中心发现可用实例（Service Discovery）。\n- 常见方案：Nacos、Eureka、Consul、Zookeeper、Kubernetes Service+DNS。\n- 需配合健康检查剔除不健康实例；客户端发现（Ribbon）vs 服务端发现（Gateway/LB）两种模式。',
    ),
    (
        'Eureka 与 Nacos 的区别？',
        '- Eureka（Netflix）：AP 模型，自我保护机制在网络分区时保留实例，适合可用性优先场景；2.x 已停更。\n- Nacos（阿里）：同时支持 AP（Distro 协议）与 CP（Raft），集成配置中心，国内生态活跃。\n- Nacos 支持命名空间、分组、权重、元数据，便于多环境与灰度；Eureka 功能相对单一。\n- Spring Cloud 2020+ 默认推荐 Nacos/Consul 替代 Eureka。',
    ),
    (
        '什么是配置中心？为什么微服务需要它？',
        '- 配置中心集中管理各服务配置，支持动态刷新、版本管理、环境隔离、加密敏感项。\n- 避免配置硬编码与散落各服务 repo，减少改配置需重新打包部署的问题。\n- 常见实现：Nacos Config、Spring Cloud Config、Apollo、Consul KV。\n- 与注册中心可合并（Nacos）或分离（Config Server + Git），注意配置变更推送一致性与回滚。',
    ),
    (
        '什么是客户端负载均衡与服务端负载均衡？',
        '- 客户端负载均衡：调用方 SDK（如 Spring Cloud LoadBalancer）从实例列表中选择目标，如轮询、随机、权重。\n- 服务端负载均衡：流量先打到 LB（Nginx、F5、云 SLB），再由 LB 转发到后端实例。\n- 微服务内部调用常用客户端 LB + 注册中心；南北向流量常用 Gateway + 服务端 LB。\n- 需关注长连接、实例权重、同 zone 优先等策略以优化延迟与亲和性。',
    ),
    (
        '什么是熔断器模式（Circuit Breaker）？',
        '- 当下游服务失败率或慢调用超阈值，熔断器打开，后续请求快速失败，避免线程堆积与级联雪崩。\n- 状态：Closed（正常）→ Open（拒绝）→ Half-Open（试探恢复）。\n- 实现：Resilience4j、Sentinel、Hystrix（已停更）。\n- 需配合降级策略（返回默认值/缓存）与监控告警，Half-Open 成功率达标后关闭熔断。',
    ),
    (
        '什么是服务降级？与熔断的区别？',
        '- 降级是在依赖不可用或系统过载时，主动关闭非核心功能，保证核心链路可用。\n- 熔断是保护调用方的自动开关机制；降级是熔断或限流触发后的业务兜底策略。\n- 降级手段：返回静态兜底数据、读缓存、简化流程、异步化非关键步骤。\n- 需提前定义降级优先级与开关，并通过演练验证效果。',
    ),
    (
        '什么是限流？常见算法有哪些？',
        '- 限流控制单位时间内请求量，保护服务不被突发流量压垮。\n- 算法：固定窗口、滑动窗口、漏桶（平滑流出）、令牌桶（允许一定突发）。\n- 粒度：单机限流（Guava RateLimiter）vs 分布式限流（Redis+Lua、Sentinel 集群）。\n- 网关层、服务层、接口层可分层限流；超限返回 429 并配合 Retry-After。',
    ),
    (
        '什么是舱壁模式（Bulkhead）？',
        '- 借鉴船舱隔离，将资源（线程池、连接池）按依赖或业务线隔离，防止某一慢依赖占满全部线程。\n- 例如为支付、查询分别分配独立线程池，支付慢时不拖垮查询。\n- Resilience4j Bulkhead、Sentinel 并发线程数隔离均支持此模式。\n- 与熔断、限流组合构成完整容错体系。',
    ),
    (
        '什么是超时与重试策略？',
        '- 每个 RPC/HTTP 调用必须设置合理超时（连接超时、读超时），避免无限等待。\n- 重试适用于幂等读操作或明确幂等的写；非幂等写盲目重试可能重复提交。\n- 指数退避+抖动（Exponential Backoff + Jitter）避免重试风暴。\n- 重试次数、仅对特定错误码（5xx/超时）重试；配合熔断防止对故障服务持续加压。',
    ),
    (
        '什么是幂等性？微服务中如何保证？',
        '- 同一请求执行多次与执行一次效果相同，是分布式重试、消息重复消费的基础。\n- 手段：唯一业务 ID + 去重表、Token 机制、数据库唯一约束、状态机 CAS、Redis SETNX。\n- 支付、下单等写操作必须设计幂等；读操作天然幂等。\n- API 设计时在文档中明确幂等键（Idempotency-Key）语义。',
    ),
    (
        '分布式事务有哪些解决方案？',
        '- 2PC/3PC：强一致但阻塞、协调者单点，生产少用（Seata AT 模式类似思路）。\n- TCC（Try-Confirm-Cancel）：业务层实现三阶段，灵活但开发成本高。\n- 本地消息表 / 事务消息（RocketMQ）：保证最终一致，适合异步场景。\n- Saga：长事务拆为本地事务+补偿；Seata Saga 状态机编排。\n- 微服务首选最终一致性，强一致场景尽量合并边界或用单服务事务。',
    ),
    (
        '什么是 CAP 定理？微服务如何权衡？',
        '- 分布式系统最多同时满足一致性（C）、可用性（A）、分区容错（P）两者；网络分区必然发生，实际在 C 与 A 间权衡。\n- CP：Zookeeper、Etcd，牺牲部分可用换强一致（选主、配置）。\n- AP：Eureka、Cassandra 部分模式，允许短暂不一致换高可用。\n- 业务上：支付等选 CP 或强一致方案；社交 feed、计数等可 AP + 最终一致。',
    ),
    (
        '什么是 BASE 理论？',
        '- Basically Available：基本可用，允许损失部分可用性（响应时间、功能降级）。\n- Soft state：软状态，允许中间状态存在。\n- Eventually consistent：最终一致性，经过一段时间后达到一致。\n- BASE 是对 CAP 中 AP 方向的工程实践总结，适用于大多数互联网业务场景。',
    ),
    (
        '什么是 Saga 模式？',
        '- 长分布式事务拆成多个本地事务，每步成功则继续，失败则执行已发生步骤的补偿操作。\n- 编排式（Orchestration）：中央协调器驱动流程；编舞式（Choreography）：各服务通过事件协作。\n- 补偿是业务语义上的“反向操作”，非数据库回滚；需设计可补偿性与幂等。\n- Seata、Temporal、Camunda 等可辅助 Saga 实现与可视化。',
    ),
    (
        '什么是 TCC？适用场景？',
        '- Try：预留资源（冻结库存、冻结余额）；Confirm：确认提交；Cancel：释放预留。\n- 三个阶段均由业务代码实现，框架（Seata TCC）负责协调与悬挂、空回滚等异常处理。\n- 适合对一致性要求高、参与方少、可建模预留资源的场景（账户、库存）。\n- 缺点：侵入性强、开发测试复杂，不应作为默认方案。',
    ),
    (
        'Seata 的 AT 模式原理是什么？',
        '- AT 模式基于数据源代理，拦截业务 SQL，记录前后镜像（undo_log），一阶段本地事务直接提交。\n- 二阶段提交：异步删除 undo_log；回滚：根据 undo_log 生成反向 SQL。\n- 依赖全局事务 ID（XID）在 RPC 链路传递；TC（Transaction Coordinator）维护全局状态。\n- 优点是对业务侵入小；需注意脏写、全局锁、undo_log 存储与性能开销。',
    ),
    (
        '什么是最终一致性？常见实现？',
        '- 允许短暂不一致，通过异步机制（消息、对账、补偿）Eventually 达到一致。\n- 实现：消息队列可靠投递+消费确认、本地消息表、CDC（Canal/Debezium）同步、定时对账。\n- 需定义一致性的时间边界（SLA）与异常人工介入流程。\n- 用户感知：订单状态延迟更新、库存显示短暂不准等需产品层接受或优化。',
    ),
    (
        '微服务如何划分数据库？',
        '- Database per Service：每服务独立库，禁止跨库 JOIN，跨服务数据通过 API 或事件同步。\n- 共享数据库反模式：多服务共表导致 schema 耦合、无法独立演进。\n- 读侧可用 CQRS：写模型在源服务，读模型通过事件投影到查询库/ES。\n- 拆分初期可先逻辑分库同实例，再物理分离，降低迁移风险。',
    ),
    (
        '什么是 CQRS？',
        '- Command Query Responsibility Segregation：命令（写）与查询（读）模型分离。\n- 写侧聚焦业务规则与一致性；读侧可 denormalize 为宽表、ES、Redis 优化查询性能。\n- 写读通过领域事件异步同步，天然适配事件驱动微服务。\n- 代价是模型同步延迟与复杂度，适合读写负载差异大、查询维度多的系统。',
    ),
    (
        '什么是事件驱动架构（EDA）？',
        '- 服务通过发布/订阅领域事件通信，生产者不直接调用消费者，解耦时间与空间。\n- 事件应表达“已发生的事实”（OrderCreated），而非命令（CreateOrder）。\n- 需处理：至少一次投递、消费幂等、事件顺序、Schema 演进（Avro/Protobuf+Schema Registry）。\n- 与 CQRS、Saga 编舞式模式天然契合。',
    ),
    (
        'Kafka 在微服务中的典型用途？',
        '- 领域事件总线：订单创建、支付成功等跨服务通知。\n- 日志聚合、CDC 数据同步、流式处理（Kafka Streams/Flink）。\n- 削峰填谷：异步处理高峰写入。\n- 注意分区键保证同实体事件有序；消费者组实现负载均衡；Retention 与 compaction 策略按 topic 设计。',
    ),
    (
        '什么是链路追踪（Distributed Tracing）？',
        '- 跨服务调用链上传递 TraceId/SpanId，记录每跳耗时与标签，定位慢请求与故障点。\n- 模型：Trace（一次请求）→ 多个 Span（各服务段），Span 可嵌套。\n- 实现：OpenTelemetry、SkyWalking、Zipkin、Jaeger；日志中注入 traceId 关联。\n- 采样率需平衡存储成本；关键业务可提高采样或在错误时全采。',
    ),
    (
        '微服务监控需要关注哪些指标？',
        '- 四个黄金信号：延迟（Latency）、流量（Traffic）、错误（Errors）、饱和度（Saturation）。\n- RED：Rate、Errors、Duration，面向请求驱动服务。\n- USE：Utilization、Saturation、Errors，面向资源（CPU/磁盘/连接池）。\n- 业务指标：订单成功率、支付转化率；基础设施：JVM GC、线程池队列、DB 连接。',
    ),
    (
        '什么是健康检查（Health Check）？',
        '- Liveness：进程是否存活，失败则重启容器。\n- Readiness：是否可接收流量，失败则从负载均衡摘除。\n- Startup：慢启动服务专用，避免 liveness 误杀。\n- Spring Boot Actuator `/actuator/health` 可聚合 DB、Redis、磁盘等依赖状态；K8s probe 配置需合理超时。',
    ),
    (
        '容器化与 Kubernetes 对微服务的价值？',
        '- Docker 统一交付物，环境一致；K8s 提供编排、自愈、滚动发布、HPA 弹性伸缩、Service Discovery。\n- Deployment+Service+Ingress 构成标准部署模型；ConfigMap/Secret 管理配置。\n- Service Mesh（Istio）在 K8s 上提供流量治理、 mTLS、可观测性。\n- 需投入学习曲线与集群运维能力，小团队可先用 Docker Compose + 简单编排。',
    ),
    (
        '什么是 Service Mesh？',
        '- 将服务间通信的横切能力（重试、熔断、 mTLS、追踪）下沉到 Sidecar 代理（如 Envoy）。\n- 控制面（Istio Pilot）下发策略，数据面 Sidecar 拦截流量执行。\n- 业务代码无 SDK 侵入，多语言统一治理；代价是 Sidecar 资源开销与运维复杂度。\n- 适合大规模、多语言、治理需求强的场景；中小规模可用 Spring Cloud 组件替代。',
    ),
    (
        '微服务如何做到灰度发布与金丝雀？',
        '- 金丝雀：少量流量到新版本，观察指标后逐步放大；蓝绿：两套环境切换流量。\n- 实现：Gateway 权重路由、K8s Rolling Update、Istio VirtualService 按 header/比例分流。\n- 需自动化监控对比（错误率、延迟）与快速回滚能力。\n- Feature Flag 可在应用层控制功能开关，与部署灰度互补。',
    ),
    (
        '微服务版本管理与 API 兼容性？',
        '- URL 版本（/v1/）、Header 版本、媒体类型版本；推荐明确弃用策略与时间线。\n- 向后兼容：只增字段不删改、枚举留扩展、消费者容错未知字段。\n- 契约测试（Pact）保证 Provider 变更不破坏 Consumer 期望。\n- 避免同时维护过多主版本，推动消费者升级。',
    ),
    (
        '什么是契约测试（Consumer-Driven Contract）？',
        '- Consumer 定义对 Provider API 的期望（契约），CI 中 Provider 验证是否满足。\n- Pact 是常用框架，生成契约文件共享到 Broker。\n- 弥补端到端测试慢、不稳定的问题，在微服务独立发布时捕获集成破坏。\n- 不能替代少量关键路径 E2E 测试。',
    ),
    (
        '微服务安全如何设计？',
        '- 认证：OAuth2/OIDC、JWT；网关统一鉴权，内部 mTLS 或 Service Account。\n- 授权：RBAC/ABAC，细粒度到 API 与数据行级。\n- 密钥管理：Vault、K8s Secret，禁止硬编码；Token 短有效期+Refresh。\n- 网络隔离：VPC、Network Policy；最小权限原则。',
    ),
    (
        'JWT 在微服务中的优缺点？',
        '- 优点：无状态、易水平扩展、跨域友好；Payload 可携带用户信息与权限声明。\n- 缺点：签发后难撤销（需黑名单/短 TTL）、Payload 不宜过大、密钥泄露风险。\n- Access Token 短效 + Refresh Token 长效存储；敏感操作二次验证。\n- 网关校验签名与 exp，内部服务可信任网关或再次校验。',
    ),
    (
        '什么是零信任架构在微服务中的体现？',
        '- 默认不信任网络内外任何实体，每次访问都需认证授权。\n- 服务间 mTLS 双向证书；Identity 基于 SPIFFE/SPIRE 或 K8s SA。\n- 细粒度策略（OPA/Istio AuthorizationPolicy）而非仅靠网络边界防火墙。\n- 持续验证、最小权限、Assume Breach 思维。',
    ),
    (
        '微服务日志如何统一管理？',
        '- 结构化日志（JSON），统一字段：timestamp、level、service、traceId、spanId、message。\n- 采集：Filebeat/Fluent Bit → Kafka/Logstash → Elasticsearch；或 Loki+Grafana。\n- 禁止仅依赖 SSH 查单机日志；traceId 串联跨服务日志。\n- 敏感信息脱敏；日志级别生产默认 INFO，动态调 DEBUG 排查。',
    ),
    (
        '微服务测试策略（测试金字塔）？',
        '- 单元测试：领域逻辑，量大、快。\n- 集成测试：服务+真实依赖（Testcontainers 启 DB/Kafka）。\n- 契约测试：服务间 API 兼容。\n- 组件/端到端测试：少量关键路径；避免过度 E2E 导致 CI 慢且 flaky。',
    ),
    (
        '什么是 Testcontainers？',
        '- Java 库在 JUnit 测试中启动真实 Docker 容器（MySQL、Redis、Kafka 等）作为依赖。\n- 比 H2 内存库更接近生产；测试结束自动销毁容器。\n- 适合微服务集成测试；CI 需 Docker 环境，注意并行测试端口冲突。\n- 与 Spring Boot `@DynamicPropertySource` 配合注入动态端口。',
    ),
    (
        '微服务反模式有哪些？',
        '- 分布式单体：拆了很多服务但强耦合、同步链路过长、共享数据库。\n- 纳米服务：服务过小导致调用开销大于业务价值。\n- 无自动化运维：手工部署、缺乏监控就上大集群。\n- 过早微服务化：业务边界不清时拆分，重构成本极高。',
    ),
    (
        '如何从单体迁移到微服务？',
        '- Strangler Fig 模式：新功能用微服务，老模块逐步替换，Facade 路由流量。\n- 先识别限界上下文与数据依赖；优先拆高频变更、需独立扩展的模块。\n- 建立 CI/CD、监控、注册中心等平台能力再大规模拆分。\n- 避免 Big Bang 重写；保持业务连续性是首要约束。',
    ),
    (
        'Spring Cloud 核心组件有哪些？',
        '- 注册发现：Nacos/Eureka；配置：Nacos Config/Config Server；网关：Gateway。\n- 负载均衡：LoadBalancer；熔断限流：Sentinel/Resilience4j；OpenFeign 声明式 HTTP 客户端。\n- 链路追踪：Micrometer Tracing + Zipkin/OTel；Bus 配置刷新（可选）。\n- Spring Cloud 2022+ 基于 Spring Boot 3，部分 Netflix 组件已移除或替代。',
    ),
    (
        'OpenFeign 的工作原理与注意事项？',
        '- 基于接口+注解声明 HTTP 调用，运行时动态代理生成实现，集成 LoadBalancer 与熔断。\n- 注意设置 connect/read 超时、重试策略、日志级别；大文件上传需调整超时与流式。\n- 与 `@Retryable`、Resilience4j 装饰器配合增强容错。\n- 避免在 Feign 接口中暴露过多细粒度调用导致 Chatty Interface。',
    ),
    (
        '什么是 Spring Cloud Alibaba？',
        '- 阿里开源微服务套件：Nacos（注册+配置）、Sentinel（流控熔断）、Seata（分布式事务）、RocketMQ 集成等。\n- 与 Spring Cloud 体系集成，国内文档与社区活跃。\n- 选型时可与 Spring Cloud Netflix 退役后的替代方案对比评估。\n- 注意版本与 Spring Boot/Cloud 的 BOM 对齐。',
    ),
    (
        '微服务中的缓存策略？',
        '- 本地缓存（Caffeine）：快但多实例不一致；分布式缓存（Redis）：一致性好、网络开销。\n- Cache-Aside：读 miss 查 DB 回填；Write-Through/Write-Behind 按一致性需求选择。\n- 缓存穿透（布隆过滤器/空值）、击穿（互斥锁）、雪崩（TTL 随机、多级缓存）。\n- 跨服务缓存失效可用消息广播或 Canal 监听 binlog。',
    ),
    (
        '什么是防腐层（Anti-Corruption Layer）？',
        '- 在限界上下文集成边界建立翻译层，将外部模型转换为本域模型，防止外部概念污染核心领域。\n- 调用 legacy 单体或第三方 API 时尤其重要。\n- 可独立为一个适配器模块或微服务。\n- 增加一层映射代码，但保护领域模型纯净与可演进性。',
    ),
]
