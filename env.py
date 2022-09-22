import os

VM_NAME = f"gitlab-builder-{os.getenv('CUSTOM_ENV_CI_RUNNER_ID')}-project-{os.getenv('CUSTOM_ENV_CI_PROJECT_ID')}-concurrent-{os.getenv('CUSTOM_ENV_CI_CONCURRENT_PROJECT_ID')}-job-{os.getenv('CUSTOM_ENV_CI_JOB_ID')}"  # noqa
FLAVOR = os.getenv("CUSTOM_ENV_FLAVOR") or os.getenv("FLAVOR")
BUILDER_IMAGE = os.getenv("CUSTOM_ENV_BUILDER_IMAGE") or os.getenv("BUILDER_IMAGE")
NETWORK = os.getenv("CUSTOM_ENV_NETWORK") or os.getenv("NETWORK")
KEY_PAIR_NAME = f'key-{VM_NAME}'
SECURITY_GROUPS = os.getenv("CUSTOM_ENV_SECURITY_GROUPS") or os.getenv("SECURITY_GROUPS")
USERNAME = os.getenv("CUSTOM_ENV_USERNAME") or os.getenv("USERNAME")
PRIVATE_KEY_PATH = f"{os.getenv('HOME')}/priv_key-{VM_NAME}"
SSH_TIMEOUT = os.getenv("CUSTOM_ENV_SSH_TIMEOUT") or os.getenv("SSH_TIMEOUT") or "20"
FLOATING_IP_NETWORK = os.getenv("FLOATING_IP_NETWORK") or "public"
SSH_IP_VERSION = os.getenv("SSH_IP_VERSION") or "4"
BUILD_FAILURE_EXIT_CODE = os.getenv("BUILD_FAILURE_EXIT_CODE")
SYSTEM_FAILURE_EXIT_CODE = os.getenv("SYSTEM_FAILURE_EXIT_CODE")
