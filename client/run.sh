IDENTITY_TEMPLATE='{"identity": {"account_number": "ACCT_PLACEHOLDER", "internal": {"org_id": "000001"}}}'
IDENTITY_HEADER="${IDENTITY_TEMPLATE/ACCT_PLACEHOLDER/$ACCOUNT_NUMBER}"    
IDENT_B64=`base64 -w0 <<< $IDENTITY_HEADER`

if [ -z "$SLEEP" ];
  then SLEEP=60
fi

cd insights-client
while true
do
  UPLOADFILE=`BYPASS_GPG=True EGG=../insights-core/insights.zip ./src/insights-client --no-gpg --debug --offline --keep-archive | grep "Archive saved" | awk '{print $NF}'`
  curl -v -F "file=@$UPLOADFILE;type=application/vnd.redhat.advisor.file+tgz" -H "x-rh-identity: $IDENT_B64" http://ingress:3000/api/ingress/v1/upload
  sleep $SLEEP
done
