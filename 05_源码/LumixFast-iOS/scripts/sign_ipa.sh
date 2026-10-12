#!/usr/bin/env bash
#
# sign_ipa.sh
#
# Signs the Release device build with your Apple Developer identity and packages
# it into an installable IPA.
#
# Requirements:
#   - Xcode installed, and your Apple ID added to Xcode (Settings > Accounts) so
#     that a valid "Apple Development" / "Apple Distribution" identity exists in
#     the keychain.  Check with:  security find-identity -v -p codesigning
#
# Usage:
#   DEVELOPMENT_TEAM=ABCDE12345 scripts/sign_ipa.sh
#
#   Optional: pin an explicit provisioning profile name
#   PROVISIONING_PROFILE_SPECIFIER="iOS Team <name>" scripts/sign_ipa.sh
#
# Output: dist/LumixFast-signed.ipa  (install to a device that matches the profile)
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

APP_NAME="LumixFast"
TEAM="${DEVELOPMENT_TEAM:?Set DEVELOPMENT_TEAM to your 10-character Apple Team ID}"
PROFILE_SPEC="${PROVISIONING_PROFILE_SPECIFIER:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
STAGE="$(mktemp -d)/sign-ipa-${STAMP}"
DIST="${ROOT}/dist"

echo "==> Checking signing identities…"
if ! security find-identity -v -p codesigning | grep -q "valid"; then
  echo "ERROR: no valid code-signing identities found." >&2
  echo "       Add your Apple ID to Xcode (Settings > Accounts) first, then retry." >&2
  exit 1
fi

ARGS=(
  -project "LumixFast.xcodeproj"
  -scheme "${APP_NAME}"
  -configuration Release
  -destination 'generic/platform=iOS'
  -derivedDataPath "${STAGE}/dd"
  CODE_SIGN_STYLE=Automatic
  DEVELOPMENT_TEAM="${TEAM}"
)
if [[ -n "${PROFILE_SPEC}" ]]; then
  ARGS+=(PROVISIONING_PROFILE_SPECIFIER="${PROFILE_SPEC}")
fi

echo "==> Building signed ${CONFIG:-Release} device build (team ${TEAM})…"
xcodebuild "${ARGS[@]}" build

APP="${STAGE}/dd/Build/Products/Release-iphoneos/${APP_NAME}.app"
[[ -d "${APP}" ]] || { echo "ERROR: no built app at ${APP}" >&2; exit 1; }

mkdir -p "${DIST}"
rm -f "${DIST}/${APP_NAME}-signed.ipa"

echo "==> Packaging ${DIST}/${APP_NAME}-signed.ipa…"
(
  cd "${STAGE}"
  mkdir -p Payload
  cp -R "${APP}" Payload/
  zip -qry "${DIST}/${APP_NAME}-signed.ipa" Payload
)

echo "==> Done: ${DIST}/${APP_NAME}-signed.ipa"
echo
echo "Install options:"
echo "  - Xcode: open the .ipa, or drag Payload/LumixFast.app to a connected device."
echo "  - Sideload: use AltStore / Sideer / Sideloadly with the signed IPA."
