
from redis import Redis



class RedisQueuesStorage(object):
    """
        Redis Lists are an ordered list, First In First Out Queue
        Redis List pushing new elements on the head (on the left) of the list.
        The max length of a list is 4,294,967,295
    """
    def __init__(self, **redis_kwargs):
        """
            host='localhost', port=6379, db=0
        """
        self.rq = Redis(**redis_kwargs)

    def size(self, key): # 큐 크기 확인
        return self.rq.llen(key)

    def isEmpty(self, key): # 비어있는 큐인지 확인
        return self.size(key) == 0

    def put(self, key, value): # 데이터 넣기,
        self.rq.lpush(key, value) # left push

    def get(self, key, isBlocking=False, timeout=None): # 데이터 꺼내기
        if isBlocking:
            element = self.rq.brpop(key, timeout=timeout) # blocking right pop
            element = element[1] # key[0], value[1]
        else:
            element = self.rq.rpop(key) # right pop
        return element
    
    def delete(self, key):
        self.rq.delete(key)

    def get_without_pop(self, key): # 꺼낼 데이터 조회
        if self.isEmpty():
            return None
        element = self.rq.lindex(key, -1)
        return element
            

