import http.client


def create(env):
    conn = http.client.HTTPSConnection(env.url, timeout=env.timeout) if env.port is None \
        else http.client.HTTPConnection(env.url, port=env.port, timeout=env.timeout)
    return conn
