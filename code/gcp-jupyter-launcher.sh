#b--vm-image-pr!/bin/bash
# Als Code formatiert
# Helper script to try launching a vertex ai notebook in all specified zones until one succeeds.

# This script uses PyTorch 1.13, to get the image name for other environments go to:
# vertex ai > user-managed notebook > create > environment > select your environment > use a previous version > copy the id there

# For more information about the launch command, visit
# https://cloud.google.com/sdk/gcloud/reference/notebooks/instances/create

# All zones with T4 GPUs, roughly ordered by latency to eastern US
# taken from https://cloud.google.com/compute/docs/gpus/gpu-regions-zones
# check https://cloudpingtest.com/gcp for latencies from your location
zones=(
"us-east1-c" "us-east1-d"
"us-east4-a" "us-east4-b" "us-east4-c"
"northamerica-northeast1-c"
"us-central1-a" "us-central1-b" "us-central1-c" "us-central1-f"
"us-west1-a" "us-west1-b"
"us-west2-b" "us-west2-c"
"us-west4-a" "us-west4-b"

"europe-west1-b" "europe-west1-c" "europe-west1-d"
"europe-west2-a" "europe-west2-b"
"europe-west3-b"
"europe-west4-a" "europe-west4-b" "europe-west4-c"
"europe-central2-b" "europe-central2-c"

"southamerica-east1-b" "southamerica-east1-c"
"me-west1-b" "me-west1-c"
"australia-southeast1-a" "australia-southeast1-c"

"asia-northeast1-a" "asia-northeast1-c"
"asia-northeast3-b" "asia-northeast3-c"
"asia-east1-a" "asia-east1-c"
"asia-east2-a" "asia-east2-c"
"asia-southeast1-a" "asia-southeast1-b" "asia-southeast1-c"
"asia-southeast2-a" "asia-southeast2-b"
"asia-south1-a" "asia-south1-b"
)

for location in ${zones[@]}; do
 gcloud notebooks instances create hw2 --vm-image-name=pytorch-1-13-cu113-v20230925-ubuntu-2004-py310 --machine-type=n1-standard-8 --accelerator-type=NVIDIA_TESLA_T4 --accelerator-core-count=1 --install-gpu-driver --location=$location --vm-image-project=deeplearning-platform-release --project=instant-shard-401604
 if [ "$?" -eq "0" ]; then
    echo Launched in zone $location
    exit 0 # Stop after one launch succeeded
 else
    echo Failed in zone $location
 fi
done
