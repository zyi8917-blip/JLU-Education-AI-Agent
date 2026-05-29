#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Append remaining interview sections to docs/互联网Java工程师面试题.md.

Run from repository root:
    python docs/build_interview_md.py
"""

from __future__ import annotations

import glob
import os
import re
import sys
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent
SOURCES_DIR = DOCS_DIR / "_sources"
TARGET_MD = DOCS_DIR / "互联网Java工程师面试题.md"
APPEND_MARKER = "## 分布式专题"
HTML_COMMENT = "<!-- 后续章节见同目录 append 脚本生成，或继续阅读下方分布式专题 -->"

sys.path.insert(0, str(DOCS_DIR))
from interview_sections.concurrency_part1 import CONCURRENCY_PART1  # noqa: E402
from interview_sections.concurrency_part2 import CONCURRENCY_PART2  # noqa: E402
from interview_sections.elasticsearch import ELASTICSEARCH_QUESTIONS  # noqa: E402
from interview_sections.microservices import MICROSERVICES_QUESTIONS  # noqa: E402

# MyBatis/Spring XML tags that Typora may mis-render without backticks
XML_TAGS = (
    "resultMap",
    "select",
    "insert",
    "update",
    "delete",
    "parameterMap",
    "sql",
    "include",
    "selectKey",
    "cache",
    "association",
    "collection",
    "trim",
    "where",
    "set",
    "foreach",
    "if",
    "choose",
    "when",
    "otherwise",
    "bind",
)


def fix_xml_tags(text: str) -> str:
    """Wrap bare MyBatis XML tags in backticks for Typora."""
    for tag in XML_TAGS:
        text = re.sub(rf"(?<![`<])<{tag}(\s|>|/)", rf"`<{tag}\1", text)
        text = re.sub(rf"</{tag}>(?!`)", rf"</{tag}>`", text)
    return text


def clean_markdown(text: str) -> str:
    """Remove TOC boilerplate and normalize whitespace."""
    text = re.sub(r"\[TOC\]\s*[-—]+\s*", "", text, count=1)
    text = re.sub(r"^#+\s*前言\s*$", "", text, flags=re.M)
    text = re.sub(r"^#+\s*基础篇\s*$", "", text, flags=re.M)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)\s*", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def strip_header_decorations(title: str) -> str:
    title = title.strip()
    title = re.sub(r"^\*+|\*+$", "", title)
    title = re.sub(r"^#+\s*", "", title)
    title = re.sub(r"^[\d]+[、\.．,，]\s*", "", title)
    title = re.sub(r"^[\d]+\.\s*", "", title)
    title = title.replace("**", "").strip()
    return title


def find_source(*patterns: str) -> Path | None:
    for pattern in patterns:
        matches = sorted(SOURCES_DIR.glob(pattern))
        if matches:
            return matches[0]
    return None


def read_source(*patterns: str) -> str:
    path = find_source(*patterns)
    if not path:
        raise FileNotFoundError(f"Source not found: {patterns}")
    return clean_markdown(path.read_text(encoding="utf-8"))


def render_questions(questions: list[tuple[str, str]]) -> str:
    lines: list[str] = []
    for idx, (title, answer) in enumerate(questions, start=1):
        lines.append(f"#### {idx}、{title}")
        lines.append("")
        lines.append(answer.strip())
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_numbered_sections(text: str) -> list[tuple[str, str]]:
    """Parse ## N.title blocks into (title, body) pairs."""
    pattern = re.compile(
        r"^##+\s*(.+?)\s*$([\s\S]*?)(?=^##+\s|\Z)",
        re.M,
    )
    results: list[tuple[str, str]] = []
    for match in pattern.finditer(text):
        raw_title = match.group(1)
        body = match.group(2).strip()
        title = strip_header_decorations(raw_title)
        if not title or title.lower() in {"前言", "基础篇", "spring boot专题"}:
            continue
        if re.match(r"^[一二三四五六七八九十]+[、\.]", title):
            continue
        if not body and len(title) > 40:
            continue
        results.append((title, body))
    return results


def parse_triple_hash_sections(text: str, min_level: int = 3) -> list[tuple[str, str]]:
    """Parse ### / #### question blocks (MySQL/JVM/Redis style)."""
    level = "#" * min_level
    pattern = re.compile(
        rf"^{level}+\s*(.+?)\s*$([\s\S]*?)(?=^#{{3,}}\s|^##+\s|\Z)",
        re.M,
    )
    results: list[tuple[str, str]] = []
    for match in pattern.finditer(text):
        raw_title = match.group(1)
        body = match.group(2).strip()
        title = strip_header_decorations(raw_title)
        if not title:
            continue
        if re.match(r"^[一二三四五六七八九十]+[、\.]", title):
            continue
        if re.match(r"^[\d]+\.[\d]", title):
            continue
        if title.endswith("篇") and len(title) < 12:
            continue
        if title.startswith("5.3.") or title.startswith("2.2"):
            continue
        results.append((title, body))
    return results


def parse_all_question_sections(text: str) -> list[tuple[str, str]]:
    """Merge ### and #### level sections, deduplicate by title."""
    merged: list[tuple[str, str]] = []
    seen: set[str] = set()
    for level in (3, 4):
        for title, body in parse_triple_hash_sections(text, min_level=level):
            key = title.lower()
            if key in seen:
                continue
            seen.add(key)
            merged.append((title, body))
    return merged


def convert_source_to_questions(text: str, limit: int | None = None) -> str:
    sections = parse_numbered_sections(text)
    if len(sections) < 3:
        sections = parse_all_question_sections(text)
    else:
        extra = parse_all_question_sections(text)
        existing = {t.lower() for t, _ in sections}
        for title, body in extra:
            if title.lower() not in existing:
                sections.append((title, body))
                existing.add(title.lower())
    if limit:
        sections = sections[:limit]
    cleaned: list[tuple[str, str]] = []
    for title, body in sections:
        if not title:
            continue
        if not body:
            body = "（参见源码框架专题同类考点。）"
        cleaned.append((title, body))
    return render_questions(cleaned)


REDIS_EXTRA = [
    (
        "Redis 单线程为什么还这么快？",
        "- 纯内存操作，读写速度极快。\n- 单线程避免上下文切换和锁竞争开销。\n- IO 多路复用（epoll）处理大量并发连接。\n- 高效的数据结构（SDS、跳表、压缩列表等）。",
    ),
    (
        "Redis 过期键删除策略？",
        "- **定时删除：** 设置过期时间时创建定时器，到期立即删除（CPU 友好，内存不友好）。\n- **惰性删除：** 访问 key 时检查是否过期（内存友好，可能占用内存）。\n- **定期删除：** 每隔一段时间随机抽查一批 key 删除过期项（折中方案，Redis 实际采用惰性+定期）。",
    ),
    (
        "Redis 内存淘汰策略有哪些？",
        "- noeviction：不淘汰，内存满时写入报错。\n- allkeys-lru / volatile-lru：LRU 淘汰。\n- allkeys-random / volatile-random：随机淘汰。\n- volatile-ttl：淘汰 TTL 最短的 key。\n- allkeys-lfu / volatile-lfu（Redis 4.0+）：LFU 淘汰。",
    ),
    (
        "Redis 管道（Pipeline）是什么？",
        "- 客户端一次性发送多条命令，服务端批量执行后一次性返回结果，减少 RTT 网络往返。\n- 与事务不同，Pipeline 不保证原子性，只是批量发送。\n- 适合批量写入/读取场景，可显著提升吞吐量。",
    ),
    (
        "Redis 发布订阅（Pub/Sub）机制？",
        "- 发布者向 channel 发送消息，所有订阅该 channel 的客户端都会收到。\n- 消息不持久化，订阅者离线期间的消息会丢失。\n- 适用于实时通知；可靠消息应使用 Stream 或 MQ。",
    ),
    (
        "Redis 与 Memcached 的区别？",
        "- Redis 支持丰富的数据类型；Memcached 仅 String。\n- Redis 支持持久化；Memcached 纯内存。\n- Redis 单线程（6.0+ 多线程 IO）；Memcached 多线程。\n- Redis 支持主从、哨兵、集群；Memcached 需客户端实现分布式。",
    ),
]

DUBBO_EXTRA = [
    (
        "Dubbo 的服务暴露和引用过程？",
        "- **暴露：** Spring 容器启动时读取 `dubbo:service` 配置，ServiceConfig 封装服务元数据，通过 ProxyFactory 生成 Invoker，经 Protocol 导出到 Registry 和本地。\n"
        "- **引用：** ReferenceConfig 向 Registry 订阅服务地址，Directory 维护 Invoker 列表，Cluster 做负载均衡与容错，ProxyFactory 生成代理供业务调用。\n"
        "- 整个流程基于 SPI 扩展点，可替换 Protocol、Registry、LoadBalance 等实现。",
    ),
]


def build_zookeeper() -> str:
    text = read_source("*zookeeper*", "*ZooKeeper*")
    extra = [
        (
            "ZAB 协议是什么？",
            "ZAB（Zookeeper Atomic Broadcast）是为 ZooKeeper 设计的原子广播协议，保证分布式环境下数据一致性和顺序性。包含两种模式：恢复模式（Leader 选举）和广播模式（事务同步）。所有事务请求由 Leader 发起广播，超过半数 Follower ACK 后提交。",
        ),
        (
            "客户端注册 Watcher 的实现原理？",
            "客户端通过 getData/exists/getChildren 注册 Watcher，将 Watcher 对象封装在 WatchRegistration 中。网络层发送请求到服务端，服务端将 Watcher 存储在 WatchManager。当节点变更时，服务端向客户端发送 WatchedEvent，客户端在 EventThread 中回调 Watcher.process()。",
        ),
        (
            "服务端处理 Watcher 的实现原理？",
            "服务端 DataTree 记录每个节点上的 Watcher 列表。节点数据变更时，ProcessRequestProcessor 触发相应 Watcher，将事件放入 outgoingQueue，由 SendThread 发送给客户端。Watcher 触发后会被移除（一次性触发）。",
        ),
        (
            "客户端回调 Watcher 的流程？",
            "SendThread 接收 WatchedEvent，交给 EventThread 异步处理，避免阻塞 IO 线程。EventThread 从 waitingEvents 队列取出事件，调用 Watcher.process()。用户逻辑应轻量，避免阻塞 EventThread。",
        ),
        (
            "ZooKeeper 如何保证顺序一致性？",
            "每个事务分配全局递增 zxid（高 32 位 epoch + 低 32 位 counter）。Leader 按顺序广播提案，Follower 按 zxid 顺序执行。客户端读请求可能读到旧数据，但同一客户端的读写顺序一致（syncConnected 后）。",
        ),
    ]
    base = parse_numbered_sections(text)
    existing_titles = {t.lower() for t, _ in base}
    for title, body in extra:
        if title.lower() not in existing_titles:
            base.append((title, body))
    return render_questions(base[:28])


def build_distributed_section() -> str:
    parts = [
        "## 分布式专题\n",
        "### ZooKeeper 面试题\n",
        build_zookeeper(),
        "### Dubbo 面试题\n",
        render_questions(
            (parse_numbered_sections(read_source("*Dubbo*")) + DUBBO_EXTRA)[:30]
        ),
        "### Elasticsearch 面试题\n",
        render_questions(ELASTICSEARCH_QUESTIONS),
        "### Redis 面试题\n",
        convert_source_to_questions(read_source("*Redis*") + "\n\n" + "\n".join(
            f"### {t}\n\n{a}" for t, a in REDIS_EXTRA
        ), limit=42),
        "### RabbitMQ 面试题\n",
        convert_source_to_questions(read_source("*Rabbit*"), limit=12),
        "### Kafka 面试题\n",
        convert_source_to_questions(read_source("*Kafka*"), limit=18),
    ]
    return "\n".join(parts)


def build_concurrency_sections() -> str:
    return (
        "## Java 核心专题 - 并发编程（一）\n\n"
        + render_questions(CONCURRENCY_PART1)
        + "\n## Java 核心专题 - 并发编程（二）\n\n"
        + render_questions(CONCURRENCY_PART2)
    )


def build_mysql_section() -> str:
    text = read_source("*MySQL*")
    sections = parse_all_question_sections(text)
    if len(sections) < 40:
        sections = parse_numbered_sections(text)
    sections = sections[:50]
    return "## 性能调优专题 - MySQL 面试题\n\n" + render_questions(
        [(t, b if b else "（详见 MySQL 官方文档与 InnoDB 存储引擎原理。）") for t, b in sections]
    )


def build_jvm_section() -> str:
    text = read_source("*JVM*")
    sections = parse_all_question_sections(text)
    if len(sections) < 10:
        sections = parse_numbered_sections(text)
    sections = sections[:13]
    return "## 性能调优专题 - JVM 面试题\n\n" + render_questions(
        [(t, b if b else "（参见 JVM 规范与《深入理解 Java 虚拟机》。）") for t, b in sections]
    )


SPRING_BOOT_EXTRA = [
    (
        "Spring Boot 中 @SpringBootApplication 注解的作用？",
        "- 组合了 `@Configuration`、`@EnableAutoConfiguration`、`@ComponentScan`。\n"
        "- `@EnableAutoConfiguration` 开启自动配置，根据 classpath 中的依赖自动装配 Bean。\n"
        "- `@ComponentScan` 扫描当前包及子包下的 Spring 组件。\n"
        "- 是 Spring Boot 应用的入口注解，标注在 main 类上。",
    ),
    (
        "Spring Boot 如何实现热部署？",
        "- 开发环境可使用 `spring-boot-devtools` 依赖，配合 IDE 自动编译实现热重启。\n"
        "- devtools 使用两个 ClassLoader：base 加载不变类，restart 加载会变更的类。\n"
        "- 生产环境不建议开启热部署，应使用蓝绿发布或滚动升级。",
    ),
]


def build_microservices_section() -> str:
    boot_text = read_source("*SpringBoot*")
    boot_sections = parse_numbered_sections(boot_text)
    boot_sections.extend(SPRING_BOOT_EXTRA)
    spring_boot = render_questions(boot_sections[:22])
    spring_cloud = convert_source_to_questions(read_source("*Spring*Cloud*"), limit=8)
    return (
        "## 微服务专题\n\n"
        "### 微服务面试题\n\n"
        + render_questions(MICROSERVICES_QUESTIONS)
        + "\n### Spring Boot 面试题\n\n"
        + spring_boot
        + "\n### Spring Cloud 面试题\n\n"
        + spring_cloud
    )


def build_append_content() -> str:
    sections = [
        build_distributed_section(),
        build_concurrency_sections(),
        build_mysql_section(),
        build_jvm_section(),
        build_microservices_section(),
    ]
    content = "\n\n---\n\n".join(s.rstrip() for s in sections) + "\n"
    return fix_xml_tags(content)


def strip_existing_append(text: str) -> str:
    """Remove HTML comment and any previously appended content."""
    text = text.replace(HTML_COMMENT, "").rstrip()
    idx = text.find(APPEND_MARKER)
    if idx != -1:
        text = text[:idx].rstrip()
    if text.endswith("---"):
        text = text.rstrip("-").rstrip()
    return text + "\n\n---\n\n"


def main() -> None:
    if not TARGET_MD.exists():
        raise SystemExit(f"Target file not found: {TARGET_MD}")

    original = TARGET_MD.read_text(encoding="utf-8")
    base = strip_existing_append(original)
    append = build_append_content()
    final = base + append
    final = fix_xml_tags(final)

    TARGET_MD.write_text(final, encoding="utf-8")

    line_count = final.count("\n") + (1 if final and not final.endswith("\n") else 0)
    size_kb = TARGET_MD.stat().st_size / 1024
    print(f"Updated: {TARGET_MD}")
    print(f"Lines:   ~{line_count}")
    print(f"Size:    {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
