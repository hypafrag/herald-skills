import redis
import config

redis = redis.Redis(host=config.redis.host,
                    port=config.redis.port,
                    db=config.redis.db,
                    password=config.redis.password)
