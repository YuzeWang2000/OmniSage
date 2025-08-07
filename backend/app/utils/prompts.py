from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any


class PromptManager:
    """Prompt模板管理器"""
    
    def __init__(self):
        self.prompts = self._init_prompts()
    
    def _init_prompts(self) -> Dict[str, Any]:
        """初始化所有prompt模板"""
        return {
            # RAG相关prompts
            "rag_default": ChatPromptTemplate.from_messages([
                SystemMessage(content="""你是一个有用的AI助手。请基于以下上下文信息来回答用户的问题。
如果上下文中没有相关信息，请说明你无法从提供的信息中找到答案，但可以基于你的知识来回答。

上下文信息：
{context}

请记住：
1. 优先使用上下文中的信息来回答问题
2. 如果上下文信息不足，可以补充你的知识
3. 回答要准确、有用、友好
4. 如果问题超出你的能力范围，请诚实说明"""),
                HumanMessage(content="{question}")
            ]),
            
            "rag_empty": ChatPromptTemplate.from_messages([
                SystemMessage(content="""你是一个有用的AI助手。用户的问题无法从知识库中找到相关信息，请基于你的知识来回答。

请记住：
1. 基于你的训练知识来回答问题
2. 回答要准确、有用、友好
3. 如果问题超出你的能力范围，请诚实说明
4. 如果问题模糊，请询问更多细节"""),
                HumanMessage(content="{question}")
            ]),
            
            # 普通聊天prompts
            "chat_default": ChatPromptTemplate.from_messages([
                SystemMessage(content="""你是一个有用的AI助手。请友好、准确地回答用户的问题。

请记住：
1. 回答要准确、有用、友好
2. 如果问题超出你的能力范围，请诚实说明
3. 如果问题模糊，请询问更多细节
4. 保持对话的自然流畅"""),
                HumanMessage(content="{question}")
            ]),
            
            "chat_creative": ChatPromptTemplate.from_messages([
                SystemMessage(content="""你是一个富有创造力的AI助手。请用有趣、创新的方式回答用户的问题。

请记住：
1. 发挥你的创造力
2. 回答要有趣、生动
3. 可以适当使用比喻、故事等方式
4. 保持友好和积极的态度"""),
                HumanMessage(content="{question}")
            ]),
            
            "chat_professional": ChatPromptTemplate.from_messages([
                SystemMessage(content="""你是一个专业的AI助手。请用专业、严谨的方式回答用户的问题。

请记住：
1. 回答要专业、准确
2. 使用清晰、逻辑的结构
3. 提供有深度的分析
4. 保持客观、中立的立场"""),
                HumanMessage(content="{question}")
            ]),
            
            # 生成任务prompts
            "generate_story": PromptTemplate(
                input_variables=["topic", "style", "length"],
                template="""请根据以下要求创作一个故事：

主题：{topic}
风格：{style}
长度：{length}

请创作一个引人入胜的故事。"""
            ),
            
            "generate_summary": PromptTemplate(
                input_variables=["content"],
                template="""请对以下内容进行总结：

{content}

请提供一个简洁、准确的总结。"""
            ),
            
            "generate_analysis": PromptTemplate(
                input_variables=["topic", "perspective"],
                template="""请从{perspective}的角度分析以下主题：

{topic}

请提供深入的分析和见解。"""
            ),
            
            # 生成模式默认prompt（使用PromptTemplate而不是ChatPromptTemplate）
            "generate_default": PromptTemplate(
                input_variables=["input"],
                template="""你是一个有用的AI助手。请友好、准确地回答用户的问题。

请记住：
1. 回答要准确、有用、友好
2. 如果问题超出你的能力范围，请诚实说明
3. 如果问题模糊，请询问更多细节
4. 保持回答的自然流畅

用户问题: {input}"""
            )
        }
    
    def get_prompt(self, prompt_name: str) -> Any:
        """获取指定的prompt模板"""
        if prompt_name not in self.prompts:
            raise ValueError(f"未知的prompt名称: {prompt_name}")
        return self.prompts[prompt_name]
    
    def list_prompts(self) -> Dict[str, str]:
        """列出所有可用的prompt模板"""
        return {
            "rag_default": "RAG默认模板 - 基于上下文回答问题",
            "rag_empty": "RAG空上下文模板 - 当没有相关上下文时使用",
            "chat_default": "聊天默认模板 - 普通对话",
            "chat_creative": "聊天创意模板 - 富有创造力的回答",
            "chat_professional": "聊天专业模板 - 专业严谨的回答",
            "generate_default": "生成默认模板 - 生成模式专用",
            "generate_story": "故事生成模板 - 创作故事",
            "generate_summary": "总结生成模板 - 内容总结",
            "generate_analysis": "分析生成模板 - 深度分析"
        }


# 全局prompt管理器实例
prompt_manager = PromptManager() 