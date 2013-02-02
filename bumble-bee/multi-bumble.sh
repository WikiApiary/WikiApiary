#!/bin/bash
#
# This script runs multiple bumble bees

if [ "$1" -gt "$2" ]; then
	echo "First segment must be less than last segment."
	exit
fi

for i in $(seq $1 $2)
do
	echo "Starting Bumble Bee for segment $i..."
	nice -n 19 ./bumble-bee.py -s $i &
done
