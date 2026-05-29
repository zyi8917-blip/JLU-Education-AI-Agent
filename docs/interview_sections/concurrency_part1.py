"""Java 并发与多线程面试题（第一部分）。"""

CONCURRENCY_PART1 = [
    (
        '在 java 中守护线程和本地线程区别？',
        '- Java 线程分用户线程（User Thread）与守护线程（Daemon Thread）；守护线程在 JVM 中为用户线程提供服务，如 GC 线程。\n- 调用 `thread.setDaemon(true)` 必须在 `start()` 之前设置，否则抛 IllegalThreadStateException。\n- 当 JVM 中所有用户线程结束时，守护线程会被自动终止，不会阻止 JVM 退出。\n- 守护线程不适合执行业务逻辑（如写文件、事务），因 JVM 退出时可能未完成；Main 线程默认是用户线程。\n- 区别总结：生命周期绑定 JVM 与用户线程集合；守护线程优先级无特殊含义，仍遵循抢占调度。',
    ),
    (
        '线程与进程的区别？',
        '- 进程是操作系统资源分配的基本单位，拥有独立地址空间、文件描述符、PID；线程是 CPU 调度的基本单位，共享所属进程的堆、方法区等资源。\n- 同一进程内多线程共享内存，通信成本低但需同步；进程间内存隔离，通信需 IPC（管道、Socket、共享内存等）。\n- 线程切换开销小于进程切换（不需切换页表等），但线程崩溃可能影响整个进程。\n- Java 程序运行在 JVM 进程中，Java 线程一般映射到 OS 原生线程（1:1 模型，如 HotSpot）。',
    ),
    (
        '什么是多线程中的上下文切换？',
        '- 上下文切换是 CPU 从执行一个线程切换到另一个线程时，保存当前线程寄存器、程序计数器、栈指针等状态，恢复目标线程状态的过程。\n- 触发原因：时间片用完、线程阻塞（IO/wait/sleep）、更高优先级线程就绪、主动 yield。\n- 开销：用户态↔内核态切换、缓存失效（CPU cache miss）、线程越多切换越频繁，有效 CPU 时间下降。\n- 优化：减少锁竞争、合理线程数（≈ CPU 核数或略多 for IO 密集）、使用协程/异步 IO 降低 OS 线程数。',
    ),
    (
        '死锁与活锁的区别，死锁与饥饿的区别？',
        '- 死锁：多个线程互相持有对方需要的锁，永久阻塞，无人推进。\n- 活锁：线程未阻塞但反复重试、退让，系统状态不改变，类似“两人走廊相遇互让却都过不去”。\n- 饥饿：某线程长期得不到资源（CPU、锁），无法进展；低优先级线程可能被高优先级持续抢占。\n- 死锁需破坏四必要条件之一预防；活锁需引入随机退避；饥饿可通过公平锁、优先级反转保护缓解。',
    ),
    (
        '什么是线程安全？如何判断？',
        '- 线程安全指多线程环境下无论调度顺序如何，程序行为正确且数据一致。\n- 竞态条件：结果依赖线程交错顺序；共享可变状态是根源。\n- 判断：是否有多个线程访问同一变量、是否存在写操作、是否同步。\n- 解决：不可变对象、线程封闭、同步机制、并发容器。',
    ),
    (
        'synchronized 关键字的用法与原理？',
        '- 可修饰实例方法（锁 this）、静态方法（锁 Class 对象）、代码块（显式指定锁对象）。\n- 基于 Monitor（管程）与对象头 Mark Word 中的锁标志；竞争失败线程进入 EntryList 阻塞。\n- JDK 1.6 后锁升级：偏向锁 → 轻量级锁（CAS）→ 重量级锁（OS Mutex），减少无竞争开销。\n- 保证互斥与可见性（unlock 前 flush 到主内存）；不保证有序性需配合 volatile 或 happens-before。',
    ),
    (
        'volatile 关键字的作用与原理？',
        '- 保证可见性：写 volatile 会刷入主内存，读会从主内存加载。\n- 禁止指令重排序：通过内存屏障（LoadLoad、StoreStore 等）约束编译器与 CPU 重排。\n- 不保证复合操作的原子性（如 i++）；适合状态标志、双重检查锁中的 instance 引用。\n- Happens-Before：对 volatile 变量的写 happens-before 后续对该变量的读。',
    ),
    (
        '什么是 CAS？ABA 问题如何解决？',
        '- CAS（Compare-And-Swap）：比较内存值与期望值，相等则更新，CPU 原子指令（如 x86 CMPXCHG）。\n- 优点：无锁、避免阻塞；缺点：自旋消耗 CPU、只能保证一个变量原子、ABA 问题。\n- ABA：值从 A→B→A，CAS 误以为未变；解决：AtomicStampedReference 带版本号、AtomicMarkableReference。\n- Java 中 AtomicInteger、LongAdder 等基于 CAS 实现。',
    ),
    (
        'AtomicInteger 与 LongAdder 的区别？',
        '- AtomicInteger 单个 CAS 变量，高并发下自旋竞争激烈。\n- LongAdder 分段累加（Cell 数组），最后 sum，写分散降低 CAS 冲突，读需合并略慢。\n- 读少写多统计场景（计数器、QPS）优先 LongAdder；需精确原子 get/set 用 AtomicInteger/Long。\n- LongAccumulator 支持自定义累加函数。',
    ),
    (
        'ReentrantLock 与 synchronized 的区别？',
        '- ReentrantLock 是 API 层显式锁，需 lock/unlock（finally 释放）；synchronized  JVM 内置，自动释放。\n- ReentrantLock 支持公平锁、可中断 lock、tryLock 超时、多个 Condition。\n- 两者均支持重入；高竞争下性能接近，ReentrantLock 在复杂场景更灵活。\n- synchronized 优化后（锁升级）大多数场景足够；需 Condition 队列分离时用 ReentrantLock。',
    ),
    (
        '什么是公平锁与非公平锁？',
        '- 公平锁：按申请顺序获取锁，FIFO，避免饥饿但吞吐量低（ReentrantLock(true)、Semaphore 公平模式）。\n- 非公平锁：允许插队，减少线程切换，默认模式，吞吐更高但可能饥饿。\n- synchronized 是非公平锁。\n- 选型：默认非公平；强公平需求（排队业务）才开公平锁。',
    ),
    (
        'ReadWriteLock 读写锁的应用场景？',
        '- 读多写少：读锁共享、写锁独占，多读可并行，提高吞吐。\n- ReentrantReadWriteLock：写锁独占时阻塞所有读写；读锁持有时写锁需等待。\n- 注意锁降级（写→读）允许，锁升级（读→写）不支持，易死锁。\n- StampedLock JDK8+ 乐观读，性能更好但不可重入，使用复杂。',
    ),
    (
        '什么是 Condition？与 wait/notify 的区别？',
        '- Condition 与 Lock 配合，实现线程等待/唤醒，可多个条件队列（如 notFull/notEmpty）。\n- await() 释放锁并等待；signal()/signalAll() 唤醒。\n- wait/notify 绑定 synchronized 与单一等待集；Condition 更灵活。\n- 始终在循环中检查条件（while 而非 if），防止虚假唤醒。',
    ),
    (
        '什么是 happens-before 原则？',
        '- JMM 定义的偏序关系，保证前者操作对后者可见。\n- 规则：程序次序、监视器锁（unlock hb 后续 lock）、volatile 写 hb 后续读、线程 start hb 其内操作、线程内操作 hb join 返回。\n- 传递性：A hb B 且 B hb C 则 A hb C。\n- 无需理解底层重排细节，正确使用 synchronized/volatile/并发工具即可建立 hb。',
    ),
    (
        'Java 内存模型（JMM）是什么？',
        '- JMM 规范线程与主内存、工作内存的交互，屏蔽硬件差异，定义可见性、有序性、原子性保证。\n- 每个线程有工作内存（CPU 缓存抽象），读写共享变量可能在工作内存与主内存间拷贝。\n- 无同步时允许编译器/CPU 重排序，导致其它线程看到不一致状态。\n- synchronized、volatile、final 域、并发包工具提供 JMM 保证。',
    ),
    (
        '什么是指令重排序？如何防止？',
        '- 编译器优化、CPU 乱序执行、内存系统重排导致代码执行顺序与源码不一致。\n- 单线程 as-if-serial 保证结果不变；多线程无同步可能暴露问题（DCL 半初始化对象）。\n- 防止：volatile、synchronized、final 安全发布、Concurrent 工具。\n- 理解 DCL 单例为何需 volatile 修饰 instance。',
    ),
    (
        '双重检查锁（DCL）单例为什么需要 volatile？',
        '- 对象创建非原子：分配内存 → 初始化 → 引用赋值，可能重排为先赋值后初始化。\n- 其它线程可能拿到未完全初始化的对象引用。\n- volatile 禁止重排序，保证写 instance 前对象已初始化完成。\n- 也可使用静态内部类或 enum 单例，JVM 保证线程安全且更简洁。',
    ),
    (
        'ThreadLocal 的原理与内存泄漏问题？',
        '- 每个 Thread 持有 ThreadLocalMap，以 ThreadLocal 为 key 存线程私有副本，避免共享竞争。\n- Entry 弱引用 key（ThreadLocal），强引用 value；ThreadLocal 被回收后 key 为 null 但 value 仍在，若线程池线程长期存活会泄漏。\n- 使用完调用 `remove()`；线程池场景尤其注意。\n- InheritableThreadLocal 子线程可继承父值；TransmittableThreadLocal（TTL）解决线程池传递。',
    ),
    (
        'InheritableThreadLocal 的局限？',
        '- 仅在创建子线程时复制父 ThreadLocal 值；线程池复用线程时不会重新 copy。\n- 异步任务（@Async、线程池）中上下文（TraceId、用户信息）丢失。\n- 解决：TransmittableThreadLocal + TtlRunnable 包装任务。\n- 或使用 Micrometer Context Propagation、Slf4j MDC 配合 TaskDecorator。',
    ),
    (
        'CountDownLatch 的使用场景与原理？',
        '- 一个或多个线程等待其它线程完成（倒计时），计数减到 0 唤醒 await 线程。\n- 不可重置，一次性；基于 AQS shared 模式。\n- 场景：主线程等待多个 worker 完成初始化、并行测试 barrier。\n- countDown 可在不同线程调用；await 可带超时。',
    ),
    (
        'CyclicBarrier 与 CountDownLatch 的区别？',
        '- CyclicBarrier 多线程互相等待到达屏障点再一起继续，可循环重用（reset）。\n- CountDownLatch 是一个等待多个完成，单向倒计时，不可 reset。\n- CyclicBarrier 支持 barrierAction（到达时执行）；BrokenBarrierException 当某线程中断或超时。\n- 分治合并、多阶段并行任务常用 CyclicBarrier。',
    ),
    (
        'Semaphore 信号量的作用？',
        '- 控制同时访问某资源的线程数（许可证），acquire 获取、release 释放。\n- 公平/非公平构造；可用于限流、连接池、停车场模型。\n- 与 Lock 区别：Semaphore 无所有权，release 不必由 acquire 线程调用。\n- 基于 AQS state 计数实现。',
    ),
    (
        'Phaser 相比 CyclicBarrier 的优势？',
        '- 动态注册/注销参与者 party，支持多阶段（phase），更灵活。\n- 可监控各 party 状态，支持分层 phaser（树形）。\n- 适合阶段数不固定、参与者动态变化的并行流水线。\n- API 较复杂，简单屏障仍用 CyclicBarrier。',
    ),
    (
        'AQS（AbstractQueuedSynchronizer）原理？',
        '- JUC 锁与同步器基础框架，核心：volatile state + FIFO CLH 双向队列。\n- 独占模式（ReentrantLock）：tryAcquire/tryRelease；共享模式（Semaphore、CountDownLatch）：tryAcquireShared。\n- 获取失败线程封装 Node 入队 park；释放时 unpark 后继。\n- 理解 AQS 是读懂 ReentrantLock、Semaphore 源码的关键。',
    ),
    (
        '线程池的核心参数有哪些？',
        '- corePoolSize：核心线程数；maximumPoolSize：最大线程数；keepAliveTime：非核心空闲存活时间。\n- workQueue：任务队列（ArrayBlockingQueue、LinkedBlockingQueue、SynchronousQueue）；threadFactory；RejectedExecutionHandler。\n- 提交顺序：核心未满创建核心线程 → 队列 → 非核心线程 → 拒绝策略。\n- Executors 工厂方法了解即可，生产应 ThreadPoolExecutor 显式配置。',
    ),
    (
        '线程池拒绝策略有哪些？',
        '- AbortPolicy：抛 RejectedExecutionException，默认。\n- CallerRunsPolicy：调用者线程执行，反压。\n- DiscardPolicy：静默丢弃。\n- DiscardOldestPolicy：丢弃队列最老任务再提交。\n- 自定义 Policy 记录日志、入 DLQ 等。',
    ),
    (
        '为什么不建议使用 Executors 创建线程池？',
        '- newFixedThreadPool / Single 使用无界 LinkedBlockingQueue，任务堆积 OOM。\n- newCachedThreadPool 最大 Integer.MAX_VALUE 线程，可能创建过多线程 OOM。\n- newScheduledThreadPool 同样无界队列风险。\n- 阿里规约要求显式 ThreadPoolExecutor + 有界队列 + 命名 ThreadFactory + 监控。',
    ),
    (
        '如何合理设置线程池大小？',
        '- CPU 密集：N ≈ CPU 核数 + 1。\n- IO 密集：N ≈ CPU 核数 × (1 + IO耗时/CPU耗时)，或 2×CPU 核数 经验值。\n- 压测调优，结合队列长度、拒绝率、P99 延迟；动态线程池（如 Hippo4j）运行时调整。\n- 异步 IO（NIO、虚拟线程）可显著减少平台线程需求。',
    ),
    (
        'Future 与 CompletableFuture 的区别？',
        '- Future 表示异步结果，get 阻塞，isDone/cancel 功能有限，不能链式组合。\n- CompletableFuture JDK8+ 支持 thenApply、thenCompose、allOf、anyOf、异常处理。\n- 默认 ForkJoinPool.commonPool() 执行 async 任务，可指定 Executor。\n- 微服务编排、并行 RPC 聚合常用 CompletableFuture。',
    ),
    (
        'ForkJoinPool 的工作原理？',
        '- 分治任务：大任务 fork 子任务，join 合并结果；Work-Stealing 双端队列，空闲线程偷取忙线程队列尾部任务。\n- 适合 CPU 密集、可递归拆分（数组求和、并行流）。\n- commonPool 并行度默认 CPU-1；IO 阻塞任务不适合，会占满池。\n- ForkJoinTask 需避免阻塞，阻塞用 ManagedBlocker 或换线程池。',
    ),
    (
        'Parallel Stream 的注意事项？',
        '- 底层 ForkJoinPool.commonPool()，默认多线程并行。\n- 需保证操作无状态、线程安全；避免修改共享变量。\n- IO 阻塞、小数据量、顺序依赖场景不适合，可能更慢。\n- 可自定义 ForkJoinPool 包裹 parallel stream 隔离 commonPool。',
    ),
    (
        'ConcurrentHashMap JDK7 与 JDK8 实现区别？',
        '- JDK7：Segment 分段锁，16 段默认，锁粒度 Segment 级。\n- JDK8：Node 数组 + 链表/红黑树，CAS + synchronized 锁桶头节点，粒度更细。\n- 扩容多线程协助 transfer；size 用 baseCount + CounterCell 类似 LongAdder。\n- 不允许 null key/value；迭代弱一致。',
    ),
    (
        'ConcurrentHashMap 的 size 方法如何实现？',
        '- JDK8：baseCount + CounterCell 数组分散计数，减少竞争；size 时求和可能非精确快照。\n- mappingCount 返回 long，size 返回 int 可能溢出截断。\n- 高并发下 size 为估计值，精确计数需外部同步或 LongAdder。\n- 理解为何 concurrent 容器许多操作为弱一致。',
    ),
    (
        'HashMap 线程不安全的表现？',
        '- JDK7 扩容头插法多线程可能环形链表死循环（CPU 100%）。\n- 多线程 put 可能丢数据、覆盖。\n- get 可能读到不一致结构（JDK8+ 改进但仍非线程安全）。\n- 并发用 ConcurrentHashMap；Collections.synchronizedMap 全表锁性能差。',
    ),
    (
        'CopyOnWriteArrayList 原理与适用场景？',
        '- 写时复制：写操作加锁并复制新数组，读无锁访问原数组引用。\n- 读多写极少（监听器列表、配置快照）；写频繁复制开销大。\n- 迭代器弱一致，反映创建时或某一时刻快照。\n- CopyOnWriteArraySet 基于 COW List 实现。',
    ),
    (
        'BlockingQueue 有哪些实现？如何选择？',
        '- ArrayBlockingQueue：有界数组，一把锁。\n- LinkedBlockingQueue：可选有界/无界，两把锁提高吞吐。\n- SynchronousQueue：不存储，直接 handoff，CachedThreadPool 使用。\n- PriorityBlockingQueue、DelayQueue（定时任务 ScheduledThreadPool）。\n- 生产者消费者模型选型：有界防 OOM、监控队列深度。',
    ),
    (
        'DelayQueue 的原理与应用？',
        '- 无界阻塞队列，元素实现 Delayed 接口，getDelay 返回剩余延迟。\n- 内部 PriorityQueue 按到期时间排序，take 阻塞直到队首到期。\n- 应用：订单超时关闭、缓存过期、ScheduledThreadPoolExecutor 任务调度。\n- 元素需正确 compareTo 与 getDelay 一致。',
    ),
    (
        '什么是 PriorityBlockingQueue？',
        '- 无界优先级阻塞队列，基于二叉堆，插入 O(log n)，take 阻塞。\n- 不保证同优先级 FIFO（JDK 未保证）；非线程安全 Comparator 需外部同步。\n- 任务调度、Dijkstra 等算法并发版本。\n- 无界需注意内存增长。',
    ),
    (
        'SynchronizedQueue 与 LinkedTransferQueue？',
        '- SynchronousQueue 零容量，put 等待 take 配对。\n- LinkedTransferQueue 结合 BlockingQueue 与 SynchronousQueue，transfer 阻塞直到消费者取走。\n- 高性能 handoff 场景；Executor 框架内部使用。\n- 理解 direct handoff 降低缓冲延迟。',
    ),
    (
        '什么是死锁？产生的四个必要条件？',
        '- 互斥、占有且等待、不可剥夺、循环等待四条件同时满足则死锁。\n- 预防：破坏任一条件，如按序加锁破坏循环等待、tryLock 破坏占有等待。\n- 检测：jstack 看 Found one Java-level deadlock；VisualVM、Arthas。\n- 银行家算法了解即可，生产多用有序加锁与超时。',
    ),
    (
        '如何排查死锁？',
        '- jstack <pid> 或 kill -3，搜索 deadlock 关键字。\n- Arthas thread -b 检测阻塞；JConsole/VisualVM 图形化。\n- 日志记录 lock 顺序；单元测试并发压测。\n- 修复：统一锁顺序、减小锁粒度、使用 tryLock 超时退出。',
    ),
    (
        '什么是线程饥饿？如何缓解？',
        '- 线程长期无法获得 CPU 或锁，无法执行；公平锁开销、非公平锁插队、高优先级独占均可导致。\n- 线程池队列满且 max 线程都在忙，新任务长期排队也是一种饥饿。\n- 缓解：公平锁、合理优先级、拆分锁、保证线程池容量。\n- 监控线程池 queue size 与 active count。',
    ),
    (
        '什么是活锁？举例说明？',
        '- 线程不断改变状态响应彼此，却无法前进；无阻塞但无进展。\n- 例：两个线程同时尝试获取两把锁，失败则释放重试，永远错开。\n- 解决：随机退避（Ethernet CSMA/CD）、优先级、限制重试次数。\n- 与死锁区别：活锁线程处于 RUNNABLE 而非 BLOCKED。',
    ),
    (
        '乐观锁与悲观锁的区别？',
        '- 悲观锁：认为冲突多，先加锁再操作（synchronized、SELECT FOR UPDATE）。\n- 乐观锁：认为冲突少，更新时 CAS 或版本号校验（version 字段、Atomic）。\n- 乐观锁适合读多写少；悲观锁适合写冲突高。\n- 乐观锁失败需重试，ABA 与热点行重试风暴需注意。',
    ),
    (
        '数据库乐观锁在 Java 中如何实现？',
        '- 表增加 version 字段，UPDATE ... SET ..., version=version+1 WHERE id=? AND version=?。\n- 影响行数 0 表示冲突，业务重试或提示。\n- MyBatis-Plus @Version、JPA @OptimisticLocking。\n- 与悲观锁 FOR UPDATE 对比：无长锁持有，吞吐高但冲突多需重试。',
    ),
    (
        '什么是可重入锁？为什么需要？',
        '- 同一线程可多次获取同一把锁而不死锁；synchronized、ReentrantLock 均可重入。\n- 递归调用、同类 synchronized 方法互相调用需要可重入。\n- 实现：锁记录持有线程与重入次数，同线程 acquire 计数+1，release 计数-1 到 0 释放。\n- 不可重入锁在同线程二次 lock 会自死锁。',
    ),
    (
        '什么是锁粗化与锁消除？',
        '- 锁消除：JIT 逃逸分析发现对象未逃逸，去掉 synchronized（StringBuffer 优化）。\n- 锁粗化：连续多次 lock/unlock 同对象合并为一次，减少开销。\n- 编译器优化，开发者无需手动，但理解有助于性能分析。\n- 过度细粒度锁反而阻碍粗化，需平衡。',
    ),
    (
        '偏向锁、轻量级锁、重量级锁的区别？',
        '- 偏向锁：无竞争时记录线程 ID，同线程再次进入几乎无开销；其它线程竞争则撤销偏向。\n- 轻量级锁：CAS 竞争，适合短临界区、低竞争。\n- 重量级锁：膨胀为 OS Mutex，线程 park，适合高竞争长临界区。\n- JDK15+ 偏向锁默认禁用，因现代应用锁模式变化。',
    ),
    (
        'Object 的 wait/notify 为什么必须在 synchronized 中？',
        '- wait 释放锁并加入 wait set；notify 从 wait set 移出线程，均需操作对象 Monitor。\n- 未持锁调用抛 IllegalMonitorStateException。\n- 防止 lost wakeup：检查条件与 wait 原子性由锁保证。\n- notifyAll 比 notify 更安全，避免信号丢失给错误线程。',
    ),
    (
        'sleep 与 wait 的区别？',
        '- sleep 是 Thread 静态方法，不释放锁，时间到自动醒；wait 是 Object 方法，释放锁，需 notify/interrupt。\n- wait 必须在 synchronized 块；sleep 可在任意处。\n- 两者均可被 interrupt，抛 InterruptedException，需恢复中断标志或退出。\n- 等待条件用 wait+while；定时延迟用 sleep 或 LockSupport.parkNanos。',
    ),
    (
        'yield 与 sleep(0) 的区别？',
        '- yield 提示调度器让出 CPU 给同级或更高优先级线程，不保证休眠时间，不释放锁。\n- sleep(0) 触发操作系统调度，行为因 OS 而异。\n- 现代 JVM 中 yield 语义弱化，少用于并发控制。\n- 优先用 Lock、Semaphore、阻塞队列而非 yield 协作。',
    ),
    (
        'interrupt 机制如何工作？',
        '- 每个线程有 interrupted 标志；interrupt() 设标志，阻塞中（sleep/wait/join）抛 InterruptedException 并清标志。\n- 正确做法：捕获后 `Thread.currentThread().interrupt()` 恢复标志或退出任务。\n- 不可吞掉中断；线程池任务应响应中断停止循环。\n- lockInterruptibly、Future.cancel(true) 支持可中断等待锁。',
    ),
    (
        '线程有哪些状态？如何转换？',
        '- NEW、RUNNABLE（含 Running/Ready）、BLOCKED（等监视器锁）、WAITING（wait/join/park）、TIMED_WAITING、TERMINATED。\n- start：NEW→RUNNABLE；synchronized 竞争失败→BLOCKED；wait→WAITING；sleep→TIMED_WAITING。\n- jstack 查看线程状态定位问题。\n- RUNNABLE 不代表在 CPU 上跑，可能等 IO。',
    ),
    (
        'start 与 run 方法的区别？',
        '- start 启动新线程，JVM 调用 run；直接 run 只是普通方法调用，在当前线程同步执行。\n- start 只能调用一次；重复 start 抛 IllegalThreadStateException。\n- 线程名、优先级在 start 前设置。\n- 面试常考基础题。',
    ),
    (
        '如何优雅停止线程？',
        '- 不推荐 stop/suspend（已废弃，不安全）；用 volatile boolean 或 interrupt 标志协作停止。\n- 线程池 shutdown → awaitTermination → shutdownNow，配合中断。\n- 长任务定期检查 interrupted，释放资源。\n- Spring @PreDestroy、ShutdownHook 注册清理逻辑。',
    ),
    (
        'Thread.join 的作用？',
        '- 当前线程等待目标线程终止；join 内部调用 wait(0) 直到目标 TERMINATED。\n- join(timeout) 限时等待。\n- 场景：主线程等待子任务完成再汇总。\n- 现代代码更推荐 CountDownLatch、CompletableFuture.allOf。',
    ),
    (
        'UncaughtExceptionHandler 的作用？',
        '- 线程内未捕获异常默认打印栈并终止线程；可 Thread.setDefaultUncaughtExceptionHandler 全局或 per-thread 处理。\n- 线程池 worker 异常若未捕获会导致线程退出并由 pool 补新线程，任务丢失需 handler 或 Future.get。\n- 生产记录日志、告警、上报 APM。\n- CompletableFuture exceptionally 处理异步异常。',
    ),
    (
        'Callable 与 Runnable 的区别？',
        '- Runnable run 无返回值、无 checked exception；Callable call 有返回值、可抛异常。\n- 提交给 ExecutorService 返回 Future<V>。\n- Lambda 表达 Callable 需明确泛型或使用 Callable<T> 形式。\n- 批量 invokeAll/invokeAny 处理多 Callable。',
    ),
    (
        'invokeAll 与 invokeAny 的区别？',
        '- invokeAll：提交集合并等待全部完成（或超时/中断），返回 Future 列表。\n- invokeAny：任一成功即返回其结果，其它 cancel；全失败抛 ExecutionException。\n- invokeAny 适合冗余查询（多数据源谁先返回用谁）。\n- 注意线程池大小与任务数匹配。',
    ),
    (
        'ScheduledThreadPoolExecutor 原理？',
        '- 继承 ThreadPoolExecutor，使用 DelayedWorkQueue 存储 ScheduledFutureTask。\n- schedule 固定延迟；scheduleAtFixedRate 固定频率（可能追赶）；scheduleWithFixedDelay 前次结束到下次开始固定间隔。\n- 核心线程默认不回收；多线程 scheduled 比 Timer 安全（Timer 单线程串行）。\n- 生产定时任务也可用 Quartz、XXL-JOB 分布式调度。',
    ),
    (
        'Timer 与 ScheduledThreadPool 的区别？',
        '- Timer 单线程，任务抛异常整个 Timer 终止；ScheduledThreadPool 多线程，任务异常不影响其它。\n- Timer 基于 java.util.TimerTask；ScheduledThreadPool 集成线程池生态。\n- 不推荐新代码使用 Timer。\n- 集群定时需分布式锁防重复执行。',
    ),
    (
        '什么是 false sharing（伪共享）？',
        '- 不同变量位于同一 CPU 缓存行，一核写导致其它核缓存行失效，性能下降。\n- JDK8 @Contended（需 JVM 参数）或 padding 字段隔离；LongAdder Cell 数组缓解。\n- 高并发计数器、队列 head/tail 需注意。\n- 通过 perf/cache-miss 或 JMH 检测。',
    ),
    (
        'LockSupport.park/unpark 原理？',
        '- 线程阻塞/唤醒的基本工具，unpark 可在 park 前调用（许可），避免 lost signal。\n- AQS 底层使用；比 wait/notify 更灵活，无需持锁。\n- park 可被 interrupt 打断；parkNanos 限时。\n- 理解 unpark 计数许可机制。',
    ),
    (
        'StampedLock 如何使用？',
        '- 三种模式：写锁、悲观读锁、乐观读（tryOptimisticRead + validate）。\n- 乐观读无锁，validate 失败再升级为读锁。\n- 不可重入、不支持 Condition、写锁饥饿读；API 复杂。\n- 读极多写少且愿意承担编码复杂度时使用。',
    ),
    (
        '什么是安全发布（Safe Publication）？',
        '- 对象被其它线程看到时状态完整一致；未安全发布可能看到半初始化对象。\n- 方式：static 初始化（类初始化线程安全）、volatile 引用、final 域（JMM final 规则）、synchronized 内赋值后 escape。\n- 单例、缓存 lazy init 必须安全发布。\n- 不可变对象天然安全发布。',
    ),
    (
        '不可变对象为什么线程安全？',
        '- 状态 final 且在构造中完全初始化，无 setter，引用泄漏时字段也是 final/immutable。\n- String、Integer、LocalDate 等；Collections.unmodifiableXxx 仅视图不可变，底层仍可变。\n- 设计：所有字段 final、深拷贝防御性复制、不暴露 mutable 内部。\n- 减少锁需求，利于并发。',
    ),
    (
        'ConcurrentLinkedQueue 原理？',
        '- 无界非阻塞队列，Michael-Scott 算法，CAS 更新 head/tail。\n- offer/poll 无锁，高吞吐；size() 线性遍历 O(n) 且非精确。\n- 适合多生产者多消费者；需要阻塞 take 用 BlockingQueue。\n- 注意 tail 滞后更新设计。',
    ),
    (
        'LinkedBlockingQueue 为什么两把锁？',
        '- putLock 与 takeLock 分离，生产者与消费者可并行，提高吞吐。\n- count 用 AtomicInteger，需同时持有两把锁更新时按固定顺序防死锁。\n- 默认无界 Integer.MAX_VALUE 容量风险。\n- ArrayBlockingQueue 单锁实现简单。',
    ),
    (
        '线程封闭有哪些方式？',
        '- Ad-hoc 线程封闭：完全无共享，靠约定。\n- ThreadLocal 每线程副本。\n- 栈封闭：对象仅在方法栈内，不逃逸。\n- 减少共享可变状态是并发设计首选。',
    ),
    (
        '什么是竞态条件（Race Condition）？',
        '- 结果依赖线程交错时序；check-then-act（if (!map.contains) map.put）非原子。\n- 修复：原子类、同步块、ConcurrentMap.putIfAbsent。\n- 单元测试难复现，需压力测试与静态分析。\n- 设计阶段识别共享可变状态。',
    ),
    (
        'ConcurrentSkipListMap 的特点？',
        '- 线程安全有序 Map，跳表实现，O(log n) 增删查。\n- 替代 synchronized TreeMap；支持 NavigableMap 接口 subMap、ceilingKey。\n- 内存开销高于 HashMap；需排序并发场景使用。\n- ConcurrentHashMap 无序。',
    ),
    (
        '什么是 ThreadPoolExecutor 的钩子方法？',
        '- beforeExecute/afterExecute：任务前后扩展（MDC 注入、计时）。\n- terminated：池关闭后清理。\n- 子类 override 实现监控与上下文传递。\n- Spring TaskDecorator 类似思路。',
    ),
    (
        '如何传递 MDC 到线程池？',
        '- MDC 基于 ThreadLocal 存 traceId；线程池复用线程导致 MDC 污染或丢失。\n- TaskDecorator 提交前 copy MDC，执行后 restore。\n- TTL（TransmittableThreadLocal）自动传递。\n- Sleuth/Brave 与 Spring Cloud 集成自动处理。',
    ),
    (
        'Java 21 虚拟线程（Virtual Thread）是什么？',
        '- 轻量级用户态线程，由 JVM 调度挂载到少量 Carrier 平台线程，阻塞时不占用 OS 线程。\n- `Thread.startVirtualThread()` 或 `Executors.newVirtualThreadPerTaskExecutor()`。\n- 适合 IO 密集高并发；CPU 密集仍用平台线程池。\n- 避免在虚拟线程上 synchronized 长时间阻塞 carrier（pinning 问题），优先 ReentrantLock。',
    ),
    (
        '虚拟线程与平台线程的区别？',
        '- 虚拟线程创建成本极低（可百万级）；平台线程映射 OS 线程，昂贵。\n- 虚拟线程不应池化，每任务一个；平台线程用线程池复用。\n- ThreadLocal 在虚拟线程上量大需注意内存；pinning 监控 Thread.ofVirtual().name。\n- Spring Boot 3.2+ 支持 virtual thread 作为 Tomcat 线程模型。',
    ),
]
