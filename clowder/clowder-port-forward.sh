#!/usr/bin/bash

declare -a SERVICES=('ingress-service' 'host-inventory-service' 'system-baseline-backend-service' 'drift-backend-service' 'historical-system-profiles-backend-service')
declare -a PORTS=('8081' '8082' '8083' '8084' '8085')

for I in ${!SERVICES[@]};
	do
		SERVICE=${SERVICES[${I}]}
		PORT=${PORTS[${I}]}
		echo "Port-forwarding $PORT to $SERVICE"
		oc port-forward "service/$SERVICE" "$PORT:8000" > /dev/null 2>&1 &
		echo $!
done

#TODO: How do we know if a port-forward stopped? PID process?
#If we find it, how to retrigger the port-forward again?
