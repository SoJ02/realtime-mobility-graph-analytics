# Streaming Graph Analytics (Kafka + Neo4j + Kubernetes)

This module is the real-time tier of the mobility analytics platform.  
It ingests trip events through Kafka, persists them to Neo4j, and runs graph algorithms over continuously updated graph state.

## What this module delivers

- Stream-to-graph ingestion pipeline
- Operational K8s manifests for distributed components
- Query scripts to validate graph behavior under live updates
- Algorithm workflows for BFS and PageRank

## Component Layout

- `zookeeper-setup.yaml` - coordination service for Kafka
- `kafka-setup.yaml` - Kafka broker deployment and service
- `neo4j-service.yaml` / `neo4j-values.yaml` - Neo4j deployment config
- `kafka-neo4j-connector.yaml` - stream sink wiring into Neo4j
- `data_producer.py` - event producer for taxi-style records
- `interface.py`, `tester.py` - analytics/query test layer

## Runtime Prerequisites

- Docker Desktop
- Minikube
- `kubectl`
- Python 3.7+
- `confluent-kafka` Python package

Install client dependency:

```bash
pip install confluent-kafka
```

## Deployment Procedure

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

## Validation Workflow

1. Open Neo4j Browser at `http://localhost:7474`
2. Confirm node/edge growth while producer is running
3. Run algorithm tests:
   - BFS traversal and path-style checks
   - PageRank ranking consistency checks
4. Use `tester.py` for repeatable validation runs

## Expected Outcomes

- Event ingestion is reflected in graph topology updates
- BFS queries return valid traversal behavior
- PageRank returns meaningful high-influence nodes/zones

## Troubleshooting Tips

- If ingestion stalls, verify port-forward sessions and connector status
- If analytics return empty results, check whether producer is actively publishing
- Inspect pod logs for Kafka, connector, and Neo4j when data flow appears interrupted
