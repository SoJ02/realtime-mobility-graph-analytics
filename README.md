# Real-Time Urban Mobility Graph Analytics

This project implements a graph-native analytics platform for urban mobility data, combining:

- **batch graph construction** for baseline experimentation, and
- **streaming ingestion** for near-real-time graph updates and querying.

Core use case: ingest NYC taxi-style trip events into Neo4j and run graph algorithms for connectivity and influence analysis.

## Why this project is useful

Mobility systems generate high-volume relational data (pickup, dropoff, route adjacency, co-occurrence).  
A graph-first pipeline makes it easier to answer questions like:

- Which zones are central in network flow?
- What are short traversal paths between key nodes?
- How do rankings change as live events arrive?

## Solution Overview

The repository is split into two operational modes:

### `Phase 1` - Batch Graph Pipeline

- Dockerized Neo4j setup
- Data loading from static files
- Algorithm execution and validation in a controlled environment

### `Phase 2` - Streaming Graph Pipeline

- Kafka and Zookeeper deployed on Kubernetes
- Event producer pushes trip records to Kafka
- Connector ingests into Neo4j continuously
- BFS and PageRank evaluated over the evolving graph

## Architecture

```text
Trip Producer -> Kafka -> Neo4j Connector -> Neo4j Graph
                                        -> Query Layer (BFS, PageRank)
```

## Tech Stack

- Python
- Neo4j + Graph Data Science
- Apache Kafka + Kafka Connect
- Docker
- Kubernetes (Minikube)

## Repository Map

- `Phase 1/` - batch setup, data loading, and local analytics scripts
- `Phase 2/Project-1-sjosh117-phase-2/` - K8s manifests + producer + analytics scripts
- `README.md` (this file) - top-level architecture and runbook

## End-to-End Runbook

### Option A: Streaming deployment (recommended)

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

Then:

1. Open Neo4j Browser at `http://localhost:7474`
2. Use `interface.py` and `tester.py` to run BFS/PageRank queries
3. Validate that rankings/paths update as additional events stream in

### Option B: Batch/local workflow

Use `Phase 1/` assets to run static ingestion and algorithm validation before moving to streaming mode.

## Results Achieved

- Built a functioning graph ingestion pipeline for taxi trip events
- Confirmed live updates from stream to graph
- Executed BFS traversal/path analysis
- Executed PageRank-based node importance scoring

## Operational Notes

- Start with batch mode for quick debugging
- Move to streaming mode for system-level validation
- Keep connector and Neo4j logs visible while validating ingestion semantics

## Potential Enhancements

- temporal graph snapshots for drift analysis,
- route-aware weighted edges,
- real-time anomaly detection over graph metrics,
- dashboard layer for rank/flow trend visualization.
