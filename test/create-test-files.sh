#!/usr/bin/sh
set -ex
rm -f traces/*
rm -f expected/*
rm -f inputs/*
rm -f files/*
get-projects.py -n IOS -t > expected/get-projects.output 2> traces/get-projects.trace
get-projects.py -n IOS -f NAME > expected/get-projects-name.output
get-projects.py -n IOS -f BOTH > expected/get-projects-both.output
cat expected/get-projects.output > inputs/get-repos.input
echo "" > expected/get-repos-empty.output
cat inputs/get-repos.input | get-repos.py -t > expected/get-repos.output 2> traces/get-repos.trace
cat inputs/get-repos.input | get-repos.py -c > expected/get-repos-count.output
cat expected/get-repos.output | grep python-postgresql-patches > inputs/get-branches.input
cat inputs/get-branches.input | get-branches.py -t > expected/get-branches.output 2> traces/get-branches.trace
cat inputs/get-branches.input | get-branches.py -n develop > expected/get-branches-name.output
cat inputs/get-branches.input | get-branches.py -n develop master > expected/get-branches-two-names.output
cat inputs/get-branches.input | get-branches.py -d > expected/get-branches-displayid.output
echo -e 'python-postgresql-patches\tIOS' | get-branches.py -n dummy -i -t > expected/get-branches-inverted.output 2> traces/get-branches-inverted.trace
cp inputs/get-branches.input inputs/get-clone-urls.input
cat inputs/get-clone-urls.input | get-clone-urls.py -t > expected/get-clone-urls.output 2> traces/get-clone-urls.trace
cat inputs/get-clone-urls.input | get-clone-urls.py -e http > expected/get-clone-urls-http.output
cp inputs/get-branches.input inputs/get-tags.input
cat inputs/get-tags.input | get-tags.py -t > expected/get-tags.output 2> traces/get-tags.trace
cat inputs/get-tags.input | get-tags.py -n 'tagg[0-9\.]*' > expected/get-tags-regex.output
cat inputs/get-tags.input | get-tags.py -d > expected/get-tags-displayid.output
echo -e 'python-postgresql-patches\tIOS' | get-tags.py -n "rc/*" -i -t > expected/get-tags-inverted.output 2> traces/get-tags-inverted.trace
cp inputs/get-branches.input inputs/get-branches-or-tags.input
cat inputs/get-branches-or-tags.input | get-branches-or-tags.py -t > expected/get-branches-or-tags.output 2> traces/get-branches-or-tags.trace
cat inputs/get-branches-or-tags.input | get-branches-or-tags.py -n develop 'tagg.*' > expected/get-branches-or-tags-names.output
cat inputs/get-branches-or-tags.input | get-branches-or-tags.py -d > expected/get-branches-or-tags-displayid.output
echo -e 'python-postgresql-patches\tIOS' | get-branches-or-tags.py -n dummy -i -t > expected/get-branches-or-tags-inverted.output 2> traces/get-branches-or-tags-inverted.trace
cat inputs/get-branches-or-tags.input | get-branches-or-tags.py > inputs/get-commits.input
cat inputs/get-commits.input | get-commits.py -t > expected/get-commits.output 2> traces/get-commits.trace
cat inputs/get-commits.input | get-commits.py > inputs/get-commit-details.input
cat inputs/get-commit-details.input | get-commit-details.py -t > expected/get-commit-details.output 2> traces/get-commit-details.trace
cat inputs/get-branches.input | get-branches.py -n develop | get-commits.py > inputs/create-branches.input
cat inputs/get-branches.input | get-branches.py -n feature/test | delete-branches.py
cat inputs/create-branches.input | create-branches.py -t feature/test > expected/create-branches.output 2> traces/create-branches.trace
cat inputs/get-tags.input | get-branches.py -n feature/test > inputs/delete-branches.input
cat inputs/get-repos.input | get-repos.py | grep python-postgresql-patches | get-branches.py | grep -vE "master|develop|rc" | sed "s/\(.*\)/refs\/heads\/develop\t\1/" > inputs/filter-branches.input
cat inputs/filter-branches.input | filter-branches.py -t > expected/filter-branches.output 2> traces/filter-branches.trace
cat expected/filter-branches.output > inputs/filter-merged.input
cat inputs/filter-merged.input | filter-merged.py -t > expected/filter-merged.output 2> traces/filter-merged.trace
cat inputs/filter-merged.input | filter-merged.py -i > expected/filter-merged-inverted.output
cat expected/get-branches.output | grep develop > inputs/get-file-names.input
cat inputs/get-file-names.input | get-file-names.py -t > expected/get-file-names.output 2> traces/get-file-names.trace
cat inputs/get-file-names.input | get-file-names.py -n pyproject.toml > expected/get-file-names-filter.output
cat inputs/get-file-names.input | get-file-names.py -m 1 > expected/get-file-names-max.output
cat inputs/get-file-names.input | get-file-names.py -c > expected/get-file-names-count.output
cp expected/get-file-names.output inputs/get-file-details.input
cat inputs/get-file-details.input | get-file-details.py -t > expected/get-file-details.output 2> traces/get-file-details.trace
cp expected/get-file-names.output inputs/get-file-ur# Needs to be anonymized
ls.input
# Needs to be anonymized
cat inputs/get-file-urls.input | get-file-urls.py | sed "s/bitb\.mynd\.se:80/127.0.0.1:8000/" | dos2unix.exe > expected/get-file-urls.output
echo "" > traces/get-file-urls.trace
cat inputs/get-file-urls.input | get-file-urls.py > inputs/get-file-lines.input
cat inputs/get-file-lines.input | get-file-content.py -t -d files lines '.*version.*' > expected/get-file-lines.output
# Needs to be anonymized
cat inputs/get-file-urls.input | get-file-urls.py | sed "s/bitb\.mynd\.se:80/127.0.0.1:8000/" | dos2unix.exe  > inputs/get-file-lines.input
cat inputs/get-repos.input | get-repos.py | grep python-postgresql-patches | get-branches.py -n feature/anonymisera feature/test | filter-merged.py -i > inputs/create-pr.input
cat inputs/create-pr.input | create-pr.py -t titel beskrivning > expected/create-pr.output 2> traces/create-pr.trace
cp expected/create-pr.output inputs/get-pr-diff.input
cat inputs/get-pr-diff.input | get-pr-diff.py -t -d files > expected/get-pr-diff.output
cat expected/get-repos.output | grep python-postgresql-patches > inputs/get-pr.input
cat inputs/get-pr.input | get-pr.py -t > expected/get-pr.output 2> traces/get-pr.trace
cat inputs/get-pr.input | get-pr.py -s DECLINED -t > expected/get-pr-declined.output 2> traces/get-pr-declined.trace
cat inputs/get-pr.input | get-pr.py -s MERGED -t > expected/get-pr-merged.output 2> traces/get-pr-merged.trace
cat inputs/get-pr.input | get-pr.py -s ALL -t > expected/get-pr-all.output 2> traces/get-pr-all.trace
cat inputs/get-pr.input | get-branches.py -n develop > inputs/get-pr-develop.input
cat inputs/get-pr-develop.input | get-pr.py -s MERGED -d IN > expected/get-pr-in.output
cat inputs/get-pr.input | get-branches.py -n develop master > inputs/get-pr-master.input
cat inputs/get-pr-master.input | get-pr.py -s MERGED > expected/get-pr-master.output
cp expected/get-pr-all.output inputs/get-pr-details.input
cat inputs/get-pr-details.input | get-pr-details.py -t > expected/get-pr-details.output 2> traces/get-pr-details.trace
cat inputs/get-pr-details.input | get-pr-details.py -j > expected/get-pr-details-json.output
cat inputs/get-repos.input | get-repos.py | grep python-postgresql-patches | get-pr.py -s ALL > inputs/filter-pr.input
cat inputs/filter-pr.input | filter-pr.py -t > expected/filter-pr.output 2> traces/filter-pr.trace
cat inputs/filter-pr.input | filter-pr.py -s UNAPPROVED > expected/filter-pr-unapproved.output
cat inputs/filter-pr.input | filter-pr.py -s APPROVED -i > expected/filter-pr-not-approved.output
cat inputs/filter-pr.input | filter-pr.py -i > expected/filter-pr-inverted.output
cp inputs/filter-pr.input inputs/get-pr-files.input
cat inputs/get-pr-files.input | get-pr-files.py -t > expected/get-pr-files.output 2> traces/get-pr-files.trace
cp expected/get-pr.output inputs/put-pr.input
# cat inputs/put-pr.input | put-pr.py -r secret.user APPROVED -t > expected/put-pr.output 2> traces/put-pr.trace
cp expected/get-pr.output inputs/merge-pr.input
cat inputs/merge-pr.input | merge-pr.py -t "Meddelande" > expected/merge-pr.output 2> traces/merge-pr.trace
cat inputs/get-branches.input | get-branches.py -n feature/test2 | delete-branches.py
cat inputs/create-branches.input | create-branches.py feature/test2
cat inputs/get-branches.input | get-branches.py -n feature/anonymisera feature/test2 | create-pr.py titel beskrivning > inputs/delete-pr.input
cat inputs/delete-pr.input | delete-pr.py -t > expected/delete-pr.output 2> traces/delete-pr.trace
cp expected/get-commit-details.output inputs/select-columns.input
echo "" > traces/select-columns.trace
cat inputs/select-columns.input | select-columns.py 4 3 2 1 0 > expected/select-columns.output
cat inputs/delete-branches.input | delete-branches.py -t > expected/delete-branches.output 2> traces/delete-branches.trace
