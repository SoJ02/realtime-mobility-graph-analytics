# Streaming Graph Analytics (Kafka + Neo4j + Kubernetes)

This module runs a real-time pipeline that streams NYC taxi events into Neo4j and executes graph analytics on the resulting graph.

## Stack

- Neo4j
- Apache Kafka + Kafka Connect
- Kubernetes (Minikube)
- Docker
- Python

## Quick start

### Prerequisites

- Docker
- Minikube
- `kubectl`
- Python 3.7+
- `pip install confluent-kafka`

### Run steps

```bash
minikube start --memory=4096 --cpus=4
kubectl apply -f zookeeper-setup.yaml
kubectl apply -f kafka-setup.yaml
kubectl apply -f neo4j-service.yaml
kubectl apply -f kafka-neo4j-connector.yaml
kubectl port-forward svc/neo4j-service 7474:7474 7687:7687
kubectl port-forward svc/kafka-service 9092:9092
python data_producer.py
```

Open Neo4j Browser at `http://localhost:7474`, then run analytics using:

- `interface.py`
- `tester.py`

## Outcomes

- Event data is ingested continuously into a graph model
- BFS queries support path and traversal analysis
- PageRank highlights high-importance nodes/locations
