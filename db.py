import redis
import os

redis = redis.Redis(host=os.environ['HS_REDIS_HOST'],
                    port=os.environ['HS_REDIS_PORT'],
                    db=0,
                    password=os.environ['HS_REDIS_PASSWORD'])
