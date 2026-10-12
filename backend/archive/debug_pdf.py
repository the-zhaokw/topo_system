#!/usr/bin/env python3
"""
PDF导出调试脚本
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import platform
    import re
    
    print("✅ 模块导入成功")
    
    chinese_font = 'Helvetica'
    system_name = platform.system()
    
    if system_name == 'Windows':
        font_paths = [
            (r'C:\Windows\Fonts\simhei.ttf', 'SimHei'),
            (r'C:\Windows\Fonts\msyh.ttc', 'Microsoft YaHei'),
            (r'C:\Windows\Fonts\simsun.ttc', 'SimSun'),
        ]
    elif system_name == 'Darwin':
        font_paths = [
            ('/System/Library/Fonts/STHeiti Light.ttc', 'STHeiti'),
            ('/System/Library/Fonts/PingFang.ttc', 'PingFang'),
        ]
    else:
        font_paths = [
            ('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 'WenQuanYi'),
            ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 'NotoSansCJK'),
        ]
    
    print(f"✅ 系统: {system_name}")
    print(f"✅ 字体路径列表: {font_paths}")
    
    for font_path, font_name in font_paths:
        print(f"检查字体: {font_path}...")
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                chinese_font = font_name
                print(f"✅ 成功注册中文字体: {font_name} from {font_path}")
                break
            except Exception as e:
                print(f"⚠️ 注册字体失败 {font_path}: {e}")
                import traceback
                traceback.print_exc()
                continue
        else:
            print(f"❌ 字体文件不存在: {font_path}")
    
    print(f"✅ 使用字体: {chinese_font}")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=chinese_font,
        fontSize=18,
        textColor=colors.black,
        spaceAfter=12,
        alignment=TA_LEFT
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=chinese_font,
        fontSize=11,
        leading=16,
        spaceAfter=6
    )
    
    story = []
    
    story.append(Paragraph("测试标题", title_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("这是测试内容，包含中文。", normal_style))
    story.append(Spacer(1, 0.2*cm))
    
    table_data = [
        ['功能', '方法', 'URL', '说明'],
        ['获取测试集列表', 'GET', '/test-management/suites/{project_id}', '获取项目下的所有测试集'],
        ['获取测试集详情', 'GET', '/test-management/suites/{suite_id}', '根据ID获取测试集详情'],
    ]
    
    pdf_table = Table(table_data)
    pdf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.25, 0.62, 1.0)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), chinese_font),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 1), (-1, -1), chinese_font),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(Spacer(1, 0.3*cm))
    story.append(pdf_table)
    
    print("✅ 开始构建PDF...")
    doc.build(story)
    buffer.seek(0)
    
    test_file = 'test_pdf_export.pdf'
    with open(test_file, 'wb') as f:
        f.write(buffer.getvalue())
    
    print(f"✅ PDF 导出测试成功！文件保存为: {test_file}")
    print("✅ 测试通过！")
    
except Exception as e:
    print(f"❌ 错误: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
