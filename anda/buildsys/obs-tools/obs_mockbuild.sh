#!/bin/bash
pushd "${1:-.}"

ITERATIONS="${ITERATIONS:-3}"
ITERATIONS="${ITERATIONS:-$2}"

TIMEOUT="${TIMEOUT:-60}"
TIMEOUT="${TIMEOUT:-$3}"

typeset -a variables=()

buildcheck="n"
while IFS= read -r line; do
   if [[ -n "$line" ]]
   then
       variables+=("$line")
       buildcheck="y"
   fi
done <<< `obs_service_pkg_list`

if [[ "$buildcheck" == "y" ]]
then
    sudo bash -x -c 'A=$1; B=$2; shift; shift; pkg_check_available ${A} ${B} "${@}"; obs_pkg_install "${@}"' "bash" "${ITERATIONS}" "${TIMEOUT}" "${variables[@]}"
    buildcheck="n"
fi

obs_service_build

while IFS= read -r line; do
   if [[ -n "$line" ]]
   then
       variables+=("$line")
       buildcheck="y"
   fi
done <<< `rpmspec --query --buildrequires .osc.temp/_output_dir/*.spec`

if [[ "$buildcheck" == "y" ]]
then
    sudo bash -x -c 'A=$1; B=$2; shift; shift; pkg_check_available ${A} ${B} "${@}"; obs_pkg_install "${@}"' "bash" "${ITERATIONS}" "${TIMEOUT}" "${variables[@]}"
    buildcheck="n"
fi

rpmbuild -br "-D_sourcedir $PWD/.osc.temp/_output_dir" "-D_srcrpmdir $PWD/.osc.temp/_output_dir" "$PWD/.osc.temp/_output_dir/"*.spec

while IFS= read -r line; do
   if [[ -n "$line" ]]
   then
       variables+=("$line")
       buildcheck="y"
   fi
done <<< `rpm -q --requires .osc.temp/_output_dir/*.buildreqs.nosrc.rpm | sed 's~^rpmlib.*~~'`

if [[ "$buildcheck" == "y" ]]
then
    sudo bash -x -c 'A=$1; B=$2; shift; shift; pkg_check_available ${A} ${B} "${@}"' "bash" "${ITERATIONS}" "${TIMEOUT}" "${variables[@]}"
fi


popd
