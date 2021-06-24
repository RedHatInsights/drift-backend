TEMPDIR=`mktemp -d`
if [[ "$OSTYPE" == "darwin"* ]]
then
	echo "THIS IS AS MACOS"
	curl -L https://github.com/openshift/source-to-image/releases/download/v1.2.0/source-to-image-v1.2.0-2a579ecd-darwin-amd64.tar.gz > $TEMPDIR/s2i.tar.gz
else
	curl -L https://github.com/openshift/source-to-image/releases/download/v1.2.0/source-to-image-v1.2.0-2a579ecd-linux-amd64.tar.gz > $TEMPDIR/s2i.tar.gz
fi

cd $TEMPDIR
tar xfz s2i.tar.gz

# s2i builds
./s2i build https://github.com/RedHatInsights/system-baseline-backend.git  centos/python-38-centos7 system-baseline:latest -e ENABLE_PIPENV=true
./s2i build https://github.com/RedHatInsights/drift-backend.git  centos/python-38-centos7 drift:latest -e ENABLE_PIPENV=true
./s2i build https://github.com/RedHatInsights/historical-system-profiles-backend.git  centos/python-38-centos7 hsp:latest -e ENABLE_PIPENV=true
#./s2i build https://github.com/RedHatInsights/insights-host-inventory.git  centos/python-36-centos7 inventory:mq -e ENABLE_PIPENV=true

# ingress build
git clone https://github.com/RedHatInsights/insights-ingress-go.git
cd insights-ingress-go
docker build . -t ingress:latest
cd ..

# puptoo build
git clone https://github.com/RedHatInsights/insights-puptoo.git
cd insights-puptoo
docker build . -t puptoo:latest
cd ..
