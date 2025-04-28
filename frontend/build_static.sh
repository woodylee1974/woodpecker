#!/bin/bash

vite build&&rm -fr ../build&&mv dist ../build
version=$(cat package.json|grep -oP '"version": "\K[^"]+')
commit_id=$(git rev-parse HEAD)
branch=$(git rev-parse --abbrev-ref HEAD)
cat <<EOF > ../build/version.rc
export VERSION=$version
export COMMIT_ID=$commit_id
export BRANCH=$branch
EOF