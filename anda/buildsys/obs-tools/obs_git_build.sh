#!/bin/bash
url="$1"
if [[ -z "$2" ]]
then
name="$(echo $1 | sed 's~.*/~~; s~.git$~~;')"
else
name="$2"
fi
outdir="${3:-_output_dir}"

declare -i i=0

if [[ "$name" == "$outdir" ]]; then
  name="${name}_0"
fi

if [[ -e "${name}" ]]; then
  while [[ -e "${name}_${i}" ]]; do
    i=$i+1
  done
  name="${name}_${i}"
fi

git clone --depth 1 "$url" "$name"

pushd "${name}"
obs_service_run
popd
mv -vTf "${name}/.osc.temp/_output_dir" "${outdir}"
