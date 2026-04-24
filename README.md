# Real-Time Urban Mobility Graph Analytics

This repository builds a graph analytics platform for NYC taxi trip data, combining batch graph modeling and real-time streaming ingestion.

## What this project does

- Ingests trip events and maps them to a graph representation
- Stores and updates graph data in Neo4j
- Runs graph analytics such as:
  - **BFS** for shortest-path style exploration
  - **PageRank** for identifying high-importance zones

## Architecture

- `Phase 1/`: Dockerized Neo4j setup, static data loading, graph algorithm execution
- `Phase 2/`: Streaming architecture with Kafka + Kubernetes + Neo4j connector

## Tech stack

- Python
- Neo4j + Graph Data Science
- Apache Kafka + Kafka Connect
- Docker
- Kubernetes (Minikube)

## How to run

### Option A: Streaming pipeline (recommended)

```bash
cd "Phase 2/Project-1-sjosh117-phase-2"
minikube start --memory=4096 --cpus=4
kubectl apply -f zookeeper-setup.yaml
kubectl apply -f kafka-setup.yaml
kubectl apply -f neo4j-service.yaml
kubectl apply -f kafka-neo4j-connector.yaml
kubectl port-forward svc/neo4j-service 7474:7474 7687:7687
kubectl port-forward svc/kafka-service 9092:9092
python data_producer.py
```

Then open Neo4j Browser at `http://localhost:7474` and run analytics via `interface.py` / `tester.py`.

### Option B: Local Docker workflow

Use the assets in `Phase 1/` for local graph loading and query-based analytics.

## Results

- Built a live-updating graph from NYC taxi events
- Verified BFS workflow for route/path queries
- Verified PageRank workflow for ranking high-traffic areas

## Folder guide

- `Phase 1/` - local/dockerized graph pipeline
- `Phase 2/Project-1-sjosh117-phase-2/` - Kubernetes streaming stack
