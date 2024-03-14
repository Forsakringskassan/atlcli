#!/usr/bin/sh
set -ex
source ../environment.sh || true
[ -d testbox ] || $PYTHON -m venv testbox
[ $MACHINE == "MinGw" ] && ACTIVATE="testbox/Scripts/activate"
[ $MACHINE == "Linux" ] && ACTIVATE="testbox/bin/activate"
source $ACTIVATE
rm actual/*
./test-get-projects.sh
./test-script.sh "atlcli bitb get-repos" get-repos
./test-script.sh "atlcli bitb get-repos -s AVAILABLE" get-repos
./test-script.sh "atlcli bitb get-repos -s INITIALISING" get-repos get-repos-empty
./test-script.sh "atlcli bitb get-repos -s INITIALISATION_FAILED" get-repos get-repos-empty
./test-script.sh "atlcli bitb get-repos -c" get-repos get-repos-count
./test-script.sh "atlcli bitb get-branches" get-branches
./test-script.sh "atlcli bitb get-branches -n develop" get-branches get-branches-name
./test-script.sh "atlcli bitb get-branches -n develop master" get-branches get-branches-two-names
./test-script.sh "atlcli bitb get-branches -d" get-branches get-branches-displayid
./test-get-branches-inverted.sh
./test-script.sh "atlcli bitb get-clone-urls" get-clone-urls
./test-script.sh "atlcli bitb get-clone-urls -e http" get-clone-urls get-clone-urls-http
./test-script.sh "atlcli bitb get-tags" get-tags
./test-script.sh 'atlcli bitb get-tags -n tagg[0-9\.]*' get-tags get-tags-regex
./test-script.sh 'atlcli bitb get-tags -d' get-tags get-tags-displayid
./test-get-tags-inverted.sh
./test-script.sh 'atlcli bitb get-branches-or-tags' get-branches-or-tags
./test-script.sh 'atlcli bitb get-branches-or-tags -n develop tagg.*' get-branches-or-tags get-branches-or-tags-names
./test-script.sh 'atlcli bitb get-branches-or-tags -d' get-branches-or-tags get-branches-or-tags-displayid
./test-get-branches-or-tags-inverted.sh
./test-script.sh 'atlcli bitb get-commits' get-commits
./test-script.sh 'atlcli bitb get-commit-details' get-commit-details
./test-script.sh "atlcli bitb create-branches feature/test" create-branches
./test-script.sh "atlcli bitb delete-branches"  delete-branches
./test-script.sh "atlcli bitb filter-branches" filter-branches
./test-script.sh "atlcli bitb filter-merged" filter-merged
./test-script.sh "atlcli bitb filter-merged -i" filter-merged filter-merged-inverted
./test-script.sh "atlcli bitb get-file-names" get-file-names
./test-script.sh "atlcli bitb get-file-names -n pyproject.toml" get-file-names get-file-names-filter
./test-script.sh "atlcli bitb get-file-names -m 1" get-file-names get-file-names-max
./test-script.sh "atlcli bitb get-file-names -c" get-file-names get-file-names-count
./test-get-file-lines.sh
./test-script.sh "atlcli bitb get-file-details" get-file-details
./test-script.sh "atlcli bitb create-pr titel beskrivning" create-pr
./test-script.sh "atlcli bitb get-pr" get-pr
./test-script.sh "atlcli bitb get-pr -s OPEN" get-pr
./test-script.sh "atlcli bitb get-pr -s DECLINED" get-pr-declined get-pr  get-pr-declined
./test-script.sh "atlcli bitb get-pr -s MERGED" get-pr-merged get-pr get-pr-merged
./test-script.sh "atlcli bitb get-pr -s ALL" get-pr-all get-pr get-pr-all
./test-script.sh "atlcli bitb get-pr -s MERGED -d IN" get-pr-merged get-pr-develop get-pr-in
./test-script.sh "atlcli bitb get-pr -s MERGED" get-pr-merged get-pr-master get-pr-master
./test-script.sh "atlcli bitb get-pr-details" get-pr-details
./test-script.sh "atlcli bitb get-pr-details -j" get-pr-details get-pr-details-json
./test-script.sh "atlcli bitb filter-pr" filter-pr
./test-script.sh "atlcli bitb filter-pr -i" filter-pr filter-pr-inverted
./test-script.sh "atlcli bitb filter-pr -s UNAPPROVED" filter-pr filter-pr-unapproved
./test-script.sh "atlcli bitb filter-pr -s APPROVED -i" filter-pr filter-pr-not-approved
./test-script.sh "atlcli bitb get-pr-files" get-pr-files
./test-script.sh "atlcli bitb merge-pr Meddelande" merge-pr
./test-script.sh "atlcli bitb delete-pr" delete-pr
./test-select-columns.sh
./test-get-pr-diff.sh
../shared/version.py
echo "All tests succeeded"
