#!/bin/bash

certbot renew --preferred-challenges=dns --cert-name $1 --force-renew --manual-auth-hook ./authentificator.sh --manual-public-ip-logging-ok
