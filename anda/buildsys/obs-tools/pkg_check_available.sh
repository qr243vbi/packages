#!/bin/bash
typeset -i "iterations=$1"
typeset -i "timeout=$2"
shift
shift

if [[ -n "$(command -v copr-sleep)" ]]
then
    alias sleep=copr-sleep
fi

for ((i=1; i<=iterations; i++))
do
    dnf provides "${@}" && break
    sleep "${timeout}"
done

