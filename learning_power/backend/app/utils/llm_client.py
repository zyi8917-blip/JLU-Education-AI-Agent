"""
LLM 客户端工具类
用于调用 SiliconFlow API 进行多指标测评评估
"""
import os
import json
import re
import logging
from openai import OpenAI
from flask import current_app

# 配置日志
logger = logging.getLogger(__name__)

def load_prompt_data():
        """加载prompt.json文件内容"""
        try:
            # 获取当前文件所在目录的父目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            prompt_path = os.path.join(current_dir, '..', 'prompt.json')
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load prompt.json: {str(e)}")
            return None

# 全局加载prompt数据
prompt_data = load_prompt_data()


class LLMClient:
    """LLM 客户端，用于调用 SiliconFlow API"""

    def __init__(self, api_key=None, base_url=None, model=None):
        """初始化 LLM 客户端"""
        # 优先从参数获取，然后从 Flask config，最后从环境变量
        try:
            if api_key:
                self.api_key = api_key
            elif current_app:
                self.api_key = current_app.config.get('SILICONFLOW_API_KEY') or current_app.config.get('OPENAI_API_KEY')
            else:
                self.api_key = os.getenv('SILICONFLOW_API_KEY') or os.getenv('OPENAI_API_KEY')

            if base_url:
                self.base_url = base_url
            elif current_app:
                self.base_url = current_app.config.get('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1')
            else:
                self.base_url = os.getenv('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1')

            if model:
                self.model = model
            elif current_app:
                self.model = current_app.config.get('SILICONFLOW_MODEL_CHAT_A', 'DeepSeek-V3')
            else:
                self.model = os.getenv('SILICONFLOW_MODEL_CHAT_A', 'DeepSeek-V3')
        except:
            # 如果没有 Flask 上下文，直接从环境变量读取
            self.api_key = api_key or os.getenv('SILICONFLOW_API_KEY') or os.getenv('OPENAI_API_KEY')
            self.base_url = base_url or os.getenv('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1')
            self.model = model or os.getenv('SILICONFLOW_MODEL_CHAT_A', 'DeepSeek-V3')

        logger.info(f"Initializing LLM Client with API key: {self.api_key[:10]}... base_url: {self.base_url}, model: {self.model}")

        if not self.api_key:
            logger.warning("SILICONFLOW_API_KEY not found, LLM evaluation will use default scores")
            self.client = None
            return

        # 初始化 OpenAI 客户端（兼容 SiliconFlow API）
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            logger.info(f"LLM Client initialized successfully with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {str(e)}")
            self.client = None

    def personalize_questions(self, questions, student_info):
        """
        根据学生个人信息个性化改写问题

        Args:
            questions: 原始问题列表 [{'id': 'Q001', 'content': '...'}, ...]
            student_info: 学生信息字典 {'name': '张三', 'grade': '大一', 'college': '计算机学院', ...}

        Returns:
            list: 个性化后的问题列表，每个问题包含 id, content, original_content
        """
        if not self.client:
            logger.warning("LLM client not available, returning original questions")
            return questions

        try:
            # 提取学生信息
            student_name = student_info.get('name', '同学')
            student_id = student_info.get('student_id', '')
            gender = student_info.get('gender', '')
            age = student_info.get('age', '')
            grade = student_info.get('grade', '')
            college = student_info.get('college', '')
            school = student_info.get('school', '吉林大学')

            # 构建学生背景描述
            student_context = f"{school}{college}{grade}的{student_name}"
            if gender:
                student_context += f"（{gender}）"
            if age:
                student_context += f"，{age}岁"

            logger.info(f"Personalizing questions for student: {student_context}")

            # 构建问题列表的JSON字符串
            questions_json = json.dumps([{
                'id': q['id'],
                'content': q['content']
            } for q in questions], ensure_ascii=False, indent=2)

            # 构建个性化改写的Prompt
            personalization_prompt = f"""# 角色设定
你是一位资深的教育心理学家和问卷设计专家，擅长根据学生的个人特点设计个性化的评估问题。

# 任务说明
现在需要你将一套标准化的心理测评问卷改写成更加个性化、贴近学生实际生活的版本。

# 学生信息
- **姓名**：{student_name}
- **学号**：{student_id}
- **性别**：{gender}
- **年龄**：{age}岁
- **年级**：{grade}
- **学院**：{college}
- **学校**：{school}

# 改写原则（核心要求）

## 1. 保持评估目标不变 ⭐⭐⭐⭐⭐
- **绝对不能改变**问题要评估的心理维度和核心意图
- 只改变场景和表述方式，不改变评估内容

## 2. 融入个性化场景 ⭐⭐⭐⭐⭐
- 将抽象的"麻烦或困难"替换为具体场景：
  - 理工科（计算机、软件等）：调试代码bug、项目deadline、算法题
  - 文科（文学、历史等）：论文选题、文献阅读、写作瓶颈
  - 医学：病例分析、实习压力、考试内容
  - 商科：案例分析、小组合作、商业计划书

- 将抽象的"朋友"替换为具体关系：
  - 本科生：室友、同班同学、社团成员
  - 研究生：同门师兄弟、实验室伙伴、导师

- 根据年级特点选择情境：
  - 大一：适应大学、探索兴趣、建立新关系
  - 大二/大三：专业学习、社团活动、实习准备
  - 大四：毕业压力、求职/考研
  - 研究生：科研压力、导师关系、学术产出

## 3. 使用自然亲切的语言 ⭐⭐⭐⭐
- 符合该年龄段学生的表达习惯
- 避免过于正式或学术化的表述

## 4. 保持问题长度适中 ⭐⭐⭐
- 改写后的问题不要过长（不超过原问题的1.5倍）
- 保持简洁明了

## 5. 保持问题的开放性 ⭐⭐⭐
- 不要将开放式问题改成封闭式问题
- 保留"请描述"、"你如何"、"为什么"等开放性引导词

# 原始问题列表
{questions_json}

# 输出格式要求
请严格按照以下JSON格式输出：

{{
  "personalized_questions": [
    "改写后的问题1",
    "改写后的问题2",
    "改写后的问题3"
  ]
}}

# 输出要求
1. **只输出JSON**，不要有任何其他文字说明
2. **问题数量必须与原始问题完全一致**（共{len(questions)}个问题）
3. **问题顺序必须与原始问题保持一致**
4. **每个问题都必须进行个性化改写**
5. **JSON格式必须正确**，可以被解析

请开始改写："""

            # 调用LLM进行个性化改写
            logger.info(f"Calling LLM for question personalization...")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位专业的教育心理学家和问卷设计专家。你的任务是根据学生的个人信息，将标准化问题改写成个性化版本，同时保持评估目标不变。"
                    },
                    {
                        "role": "user",
                        "content": personalization_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )

            # 解析LLM返回的结果
            result_text = response.choices[0].message.content.strip()
            logger.info(f"LLM response received, length: {len(result_text)}")

            # 尝试提取JSON（处理可能的markdown代码块）
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)
            elif result_text.startswith('```') and result_text.endswith('```'):
                result_text = result_text[3:-3].strip()
                if result_text.startswith('json'):
                    result_text = result_text[4:].strip()

            # 解析JSON
            result_data = json.loads(result_text)
            personalized_contents = result_data.get('personalized_questions', [])

            # 验证返回的问题数量
            if len(personalized_contents) != len(questions):
                logger.warning(f"Personalized questions count mismatch: expected {len(questions)}, got {len(personalized_contents)}")
                return questions

            # 构建个性化后的问题列表
            personalized_questions = []
            for i, question in enumerate(questions):
                personalized_questions.append({
                    'id': question['id'],
                    'content': personalized_contents[i],
                    'original_content': question['content']  # 保留原始问题供参考
                })

            logger.info(f"Successfully personalized {len(personalized_questions)} questions")
            return personalized_questions

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.error(f"Response text: {result_text[:500]}")
            return questions
        except Exception as e:
            logger.error(f"Error personalizing questions: {str(e)}")
            return questions

    def batch_evaluate_answers(self, question_answer_pairs, evaluation_type):
        """
        批量评估所有答案，根据测评类型使用相应的prompt模板

        Args:
            question_answer_pairs: 问题-答案对列表，每个元素为 {'question': str, 'answer': str}
            evaluation_type: 测评类型，如 'social_emotional', 'metacognition', 'learning_motivation' 等

        Returns:
            dict: 包含详细评分和总分的字典
            {
                'total_score': float,
                'final_scores': dict,  # 各维度总分
                'detailed_scores': list,  # 每题的详细评分
                'feedback': dict,  # 总体反馈
                'level': str  # 等级评定
            }
        """
        # 如果客户端未初始化，返回默认分数
        if not self.client:
            logger.warning("LLM client not available, using default scores")
            return self._get_default_batch_scores(question_answer_pairs, evaluation_type)

        try:
            if not prompt_data or evaluation_type not in prompt_data:
                logger.error(f"Evaluation type {evaluation_type} not found in prompt data")
                return self._get_default_batch_scores(question_answer_pairs, evaluation_type)
            
            # 获取测评类型的配置
            evaluation_config = prompt_data[evaluation_type]
            prompt_template = evaluation_config.get('prompt', '')
            output_template = evaluation_config.get('output_template', {})
            
            # 构建所有问题和答案的文本
            all_questions_answers = ""
            for idx, pair in enumerate(question_answer_pairs, 1):
                all_questions_answers += f"问题{idx}: {pair['question_content']}\n"
                all_questions_answers += f"答案{idx}: {pair['answer_content']}\n\n"
            
            # 构建评估提示词
            evaluation_prompt = f"""
                {prompt_template}

                # 测评问题及用户答案
                {all_questions_answers}

                # 输出格式
                请严格按照以下JSON格式返回评分结果，以能够被python中json.loads解析的形式直接输出，不要输出任何多余内容：
                {json.dumps(output_template, ensure_ascii=False, indent=2)}
            """
            
            logger.info(f"Batch evaluating {len(question_answer_pairs)} answers for evaluation type: {evaluation_type}")
            logger.debug(f"Prompt: {evaluation_prompt[:500]}...")
            
            # 调用 LLM（增加超时时间以处理批量评估）
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位专业的教育心理学家，根据学生对开放性问卷答案评估其对应指标的学习能力。请严格按照要求返回JSON格式的评分结果。"
                    },
                    {
                        "role": "user",
                        "content": evaluation_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,  # 增加token数量以处理批量结果
                timeout=120  # 120秒超时（批量评估需要更长时间）
            )
            
            # 提取响应内容
            result_text = response.choices[0].message.content.strip()
            logger.info(f"LLM Response (first 500 chars): {result_text[:500]}")

            # 解析 JSON 结果
            scores = self._parse_batch_evaluation_result(result_text, evaluation_type)

            logger.info(f"Batch evaluation completed: {scores}")
            return scores
            
        except Exception as e:
            logger.error(f"Error in batch evaluation: {str(e)}", exc_info=True)
            print(f"Error in batch evaluation: {str(e)}")
            # 返回默认分数
            return self._get_default_batch_scores(question_answer_pairs, evaluation_type)
    
    def evaluate_answer(self, question_content, answer_content, evaluation_type='creativity'):
        """
        评估单个答案（保留此方法以兼容旧代码，但建议使用批量评估）

        Args:
            question_content: 题目内容
            answer_content: 学生答案
            evaluation_type: 测评类型

        Returns:
            dict: 包含维度分数的字典
        """
        # 如果客户端未初始化，返回默认分数
        if not self.client:
            logger.warning("LLM client not available, using default scores")
            return self._get_default_scores(evaluation_type)

        try:
            # 加载prompt数据
            if not prompt_data or evaluation_type not in prompt_data:
                logger.error(f"Evaluation type {evaluation_type} not found in prompt data")
                return self._get_default_scores(evaluation_type)
            
            # 获取测评类型的配置
            evaluation_config = prompt_data[evaluation_type]
            prompt_template = evaluation_config.get('prompt', '')
            output_template = evaluation_config.get('output_template', {})
            
            # 构建评估提示词
            evaluation_prompt = f"""{prompt_template}

            问题: {question_content}
            答案: {answer_content}

            请严格按照以下JSON格式返回评分结果：
            {json.dumps(output_template, ensure_ascii=False, indent=2)}
            """
            
            logger.info(f"Evaluating answer for evaluation type: {evaluation_type}")
            logger.debug(f"Prompt: {evaluation_prompt[:200]}...")
            
            # 调用 LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位专业的教育心理学家，根据学生对开放性问卷答案评估其对应指标的学习能力。请严格按照要求返回JSON格式的评分结果。"
                    },
                    {
                        "role": "user",
                        "content": evaluation_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000,
                timeout=60
            )
            
            # 提取响应内容
            result_text = response.choices[0].message.content.strip()
            logger.info(f"LLM Response (first 200 chars): {result_text[:200]}")

            # 解析 JSON 结果
            scores = self._parse_single_evaluation_result(result_text, evaluation_type)

            logger.info(f"Evaluation completed: {scores}")
            return scores
            
        except Exception as e:
            logger.error(f"Error evaluating answer: {str(e)}", exc_info=True)
            print(f"Error evaluating answer: {str(e)}")
            # 返回默认分数
            return self._get_default_scores(evaluation_type)
    
    def _parse_batch_evaluation_result(self, result_text, evaluation_type):
        """
        解析批量评估的 LLM 返回结果
        
        Args:
            result_text: LLM 返回的文本
            evaluation_type: 测评类型
            
        Returns:
            dict: 解析后的评分结果
        """
        try:
            # 尝试直接解析 JSON
            result = json.loads(result_text)
            
            # 验证必需字段  （根据json文件修改）
            required_fields = ['detailed_scores', 'rating_summary', 'feedback', 'grade_level']
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Missing required field: {field}")
                    # 如果缺少字段，设置默认值
                    if field == 'detailed_scores':
                        result[field] = {}  # 默认空字典
                    elif field == 'rating_summary':
                        result[field] = {}  # 默认空字典
                    elif field == 'feedback':
                        result[field] = {}  # 默认反馈
                    elif field == 'grade_level':
                        result[field] = 'B'  # 默认等级
            
            return result
            
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取 JSON 片段
            logger.warning(f"Direct JSON parsing failed, trying to extract JSON fragment from: {result_text[:100]}")

            # 尝试提取代码块中的 JSON（优先）
            code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', result_text, re.DOTALL)
            if code_block_match:
                try:
                    result = json.loads(code_block_match.group(1))
                    logger.info("Successfully extracted JSON from code block")
                    return self._parse_batch_evaluation_result(json.dumps(result), evaluation_type)
                except Exception as e:
                    logger.warning(f"Failed to parse code block JSON: {e}")

            # 尝试提取 {} 之间的内容（支持嵌套）
            json_match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', result_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group(0))
                    logger.info("Successfully extracted JSON from text")
                    return self._parse_batch_evaluation_result(json.dumps(result), evaluation_type)
                except Exception as e:
                    logger.warning(f"Failed to parse extracted JSON: {e}")

            logger.error(f"Failed to parse batch evaluation result: {result_text[:200]}")
            return self._get_default_batch_scores([], evaluation_type)
        
        except Exception as e:
            logger.error(f"Error parsing batch evaluation result: {str(e)}", exc_info=True)
            return self._get_default_batch_scores([], evaluation_type)
    
    def _parse_single_evaluation_result(self, result_text, evaluation_type):
        """
        解析单个评估的 LLM 返回结果
        
        Args:
            result_text: LLM 返回的文本
            evaluation_type: 测评类型
            
        Returns:
            dict: 解析后的评分结果
        """
        try:
            # 尝试直接解析 JSON
            result = json.loads(result_text)
            
            # 根据测评类型验证必需字段
            if evaluation_type == 'creativity':
                required_fields = ['fluency', 'flexibility', 'originality', 'elaboration']
            else:
                # 对于其他测评类型，检查是否有分数字段
                required_fields = []
                for key in result.keys():
                    if 'score' in key.lower():
                        required_fields.append(key)
                # 如果没有找到分数字段，使用通用字段
                if not required_fields:
                    required_fields = ['score']
            
            # 确保所有必需字段存在
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Missing required field: {field}")
                    result[field] = 7.0  # 默认分数
                else:
                    # 确保分数是有效的数字
                    try:
                        score = float(result[field])
                        result[field] = score
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid score value for {field}: {result[field]}, using default")
                        result[field] = 7.0
            
            # 确保有 comments 字段
            if 'comments' not in result:
                result['comments'] = '评估完成'
            
            return result
            
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取 JSON 片段
            logger.warning(f"Direct JSON parsing failed, trying to extract JSON fragment from: {result_text[:100]}")

            # 尝试提取代码块中的 JSON（优先）
            code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', result_text, re.DOTALL)
            if code_block_match:
                try:
                    result = json.loads(code_block_match.group(1))
                    logger.info("Successfully extracted JSON from code block")
                    return self._parse_single_evaluation_result(json.dumps(result), evaluation_type)
                except Exception as e:
                    logger.warning(f"Failed to parse code block JSON: {e}")

            # 尝试提取 {} 之间的内容（支持嵌套）
            json_match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', result_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group(0))
                    logger.info("Successfully extracted JSON from text")
                    return self._parse_single_evaluation_result(json.dumps(result), evaluation_type)
                except Exception as e:
                    logger.warning(f"Failed to parse extracted JSON: {e}")

            logger.error(f"Failed to parse evaluation result: {result_text[:200]}")
            return self._get_default_scores(evaluation_type)
        
        except Exception as e:
            logger.error(f"Error parsing evaluation result: {str(e)}", exc_info=True)
            return self._get_default_scores(evaluation_type)
    
    def _get_default_scores(self, evaluation_type='creativity'):
        """返回默认分数（当评估失败时使用）"""
        if evaluation_type == 'creativity':
            return {
                'fluency': 7.0,
                'flexibility': 7.0,
                'originality': 7.0,
                'elaboration': 7.0,
                'comments': '评估过程出现问题，使用默认分数'
            }
        else:
            # 对于其他测评类型，返回通用默认分数
            return {
                'score': 7.0,
                'comments': '评估过程出现问题，使用默认分数'
            }
    
    def _get_default_batch_scores(self, question_answer_pairs, evaluation_type):
        """返回批量评估的默认分数（当评估失败时使用）"""
        num_questions = len(question_answer_pairs)
        
        # 根据测评类型设置不同的默认详细分数
        detailed_scores = []
        if evaluation_type == 'creativity':
            for i in range(num_questions):
                detailed_scores.append({
                    'question_id': f"Q1",
                    'question': question_answer_pairs[i]['question'] if i < num_questions else "",
                    'answer': question_answer_pairs[i]['answer'] if i < num_questions else "",
                    'fluency': 7.0,
                    'flexibility': 7.0,
                    'originality': 7.0,
                    'elaboration': 7.0,
                    'comments': '评估过程出现问题，使用默认分数'
                })
            final_scores = {
                'fluency': 7.0 * num_questions,
                'flexibility': 7.0 * num_questions,
                'originality': 7.0 * num_questions,
                'elaboration': 7.0 * num_questions
            }
        else:
            # 对于其他测评类型，使用通用分数
            for i in range(num_questions):
                detailed_scores.append({
                    'question_id': f"Q{i+1:03d}",
                    'question': question_answer_pairs[i]['question'] if i < num_questions else "",
                    'answer': question_answer_pairs[i]['answer'] if i < num_questions else "",
                    'score': 7.0,
                    'comments': '评估过程出现问题，使用默认分数'
                })
            final_scores = {'score': 7.0 * num_questions}
        
        return {
            'total_score': 70.0,  # 默认总分
            'final_scores': final_scores,
            'detailed_scores': detailed_scores,
            'feedback': '评估过程出现问题，使用默认分数',
            'level': '中等'
        }


# 创建全局 LLM 客户端实例
_llm_client = None

def get_llm_client():
    """获取 LLM 客户端实例（单例模式）"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client

