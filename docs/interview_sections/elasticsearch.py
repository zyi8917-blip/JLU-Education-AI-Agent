"""Elasticsearch 面试题与参考答案。"""

ELASTICSEARCH_QUESTIONS = [
    (
        '什么是 Elasticsearch？它解决什么问题？',
        '- Elasticsearch（ES）是基于 Apache Lucene 构建的分布式搜索与分析引擎，默认以 RESTful API 对外提供服务。\n- 核心能力包括全文检索、结构化查询、聚合统计、近实时数据分析，常用于日志检索（ELK）、商品搜索、监控告警等场景。\n- 相比直接在关系型数据库上做 LIKE 查询，ES 利用倒排索引实现毫秒级检索，并可通过水平扩展应对海量数据。\n- ES 是文档型 NoSQL 存储，数据以 JSON 文档形式组织，Schema 相对灵活，适合读多写少、检索维度多的业务。',
    ),
    (
        'Elasticsearch 与 Lucene 的关系是什么？',
        '- Lucene 是单机全文检索库，提供倒排索引、分词、打分等底层能力；Elasticsearch 在其之上封装了分布式、REST API、集群管理、Mapping 等能力。\n- ES 中每个分片（Shard）底层对应一个 Lucene Index，一个 Lucene Index 由多个 Segment 组成。\n- ES 负责路由、副本复制、Master 选举、协调搜索等分布式逻辑；真正的索引写入、查询执行仍由 Lucene 完成。\n- 理解 Lucene 的 Segment 不可变、写入先内存后刷盘等机制，是分析 ES 写入性能与 merge 开销的基础。',
    ),
    (
        '倒排索引的原理是什么？',
        '- 正排索引：文档 ID → 文档内容；倒排索引：词条（Term）→ 包含该词条的文档列表（Posting List）。\n- 写入时分词器将文本拆成 Term，对每个 Term 记录其出现的文档 ID、位置、偏移、词频（TF）等信息。\n- 查询时对查询语句分词，在倒排表中快速定位 Term 对应的 Posting List，再对多个 Term 的结果做交集/并集/布尔运算。\n- 倒排索引适合“由词找文档”的场景；范围查询、聚合等会结合 BKD 树、Doc Values 等结构辅助完成。',
    ),
    (
        'Elasticsearch 集群中有哪些节点角色？',
        '- Master-eligible Node：参与 Master 选举，负责集群元数据管理（索引创建、分片分配、Mapping 变更等）。\n- Data Node：存储分片数据，执行索引与搜索，承担主要 IO 和计算压力。\n- Coordinating Node：接收客户端请求，路由到目标分片，合并各分片结果后返回（默认所有节点均可协调）。\n- Ingest Node：执行 Ingest Pipeline 预处理；ML Node、Transform Node 等用于机器学习与数据转换（可选）。\n- 生产环境建议专用 Master 节点（通常 3 个），与 Data 节点分离，降低 Full GC 或 heavy search 影响集群稳定性。',
    ),
    (
        'Elasticsearch Master 选举机制是怎样的？',
        '- ES 7+ 采用类似 Raft 的选举思路（基于 Zen Discovery / 集群状态发布），只有 Master-eligible 节点参与选举。\n- 每个节点维护集群状态版本，通过投票选出唯一 Active Master；Master 负责发布 Cluster State 到所有节点。\n- 配置 `discovery.seed_hosts`、`cluster.initial_master_nodes` 保证首次集群组建与节点发现。\n- 旧 Master 失联后，剩余 Master-eligible 节点会发起新一轮选举；选举期间部分管理操作可能短暂不可用。\n- 避免脑裂：合理设置 Master-eligible 节点为奇数且 ≥3，保证网络分区时多数派可用。',
    ),
    (
        '分片（Shard）与副本（Replica）的作用是什么？',
        '- 主分片（Primary Shard）：索引数据的逻辑分区，写入时按 routing 定位到某个主分片，保证水平扩展能力。\n- 副本分片（Replica Shard）：主分片的拷贝，提供读扩展与高可用；主分片故障时副本可提升为主分片。\n- 分片数在索引创建时确定，之后只能增加副本数，主分片数扩容通常需 reindex 或 shrink/split 等操作。\n- 分片过多会增加集群元数据与 merge 开销；过少则无法利用多节点并行，需按数据量与节点数综合规划。',
    ),
    (
        'Elasticsearch 写入（Indexing）流程是怎样的？',
        '- 客户端发送 Index 请求到 Coordinating Node，根据 `_routing`（默认 `_id`）计算 `shard = hash(routing) % num_primary_shards`。\n- 请求转发到目标 Primary Shard，在 Lucene 中写入内存缓冲区，同时写 Translog 保证宕机可恢复。\n- 默认每 1s Refresh 将内存缓冲区的 Segment 变为可读（近实时），此时文档可被搜索但尚未 fsync 到磁盘。\n- Primary 写入成功后并行复制到 Replica；Replica 确认后返回客户端。Flush 时将 Segment 持久化并清理 Translog。',
    ),
    (
        'Elasticsearch 搜索（Search）流程是怎样的？',
        '- Query 阶段：Coordinating Node 将请求广播到相关分片（Primary 或 Replica），各分片本地 Lucene 检索，返回文档 ID 与 score/排序值。\n- Fetch 阶段：Coordinating Node 根据 ID 到各分片拉取完整 `_source`（或指定字段），合并、排序、分页后返回。\n- 分布式搜索的 score 合并需考虑 IDF 等全局统计；ES 通过 DFS Query Then Fetch 等模式优化打分准确性（代价更高）。\n- Filter 上下文不参与打分，结果可缓存；Query 上下文参与 BM25 等相关性计算。',
    ),
    (
        'ES 写入一致性有哪些级别？',
        '- `write consistency` 控制写入需多少分片副本确认：`quorum`（默认，多数）、`one`、`all`。\n- `wait_for_active_shards` 可要求写入前至少有 N 个活跃分片副本，避免在集群 yellow 时写入不可检索数据。\n- Primary 写入失败不会切换路由；Replica 复制失败会标记分片 stale 并尝试重新分配。\n- 强一致读 ES 不原生提供；通常通过 `refresh=wait_for` 或写入后读 Primary 等方式满足业务需求。',
    ),
    (
        '深分页（Deep Pagination）有什么问题？如何解决？',
        '- `from + size` 分页在深度较大时，协调节点需合并并排序大量文档 ID，内存与延迟急剧上升（默认 max_result_window=10000）。\n- 每个分片需返回 `from + size` 条结果供全局排序，分片越多开销越大。\n- 解决方案：Search After（基于上一页 sort values 游标）、Scroll（快照遍历，适合导出）、Point in Time（PIT + search_after，7.10+）。\n- 业务侧应避免用户翻到极深页码；导出类任务用 Scroll/PIT，实时翻页用 Search After。',
    ),
    (
        'Mapping 是什么？Dynamic Mapping 有什么风险？',
        '- Mapping 定义字段类型、分词器、是否索引、Doc Values 等，类似关系库表结构但更具弹性。\n- Dynamic Mapping 会根据首次见到的字段值自动推断类型（如 long、text、date）。\n- 风险：同一字段名先后写入字符串与数字会导致类型冲突；text 字段默认分词可能不符合预期。\n- 生产环境建议显式定义 Mapping，对不需要检索的字段设置 `index: false`，大文本与高基数字段合理选择 keyword/text。',
    ),
    (
        'Elasticsearch 聚合（Aggregation）有哪些类型？',
        '- 桶聚合（Bucket）：terms、date_histogram、range 等，用于分组统计。\n- 指标聚合（Metric）：sum、avg、max、min、cardinality、percentiles 等，用于计算度量值。\n- 管道聚合（Pipeline）：对其它聚合结果再加工，如 derivative、moving_avg。\n- 聚合默认在分片级计算再合并；高基数字段 cardinality 等使用 HyperLogLog++ 近似算法，注意精度与内存。',
    ),
    (
        'Elasticsearch 性能调优有哪些常见手段？',
        '- 硬件：SSD、充足堆外内存给 Lucene OS Cache，JVM 堆一般设为物理内存一半且不超过 32GB（压缩指针）。\n- 索引设计：合理分片数、避免过多小索引、冷热分离、禁用不必要的 `_source` 或大字段索引。\n- 写入调优：批量 Bulk、适当增大 refresh_interval、异步 replica、减少副本数后再 reindex 扩容。\n- 查询调优：Filter 代替 Query、路由减少分片 fan-out、避免深分页、使用 Doc Values 做排序聚合。',
    ),
    (
        '什么是脑裂（Split Brain）？如何防止？',
        '- 脑裂指集群因网络分区形成两个子集群，各自选举 Master 并独立接受写入，恢复后数据可能冲突。\n- 6.x 通过 `discovery.zen.minimum_master_nodes = N/2 + 1` 防止少数派成为合法 Master。\n- 7.x 后依赖全新集群引导与 Master 投票机制，仍需保证 Master-eligible 节点为奇数且网络稳定。\n- 运维上专用 Master 节点、合理超时、避免跨机房脑裂，必要时使用 Tie-breaker 节点。',
    ),
    (
        'Refresh 与 Flush 的区别是什么？',
        '- Refresh：使新写入 Segment 对搜索可见，默认 1s；仅将内存索引变为可读文件，不一定 fsync。\n- Flush：将 Translog 与 Segment 持久化到磁盘，触发 commit，清空 Translog；频率由 translog 大小与时间策略决定。\n- 增大 `refresh_interval`（如 30s）可提升写入吞吐，但搜索延迟增加。\n- 理解二者区别有助于解释“写入成功但暂时搜不到”的近实时特性。',
    ),
    (
        'Translog 的作用是什么？',
        '- Translog（事务日志）记录尚未 commit 到 Lucene 的操作，保证节点宕机后可通过重放恢复数据。\n- 每次写入同时更新内存 Index 与 Translog；Flush 成功后对应 Translog 段被清除。\n- `index.translog.durability` 可设为 `request`（每次 fsync，更安全）或 `async`（异步，性能更好）。\n- 与 MySQL redo log 类似，是 ES 持久性保证的关键组件。',
    ),
    (
        'Segment Merge 是什么？为什么需要？',
        '- Lucene 写入产生多个不可变 Segment；Segment 过多会增大搜索需遍历的文件数，影响性能。\n- 后台 Merge 线程将多个小 Segment 合并为大 Segment，并清理已删除文档（逻辑删除标记）。\n- Merge 消耗 CPU 与 IO，写入高峰期可能引发 IO 竞争；可通过 `index.merge.policy` 等调优。\n- Force Merge 可手动合并为单个 Segment，适合不再写入的索引，但操作重且需维护窗口执行。',
    ),
    (
        'Elasticsearch 与 Solr 的主要区别？',
        '- 二者均基于 Lucene；Solr 传统上偏企业级配置化搜索，ES 偏云原生分布式与 REST API。\n- ES 天生分布式，分片副本机制内置；SolrCloud 也支持分布式但运维模型不同。\n- ES 在日志分析、实时聚合、DevOps 生态（ELK）更流行；Solr 在严格 Schema、富文本检索等传统搜索仍有应用。\n- 选型看团队生态、运维能力、实时分析需求与现有技术栈。',
    ),
    (
        'Elasticsearch 如何实现滚动升级？',
        '- 滚动升级：逐节点停止 → 升级版本 → 重启加入集群，保证集群始终可用（分片副本保障）。\n- 升级前备份快照、检查 Breaking Changes、先在非生产验证；大版本跨越多主版本时需逐级升级。\n- 升级期间可能禁止部分集群设置变更；需关注 shard 重新分配与 recovery 对性能的影响。\n- 使用 Index Lifecycle Management（ILM）与 Snapshot 降低回滚风险。',
    ),
    (
        '索引别名（Alias）与 Reindex 的使用场景？',
        '- Alias 是指向一个或多个索引的逻辑名称，支持零停机切换（如 my_index_v1 → my_index_v2）。\n- 蓝绿发布：新索引构建完成后切换 Alias，旧索引保留回滚。\n- Reindex 用于 Mapping 变更、分片数调整、跨集群迁移；`_reindex` API 从源索引批量读取写入目标索引。\n- 大数据量 Reindex 需控制 slices 并行度、限流，并在低峰期执行。',
    ),
    (
        'ES 默认使用什么打分算法？',
        '- ES 5+ 默认使用 BM25（Best Matching 25）作为文本相关性打分，替代 TF-IDF。\n- BM25 对词频有饱和效应，避免某个词出现次数过多导致分数无限增大；考虑文档长度归一化。\n- 可通过 `function_score`、`script_score` 自定义打分；业务排序常用 `_score` 与字段 sort 组合。\n- 纯过滤（Filter）不参与打分，适合精确匹配场景。',
    ),
    (
        'Query 与 Filter 上下文有什么区别？',
        '- Query 上下文：参与相关性打分，结果不缓存（打分上下文），适合全文检索。\n- Filter 上下文：二元匹配（是/否），不参与打分，结果可缓存，适合状态、标签、范围等精确过滤。\n- Bool 查询中 `must/should` 处于 Query 上下文，`filter` 处于 Filter 上下文。\n- 性能优化：能 Filter 的尽量 Filter，减少打分开销并利用缓存。',
    ),
    (
        '什么是 Elasticsearch 冷热架构？',
        '- 热节点（Hot）：SSD、高配置，承载最新、高频访问索引。\n- 温节点（Warm）：仍可能查询但频率降低，可用较大容量磁盘。\n- 冷节点（Cold）：极少查询，高存储密度；冻结层（Frozen）进一步降低成本，查询时从快照拉取。\n- 配合 ILM 自动 rollover、shrink、forcemerge、迁移节点 tier，实现成本与性能平衡。',
    ),
    (
        'Elasticsearch 集群监控与常见故障排查思路？',
        '- 关键指标：集群状态（green/yellow/red）、JVM GC、CPU、磁盘水位、线程池拒绝数、search/index 延迟。\n- `_cat/shards`、`_cluster/health`、`_nodes/stats` 快速定位未分配分片、热点节点。\n- 常见问题：磁盘满导致只读、Mapping 爆炸、慢查询、Merge 打满 IO、Circuit Breaker 触发。\n- 使用 Slowlog 分析慢查询，结合 APM/Elastic Stack 或 Prometheus Exporter 做长期监控告警。',
    ),
]
