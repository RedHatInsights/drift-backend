FROM registry.access.redhat.com/ubi8/ubi-minimal

ENV LC_ALL=C.utf8
ENV LANG=C.utf8

ENV APP_ROOT=/opt/app-root
ENV PIP_NO_CACHE_DIR=1
ENV PIPENV_CLEAR=1
ENV PIPENV_VENV_IN_PROJECT=1

ENV UNLEASH_CACHE_DIR=/tmp/unleash_cache

COPY . ${APP_ROOT}/src

WORKDIR ${APP_ROOT}/src

RUN microdnf install --setopt=install_weak_deps=0 --setopt=tsflags=nodocs -y \
    git-core python38 python38-pip tzdata && \
    rpm -qa | sort > packages-before-devel-install.txt && \
    microdnf install --setopt=tsflags=nodocs -y libpq-devel python38-devel gcc && \
    rpm -qa | sort > packages-after-devel-install.txt 

RUN pip3 install --upgrade pip setuptools wheel && \
    pip3 install --upgrade pipenv

RUN microdnf remove -y $( comm -13 packages-before-devel-install.txt packages-after-devel-install.txt ) && \
    rm packages-before-devel-install.txt packages-after-devel-install.txt && \
    microdnf clean all

RUN pipenv sync

CMD pipenv run ./run_app.sh
