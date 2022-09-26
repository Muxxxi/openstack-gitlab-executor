#!/usr/bin/env python
import traceback
import openstack
import env
import os
import sys


def main() -> None:
    print("Delete openstack instances", flush=True)
    try:
        conn = openstack.connect()
        for server in conn.compute.servers(name=env.VM_NAME):
            conn.delete_server(server.id, wait=True, delete_ips=True)
        if os.path.exists(env.PRIVATE_KEY_PATH):
            os.remove(env.PRIVATE_KEY_PATH)
        conn.delete_keypair(env.KEY_PAIR_NAME)
        conn.close()
    except Exception as e:
        traceback.print_exc()
        sys.exit(int(env.SYSTEM_FAILURE_EXIT_CODE))


if __name__ == "__main__":
    main()
