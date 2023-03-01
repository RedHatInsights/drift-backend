FROM registry.access.redhat.com/ubi8/ubi-minimal

ARG TEST_IMAGE=false

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
    git-core python38 python38-pip tzdata libpq-devel && \
    rpm -qa | sort > packages-before-devel-install.txt && \
    microdnf install --setopt=tsflags=nodocs -y python38-devel gcc && \
    rpm -qa | sort > packages-after-devel-install.txt 

RUN pip3 install --upgrade pip && \
    pip3 install --upgrade pipenv && \
    pipenv sync

# allows unit tests to run successfully within the container if image is built in "test" environment
RUN if [ "$TEST_IMAGE" = "true" ]; then chgrp -R 0 $APP_ROOT && chmod -R g=u $APP_ROOT; fi

#RUN microdnf remove -y $( comm -13 packages-before-devel-install.txt packages-after-devel-install.txt ) && \
#    rm packages-before-devel-install.txt packages-after-devel-install.txt && \
#    microdnf clean all

CMD pipenv run ./run_app.sh

