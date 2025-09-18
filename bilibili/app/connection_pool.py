import pymysql
import psycopg2
from queue import Queue
import threading


class ConnectionPool:
    def __init__(self, driver, max_connections, **kwargs):
        self.driver = driver
        self.max_connections = max_connections
        self.connections = Queue(max_connections)
        self.kwargs = kwargs
        self.lock = threading.Lock()

        # 初始化连接池
        for _ in range(max_connections):
            conn = self._create_connection()
            self.connections.put(conn)

    def _create_connection(self):
        if self.driver == 'postgres':
            return psycopg2.connect(**self.kwargs)
        elif self.driver == 'mysql':
            return pymysql.connect(**self.kwargs)
        # 添加更多适配器
        else:
            raise ValueError(f"Unsupported database driver: {self.driver}")

    def get_connection(self):
        """
        从连接池获取一个连接
        """
        try:
            # 从队列中获取连接（阻塞等待直到有可用连接）
            connection = self.connections.get(timeout=10)
            return ConnectionWrapper(connection, self)
        except Exception as e:
            raise Exception(f"Failed to get connection from pool: {e}")

    def return_connection(self, connection):
        """
        将连接返回到连接池
        """
        try:
            # 检查连接是否有效
            if self._is_connection_valid(connection):
                self.connections.put(connection)
            else:
                # 如果连接无效，创建新连接
                new_connection = self._create_connection()
                self.connections.put(new_connection)
        except Exception as e:
            print(f"Error returning connection to pool: {e}")

    def _is_connection_valid(self, connection):
        """
        检查连接是否仍然有效
        """
        try:
            if self.driver == 'mysql':
                connection.ping(reconnect=True)
                return True
            elif self.driver == 'postgres':
                # 对于PostgreSQL，可以执行一个简单的查询
                with connection.cursor() as cursor:
                    cursor.execute('SELECT 1')
                return True
            return True
        except:
            return False

    def close_all_connections(self):
        """
        关闭连接池中的所有连接
        """
        while not self.connections.empty():
            try:
                connection = self.connections.get_nowait()
                connection.close()
            except:
                pass


class ConnectionWrapper:
    """
    连接包装器，确保连接使用后能正确返回到连接池
    """

    def __init__(self, connection, pool):
        self.connection = connection
        self.pool = pool

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.return_connection(self.connection)

    def __getattr__(self, name):
        # 将所有其他方法调用委托给实际的连接对象
        return getattr(self.connection, name)

    def close(self):
        # 重写close方法，使其将连接返回到池中而不是真正关闭
        self.pool.return_connection(self.connection)