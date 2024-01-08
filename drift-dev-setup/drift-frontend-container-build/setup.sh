echo "127.0.0.1 ci.foo.redhat.com" >> /etc/hosts
echo "127.0.0.1 qa.foo.redhat.com" >> /etc/hosts
echo "127.0.0.1 stage.foo.redhat.com" >> /etc/hosts
echo "127.0.0.1 prod.foo.redhat.com" >> /etc/hosts

dnf install -y git-core npm
git clone https://github.com/RedHatInsights/drift-frontend.git
cd drift-frontend
npm install
