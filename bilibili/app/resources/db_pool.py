from peewee import *
from playhouse.pool import PooledMySQLDatabase
import threading


class DatabasePool:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabasePool, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # 创建连接池
        self.db = PooledMySQLDatabase(
            'cofood',
            user='root',
            password='root',
            host='localhost',
            port=3307,
            max_connections=10,
            stale_timeout=300,  # 5分钟
            timeout=10,  # 10秒超时
        )

        # 定义模型
        class BaseModel(Model):
            class Meta:
                database = self.db

        class CategoryBase(BaseModel):
            identity = CharField(max_length=32)

            class Meta:
                table_name = 'category_base'

        self.BaseModel = BaseModel
        self.CategoryBase = CategoryBase
        self._initialized = True

    def get_db(self):
        """获取数据库连接"""
        return self.db

    def get_category_model(self):
        """获取CategoryBase模型"""
        return self.CategoryBase

    def connect(self):
        """连接数据库"""
        if self.db.is_closed():
            self.db.connect()

    def close(self):
        """关闭数据库连接"""
        if not self.db.is_closed():
            self.db.close()

    def execute_query(self, query):
        """执行查询"""
        try:
            self.connect()
            return query
        except Exception as e:
            print(f"数据库查询出错: {e}")
            raise

    def execute_transaction(self, func):
        """执行事务"""
        try:
            self.connect()
            with self.db.atomic():
                return func()
        except Exception as e:
            print(f"数据库事务出错: {e}")
            raise