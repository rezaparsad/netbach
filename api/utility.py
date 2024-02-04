from config.settings import hetzner, linode, redis


def get_datacenter(server):
    if server.datacenter.name.lower() == "hetzner":
        return hetzner
    elif server.datacenter.name.lower() == "linode":
        return linode
    else:
        return None


def set_server_limit(server, action, ex=300):
    redis.set(f"CheckLimitServer-{server.user.pk}-{server.slug}-{action}", "limited", ex=ex)


def is_server_limited(server, action):
    key = f"CheckLimitServer-{server.user.pk}-{server.slug}-{action}"
    if redis.get(key):
        ttl = redis.ttl(key)
        return True, ttl
    return False, None
