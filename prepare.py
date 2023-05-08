#!/usr/bin/env python
import sys
import time
import traceback
import ipaddress
import openstack
import paramiko
from tenacity import retry
from tenacity import RetryCallState
from tenacity import stop_after_attempt
from tenacity import wait_fixed
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

import env

def provision_server(
    conn: openstack.connection.Connection,
    public_key: str
) -> openstack.compute.v2.server.Server:
    floating_ip = True if env.SSH_IP_VERSION == "4" else False
    conn.create_keypair(env.KEY_PAIR_NAME, public_key=public_key)
    image = conn.compute.find_image(env.BUILDER_IMAGE)
    flavor = conn.compute.find_flavor(env.FLAVOR)
    network = conn.network.find_network(env.NETWORK)
    server = conn.create_server(
        name=env.VM_NAME,
        flavor=flavor.id,
        image=image.id,
        auto_ip=floating_ip,
        wait=True,
        timeout=env.SERVER_CREATION_TIMEOUT,
        boot_from_volume=True,
        terminate_volume=True,
        volume_size=env.VOLUME_SIZE,
        key_name=env.KEY_PAIR_NAME,
        security_groups=[group for group in env.SECURITY_GROUPS.split()],
        network=network.id
    )

    return server


def get_server_ip(
    conn: openstack.connection.Connection, server: openstack.compute.v2.server.Server
) -> str:
    for i in range(3):
        ips = [ipaddress.ip_address(ip.address) for ip in list(conn.compute.server_ips(server.id))]
        print(ips)
        for ip in ips:
            if env.SSH_IP_VERSION == str(ip.version) and ip.is_global:
                return str(ip)
        time.sleep(10)
    raise RuntimeError("No working ip address found")
    
        

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


def generate_rsa_keypair():
    # generate private/public key pair
    key = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, \
        key_size=2048)

    # get public key in OpenSSH format
    public_key = key.public_key().public_bytes(serialization.Encoding.OpenSSH, \
        serialization.PublicFormat.OpenSSH)

    # get private key in PEM container format
    pem = key.private_bytes(encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption())

    with open(env.PRIVATE_KEY_PATH, 'w') as content_file:
        content_file.write(pem.decode('utf-8'))
    public_key_str = public_key.decode('utf-8')
    return public_key_str


def main() -> None:
    print(
        "Source code of this driver https://github.com/RedHatQE/openstack-gitlab-executor",
        flush=True,
    )
    print("Connecting to Openstack", flush=True)
    try:
        conn = openstack.connect()
        print(f"Provisioning an instance {env.VM_NAME}", flush=True)
        public_key = generate_rsa_keypair()
        print(f'Public Key: {public_key}', flush=True)
        server = provision_server(conn, public_key)
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
