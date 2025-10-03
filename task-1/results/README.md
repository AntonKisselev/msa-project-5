## Обоснование

Стек легко интегрируется с BigQuery, Redshift, Kafka и Spark, тк есть готовые операторы для этих систем<br>
В качестве примера развернуто ниже задача:
формируется csv файл , в котором есть числа от 0 до 100, и ветвление - считает среднее значение этих чисел, если оно больше или меньше 50


## Список команд для разворачивания стека
только для локальной разработки, нужно предварительно развернуть kubernetes, если уже есть кубер, можно этот шаг пропустить
```
minikube start --driver=docker
```

установка airflow, из официпльных репозиториев не сработало, скачал официальный чарт
```
kubectl create namespace airflow
helm install airflow airflow -n airflow
```

проброс папки с dag
```
cd dags
kubectl create configmap airflow-dags \
  --namespace airflow \
  --from-file=./dags \
  --dry-run=client -o yaml | kubectl apply -f -
helm upgrade airflow airflow -n airflow  
```

проброс порта
```
kubectl port-forward svc/airflow-web 8080:8080 -n airflow
```

## Результат показан на скринах с последовательной нумерацией в папке screen