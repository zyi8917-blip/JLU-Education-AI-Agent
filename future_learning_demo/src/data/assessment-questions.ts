export type AssessmentQuestion = {
  id: string;
  dimension: string;
  prompt: string;
  placeholder: string;
};

export const assessmentQuestions: AssessmentQuestion[] = [
  {
    id: "learning-motivation-1",
    dimension: "学习动机",
    prompt: "当你接触一门全新的课程时，通常是什么原因会驱动你开始认真学习？",
    placeholder: "输入你最真实的学习动机...",
  },
  {
    id: "learning-motivation-2",
    dimension: "学习动机",
    prompt: "如果这门课暂时看不到立刻的成绩回报，你会怎样保持投入？",
    placeholder: "说说你会怎么坚持...",
  },
  {
    id: "learning-experience-1",
    dimension: "学习体验",
    prompt: "回想一次你学得最投入的经历，当时是什么让你有“进入状态”的感觉？",
    placeholder: "描述那次学习体验...",
  },
  {
    id: "learning-experience-2",
    dimension: "学习体验",
    prompt: "当学习内容很抽象时，你通常怎样让自己不那么焦虑或抗拒？",
    placeholder: "可以说说你的调节方式...",
  },
  {
    id: "delay-gratification-1",
    dimension: "学业延迟满足",
    prompt: "如果一个任务短期很辛苦，但长期收益很高，你通常会怎么安排自己完成它？",
    placeholder: "写下你的做法...",
  },
  {
    id: "delay-gratification-2",
    dimension: "学业延迟满足",
    prompt: "当娱乐和学习发生冲突时，你一般怎么做决定？",
    placeholder: "说说你的权衡方式...",
  },
  {
    id: "problem-solving-1",
    dimension: "问题解决",
    prompt: "遇到不会做的题目或项目任务时，你通常第一步会做什么？",
    placeholder: "描述你的起手动作...",
  },
  {
    id: "problem-solving-2",
    dimension: "问题解决",
    prompt: "如果一个问题尝试两次都没有结果，你会如何调整策略？",
    placeholder: "说说你会怎么转向...",
  },
  {
    id: "learning-strategy-1",
    dimension: "学习策略(综合)",
    prompt: "你通常会怎么整理一门课的重点内容，方便自己复习和迁移？",
    placeholder: "例如笔记、框架、例题等...",
  },
  {
    id: "learning-strategy-2",
    dimension: "学习策略(综合)",
    prompt: "为了确保自己真的学会了，你会用什么方式检查学习效果？",
    placeholder: "写下你的自检方法...",
  },
];
