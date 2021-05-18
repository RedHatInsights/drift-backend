FROM registry.access.redhat.com/ubi8/python-38

# Install dependencies and clean cache to make the image cleaner

USER 0
RUN rpm -ivh https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm && \
    yum install -y hostname shared-mime-info && \
    yum clean all -y

COPY . /tmp/src
RUN chown -R 1001:0 /tmp/src

USER 1001

ENV ENABLE_PIPENV=true

# https://github.com/RedHatInsights/drift-backend.git

# Install the dependencies
RUN /usr/libexec/s2i/assemble

#CMD ["/opt/app-root/src/deploy/entrypoint.sh"]
CMD bash
