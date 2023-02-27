FROM registry.access.redhat.com/ubi8/ubi-minimal

RUN microdnf install --setopt=install_weak_deps=0 --setopt=tsflags=nodocs -y \
    git-core python38 python38-pip tzdata && \
    microdnf clean all

RUN adduser --gid 0 -d /opt/app-root --no-create-home insights

ENV LC_ALL=C.utf8
ENV LANG=C.utf8

ENV APP_ROOT=/opt/app-root
ENV PIPENV_VENV_IN_PROJECT=1

ENV UNLEASH_CACHE_DIR=/tmp/unleash_cache

COPY . ${APP_ROOT}/src

WORKDIR ${APP_ROOT}/src

RUN pip3 install --upgrade pip && \
    pip3 install --upgrade pipenv

RUN pipenv sync

RUN chown -R insights:0 /opt/app-root  && \
    chgrp -R 0 /opt/app-root && \
    chmod -R g=u /opt/app-root

USER insights

CMD pipenv run ./run_app.sh
