"""
PDF导出HTML解析修复模块
使用BeautifulSoup进行更可靠的HTML解析
"""
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
import re
import html
import logging

logger = logging.getLogger(__name__)


def html_to_pdf_elements(content, chinese_font, styles, article_id=None):
    """将HTML内容转换为PDF元素列表"""
    logger.info(f"=== PDF导出开始 ===")
    logger.info(f"内容长度: {len(content) if content else 0}")

    if not content:
        logger.warning("内容为空")
        return []

    # 记录原始内容的前500字符用于调试
    logger.info(f"原始内容前500字符: {content[:500]}")

    try:
        from bs4 import BeautifulSoup
        has_bs4 = True
        logger.info("使用BeautifulSoup解析")
    except ImportError:
        has_bs4 = False
        logger.warning("BeautifulSoup未安装，使用备用解析方法")

    if has_bs4:
        result = _parse_with_bs4(content, chinese_font, styles)
    else:
        result = _parse_with_regex(content, chinese_font, styles)

    logger.info(f"生成的PDF元素数量: {len(result)}")
    logger.info(f"=== PDF导出结束 ===")
    return result


def _parse_with_bs4(content, chinese_font, styles):
    """使用BeautifulSoup解析HTML"""
    from bs4 import BeautifulSoup, NavigableString
    from flask import request
    from io import BytesIO
    import urllib.request

    soup = BeautifulSoup(content, 'html.parser')

    # 定义样式
    h1_style = ParagraphStyle(
        'H1', parent=styles['Heading1'], fontName=chinese_font, fontSize=20,
        textColor=colors.black, spaceBefore=16, spaceAfter=8, alignment=TA_LEFT
    )
    h2_style = ParagraphStyle(
        'H2', parent=styles['Heading2'], fontName=chinese_font, fontSize=16,
        textColor=colors.black, spaceBefore=14, spaceAfter=6, alignment=TA_LEFT
    )
    h3_style = ParagraphStyle(
        'H3', parent=styles['Heading3'], fontName=chinese_font, fontSize=14,
        textColor=colors.black, spaceBefore=12, spaceAfter=4, alignment=TA_LEFT
    )
    normal_style = ParagraphStyle(
        'Normal', parent=styles['Normal'], fontName=chinese_font, fontSize=11,
        leading=18, spaceAfter=8, alignment=TA_LEFT
    )
    list_style = ParagraphStyle(
        'List', parent=styles['Normal'], fontName=chinese_font, fontSize=11,
        leading=16, leftIndent=24, spaceAfter=4, alignment=TA_LEFT
    )
    code_style = ParagraphStyle(
        'Code', parent=styles['Code'], fontName='Courier', fontSize=10,
        backColor=colors.Color(0.95, 0.95, 0.95), leftIndent=12,
        rightIndent=12, spaceBefore=8, spaceAfter=8
    )

    elements = []

    def clean_text(text):
        """清理文本，处理emoji和特殊字符"""
        if not text:
            return ''
        # 解码HTML实体
        text = html.unescape(text)

        # 替换常见的emoji为文字描述
        emoji_replacements = {
            '☑️': '[完成] ',
            '✅': '[完成] ',
            '☐': '[ ] ',
            '□': '[ ] ',
            '📋': '[文档] ',
            '📞': '[电话] ',
            '📱': '[手机] ',
            '💻': '[电脑] ',
            '🔧': '[工具] ',
            '⚙️': '[设置] ',
            '📊': '[图表] ',
            '📈': '[上升] ',
            '📉': '[下降] ',
            '✨': '[亮点] ',
            '🌟': '[星标] ',
            '⭐': '[星星] ',
            '🔴': '[红] ',
            '🟢': '[绿] ',
            '🔵': '[蓝] ',
            '🟡': '[黄] ',
            '⚠️': '[警告] ',
            '❌': '[错误] ',
            '✔️': '[对勾] ',
            '✓': '[对勾] ',
            '→': '-> ',
            '←': '<- ',
            '⇒': '=> ',
            '•': '* ',  # 项目符号替换为星号
        }

        for emoji, replacement in emoji_replacements.items():
            text = text.replace(emoji, replacement)

        # 规范化空白，但保留换行
        lines = text.split('\n')
        lines = [' '.join(line.split()) for line in lines]
        text = '\n'.join(lines)
        return text.strip()

    def process_element(element):
        """递归处理元素"""
        nonlocal elements

        if element is None:
            return

        # 跳过script和style
        if element.name in ['script', 'style', 'nav']:
            return

        # 跳过纯文本节点（由父元素处理）
        if isinstance(element, NavigableString):
            return

        # 获取元素的纯文本内容
        text = clean_text(element.get_text(separator='\n', strip=True))

        # 处理标题
        if element.name == 'h1':
            if text:
                logger.info(f"添加H1: {text[:50]}")
                elements.append(Paragraph(text, h1_style))
        elif element.name == 'h2':
            if text:
                logger.info(f"添加H2: {text[:50]}")
                elements.append(Paragraph(text, h2_style))
        elif element.name in ['h3', 'h4', 'h5', 'h6']:
            if text:
                logger.info(f"添加H3+: {text[:50]}")
                elements.append(Paragraph(text, h3_style))

        # 处理段落
        elif element.name == 'p':
            if text:
                logger.info(f"添加段落: {text[:50]}")
                elements.append(Paragraph(text, normal_style))

        # 处理div（如果包含文本但没有其他块级子元素）
        elif element.name == 'div':
            # 检查是否直接包含文本
            has_block_children = any(
                child.name in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'table', 'pre']
                for child in element.children if hasattr(child, 'name')
            )
            if not has_block_children and text:
                logger.info(f"添加div文本: {text[:50]}")
                elements.append(Paragraph(text, normal_style))

        # 处理无序列表
        elif element.name == 'ul':
            logger.info(f"处理无序列表，包含 {len(element.find_all('li', recursive=False))} 项")
            for li in element.find_all('li', recursive=False):
                li_text = clean_text(li.get_text())
                if li_text:
                    bullet_text = f'• {li_text}'
                    elements.append(Paragraph(bullet_text, list_style))
            elements.append(Spacer(1, 0.1*cm))

        # 处理有序列表
        elif element.name == 'ol':
            logger.info(f"处理有序列表，包含 {len(element.find_all('li', recursive=False))} 项")
            for idx, li in enumerate(element.find_all('li', recursive=False), 1):
                li_text = clean_text(li.get_text())
                if li_text:
                    numbered_text = f'{idx}. {li_text}'
                    elements.append(Paragraph(numbered_text, list_style))
            elements.append(Spacer(1, 0.1*cm))

        # 处理代码块
        elif element.name == 'pre':
            if text:
                logger.info(f"添加代码块: {text[:50]}")
                for line in text.split('\n'):
                    if line.strip():
                        elements.append(Paragraph(line, code_style))
                elements.append(Spacer(1, 0.2*cm))

        # 处理表格
        elif element.name == 'table':
            rows = []
            for tr in element.find_all('tr'):
                row = []
                for cell in tr.find_all(['td', 'th']):
                    row.append(clean_text(cell.get_text()))
                if row:
                    rows.append(row)

            if rows:
                logger.info(f"添加表格: {len(rows)} 行")
                table = Table(rows)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.5, 0.9)),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), chinese_font),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('TOPPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('FONTNAME', (0, 1), (-1, -1), chinese_font),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ]))
                elements.append(Spacer(1, 0.3*cm))
                elements.append(table)
                elements.append(Spacer(1, 0.3*cm))

        # 处理图片
        elif element.name == 'img':
            src = element.get('src', '')
            if src and not src.startswith('data:'):
                logger.info(f"添加图片: {src}")
                try:
                    img_url = src
                    if not img_url.startswith(('http://', 'https://')):
                        base_url = request.host_url.rstrip('/') if hasattr(request, 'host_url') else ''
                        if img_url.startswith('/'):
                            img_url = base_url + img_url
                        else:
                            img_url = base_url + '/' + img_url

                    req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=10) as response:
                        img_data = response.read()

                    img_buffer = BytesIO(img_data)
                    max_width, max_height = 14 * cm, 10 * cm

                    from PIL import Image as PILImage
                    with PILImage.open(img_buffer) as pil_img:
                        w, h = pil_img.size
                        ratio = min(max_width / w, max_height / h, 1.0)
                        new_w, new_h = w * ratio, h * ratio

                    img_buffer.seek(0)
                    img = Image(img_buffer, width=new_w, height=new_h)
                    elements.append(Spacer(1, 0.2*cm))
                    elements.append(img)
                    elements.append(Spacer(1, 0.2*cm))
                except Exception as e:
                    logger.warning(f"图片加载失败: {e}")

        # 递归处理子元素（对于容器元素）
        if element.name in ['article', 'section', 'main', 'body', 'html', 'div']:
            for child in element.children:
                if hasattr(child, 'name') or isinstance(child, NavigableString):
                    process_element(child)

    # 处理body或直接使用soup
    body = soup.find('body')
    if body:
        logger.info("从body标签开始解析")
        for child in body.children:
            process_element(child)
    else:
        logger.info("直接解析soup内容")
        for child in soup.children:
            process_element(child)

    return elements


def _parse_with_regex(content, chinese_font, styles):
    """备用：使用正则表达式解析HTML"""
    elements = []

    normal_style = ParagraphStyle(
        'Normal', parent=styles['Normal'], fontName=chinese_font, fontSize=11,
        leading=18, spaceAfter=8, alignment=TA_LEFT
    )

    # 移除script和style
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)

    # 简单的段落分割
    # 先处理块级标签
    content = re.sub(r'</(p|div|h[1-6]|ul|ol|table|pre)>', r'\n\n', content, flags=re.IGNORECASE)
    content = re.sub(r'<(p|div)[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</(p|div)>', '', content, flags=re.IGNORECASE)

    # 处理标题
    for i in range(1, 7):
        content = re.sub(rf'<h{i}[^>]*>(.*?)</h{i}>', r'\n\n【标题】\1\n\n', content, flags=re.DOTALL | re.IGNORECASE)

    # 处理列表
    content = re.sub(r'<li[^>]*>(.*?)</li>', r'\n• \1', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<ul[^>]*>.*?</ul>', lambda m: m.group(0).replace('<li>', '\n• ').replace('</li>', ''), content, flags=re.DOTALL | re.IGNORECASE)

    # 清理其他标签
    content = re.sub(r'<[^>]+>', '', content)

    # 解码HTML实体
    content = html.unescape(content)

    # 分割段落
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

    for para in paragraphs:
        if para.startswith('【标题】'):
            para = para.replace('【标题】', '')
        elements.append(Paragraph(para, normal_style))

    return elements
