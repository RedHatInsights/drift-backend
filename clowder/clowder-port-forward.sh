#!/usr/bin/env

declare -a APPS=('ingress-service' 'host-inventory-service' 'system-baseline-backend' 'drift-backend' 'historical-system-profiles-backend')
declare -a PORTS=('8081' '8082' '8083' '8084' '8085')

for I in ${!APPS[@]}; 
	do
		PODNAME=`oc get pod | awk '{print $1}' | grep ${APPS[${I}]} | head -1`
		PORT=${PORTS[${I}]} 
		echo "Port-forwarding ${APPS[${I}]} to $PODNAME"
		oc port-forward $PODNAME $PORT:8000 > /dev/null 2>&1 &
		echo $!
done 

#TODO: How do we know if a port-forward stopped? PID process?
#If we find it, how to retrigger the port-forward again?