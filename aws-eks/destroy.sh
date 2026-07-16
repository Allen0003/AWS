#!/bin/bash

echo "=== 開始清理 K8s 內部的服務 ==="
# 先刪除 K8s 內的 LoadBalancer，讓 AWS 有時間把 ELB 資源釋放
kubectl delete -f java-app.yaml
kubectl delete -f infrastructure.yaml

echo "等待 30 秒確保 AWS Load Balancer 已經順利卸載..."
sleep 30

echo "=== 開始透過 CloudFormation 刪除 EKS 叢集 ==="
# eksctl 會去觸發 CloudFormation 刪除 Stack，把 VPC、EC2、EKS 全數清空
eksctl delete cluster -f cluster.yaml

echo "=== 清理完成！ ==="