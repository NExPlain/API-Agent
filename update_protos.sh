#!/bin/bash

# Get the directory of the script. This ensures that the script can be run
# from any directory, and it will still find the right files.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# Change to the directory where your protos are
cd "${SCRIPT_DIR}/api_gpt/data_structures/proto"

# Run your protoc command
protol \
  --create-package \
  --in-place \
  --python-out generated \
  protoc --proto-path=. intent_data.proto intent_input.proto execution_data.proto intent_template.proto meta_data.proto parameter.proto workflow_example.proto workflow_template.proto workflow.proto