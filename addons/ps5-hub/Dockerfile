# --- Stage 1: fetch plugin sources from their real upstream repos ---
FROM alpine:3.20 AS fetch

RUN apk add --no-cache git bash python3 nodejs openssl

WORKDIR /src

# Each plugin fetch is isolated and allowed to fail on its own: a broken
# upstream (renamed repo, network hiccup, a patch script that no longer
# applies) must not block the other plugins or the dashboard from
# building. A failed fetch leaves behind a placeholder page instead of
# the real plugin; server.py serves whatever directory exists.

# webkit-autoloader: full build pipeline (submodules + patch scripts +
# download_deps.sh) — only frontend/autoloader/ is needed, everything
# else (native ELF build, PC-host build) is skipped.
RUN set +e; \
    git clone --recurse-submodules https://github.com/itsPLK/ps5-webkit-autoloader.git webkit-autoloader && \
    cd webkit-autoloader && \
    git submodule update --init --recursive \
      third_party/relapse third_party/slopkit third_party/umtx2 \
      third_party/ps5-elfldr third_party/ps5-unified-autoloader && \
    bash tools/apply_relapse_patch.sh && \
    bash tools/apply_slopkit_patch.sh && \
    bash tools/apply_umtx2_patch.sh && \
    bash tools/download_deps.sh && \
    rm -f frontend/autoloader/placeholder.txt && \
    find frontend/autoloader -maxdepth 2 -name .git -type d -exec rm -rf {} + ; \
    cd /src; \
    if [ ! -f webkit-autoloader/frontend/autoloader/index.html ]; then \
      echo "[fetch] webkit-autoloader build failed, writing placeholder" >&2; \
      rm -rf webkit-autoloader; \
      mkdir -p webkit-autoloader/frontend/autoloader; \
      echo "<h1>WebKit Autoloader unavailable</h1><p>Build from itsPLK/ps5-webkit-autoloader failed at image build time.</p>" \
        > webkit-autoloader/frontend/autoloader/index.html; \
    fi

# relapse (ntfargo): plain static site, no build step.
RUN set +e; \
    git clone --depth=1 https://github.com/ntfargo/Relapse-Exploit.git relapse-ntfargo && \
    rm -rf relapse-ntfargo/.git relapse-ntfargo/payloads; \
    if [ ! -f relapse-ntfargo/index.html ]; then \
      echo "[fetch] relapse-ntfargo clone failed, writing placeholder" >&2; \
      rm -rf relapse-ntfargo; \
      mkdir -p relapse-ntfargo; \
      echo "<h1>Relapse Exploit unavailable</h1><p>Clone from ntfargo/Relapse-Exploit failed at image build time.</p>" \
        > relapse-ntfargo/index.html; \
    fi

# relapse (soniciso1): plain static site, no build step. api/ (optional
# server-assisted payload send for the already-jailbroken case) and
# elf.html are not needed — README says the exploit itself works from
# any static host with no server-side support.
RUN set +e; \
    git clone --depth=1 https://github.com/soniciso1/relapse.git relapse-sonic && \
    rm -rf relapse-sonic/.git relapse-sonic/api relapse-sonic/elf.html; \
    if [ ! -f relapse-sonic/index.html ]; then \
      echo "[fetch] relapse-sonic clone failed, writing placeholder" >&2; \
      rm -rf relapse-sonic; \
      mkdir -p relapse-sonic; \
      echo "<h1>Relapse (soniciso1) unavailable</h1><p>Clone from soniciso1/relapse failed at image build time.</p>" \
        > relapse-sonic/index.html; \
    fi

# --- Stage 2: the actual add-on image ---
ARG BUILD_FROM
FROM ${BUILD_FROM:-homeassistant/aarch64-base:latest}

RUN apk add --no-cache python3 gettext openssl

WORKDIR /app

COPY run.sh server.py /app/
RUN chmod +x /app/run.sh

COPY www/ /app/www/

COPY --from=fetch /src/webkit-autoloader/frontend/autoloader /app/plugins/webkit-autoloader
COPY --from=fetch /src/relapse-ntfargo /app/plugins/relapse
COPY --from=fetch /src/relapse-sonic /app/plugins/relapse-sonic

CMD ["/app/run.sh"]
