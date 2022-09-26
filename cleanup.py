#!/usr/bin/env python
import openstack
import env
import os


def main() -> None:
    conn = openstack.connect()
    for server in conn.compute.servers(name=env.VM_NAME):
        conn.delete_server(server.id, wait=True, delete_ips=True)
    if os.path.exists(env.PRIVATE_KEY_PATH):
        os.remove(env.PRIVATE_KEY_PATH)
    conn.delete_keypair(env.KEY_PAIR_NAME)


if __name__ == "__main__":
    main()
