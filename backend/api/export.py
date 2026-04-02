"""
通用数据导出服务
支持多种格式：Excel, CSV, PDF, JSON
"""
from flask import Blueprint, request, jsonify, send_file
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from io import BytesIO
import json

export_bp = Blueprint('export', __name__, url_prefix='/export')
export_api = Api(export_bp)

class DataExportService:
    """数据导出服务"""
    
    @staticmethod
    def to_excel(data, columns=None, sheet_name='Sheet1'):
        """导出为 Excel"""
        try:
            import pandas as pd
            
            df = pd.DataFrame(data, columns=columns)
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                # 自动调整列宽
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            output.seek(0)
            return output
        except ImportError:
            raise Exception('需要安装 pandas 和 openpyxl: pip install pandas openpyxl')
    
    @staticmethod
    def to_csv(data, columns=None):
        """导出为 CSV"""
        try:
            import pandas as pd
            
            df = pd.DataFrame(data, columns=columns)
            output = BytesIO()
            df.to_csv(output, index=False, encoding='utf-8-sig')
            output.seek(0)
            return output
        except ImportError:
            raise Exception('需要安装 pandas: pip install pandas')
    
    @staticmethod
    def to_pdf(data, columns=None, title='Export'):
        """导出为 PDF"""
        try:
            from io import BytesIO
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            import platform
            
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
            
            for font_path, font_name in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                        chinese_font = font_name
                        break
                    except:
                        continue
            
            output = BytesIO()
            doc = SimpleDocTemplate(output, pagesize=landscape(A4))
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=chinese_font,
                fontSize=16,
                alignment=TA_CENTER,
                spaceAfter=20
            )
            
            elements = []
            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 20))
            
            if data:
                headers = columns if columns else list(data[0].keys())
                table_data = [headers]
                
                for row in data:
                    table_data.append([str(row.get(col, '')) for col in headers])
                
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.25, 0.62, 1.0)),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), chinese_font),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('TOPPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('FONTNAME', (0, 1), (-1, -1), chinese_font),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ]))
                
                elements.append(table)
            
            doc.build(elements)
            output.seek(0)
            return output
            
        except ImportError:
            raise Exception('需要安装 reportlab: pip install reportlab')
    
    @staticmethod
    def to_json(data):
        """导出为 JSON"""
        output = BytesIO()
        output.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
        output.seek(0)
        return output

import os

class GenericExportResource(Resource):
    """通用数据导出 API"""
    
    method_decorators = {'post': [jwt_required()]}
    
    def post(self):
        """导出数据"""
        data = request.get_json()
        
        if not data:
            return {'error': '请求数据不能为空'}, 400
        
        export_data = data.get('data', [])
        columns = data.get('columns')
        format_type = data.get('format', 'excel').lower()
        filename = data.get('filename', 'export')
        title = data.get('title', 'Data Export')
        
        if not export_data:
            return {'error': '导出数据不能为空'}, 400
        
        try:
            if format_type == 'excel':
                output = DataExportService.to_excel(export_data, columns, title)
                mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                ext = 'xlsx'
            elif format_type == 'csv':
                output = DataExportService.to_csv(export_data, columns)
                mimetype = 'text/csv'
                ext = 'csv'
            elif format_type == 'pdf':
                output = DataExportService.to_pdf(export_data, columns, title)
                mimetype = 'application/pdf'
                ext = 'pdf'
            elif format_type == 'json':
                output = DataExportService.to_json(export_data)
                mimetype = 'application/json'
                ext = 'json'
            else:
                return {'error': f'不支持的格式: {format_type}'}, 400
            
            return send_file(
                output,
                mimetype=mimetype,
                as_attachment=True,
                download_name=f'{filename}.{ext}'
            )
            
        except Exception as e:
            return {'error': f'导出失败: {str(e)}'}, 500

class ExportTemplateResource(Resource):
    """导出模板下载"""
    
    method_decorators = {'get': [jwt_required()]}
    
    def get(self, template_type):
        """下载导入模板"""
        templates = {
            'users': {
                'columns': ['username', 'email', 'first_name', 'last_name', 'department', 'position', 'role'],
                'sample': [
                    {'username': 'zhangsan', 'email': 'zhangsan@example.com', 'first_name': '张', 'last_name': '三', 'department': '技术部', 'position': '工程师', 'role': 'developer'},
                    {'username': 'lisi', 'email': 'lisi@example.com', 'first_name': '李', 'last_name': '四', 'department': '测试部', 'position': '测试工程师', 'role': 'tester'}
                ]
            },
            'projects': {
                'columns': ['name', 'code', 'description', 'status', 'start_date', 'end_date'],
                'sample': [
                    {'name': '示例项目', 'code': 'PROJ001', 'description': '项目描述', 'status': 'active', 'start_date': '2026-01-01', 'end_date': '2026-12-31'}
                ]
            },
            'bugs': {
                'columns': ['title', 'description', 'severity', 'priority', 'project_id'],
                'sample': [
                    {'title': '示例Bug', 'description': 'Bug描述', 'severity': 'medium', 'priority': 'high', 'project_id': 1}
                ]
            },
            'materials': {
                'columns': ['name', 'code', 'category', 'unit', 'quantity'],
                'sample': [
                    {'name': '示例物料', 'code': 'MAT001', 'category': '电子元件', 'unit': '个', 'quantity': 100}
                ]
            }
        }
        
        if template_type not in templates:
            return {'error': f'未知模板类型: {template_type}'}, 404
        
        template = templates[template_type]
        
        try:
            import pandas as pd
            
            df = pd.DataFrame(template['sample'], columns=template['columns'])
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Template', index=False)
                
                # 添加说明 sheet
                instructions = pd.DataFrame({
                    '字段名': template['columns'],
                    '说明': ['请填写' for _ in template['columns']],
                    '必填': ['是' for _ in template['columns']]
                })
                instructions.to_excel(writer, sheet_name='Instructions', index=False)
            
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'{template_type}_template.xlsx'
            )
            
        except ImportError:
            return {'error': '需要安装 pandas 和 openpyxl'}, 500

# 注册路由
export_api.add_resource(GenericExportResource, '/')
export_api.add_resource(ExportTemplateResource, '/template/<string:template_type>')
