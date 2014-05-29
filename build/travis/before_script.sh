#!/bin/bash


## Download the Maxmind GeoLite database
function downloadMaxmind {

    wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
    gunzip GeoLiteCity.dat.gz

    mkdir -p config/

    mv GeoLiteCity.dat config/

}

downloadMaxmind
