# Kubernetes Jobs Cleanup

If your K8s cluster support alpha features, you can use [TTLAfterFinished](https://kubernetes.io/docs/concepts/workloads/controllers/ttlafterfinished/) option instead this image.

## Describe
This is source code from [Docker image](https://hub.docker.com/r/gatchenko/k8s-jobs-cleanup) which built on **Python 3.7 Alpine** image. The image is designed to run by **CronJob**, to clear Jobs in the status of "**completed**" and their pods.

## Options
| Option | Describe | Default value | Required |
| ------ | ------ | ------ | ------ |
| CLEANUP_TIMEOUT | The time in seconds after completion of a job before deleted  | 60 | No |
| KUBERNETES_NAMESPACE | Kubernetes namespace | default | No |

## Kubernetes RBAC
```yaml
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: jobs-cleanup
automountServiceAccountToken: false
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: jobs-cleanup
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list", "delete"]
- apiGroups: ["batch", "extensions"]
  resources: ["jobs"]
  verbs: ["get", "list", "watch", "delete"]
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: jobs-cleanup
subjects:
- kind: ServiceAccount
  name: jobs-cleanup
  namespace: default
roleRef:
  kind: ClusterRole
  name: jobs-cleanup
  apiGroup: rbac.authorization.k8s.io
```

## CronJob
```yaml
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: jobs-cleanup
  namespace: kube-system
spec:
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: jobs-cleanup
            image: gatchenko/k8s-jobs-cleanup:latest
            env:
            - name: CLEANUP_TIMEOUT
              value: "60"
            - name: KUBERNETES_NAMESPACE
              value: "default"
          restartPolicy: OnFailure
          serviceAccountName: jobs-cleanup
          automountServiceAccountToken: true
```
