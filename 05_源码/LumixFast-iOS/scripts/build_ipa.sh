#!/usr/bin/env bash
#
# build_ipa.sh
#
# Builds the Release device binary and packages it into an IPA.
#
# NOTE: This produces an UNSIGNED .ipa. An unsigned IPA cannot be installed on
# a device. To make it installable, run scripts/sign_ipa.sh (requires your
# Apple Developer team / signing identity). See README.md.
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

PROJECT="LumixFast.xcodeproj"
SCHEME="LumixFast"
CONFIG="Release"
APP_NAME="LumixFast"
STAMP="$(date +%Y%m%d-%H%M%S)"
STAGE="$(mktemp -d)/build-ipa-${STAMP}"
DIST="${ROOT}/dist"

echo "==> Building ${CONFIG} device build (unsigned)…"
xcodebuild \
  -project "${PROJECT}" \
  -scheme "${SCHEME}" \
  -configuration "${CONFIG}" \
  -destination 'generic/platform=iOS' \
  -derivedDataPath "${STAGE}/dd" \
  CODE_SIGNING_ALLOWED=NO \
  CODE_SIGNING_REQUIRED=NO \
  build

APP="${STAGE}/dd/Build/Products/Release-iphoneos/${APP_NAME}.app"
if [[ ! -d "${APP}" ]]; then
  echo "ERROR: could not find built app at ${APP}" >&2
  exit 1
fi

mkdir -p "${DIST}"
rm -f "${DIST}/${APP_NAME}.ipa"

echo "==> Packaging ${DIST}/${APP_NAME}.ipa (UNSIGNED)…"
(
  cd "${STAGE}"
  mkdir -p Payload
  cp -R "${APP}" Payload/
  zip -qry "${DIST}/${APP_NAME}.ipa" Payload
)

echo "==> Done: ${DIST}/${APP_NAME}.ipa"
echo
echo "This IPA is UNSIGNED and cannot be installed directly."
echo "To make it installable, run:  DEVELOPMENT_TEAM=<your 10-char team id> scripts/sign_ipa.sh"
