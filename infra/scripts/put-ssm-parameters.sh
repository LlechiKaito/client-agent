#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARAMS_FILE="${1:-${SCRIPT_DIR}/../ssm-parameters.json}"

if [[ ! -f "$PARAMS_FILE" ]]; then
  echo "Error: $PARAMS_FILE not found"
  echo "Usage: $0 [path/to/ssm-parameters.json]"
  echo ""
  echo "Create from example:"
  echo "  cp infra/ssm-parameters.example.json infra/ssm-parameters.json"
  echo "  # Edit values, then run this script"
  exit 1
fi

COUNT=$(jq length "$PARAMS_FILE")
echo "Creating $COUNT SSM parameters..."

for i in $(seq 0 $((COUNT - 1))); do
  NAME=$(jq -r ".[$i].Name" "$PARAMS_FILE")
  VALUE=$(jq -r ".[$i].Value" "$PARAMS_FILE")
  TYPE=$(jq -r ".[$i].Type" "$PARAMS_FILE")
  DESC=$(jq -r ".[$i].Description" "$PARAMS_FILE")

  echo "  -> $NAME"
  aws ssm put-parameter \
    --name "$NAME" \
    --value "$VALUE" \
    --type "$TYPE" \
    --description "$DESC" \
    --overwrite
done

echo "Done."
