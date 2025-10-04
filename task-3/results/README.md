список команд:
```
docker build -t cron_cargo:latest .
minikube image load cron_cargo:latest
kubectl apply -f config_map.yaml
kubectl apply -f export_volume.yaml
kubectl apply -f cron.yaml
```
