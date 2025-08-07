import re
from typing import List
from langchain_core.documents import Document


def under_non_alpha_ratio(text: str, threshold: float = 0.5) -> bool:
    """
    检查文本中非字母字符的比例是否超过给定阈值
    这有助于防止像 "-----------BREAK---------" 这样的文本被标记为标题
    
    Args:
        text: 要测试的输入字符串
        threshold: 如果非字母字符的比例超过此阈值，函数返回False
        
    Returns:
        bool: 是否低于阈值
    """
    if len(text) == 0:
        return False

    alpha_count = len([char for char in text if char.strip() and char.isalpha()])
    total_count = len([char for char in text if char.strip()])
    try:
        ratio = alpha_count / total_count
        return ratio < threshold
    except:
        return False


def is_possible_title(
        text: str,
        title_max_word_length: int = 20,
        non_alpha_threshold: float = 0.5,
) -> bool:
    """
    检查文本是否通过所有有效标题的检查
    
    Args:
        text: 要检查的输入文本
        title_max_word_length: 标题可以包含的最大字符数
        non_alpha_threshold: 文本需要被视为标题的最小字母字符数
        
    Returns:
        bool: 是否为可能的标题
    """
    # 文本长度为0的话，肯定不是title
    if len(text) == 0:
        return False

    # 文本中有标点符号，就不是title
    ENDS_IN_PUNCT_PATTERN = r"[^\w\s]\Z"
    ENDS_IN_PUNCT_RE = re.compile(ENDS_IN_PUNCT_PATTERN)
    if ENDS_IN_PUNCT_RE.search(text) is not None:
        return False

    # 文本长度不能超过设定值，默认20
    if len(text) > title_max_word_length:
        return False

    # 文本中数字的占比不能太高，否则不是title
    if under_non_alpha_ratio(text, threshold=non_alpha_threshold):
        return False

    # 防止标记像 "To My Dearest Friends," 这样的称呼为标题
    if text.endswith((",", ".", "，", "。")):
        return False

    if text.isnumeric():
        return False

    # 开头的字符内应该有数字，默认5个字符内
    if len(text) < 5:
        text_5 = text
    else:
        text_5 = text[:5]
    alpha_in_text_5 = sum(list(map(lambda x: x.isnumeric(), list(text_5))))
    if not alpha_in_text_5:
        return False

    return True


def zh_title_enhance(docs: List[Document]) -> List[Document]:
    """
    对文档进行中文标题增强处理
    
    Args:
        docs: 文档列表
        
    Returns:
        List[Document]: 增强后的文档列表
    """
    title = None
    if len(docs) > 0:
        for doc in docs:
            if is_possible_title(doc.page_content):
                doc.metadata['category'] = 'cn_Title'
                title = doc.page_content
            elif title:
                doc.page_content = f"下文与({title})有关。{doc.page_content}"
        return docs
    else:
        print("文件不存在")
        return docs 