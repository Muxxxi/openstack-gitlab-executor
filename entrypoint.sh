#!/bin/bash

trap cleanup SIGTERM SIGINT

cleanup() {
    gitlab-runner unregister --all-runners
    sleep 5
}

if [[ "$TLS_CA_CERT" ]]; then
    mkdir -p "$HOME"/.gitlab-runner/certs/
    echo "$TLS_CA_CERT" > "$HOME"/.gitlab-runner/certs/$(echo "$CI_SERVER_URL" | cut -d'/' -f3 | cut -d':' -f1).crt
fi

echo "$PRIVATE_KEY" > "$HOME"/priv_key

gitlab-runner register --non-interactive \
                       --executor=custom \
                       --custom-config-exec=/data/config.sh \
                       --custom-prepare-exec=/data/prepare.py \
                       --custom-run-exec=/data/run.py \
                       --custom-cleanup-exec=/data/cleanup.py

if [[ "$CONCURRENT" ]]; then
    sed -i "s/concurrent = .*/concurrent = $CONCURRENT/g" $HOME/.gitlab-runner/config.toml
fi

gitlab-runner run
