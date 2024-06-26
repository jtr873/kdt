#!/bin/bash

# Function to download a file with error handling and retries
download_artifact() {
  local url="$1"
  local filename="$2"
  local max_retries=${3:-5}  # Default to 5 retries if no retry count provided
  local retry_count=0

  # Loop for retries
  while [[ $retry_count -lt $max_retries ]]; do
    # Download the file and check for HTTP errors
    curl -L "$url" -H "Accept: application/json" -o "$filename" -w "%{http_code}\n" || {
      echo "Error downloading $filename (HTTP code: $?) on attempt $((retry_count + 1))" >&2
      let retry_count++
    }

    # Check if downloaded file exists and is non-empty after each attempt
    if [[ -f "$filename" && $(stat -c %s "$filename") -gt 0 ]]; then
      break  # Successful download, exit loop
    fi
  done

  # Check if all retries failed
  if [[ $retry_count -eq $max_retries ]]; then
    echo "Error: Downloading $filename failed after $max_retries retries." >&2
    exit 1
  fi
}

# Validate and get AAEBID from the first argument
if [[ -z "$1" ]]; then
  echo "Error: Please provide an AAEBID as the first argument." >&2
  exit 1
fi
AAEBID="$1"

# Define build target, server URL, and filenames
TARGET="aosp_cf_riscv64_phone-trunk_staging-userdebug"
SERVER_URL="https://androidbuildinternal.googleapis.com/android/internal/build/v3/builds/$AAEBID/$TARGET/attempts/latest/artifacts"
IMG_NAME="aosp_cf_riscv64_phone-img-${AAEBID}.zip"
HOST_PACKAGE_NAME="cvd-host_package-x86_64.tar.gz"
MANIFEST="manifest_${AAEBID}.xml"

# Create directory for the build (handle errors)
mkdir -p "$AAEBID" || {
  echo "Error creating directory $AAEBID" >&2
  exit 1
}

# Download artifacts using the download function with 5 retries
download_artifact "$SERVER_URL/$IMG_NAME/url" "$AAEBID/$IMG_NAME"
download_artifact "$SERVER_URL/$HOST_PACKAGE_NAME/url" "$AAEBID/$HOST_PACKAGE_NAME"
download_artifact "$SERVER_URL/$MANIFEST/url" "$AAEBID/$MANIFEST"

echo "Download complete!"

