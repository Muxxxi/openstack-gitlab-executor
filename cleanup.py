#!/usr/bin/env python
import traceback
import openstack
import env
import os
import sys
import time

def main() -> None:
    print("Delete openstack instances", flush=True)
    try:
        conn = openstack.connect()

        for server in conn.compute.servers(name=env.VM_NAME):
            volumes = server.attached_volumes
            for i in range(5):
                conn.delete_server(server.id, delete_ips=True)
                time.sleep(5)
                state = conn.compute.find_server(server.id, ignore_missing=True)
                if state is None:
                    print(f'Delete server {server.id} successful', flush=True)
                    break
            
            for volume in volumes:
                start_time = time.time()
                while time.time() - start_time < 300:  # Keep trying for up to 5 minutes
                    try:
                        if conn.block_storage.find_volume(volume.id):
                            conn.block_storage.delete_volume(volume.id)
                        print(f"Successfully deleted volume with ID {volume.id}", flush=True)
                        break
                    except openstack.exceptions.SDKException as e:
                        print(f"Error deleting volume with ID {volume.id}: {e}", flush=True)
                        print("Retrying in 10 seconds...", flush=True)
                        time.sleep(10)

        if os.path.exists(env.PRIVATE_KEY_PATH):
            os.remove(env.PRIVATE_KEY_PATH)
        conn.delete_keypair(env.KEY_PAIR_NAME)
  
        conn.close()
    except Exception as e:
        traceback.print_exc()
        sys.exit(int(env.SYSTEM_FAILURE_EXIT_CODE))


if __name__ == "__main__":
    main()
