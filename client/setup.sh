dnf install -y git-core autoconf automake pkg-config python38 wget binutils make zip
git clone https://github.com/RedHatInsights/insights-client.git
git clone https://github.com/RedHatInsights/insights-core.git
cd insights-client/
./autogen.sh 
mkdir -p /usr/local/lib/python3.8/site-packages/
ln -s /usr/bin/python3 /usr/bin/python
make
mkdir /etc/insights-client
cp data/insights-client.conf data/.fallback.json data/.exp.sed /etc/insights-client
cd ../insights-core
python3 setup.py install
./build_client_egg.sh 
