#!/bin/bash
set -e

FORCE=false
for arg in "$@"; do
  case "$arg" in
    --force)
      FORCE=true
      ;;
    *)
      echo "Unknown option: $arg" >&2
      echo "Usage: $0 [--force]" >&2
      exit 1
      ;;
  esac
done

hugo

if [ "$FORCE" = true ]; then
  echo "Force mode: re-uploading every file regardless of size"
  aws s3 cp public/ s3://sv-new-horizon --recursive
fi

aws s3 sync public/ s3://sv-new-horizon --delete --size-only
aws cloudfront create-invalidation --distribution-id E35L31NHLTJX3U --paths "/*"
