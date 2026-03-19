#!/usr/bin/env python3
"""
一人制研究公司 Agent OS — 七核系统实现
One-Person Research Company Agent OS — Seven-Core System

Usage:
  python3 research_company_agent.py                    # 演示模式（无需 API Key）
  python3 research_company_agent.py --live "研究问题"   # 真实 API 模式
  ANTHROPIC_API_KEY=xxx python3 research_company_agent.py --live "你的问题"
"""

import os
import sys
import time
import textwrap
import anthropic

# ─────────────────────────────────────────────
# 颜色与显示工具
# ─────────────────────────────────────────────

COLORS = {
    "reset":   "\033[0m",
    "bold":    "\033[1m",
    "dim":     "\033[2m",
    "yellow":  "\033[93m",
    "blue":    "\033[94m",
    "cyan":    "\033[96m",
    "green":   "\033[92m",
    "red":     "\033[91m",
    "magenta": "\033[95m",
    "white":   "\033[97m",
    "gray":    "\033[90m",
}

def c(color, text):
    return f"{COLORS.get(color,'')}{text}{COLORS['reset']}"

def print_header(title, emoji="", width=60):
    line = "═" * width
    print(f"\n{c('bold', c('cyan', line))}")
    label = f" {emoji}  {title} " if emoji else f" {title} "
    padding = (width - len(label)) // 2
    print(c('bold', c('cyan', "║")) + " " * padding + c('bold', c('white', label)) + " " * (width - padding - len(label)) + c('bold', c('cyan', "║")))
    print(f"{c('bold', c('cyan', line))}")

def print_agent_header(name, num, emoji):
    print(f"\n{c('bold', c('yellow', f'▶  核 {num}：{name} {emoji}'))}")
    print(c('gray', "─" * 55))

def print_section(label, content, color="white"):
    print(f"\n  {c('dim', label)}")
    wrapped = textwrap.fill(content, width=70, initial_indent="  ", subsequent_indent="  ")
    print(c(color, wrapped))

def typewriter(text, delay=0.012, indent="  "):
    """打字机效果输出"""
    lines = textwrap.wrap(text, width=68)
    for line in lines:
        for ch in (indent + line + "\n"):
            sys.stdout.write(ch)
            sys.stdout.flush()
            if ch not in ('\n', ' '):
                time.sleep(delay)
    print()


# ─────────────────────────────────────────────
# 七核 Agent 系统提示词
# ─────────────────────────────────────────────

SYSTEM_PROMPTS = {
    "chief": """你是主经营智能体（Chief Operating Agent），负责将主理人的研究意图翻译成清晰任务，
并协调七核岗位系统的运行。你需要简洁地输出：任务描述、任务类型判断、需要七核做什么。
用中文回答，控制在200字以内。""",

    "judgment": """你是判断 Agent（七核系统第一核），负责判断研究任务是否成立、值得做、怎么做。
你的输出格式：
判断结论：[做/不做/暂缓]
研究分级：[轻研究/标准研究/深研究]
核心问题：[一句话]
研究边界：[不包括什么]
主要风险：[1-2条]
用中文，简洁。""",

    "orchestration": """你是编排 Agent（七核系统第二核），负责把研究任务拆解成可执行的阶段结构。
你的输出格式：
阶段一：[名称] → 目标：[描述]
阶段二：[名称] → 目标：[描述]
阶段三：[名称] → 目标：[描述]
仲裁点：[哪个阶段后需要主理人确认]
研究深度：[由判断Agent分级决定]
用中文，简洁。""",

    "research": """你是研究 Agent（七核系统第三核），负责搜集、筛选、提炼研究信息。
你的输出格式：
关键事实：
• [事实1]（确定性：高/中/低）
• [事实2]（确定性：高/中/低）
• [事实3]（确定性：高/中/低）
关键变量：[影响判断的核心变量]
主要矛盾：[不同观点/来源的核心矛盾]
不确定性：[需要进一步求证的内容]
用中文，基于你的知识给出真实有价值的信息。""",

    "expression": """你是表达 Agent（七核系统第四核），负责将研究材料转化为可判断的结构化成果。
你的输出格式：
核心结论：[2-3句话，直接回答研究问题]
关键发现：
1. [发现1]
2. [发现2]
3. [发现3]
主要不确定性：[1-2条诚实的不确定性说明]
建议下一步：[具体的行动建议]
用中文，让主理人看完能做判断。""",

    "execution": """你是执行 Agent（七核系统第五核），负责把研究结论推进到现实行动。
你的输出格式：
执行计划：
• 立即可做：[具体动作]
• 本周内：[具体动作]
• 持续跟踪：[具体动作]
执行边界：[这些动作需要主理人确认后再执行]
用中文，具体可操作。""",

    "audit": """你是监督审计 Agent（七核系统第六核），负责检查整个研究过程的质量。
你的输出格式：
质量评级：[优/良/待改进]
发现的问题：
• [问题1及严重程度]
• [问题2及严重程度]
留痕确认：[关键节点是否有记录]
改进建议：[对本次研究和系统的建议]
用中文，诚实评估，不回避问题。""",

    "memory": """你是记忆 Agent（七核系统第七核），负责将本次研究沉淀为可复用资产。
你的输出格式：
核心结论摘要：[1-2句话]
新增来源/框架：[本次发现的高价值来源或分析框架]
待持续跟踪：[值得长期关注的变量或主题]
本次教训：[下次研究要避免的问题]
下一轮建议：[自然衍生的后续研究方向]
用中文，为未来研究创造复利。""",
}


# ─────────────────────────────────────────────
# 真实 API 调用
# ─────────────────────────────────────────────

def call_agent_streaming(client, agent_key, context, task):
    """调用单个 Agent，流式输出"""
    system = SYSTEM_PROMPTS[agent_key]
    user_msg = f"研究任务：{task}\n\n上下文：{context}"

    full_text = ""
    print("  ", end="", flush=True)

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=600,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
        thinking={"type": "adaptive"},
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if hasattr(event.delta, "text"):
                    chunk = event.delta.text
                    full_text += chunk
                    # 简单格式化输出
                    for ch in chunk:
                        if ch == '\n':
                            sys.stdout.write('\n  ')
                        else:
                            sys.stdout.write(ch)
                        sys.stdout.flush()

    print("\n")
    return full_text


def run_live_mode(task):
    """真实 API 模式运行七核系统"""
    client = anthropic.Anthropic()

    print_header("一人制研究公司 Agent OS", "🏢")
    print(f"\n  {c('dim', '研究任务：')}{c('white', task)}")
    print(f"  {c('dim', '模式：')}{c('green', '真实 API 模式 (claude-opus-4-6)')}")
    print(f"  {c('dim', '时间：')}{c('gray', time.strftime('%Y-%m-%d %H:%M'))}\n")

    context_chain = ""
    agents = [
        ("chief",        "主经营智能体",    "🎛️",  "0"),
        ("judgment",     "判断 Agent",      "🎯",  "1"),
        ("orchestration","编排 Agent",      "📋",  "2"),
        ("research",     "研究 Agent",      "🔍",  "3"),
        ("expression",   "表达 Agent",      "✍️",  "4"),
        ("execution",    "执行 Agent",      "⚡",  "5"),
        ("audit",        "监督审计 Agent",  "🔎",  "6"),
        ("memory",       "记忆 Agent",      "🧠",  "7"),
    ]

    for agent_key, agent_name, emoji, num in agents:
        print_agent_header(agent_name, num, emoji)
        output = call_agent_streaming(client, agent_key, context_chain, task)
        context_chain += f"\n\n【{agent_name}输出】\n{output}"

    print_header("研究任务完成", "✅")
    print(f"\n  {c('green', '七核系统已完成完整运行。')}")
    print(f"  {c('dim', '查看各核输出，即可了解本次研究的完整闭环。')}\n")


# ─────────────────────────────────────────────
# 模拟演示模式（无需 API Key）
# ─────────────────────────────────────────────

DEMO_TASK = "AI Agent 在一人制公司经营中，目前最实际可用的应用场景是什么？"

DEMO_OUTPUTS = {
    "chief": """\
任务描述：研究 AI Agent 在一人制公司经营中的实际可用场景，目标是形成一份可指导决策的研究摘要。

任务类型：标准研究任务（需要信息搜集 + 结构化分析 + 判断输出）

七核分工：
• 判断 Agent → 确认研究边界，对任务分级
• 编排 Agent → 拆解研究阶段，设置主理人仲裁点
• 研究 Agent → 搜集 AI Agent 实际用例信息
• 表达 Agent → 输出结构化研究摘要
• 执行 Agent → 把结论转成可落地的行动清单
• 监督审计 Agent → 检查研究质量与结论可靠性
• 记忆 Agent → 沉淀研究框架和高价值发现""",

    "judgment": """\
判断结论：做（问题清晰，当前信息充足，有判断价值）

研究分级：标准研究（需要搜集多来源信息，2-4 小时可完成）

核心问题：在 2025-2026 年，AI Agent 在一人公司中哪些场景已经真实可用，而不只是演示？

研究边界：
• 不涉及企业级/团队场景
• 不评测具体工具，聚焦场景和使用模式
• 不预测未来，只关注当前已有真实使用

主要风险：
• 风险1：公开信息多为宣传内容，实际可用性存疑（应对：优先找真实用户反馈）
• 风险2：领域变化快，三个月前的信息可能已过时（应对：标注信息时效性）""",

    "orchestration": """\
阶段一：问题定义与边界确认 → 目标：明确"实际可用"的判断标准，锁定研究范围
阶段二：场景搜集与分类 → 目标：整理 5-8 个有真实证据支撑的应用场景
阶段三：深度验证 → 目标：对每个场景判断：可用程度、常见卡点、适合谁用
阶段四：结构化输出 → 目标：形成可判断的研究摘要，含行动建议

仲裁点：阶段二结束后，主理人确认场景分类方向是否符合预期

研究深度：标准研究（判断 Agent 分级结果）""",

    "research": """\
关键事实：
• 内容创作流程自动化（写作、排版、发布）是目前最成熟的场景，大量独立创作者在用（确定性：高）
• 客服与邮件处理自动化已被大量一人电商/服务业者采用，节省60-80%重复工作时间（确定性：高）
• 代码生成与调试场景中，独立开发者将 AI Agent 作为"结对编程伙伴"，效率提升显著（确定性：高）
• 研究与信息整合（每日摘要、竞品追踪）已有成熟工具链支持（确定性：中）
• 销售流程自动化（潜在客户挖掘、个性化邮件）处于早期可用阶段（确定性：中）

关键变量：
• 任务重复性：越重复的任务，Agent 越成熟可用
• 技术门槛：需要用户有基本的工具配置能力
• 输出质量要求：低容错率场景仍需人工介入

主要矛盾：
• 工具演示层面"全场景可用"VS 真实用户反馈中"高频卡点多"之间的落差
• 效率提升的真实幅度：宣传材料说90%，用户反馈普遍是40-60%

不确定性：
• 各场景的实际学习成本和配置时间缺乏可靠数据
• 非技术背景用户的实际使用成功率不明""",

    "expression": """\
核心结论：
当前 AI Agent 在一人制公司中，最实际可用的场景集中在内容创作自动化、客服/邮件处理、代码辅助这三类——它们共同特征是任务重复性高、容错率相对宽松、工具链已经成熟。研究/信息整合和销售流程处于"可用但需要较高配置成本"的阶段。

关键发现：
1. 重复性工作自动化已成熟：内容发布、邮件回复、代码调试——这三类场景的工具链完整，真实用户验证充分
2. "全流程 Agent"仍是早期：一人公司期待的"什么都自动化"在2026年初仍不现实，真正可用的是"单任务 Agent + 人工衔接"的模式
3. 技术门槛是最大瓶颈：对非技术背景的一人创业者，配置成本往往超过预期收益

主要不确定性：
• 各工具的实际稳定性和长期可维护性仍需时间验证
• 非技术用户群体的真实使用成功率数据缺乏

建议下一步：
选择一个与自身业务最匹配的单一场景（推荐：内容创作或客服），跑通一个完整的"任务进入→执行→质量检查"小闭环，再考虑扩展""",

    "execution": """\
执行计划：

• 立即可做：
  — 整理自己的日常工作中，重复性最高的 3 个任务
  — 对每个任务评估：重复度、容错率、信息结构化程度

• 本周内：
  — 选择一个任务，找到对应的主流 Agent 工具（如 content: Claude/Notion AI；email: Superhuman/Front；code: Cursor/GitHub Copilot）
  — 跑一次完整的小任务闭环，记录实际耗时与质量

• 持续跟踪：
  — 每两周做一次"时间账本"：Agent 帮我节省了多少时间？哪里还需要我介入？
  — 关注该场景的工具更新动态

执行边界：
以上计划中，工具的付费决策（选择哪个工具付费）需要主理人确认后再执行""",

    "audit": """\
质量评级：良

发现的问题：
• 问题1：研究 Agent 的"关键事实"部分以知识库信息为主，缺乏对当前真实用户案例的验证（严重程度：中）
• 问题2：表达 Agent 的"建议下一步"略显笼统，与主理人的具体业务情况缺乏对应（严重程度：轻）
• 问题3：本次研究未主动寻找"反方证据"——即 AI Agent 在一人公司中失败的案例（严重程度：中）

留痕确认：
• 判断 Agent 的分级有记录 ✓
• 各核的输入输出有传递 ✓
• 仲裁点设置了，但主理人未实际介入（演示模式）○

改进建议：
• 下一次研究建议在"研究 Agent"阶段主动设置"反方视角搜集"环节
• 表达 Agent 输出应增加"对什么类型的主理人最适用"的受众适配说明""",

    "memory": """\
核心结论摘要：
2026年初，AI Agent 在一人公司中的实际可用场景集中在重复性高、容错率宽松的任务（内容创作、客服、代码辅助），全流程自动化仍是早期。

新增来源/框架：
• 分析框架："重复性 × 容错率 × 工具成熟度"三维评估矩阵——可复用于评估未来任何新 Agent 场景
• 建议追踪来源：独立创作者社区的真实用户反馈（非工具官方文档）

待持续跟踪：
• 非技术背景用户的 Agent 实际使用成功率数据
• 2026 下半年"全流程 Agent"场景是否出现突破

本次教训：
• 研究开始前应明确"实际可用"的判断标准（本次是事后才意识到这个定义很关键）
• 应主动设置"反方证据搜集"环节，避免确认偏误

下一轮建议：
• 深研究：针对主理人最相关的 1 个场景（如内容创作），做一次完整的工具对比研究""",
}

AGENT_META = [
    ("chief",        "主经营智能体",    "🎛️",  "0"),
    ("judgment",     "判断 Agent",      "🎯",  "1"),
    ("orchestration","编排 Agent",      "📋",  "2"),
    ("research",     "研究 Agent",      "🔍",  "3"),
    ("expression",   "表达 Agent",      "✍️",  "4"),
    ("execution",    "执行 Agent",      "⚡",  "5"),
    ("audit",        "监督审计 Agent",  "🔎",  "6"),
    ("memory",       "记忆 Agent",      "🧠",  "7"),
]


def run_demo_mode():
    """模拟演示模式，不需要 API Key"""
    print_header("一人制研究公司 Agent OS", "🏢")
    print(f"\n  {c('dim', '研究任务：')}{c('white', DEMO_TASK)}")
    print(f"  {c('dim', '模式：')}{c('yellow', '演示模式（预置输出，展示系统架构）')}")
    live_cmd = 'ANTHROPIC_API_KEY=xxx python3 research_company_agent.py --live "你的问题"'
    print(f"  {c('dim', '真实模式：')}{c('gray', live_cmd)}")
    print(f"  {c('dim', '时间：')}{c('gray', time.strftime('%Y-%m-%d %H:%M'))}\n")

    time.sleep(0.5)

    for agent_key, agent_name, emoji, num in AGENT_META:
        print_agent_header(agent_name, num, emoji)
        time.sleep(0.3)
        output = DEMO_OUTPUTS[agent_key]
        for line in output.split('\n'):
            if line.startswith('•') or line.startswith('—'):
                print(f"  {c('cyan', line)}")
            elif '：' in line and len(line) < 30:
                parts = line.split('：', 1)
                print(f"  {c('dim', parts[0]+'：')}{c('white', parts[1] if len(parts)>1 else '')}")
            elif line.startswith('关键') or line.startswith('主要') or line.startswith('核心') or line.startswith('建议') or line.startswith('执行') or line.startswith('待持续') or line.startswith('本次'):
                print(f"\n  {c('bold', c('yellow', line))}")
            elif line.strip().startswith(('1.', '2.', '3.')):
                print(f"  {c('green', line)}")
            else:
                print(f"  {c('white', line)}")
            time.sleep(0.015)
        print()
        time.sleep(0.2)

    print_header("系统运行完成", "✅")
    print(f"""
  {c('green', '七核系统完整跑通。')}

  {c('dim', '运行闭环：')}
  {c('cyan', '主理人意图')} → {c('yellow', '主经营智能体翻译')} → {c('cyan', '判断分级')} →
  {c('cyan', '编排结构')} → {c('cyan', '研究输入')} → {c('cyan', '表达成果')} →
  {c('cyan', '执行计划')} → {c('cyan', '监督审计')} → {c('cyan', '记忆沉淀')}

  {c('dim', '要用真实 Claude API 运行：')}
  {c('gray', '  export ANTHROPIC_API_KEY=your_key')}
  {c('gray', '  python3 research_company_agent.py --live "你的研究问题"')}
""")


# ─────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if "--live" in args:
        idx = args.index("--live")
        task = args[idx + 1] if idx + 1 < len(args) else DEMO_TASK
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print(c("red", "\n  错误：真实模式需要设置 ANTHROPIC_API_KEY 环境变量"))
            print(c("gray", "  export ANTHROPIC_API_KEY=your_key\n"))
            sys.exit(1)
        run_live_mode(task)
    else:
        run_demo_mode()


if __name__ == "__main__":
    main()
