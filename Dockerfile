FROM python:3-slim

ARG GITLAB_RUNNER_VERSION=v15.2.1
ENV GITLAB_RUNNER_URL="https://gitlab-runner-downloads.s3.amazonaws.com/${GITLAB_RUNNER_VERSION}/binaries/gitlab-runner-linux-amd64"

LABEL maintainer="Max Reinheimer <max@reinheimer.dev>" \
      io.openshift.tags="gitlab,ci,runner" \
      name="openstack-gitlab-runner" \
      io.k8s.display-name="GitLab runner" \
      summary="GitLab runner" \
      description="A GitLab runner image with openstack custom executor." \
      io.k8s.description="A GitLab runner image with openstack custom executor."

COPY cleanup.py env.py config.sh prepare.py run.py requirements.txt /data/
COPY entrypoint.sh /usr/bin/entrypoint

RUN apt-get update && apt-get -y install curl dumb-init gcc libffi-dev && \
    curl -L --output /usr/bin/gitlab-runner "${GITLAB_RUNNER_URL}" && \
    pip3 install -r /data/requirements.txt && \
    chmod +x /data/* /usr/bin/entrypoint /usr/bin/gitlab-runner && \
    useradd --comment 'GitLab Runner' --create-home gitlab-runner --shell /bin/bash && \
    apt-get remove -y gcc curl && apt autoremove -y && apt-get clean

USER gitlab-runner
WORKDIR /data

ENTRYPOINT ["dumb-init", "--"]
CMD ["entrypoint"]
