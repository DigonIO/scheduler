# caddy:2.10.2-alpine
# https://hub.docker.com/layers/library/caddy/2.10.2-alpine/images/sha256-5c18f4b845cd8f2cbb344ffa6fe0391d8c975ed921848c9968298f1eb8940a97
FROM caddy@sha256:953131cfea8e12bfe1c631a36308e9660e4389f0c3dfb3be957044d3ac92d446

COPY _build/ /usr/share/caddy/
COPY Caddyfile /etc/caddy/Caddyfile

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://localhost/ || exit 1
