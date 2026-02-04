#!/bin/bash
# Hook: Post-deploy verification for Astro sites
# Event: PostToolUse (Bash - after deploy commands)
# Purpose: Verify deployed site is accessible and functioning

TOOL_NAME="$1"
SITE_URL=""

# Extract site URL from astro.config.mjs (POSIX-compatible)
get_site_url() {
  local config_file=""
  if [ -f "astro.config.mjs" ]; then
    config_file="astro.config.mjs"
  elif [ -f "astro.config.ts" ]; then
    config_file="astro.config.ts"
  fi

  if [ -n "$config_file" ]; then
    SITE_URL=$(sed -nE "s/.*site:[[:space:]]*['\"]([^'\"]+)['\"].*/\1/p" "$config_file")
    BASE_PATH=$(sed -nE "s/.*base:[[:space:]]*['\"]([^'\"]+)['\"].*/\1/p" "$config_file")
    if [ -n "$BASE_PATH" ]; then
      SITE_URL="${SITE_URL}${BASE_PATH}"
    fi
  fi
}

# Only run after deploy-related commands
case "$TOOL_NAME" in
  "deploy"|"publish"|"push")
    get_site_url

    if [ -n "$SITE_URL" ]; then
      echo "[astro-deploy-verify] Checking deployed site: $SITE_URL"

      # Wait for deployment propagation
      sleep 5

      # Check HTTP status with timeouts
      if command -v curl &> /dev/null; then
        HTTP_STATUS=$(curl -sS --connect-timeout 5 --max-time 15 -o /dev/null -w "%{http_code}" "$SITE_URL" 2>/dev/null)
        if [ "$HTTP_STATUS" = "200" ]; then
          echo "[astro-deploy-verify] PASSED: Site returned HTTP 200"
        elif [ "$HTTP_STATUS" = "301" ] || [ "$HTTP_STATUS" = "302" ]; then
          echo "[astro-deploy-verify] INFO: Site returned redirect ($HTTP_STATUS)"
        else
          echo "[astro-deploy-verify] WARNING: Site returned HTTP $HTTP_STATUS"
        fi
      else
        echo "[astro-deploy-verify] SKIP: curl not available for verification"
      fi

      # Check dist directory exists locally
      if [ -d "dist" ]; then
        FILE_COUNT=$(find dist -type f | wc -l)
        echo "[astro-deploy-verify] Build output: $FILE_COUNT files in dist/"
      fi
    else
      echo "[astro-deploy-verify] SKIP: No site URL found in astro config"
    fi
    ;;
esac

exit 0
