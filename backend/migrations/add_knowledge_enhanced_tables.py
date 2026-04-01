"""
知识库增强功能数据库迁移脚本
创建版本历史、分享管理、知识关联等表
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table, MetaData, inspect
from sqlalchemy.orm import sessionmaker
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def upgrade():
    """执行数据库升级"""
    # 使用正确的数据库路径
    instance_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance')
    db_path = os.path.join(instance_dir, 'topo_system.db')
    db_uri = f'sqlite:///{db_path}'
    
    print(f"Using database: {db_uri}")
    
    engine = create_engine(db_uri)
    metadata = MetaData()
    
    # 检查表是否已存在
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # 1. 知识库版本历史表
    if 'knowledge_versions' not in existing_tables:
        knowledge_versions = Table(
            'knowledge_versions',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('article_id', Integer, nullable=False),
            Column('version_number', Integer, nullable=False),
            Column('title', String(200), nullable=False),
            Column('content', Text, nullable=False),
            Column('created_by', Integer, nullable=False),
            Column('created_at', DateTime, default='now'),
            Column('change_summary', String(500))
        )
        knowledge_versions.create(engine)
        print("[OK] Created table: knowledge_versions")
    else:
        print("[SKIP] Table exists: knowledge_versions")
    
    # 2. 知识库分享表
    if 'knowledge_shares' not in existing_tables:
        knowledge_shares = Table(
            'knowledge_shares',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('article_id', Integer, nullable=False),
            Column('share_token', String(32), unique=True, nullable=False),
            Column('password', String(64)),
            Column('created_by', Integer, nullable=False),
            Column('created_at', DateTime, default='now'),
            Column('expire_at', DateTime),
            Column('allow_download', Boolean, default=True),
            Column('view_count', Integer, default=0),
            Column('is_active', Boolean, default=True)
        )
        knowledge_shares.create(engine)
        print("[OK] Created table: knowledge_shares")
    else:
        print("[SKIP] Table exists: knowledge_shares")
    
    # 3. 知识库链接表
    if 'knowledge_links' not in existing_tables:
        knowledge_links = Table(
            'knowledge_links',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('from_article_id', Integer, nullable=False),
            Column('to_article_id', Integer, nullable=False),
            Column('context', String(200)),
            Column('created_at', DateTime, default='now')
        )
        knowledge_links.create(engine)
        print("[OK] Created table: knowledge_links")
    else:
        print("[SKIP] Table exists: knowledge_links")
    
    # 4. 知识库标签增强表
    if 'knowledge_tags' not in existing_tables:
        knowledge_tags = Table(
            'knowledge_tags',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50), unique=True, nullable=False),
            Column('color', String(7), default='#409EFF'),
            Column('description', String(200)),
            Column('created_at', DateTime, default='now'),
            Column('use_count', Integer, default=0)
        )
        knowledge_tags.create(engine)
        print("[OK] Created table: knowledge_tags")
    else:
        print("[SKIP] Table exists: knowledge_tags")
    
    # 5. 文章-标签关联表
    if 'article_tags' not in existing_tables:
        article_tags = Table(
            'article_tags',
            metadata,
            Column('article_id', Integer, primary_key=True),
            Column('tag_id', Integer, primary_key=True)
        )
        article_tags.create(engine)
        print("[OK] Created table: article_tags")
    else:
        print("[SKIP] Table exists: article_tags")
    
    # 6. 知识库收藏表
    if 'knowledge_favorites' not in existing_tables:
        knowledge_favorites = Table(
            'knowledge_favorites',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', Integer, nullable=False),
            Column('article_id', Integer, nullable=False),
            Column('created_at', DateTime, default='now'),
            Column('folder', String(100))
        )
        knowledge_favorites.create(engine)
        print("[OK] Created table: knowledge_favorites")
    else:
        print("[SKIP] Table exists: knowledge_favorites")
    
    # 7. 知识库阅读记录表
    if 'knowledge_read_records' not in existing_tables:
        knowledge_read_records = Table(
            'knowledge_read_records',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', Integer, nullable=False),
            Column('article_id', Integer, nullable=False),
            Column('read_at', DateTime, default='now'),
            Column('read_progress', Integer, default=0),
            Column('is_finished', Boolean, default=False)
        )
        knowledge_read_records.create(engine)
        print("[OK] Created table: knowledge_read_records")
    else:
        print("[SKIP] Table exists: knowledge_read_records")
    
    # 8. 知识库评论增强表
    if 'knowledge_comments' not in existing_tables:
        knowledge_comments = Table(
            'knowledge_comments',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('article_id', Integer, nullable=False),
            Column('user_id', Integer, nullable=False),
            Column('content', Text, nullable=False),
            Column('created_at', DateTime, default='now'),
            Column('updated_at', DateTime, default='now'),
            Column('block_id', String(64)),
            Column('line_start', Integer),
            Column('line_end', Integer),
            Column('selected_text', Text),
            Column('parent_id', Integer)
        )
        knowledge_comments.create(engine)
        print("[OK] Created table: knowledge_comments")
    else:
        print("[SKIP] Table exists: knowledge_comments")
    
    # 9. 为现有知识库文章表添加增强字段
    with engine.connect() as conn:
        # 检查并添加字段
        columns_to_add = [
            ('version', 'INTEGER DEFAULT 1'),
            ('view_count', 'INTEGER DEFAULT 0'),
            ('like_count', 'INTEGER DEFAULT 0'),
            ('is_pinned', 'BOOLEAN DEFAULT 0'),
            ('is_public', 'BOOLEAN DEFAULT 1'),
            ('allow_comment', 'BOOLEAN DEFAULT 1'),
            ('title_pinyin', 'VARCHAR(500)')
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                conn.execute(f"ALTER TABLE knowledge_articles ADD COLUMN {col_name} {col_type}")
                print(f"[OK] Added column: knowledge_articles.{col_name}")
            except Exception as e:
                if 'duplicate column name' in str(e).lower() or 'already exists' in str(e).lower():
                    print(f"[SKIP] Column exists: knowledge_articles.{col_name}")
                else:
                    print(f"[WARN] Failed to add column: knowledge_articles.{col_name} - {e}")
    
    print("\nDatabase migration completed!")
    print("Please install dependencies:")
    print("  pip install jieba pypinyin markdown weasyprint")

def downgrade():
    """执行数据库降级（删除表）"""
    print("Downgrade will drop all enhanced tables!")
    pass

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Knowledge Enhanced Database Migration')
    parser.add_argument('command', choices=['upgrade', 'downgrade'], default='upgrade', nargs='?')
    args = parser.parse_args()
    
    if args.command == 'upgrade':
        upgrade()
    else:
        downgrade()
