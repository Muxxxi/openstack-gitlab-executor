#!/usr/bin/env python
import sys
import traceback

import openstack
import paramiko
from tenacity import retry
from tenacity import RetryCallState
from tenacity import stop_after_attempt
from tenacity import wait_fixed

import env


def provision_server(
    conn: openstack.connection.Connection,
) -> openstack.compute.v2.server.Server:
    image = conn.compute.find_image(env.BUILDER_IMAGE)
    flavor = conn.compute.find_flavor(env.FLAVOR)
    network = conn.network.find_network(env.NETWORK)
    server = conn.compute.create_server(
        name=env.VM_NAME,
        flavor_id=flavor.id,
        image_id=image.id,
        key_name=env.KEY_PAIR_NAME,
        security_groups=[{"name": group} for group in env.SECURITY_GROUPS.split()],
        networks=[{"uuid": network.id}],
    )
    return conn.compute.wait_for_server(server, wait=600)


def get_server_ip(
    conn: openstack.connection.Connection, server: openstack.compute.v2.server.Server
) -> str:
    return list(conn.compute.server_ips(server))[0].address


def check_ssh(ip: str) -> None:
    ssh_client = paramiko.client.SSHClient()
    pkey = paramiko.rsakey.RSAKey.from_private_key_file(env.PRIVATE_KEY_PATH)
    ssh_client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())

    def before_callback(retry_state: RetryCallState):
        print(
            f"Attempt: {retry_state.attempt_number}; timeout: {env.SSH_TIMEOUT} seconds",
            flush=True,
        )

    @retry(
        reraise=True,
        stop=stop_after_attempt(10),
        wait=wait_fixed(int(env.SSH_TIMEOUT)),
        before=before_callback,
    )
    def connect():
        ssh_client.connect(
            hostname=ip,
            username=env.USERNAME,
            pkey=pkey,
            look_for_keys=False,
            allow_agent=False,
            timeout=int(env.SSH_TIMEOUT),
        )

    connect()
    ssh_client.close()


def main() -> None:
    print(
        "Source code of this driver https://github.com/RedHatQE/openstack-gitlab-executor",
        flush=True,
    )
    print("Connecting to Openstack", flush=True)
    try:
        conn = openstack.connect()
        print(f"Provisioning an instance {env.VM_NAME}", flush=True)
        server = provision_server(conn)
        ip = get_server_ip(conn, server)
        print(f"Instance {env.VM_NAME} is running on address {ip}", flush=True)
        conn.close()
        print("Waiting for SSH connection", flush=True)
        check_ssh(ip)
        print("SSH connection has been established", flush=True)
    except Exception:
        traceback.print_exc()
        sys.exit(int(env.SYSTEM_FAILURE_EXIT_CODE))


if __name__ == "__main__":
    main()
