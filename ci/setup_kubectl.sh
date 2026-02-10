echo "${K8S_CERT}" | base64 --decode > deploy.crt
kubectl config set-cluster K8S --server="${K8S_HOST}" --certificate-authority=deploy.crt
kubectl config set-credentials cicd-account --token="${K8S_BEARER_TOKEN}"
kubectl config set-context K8S --cluster K8S --user cicd-account --namespace "${K8S_NAMESPACE}"
kubectl config use-context K8S