import requests
import argparse


def user_43(n):
    return {"username": f"u{n}", "password": "pass"}


def user_42(n):
    return {"login": f"u{n}", "password": "pass", "is_superuser": False}


def acl_43(n):
    return [
        {
            "login": f"u{n}",
            "topic": "/#",
            "action": "pubsub",
            "access": "deny",
        },
        {
            "login": f"u{n}",
            "topic": f"/c/{n}/#",
            "action": "pubsub",
            "access": "allow",
        },
    ]


def acl_42(n):
    return [
        {
            "login": f"u{n}",
            "topic": "/#",
            "action": "pubsub",
            "allow": False,
        },
        {
            "login": f"u{n}",
            "topic": f"/c/{n}/#",
            "action": "pubsub",
            "allow": True,
        },
    ]


VARIANTS = {
    "4.3": {
        "user_factory": user_43,
        "user_path": "auth_username",
        "acl_path": "acl",
        "acl_factory": acl_43,
    },
    "4.2": {
        "user_factory": user_42,
        "user_path": "mqtt_user",
        "acl_path": "mqtt_acl",
        "acl_factory": acl_42,
    },
}

parser = argparse.ArgumentParser("prepare-acl")
parser.add_argument("version", type=str, choices=["4.3", "4.2"])
parser.add_argument("count", type=int, default=5000)
parser.add_argument("--host", "-H", type=str, default="localhost")
parser.add_argument("--port", "-p", type=int, default=8081)

opts = parser.parse_args()

variant = VARIANTS[opts.version]
user_factory = variant["user_factory"]
acl_factory = variant["acl_factory"]

users = [user_factory(n) for n in range(opts.count)]
users_url = f"http://{opts.host}:{opts.port}/api/v4/{variant['user_path']}"

print(f"Posting {opts.count} users to {users_url}")
requests.post(users_url, json=users, auth=("admin", "public")).raise_for_status()

acls = [acl for n in range(opts.count) for acl in acl_factory(n)]
acls_url = f"http://{opts.host}:{opts.port}/api/v4/{variant['acl_path']}"

print(f"Posting {opts.count} acls to {acls_url}")
requests.post(acls_url, json=acls, auth=("admin", "public")).raise_for_status()
