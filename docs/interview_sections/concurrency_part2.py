"""Java 并发与多线程面试题（第二部分）。"""

CONCURRENCY_PART2 = [
    (
        '并发编三要素？',
        '- 原子性：操作不可被中途打断，要么全部执行要么都不执行；synchronized、Lock、CAS、Atomic 类保证。\n- 可见性：一个线程修改共享变量，其它线程能立即看到；volatile、synchronized、final 保证。\n- 有序性：程序执行顺序按代码逻辑；happens-before 规则禁止有害重排序。\n- 三者缺一不可；仅 volatile 保证可见性与有序性，不保证复合操作原子性。',
    ),
    (
        '实现可见性的方法有哪些？',
        '- volatile：写刷主内存，读从主内存加载。\n- synchronized：unlock 前 flush，lock 时从主内存读。\n- final 域：构造完成后其它线程看到 final 字段正确值（安全发布）。\n- Lock/Atomic 类内部 volatile 或 CAS + hb 语义。\n- Thread.start/join 也建立 happens-before 可见性。',
    ),
    (
        '多线程的价值？',
        '- 充分利用多核 CPU，提高 CPU 密集型任务吞吐。\n- IO 密集型任务重叠等待时间，提高资源利用率与响应速度。\n- 改善用户体验：后台任务、异步通知、并行加载。\n- 模块化：独立子任务解耦；但需权衡复杂性与调试成本。',
    ),
    (
        '创建线程的有哪些方式？',
        '- 继承 Thread 重写 run（不推荐，单继承限制）。\n- 实现 Runnable 接口，传给 Thread 或线程池（推荐）。\n- 实现 Callable<V>，配合 Future 获取返回值。\n- 线程池 ExecutorService 提交任务（生产首选）。\n- JDK21：`Thread.ofVirtual().start(runnable)` 创建虚拟线程。',
    ),
    (
        'Runnable 与 Callable 在线程池中的使用？',
        '- execute(Runnable) 无返回值；submit 返回 Future，Runnable 结果 null，Callable 返回 V。\n- submit 异常封装在 Future.get 的 ExecutionException 中；execute 未捕获异常走 UncaughtExceptionHandler。\n- 批量任务 invokeAll/invokeAny 提交 Callable 集合。\n- Lambda 简写：`() -> {}` 与 `() -> result`。',
    ),
    (
        '线程池 submit 与 execute 的区别？',
        '- execute 提交 Runnable，异常直接抛出到 handler；submit 包装为 FutureTask，异常存 Future。\n- submit 可提交 Callable/Runnable+result。\n- 生产需 Future.get 或 whenComplete 处理 submit 异常，否则静默失败。\n- 定时池 schedule 类似 submit 语义。',
    ),
    (
        'FutureTask 的实现原理？',
        '- 实现 RunnableFuture，既可在新 Thread 跑也可线程池 execute。\n- 基于 AQS 共享模式，state 表示运行/完成/取消；run 执行 Callable，set 结果并 releaseShared 唤醒 get 等待线程。\n- get 阻塞直到 done 或超时/中断。\n- 理解 FutureTask 是线程池 submit 的核心包装类。',
    ),
    (
        'CompletableFuture 常用组合 API？',
        '- thenApply/thenAccept/thenRun 链式同步阶段；thenApplyAsync 异步。\n- thenCompose 扁平化嵌套 Future；thenCombine 合并两 Future。\n- allOf/anyOf 多路汇聚；exceptionally/handle 异常处理。\n- supplyAsync 指定自定义 Executor 隔离 commonPool。',
    ),
    (
        'CompletableFuture 异常如何处理？',
        '- exceptionally 返回兜底值；handle(biFunction) 同时处理结果与异常。\n- whenComplete 消费结果不转换；completeExceptionally 手动失败。\n- 链式中间 stage 异常传播到后续 exceptionally，类似 try-catch-finally 链。\n- 未处理的异常 completion 阶段可能静默，需 always 记录日志。',
    ),
    (
        '什么是 ForkJoinPool 的 commonPool？',
        '- 静态共享池，parallelStream、CompletableFuture 默认使用。\n- 并行度 Runtime.getProcessors()-1；全局竞争可能影响 unrelated 任务。\n- 隔离：`ForkJoinPool pool = new ForkJoinPool(n); pool.submit(() -> list.parallelStream()...).get()`。\n- 监控 commonPool 队列与 steal 次数评估是否瓶颈。',
    ),
    (
        'Stream parallel 与 parallelStream 区别？',
        '- collection.parallelStream() 便捷；stream().parallel() 等价。\n- parallel 是有状态的中间操作可能需合并开销。\n- 数据源需 Spliterator 支持高效拆分（ArrayList 好，LinkedList 差）。\n- 终端操作触发 ForkJoin 执行。',
    ),
    (
        'synchronized 锁升级过程？',
        '- 无锁 → 偏向锁（记录线程 ID）→ 撤销偏向 → 轻量级锁 CAS → 膨胀重量级 Monitor。\n- 竞争加剧锁粒度变大，开销上升。\n- JDK15 默认关闭偏向锁 `-XX:-UseBiasedLocking`。\n- 减少锁竞争比关注升级细节更重要。',
    ),
    (
        'Monitor 对象监视器结构？',
        '- 对象头 Mark Word 存锁状态；Monitor 有 Owner、EntryList、WaitSet。\n- 竞争锁失败进 EntryList 阻塞；wait 进 WaitSet。\n- synchronized 字节码 monitorenter/monitorexit 配合。\n- AQS 抽象了更通用的队列同步器。',
    ),
    (
        'ReentrantReadWriteLock 锁降级如何实现？',
        '- 持有写锁 → 获取读锁 → 释放写锁，变为读锁，允许其它读继续。\n- 防止写锁释放瞬间被其它写抢占，保持数据一致性读取。\n- 代码：`wlock.lock(); try { update(); rlock.lock(); } finally { wlock.unlock(); }` 再释 rlock。\n- 锁升级（读→写）不支持，会死锁。',
    ),
    (
        'StampedLock 乐观读流程？',
        '- long stamp = lock.tryOptimisticRead(); 读数据；if (!lock.validate(stamp)) { 获取悲观读锁重读 }。\n- validate 检查 stamp 是否被写锁破坏。\n- 写锁与乐观读互斥；适合读多写少且读段短。\n- 不可重入，嵌套使用易错。',
    ),
    (
        'AtomicReference 的应用？',
        '- CAS 更新引用，实现无锁数据结构（栈、链表头）。\n- AtomicReferenceFieldUpdater 减少对象开销，更新 volatile 字段。\n- compareAndSet(expected, update) 失败需重试循环。\n- 配合不可变对象替换实现线程安全容器更新。',
    ),
    (
        'LongAdder 为什么比 AtomicLong 快？',
        '- 热点写分散到多个 Cell，降低 CAS 失败自旋。\n- sum 遍历 Cell 求和，非原子快照。\n- 高并发计数、Metrics 首选 LongAdder。\n- 需要 compareAndSet 精确控制时用 AtomicLong。',
    ),
    (
        '什么是 Unsafe 类？',
        '- sun.misc.Unsafe / jdk.internal.misc.Unsafe 提供 CAS、内存屏障、直接内存等底层 API。\n- Atomic、AQS、ConcurrentHashMap 内部依赖。\n- 普通业务不应直接使用；模块系统限制访问。\n- Foreign Memory API（Panama）部分替代直接内存操作。',
    ),
    (
        'VarHandle 与 Unsafe 的关系？',
        '- JDK9 VarHandle 提供标准化字段/数组元素 CAS、volatile 访问，替代部分 Unsafe。\n- 类型安全、支持访问控制检查。\n- 新并发库代码优先 VarHandle。\n- MethodHandles.lookup().findVarHandle 获取。',
    ),
    (
        'ConcurrentHashMap compute 系列方法？',
        '- compute/computeIfAbsent/computeIfPresent/merge 原子地对 key 计算新 value。\n- 避免 get-put 竞态；函数内不应修改其它 bucket 防死锁。\n- computeIfAbsent 适合缓存 lazy load。\n- merge 用于计数合并（BiFunction remappingFunction）。',
    ),
    (
        'ConcurrentHashMap 的 keySet/views 线程安全吗？',
        '- keySet、values、entrySet 弱一致迭代，反映某一时刻或部分更新。\n- size 非精确；containsKey get 线程安全。\n- 批量 forEach 支持并行 forEach(parallelismThreshold, action)。\n- 迭代中 remove 需用 Iterator.remove 或 remove(key)。',
    ),
    (
        'Collections.synchronizedXxx 原理？',
        '- 包装原集合，每个方法 synchronized(mutex) 互斥。\n- 迭代需手动 synchronized 包裹 iterator，否则 fail-fast 与并发修改问题。\n- 单一锁，并发度低；高并发用 Concurrent 容器。\n- synchronizedList/Map/Set 简单场景可用。',
    ),
    (
        'Vector 与 Hashtable 还有必要用吗？',
        '- 方法级 synchronized，并发性能差；已被 ConcurrentHashMap、CopyOnWriteArrayList 替代。\n- 遗留 API 兼容；新代码不应使用。\n- Properties 继承 Hashtable，配置读取单线程场景仍常见。\n- 了解历史线程安全容器演进。',
    ),
    (
        'BlockingDeque 的应用？',
        '- 双端阻塞队列，LinkedBlockingDeque、ArrayBlockingDeque。\n- 支持 putFirst/takeLast 等，工作窃取、链式 pipeline。\n- LinkedBlockingDeque 可选 capacity。\n- 比普通 BlockingQueue 更灵活的双向操作。',
    ),
    (
        'ThreadLocalRandom 的优势？',
        '- 避免 Random 全局 seed 的 CAS 竞争；每线程独立生成器。\n- `ThreadLocalRandom.current().nextInt()` 并发环境性能更好。\n- SplittableRandom 可 fork 拆分用于 parallel 计算。\n- 不要在多线程共享 Random 实例。',
    ),
    (
        '什么是信号量控制连接池？',
        '- 数据库连接池本质是限制并发连接数；Semaphore 可模拟简易池。\n- acquire 获取连接许可，release 归还；与真实池的 idle/active 管理结合。\n- HikariCP 内部用 ConcurrentBag 等结构，思想类似资源限流。\n- 理解信号量建模资源配额。',
    ),
    (
        'CountDownLatch 在单元测试中的应用？',
        '- 并发测试：N 个线程 countDown，主线程 await 验证结果。\n- 模拟多线程同时起跑：`new CountDownLatch(1)` 所有线程 await，主线程 countDown 发令枪。\n- 不可 reset，重复场景用 CyclicBarrier。\n- 配合 ExecutorService 与断言工具。',
    ),
    (
        'CyclicBarrier 的 barrierAction？',
        '- 构造传入 Runnable，最后一个到达屏障的线程执行 action 后其它继续。\n- 用于汇总分片结果、打印阶段完成日志。\n- 任一线程中断或超时 broken，所有 await 抛 BrokenBarrierException。\n- reset 后可新一轮屏障。',
    ),
    (
        'AQS 共享模式与独占模式？',
        '- 独占：ReentrantLock，state 0/1，一个线程持有。\n- 共享：Semaphore/CountDownLatch，state 表示剩余许可或计数，多线程可同时 acquire。\n- tryReleaseShared 唤醒后继共享节点 propagate。\n- Condition 基于 AQS 另建等待队列。',
    ),
    (
        'CLH 队列是什么？',
        '- Craig-Landin-Hager 自旋锁队列，FIFO 公平；AQS 变体 CLH 双向队列用于阻塞同步器。\n- 节点 waitStatus 表示 CANCELLED、SIGNAL、CONDITION 等。\n- park/unpark 挂起唤醒，避免无限自旋。\n- 理解有助于读 AQS acquire 源码。',
    ),
    (
        '线程池 core 线程会被回收吗？',
        '- allowCoreThreadTimeOut(true) 且 keepAliveTime>0 时，核心线程空闲超时也可回收。\n- 默认 false，核心线程常驻。\n- prestartAllCoreThreads 预启动全部核心线程减少冷启动延迟。\n- 动态线程池根据负载调整 core/max。',
    ),
    (
        '线程池队列如何选择？',
        '- 有界 ArrayBlockingQueue：固定容量，防 OOM，可能触发 max 线程。\n- LinkedBlockingQueue：可选无界，仅扩 max 线程当 core 满且 queue 满（有界时）。\n- SynchronousQueue：直接交接，适合 Cached 风格。\n- 优先有界 + CallerRunsPolicy 反压。',
    ),
    (
        '什么是线程池预热？',
        '- 启动时 prestartCoreThread(s) 创建核心线程 idle 等待任务。\n- 避免首请求临时建线程延迟。\n- 配合压测流量 warm-up JVM（CJIT 编译）。\n- 微服务启动探针 ready 前完成预热。',
    ),
    (
        '如何监控线程池健康？',
        '- 暴露 metrics：activeCount、poolSize、queue.size、completedTaskCount、reject 次数。\n- Micrometer + Prometheus/Grafana 告警 queue 堆积。\n- 动态线程池框架 Hippo4j、DynamicTp 运行时调参。\n- 日志 dump 线程栈分析 blocked 任务。',
    ),
    (
        'ForkJoinTask 的 fork/join 注意点？',
        '- fork 异步执行子任务；join 阻塞等结果，应用在当前线程先 helpSteal 再 join 减少空等。\n- 任务粒度适中，过细 fork 开销大于收益。\n- 避免在 FJP 内阻塞 IO，用 Async 或单独线程池。\n- RecursiveTask/RecursiveAction 模板。',
    ),
    (
        '什么是 Work-Stealing？',
        '- 每个 worker 双端队列，自己从 head 取任务，空闲线程从其它队列 tail 偷任务。\n- 减少全局队列锁竞争，适合分治不平衡负载。\n- ForkJoinPool、某些 Executor 实现采用。\n- steal 次数高说明负载不均或任务过小。',
    ),
    (
        'parallelStream 一定更快吗？',
        '- 不一定：数据小、任务轻，拆分与调度开销超过收益。\n- 需 CPU 密集且可并行；IO、顺序依赖、共享 mutable 状态更慢或错误。\n- 应用 JMH 基准测试验证。\n- 默认 commonPool 与其它任务争用。',
    ),
    (
        '如何取消长时间运行的任务？',
        '- Future.cancel(mayInterruptIfRunning)；中断标志通知任务退出。\n- 任务内定期检查 Thread.interrupted()。\n- CompletableFuture.cancel 依赖底层任务可中断。\n- shutdownNow 向池内任务发 interrupt。',
    ),
    (
        '线程池 shutdown 流程？',
        '- shutdown：停止接收新任务，已提交继续执行。\n- shutdownNow：尝试 interrupt 所有 worker，返回未执行任务列表。\n- awaitTermination(timeout) 等待结束。\n- Spring 容器销毁时优雅关闭 @Bean(destroyMethod=shutdown) Executor。',
    ),
    (
        '什么是 double-checked locking 问题集合？',
        '- 半初始化对象、指令重排需 volatile。\n- 懒加载 singleton、延迟初始化缓存均需注意 safe publication。\n- 静态内部类、enum 是更优单例方案。\n- 理解 JMM 与 DCL 是并发基础考点。',
    ),
    (
        '什么是 happens-before 与 as-if-serial？',
        '- as-if-serial：单线程内重排不改变语义。\n- happens-before 跨线程可见性保证；若无 hb 关系，JVM 可任意重排。\n- 程序员通过同步工具建立 hb，无需记忆所有硬件细节。\n- 并发 bug 本质是缺少 hb。',
    ),
    (
        '内存屏障（Memory Barrier）类型？',
        '- LoadLoad、StoreStore、LoadStore、StoreLoad；StoreLoad 最强。\n- volatile 写后插入 StoreStore+StoreLoad，读前 LoadLoad+LoadStore。\n- CPU 指令如 mfence、lock 前缀。\n- JMM 对程序员抽象为 volatile/synchronized 语义。',
    ),
    (
        'Java 并发包（JUC）核心类分类？',
        '- 锁：ReentrantLock、ReadWriteLock、StampedLock。\n- 同步器：CountDownLatch、Semaphore、CyclicBarrier、Phaser。\n- 并发集合：ConcurrentHashMap、CopyOnWriteArrayList、BlockingQueue 系列。\n- 原子类：Atomic*、LongAdder；线程池：ThreadPoolExecutor、ForkJoinPool。',
    ),
    (
        '并发编程有哪些设计模式？',
        '- 保护性暂停（Guarded Suspension）：wait until condition。\n- Balking：条件不满足直接返回。\n- 生产者消费者、Thread-Specific Storage、Future、Master-Worker。\n- 读写锁分离、不变模式（Immutable）。',
    ),
    (
        '生产者消费者模式 Java 实现？',
        '- wait/notify + synchronized 缓冲区；BlockingQueue 更简洁。\n- put 阻塞满队列，take 阻塞空队列。\n- 多生产者多消费者 BlockingQueue 线程安全。\n- 背压：有界队列 + 拒绝策略。',
    ),
    (
        'ConcurrentHashMap 1.8 为什么引入红黑树？',
        '- 单 bucket 链表过长（>8 且 table>=64）转红黑树，查询 O(log n)。\n- 哈希冲突极端时避免链表退化 O(n)。\n- 节点少时退化为链表。\n- 平衡空间与查询性能。',
    ),
    (
        'enum 单例为什么推荐？',
        '- JVM 保证 enum 实例唯一且线程安全，反序列化仍同一实例。\n- 代码简洁：`enum Singleton { INSTANCE; public void doSomething(){} }`。\n- Effective Java 推荐，天然防反射与序列化破坏单例。\n- 缺点是不能 lazy load（类加载时初始化）。',
    ),
    (
        '静态内部类单例如何实现 lazy 加载？',
        '- 私有构造 + 静态内部类 Holder 持有 INSTANCE，类初始化 JVM 保证线程安全。\n- 第一次调用 getInstance 才加载 Holder，实现延迟初始化。\n- 无 synchronized 性能开销，无 DCL volatile 复杂度。\n- 常用单例最佳实践之一。',
    ),
]
