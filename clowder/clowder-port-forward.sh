#!/usr/bin/bash

declare -a SERVICES=('ingress-service' 'host-inventory-service' 'system-baseline-backend-service' 'drift-backend-service' 'historical-system-profiles-backend-service', 'rbac-service')
declare -a PORTS=('8081' '8082' '8083' '8084' '8085' '8086')
declare -a DBS=('system-baseline-db' 'historical-system-profiles-db')
declare -a DB_PORTS=('5433' '5434')
KAFKA_SVCS=$(oc get service | grep kafka-bootstrap | awk '{print $1}')
KAFKA_PORT='9092'

for I in ${!SERVICES[@]};
	do
		SERVICE=${SERVICES[${I}]}
		PORT=${PORTS[${I}]}
		echo "Port-forwarding $PORT to $SERVICE"
		oc port-forward "service/$SERVICE" "$PORT:8000" > /dev/null 2>&1 &
		echo $!
done

for I in ${!DBS[@]};
	do
		DB=${DBS[${I}]}
		PORT=${DB_PORTS[${I}]}
		echo "Port-forwarding $PORT to $DB"
		oc port-forward "service/$DB" "$PORT:5432" > /dev/null 2>&1 &
		echo $!
done

echo "Port-forwarding $KAFKA_PORT to $KAFKA_SVCS"
oc port-forward "service/$KAFKA_SVCS" "$KAFKA_PORT:9092" > /dev/null 2>&1 &
echo $!

#TODO: How do we know if a port-forward stopped? PID process?
#If we find it, how to retrigger the port-forward again?
