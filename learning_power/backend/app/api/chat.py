"""
对话API - 学习力画像智能助手
"""
from flask import request
from datetime import datetime
import json
import logging
import os

from app.api import chat_bp
from app.utils.response import success_response, error_response
from app.utils.llm_client import LLMClient

logger = logging.getLogger(__name__)


@chat_bp.route('/portrait', methods=['POST'])
def chat_with_portrait():
    """
    与学习力画像智能助手对话
    
    请求参数:
    {
        "student_id": "2024001",
        "student_name": "张三",
        "message": "我的认知能力怎么样？",
        "portrait_data": {
            "total_dict": {...},
            "rating_dict": {...},
            "feedback_dict": {...}
        },
        "chat_history": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }
    
    返回:
    {
        "code": 200,
        "message": "success",
        "data": {
            "reply": "根据您的测评结果...",
            "timestamp": "2025-11-17T10:30:00"
        }
    }
    """
    try:
        data = request.get_json()
        
        student_id = data.get('student_id', '')
        student_name = data.get('student_name', '同学')
        message = data.get('message', '')
        portrait_data = data.get('portrait_data', {})
        chat_history = data.get('chat_history', [])
        
        if not message:
            return error_response('消息内容不能为空', 400)
        
        logger.info(f"Chat request from student {student_id}: {message[:50]}...")
        
        # 构建丰富的系统提示词
        system_prompt = build_system_prompt(student_name, portrait_data)
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 添加历史对话（最多保留最近5轮）
        if chat_history:
            recent_history = chat_history[-10:]  # 最多保留10条消息（5轮对话）
            messages.extend(recent_history)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": message})
        
        reply = None
        use_lc = os.getenv("USE_LC_EVAL", "true").lower() in ("1", "true", "yes")
        if use_lc:
            try:
                from app.agents.lc_portrait_chat import portrait_reply_lc

                reply = portrait_reply_lc(
                    system_prompt=system_prompt,
                    message=message,
                    chat_history=chat_history,
                )
            except Exception as lc_exc:
                logger.warning("LangChain portrait chat failed, fallback: %s", lc_exc)

        if reply is None:
            llm_client = LLMClient()
            if not llm_client.client:
                return error_response('LLM服务暂时不可用', 503)

            response = llm_client.client.chat.completions.create(
                model=llm_client.model,
                messages=messages,
                temperature=0.7,
                max_tokens=800,
                timeout=30,
            )
            reply = response.choices[0].message.content.strip()
        
        logger.info(f"Chat response generated successfully (length: {len(reply)})")
        
        return success_response({
            'reply': reply,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat_with_portrait: {str(e)}", exc_info=True)
        return error_response(f'对话失败: {str(e)}', 500)


def build_system_prompt(student_name, portrait_data):
    """
    构建丰富的系统提示词
    
    Args:
        student_name: 学生姓名
        portrait_data: 学习力画像数据
    
    Returns:
        str: 系统提示词
    """
    # 提取数据
    total_dict = portrait_data.get('total_dict', {})
    rating_dict = portrait_data.get('rating_dict', {})
    feedback_dict = portrait_data.get('feedback_dict', {})
    
    # 维度名称映射
    dimension_names = {
        'cognitive_strategy': '认知策略',
        'metacognition': '元认知能力',
        'critical_thinking': '批判性思维',
        'learning_motivation': '学习动机',
        'social_emotional': '社会情感能力'
    }
    
    # 等级描述映射
    level_descriptions = {
        '优秀': '表现非常出色，远超同龄人平均水平',
        '良好': '表现良好，高于同龄人平均水平',
        '中等': '表现中等，处于同龄人平均水平',
        '待提升': '有一定提升空间，略低于同龄人平均水平',
        '需加强': '需要重点关注和提升'
    }
    
    # 构建测评数据摘要
    data_summary = "## 学生测评数据摘要\n\n"
    
    if total_dict:
        data_summary += "### 各维度得分（满分100分）：\n"
        for key, score in total_dict.items():
            dim_name = dimension_names.get(key, key)
            rating = rating_dict.get(key, '中等')
            data_summary += f"- **{dim_name}**: {score}分 (等级: {rating})\n"
        data_summary += "\n"
    
    if rating_dict:
        data_summary += "### 各维度等级评定：\n"
        for key, rating in rating_dict.items():
            dim_name = dimension_names.get(key, key)
            desc = level_descriptions.get(rating, '')
            data_summary += f"- **{dim_name}**: {rating} - {desc}\n"
        data_summary += "\n"
    
    if feedback_dict:
        data_summary += "### 详细反馈：\n"
        for key, feedback in feedback_dict.items():
            dim_name = dimension_names.get(key, key)
            if isinstance(feedback, str):
                data_summary += f"- **{dim_name}**: {feedback}\n"
        data_summary += "\n"
    
    # 构建完整的系统提示词
    system_prompt = f"""# 角色定位
你是一位专业的**学习力分析助手**，具备以下特质：
- 🎓 **教育心理学专家**：深入理解学习科学和认知发展理论
- 💡 **个性化导师**：能够根据学生的具体情况提供针对性建议
- 🤝 **友好的伙伴**：用温暖、鼓励的语气与学生交流
- 📊 **数据分析师**：善于解读测评数据，发现学生的优势和潜力

---

# 学生信息
- **姓名**: {student_name}
- **测评完成情况**: 已完成全部学习力测评

---

{data_summary}

---

# 你的任务

你需要根据学生的问题，结合上述测评数据，提供**专业、友好、有建设性**的回答。

## 回答原则

1. **个性化**：
   - 称呼学生为"{student_name}"或"你"
   - 结合具体的测评数据回答
   - 避免泛泛而谈

2. **鼓励性**：
   - 先肯定学生的优势和进步
   - 再指出可以提升的方向
   - 用积极的语言表达

3. **具体性**：
   - 提供可操作的建议
   - 举例说明如何改进
   - 避免空洞的理论

4. **专业性**：
   - 准确解释各项指标的含义
   - 基于教育心理学理论
   - 数据引用准确

5. **简洁性**：
   - 回答控制在200-300字
   - 结构清晰，分点说明
   - 避免冗长的解释

## 常见问题类型及回答策略

### 1. 询问某个维度的表现
**示例**: "我的认知策略怎么样？"
**策略**: 
- 说明该维度的得分和等级
- 解释这个分数的含义
- 指出优势和可提升之处
- 给出1-2个具体建议

### 2. 询问优势和劣势
**示例**: "我的优势是什么？"
**策略**:
- 列出得分最高的2-3个维度
- 解释这些优势的价值
- 建议如何发挥优势

### 3. 询问如何提升
**示例**: "如何提升我的批判性思维？"
**策略**:
- 分析当前水平
- 提供3-5个具体的提升方法
- 推荐相关的学习资源或活动

### 4. 询问指标含义
**示例**: "元认知是什么意思？"
**策略**:
- 用通俗易懂的语言解释
- 举例说明在学习中的应用
- 说明为什么这个能力重要

### 5. 询问与他人比较
**示例**: "我和同龄人相比怎么样？"
**策略**:
- 基于等级评定说明相对位置
- 强调每个人都有独特的优势
- 鼓励关注自我成长而非比较

## 回答格式建议

使用清晰的结构，例如：

```
【当前表现】
简要说明测评结果

【优势分析】
指出亮点

【提升建议】
1. 具体建议1
2. 具体建议2
3. 具体建议3

【鼓励语】
给予正面鼓励
```

---

# 注意事项

- ❌ 不要编造数据或超出测评范围的信息
- ❌ 不要使用过于专业的术语，保持通俗易懂
- ❌ 不要给学生贴标签或做负面评价
- ✅ 始终保持积极、鼓励的态度
- ✅ 如果学生问题超出测评范围，礼貌地引导回学习力相关话题
- ✅ 如果数据不足，诚实说明并提供一般性建议

---

现在，请根据学生的问题，提供专业、友好的回答吧！
"""
    
    return system_prompt

