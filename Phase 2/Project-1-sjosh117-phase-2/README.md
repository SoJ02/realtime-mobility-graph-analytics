# Project-1-sjosh117 Phase2

This project demonstrates the development of a scalable, real-time graph analytics pipeline using Neo4j, Apache Kafka, Docker, and Kubernetes. It processes NYC Yellow Cab trip data, models it as a graph, and applies graph algorithms like PageRank and Breadth-First Search (BFS).

## Technologies Used

- Neo4j
- Apache Kafka
- Kafka Connect
- Docker
- Kubernetes
- Python 3

## Project Structure

- **Phase 1**: Setup of a Neo4j database in Docker, static graph modeling, and running PageRank and BFS algorithms.
- **Phase 2**: Build of a distributed streaming pipeline using Kubernetes and Kafka, with real-time data ingestion into Neo4j.

## Setup Instructions

### Prerequisites

- Docker
- Minikube (for Kubernetes)
- kubectl
- Python 3.7+
- Confluent Kafka Python client (`pip install confluent-kafka`)

### Installation Steps

1. **Clone the repository:**

  ```bash
  git clone --single-branch --branch phase-2 https://github.com/your-username/your-repo.git
  ```

2. **Start Minikube:**

  ```bash
  minikube start --memory=4096 --cpus=4
  ```

3. **Deploy Services:**

  ```bash
  kubectl apply -f zookeeper-setup.yaml
  kubectl apply -f kafka-setup.yaml
  kubectl apply -f neo4j-service.yaml
  kubectl apply -f kafka-neo4j-connector.yaml
  ```

4. **Port Forward:**

  ```bash
  kubectl port-forward svc/neo4j-service 7474:7474 7687:7687
  kubectl port-forward svc/kafka-service 9092:9092
  ```

5. **Run Data Producer:**

  ```bash
  python data_producer.py
  ```

6. **Access Neo4j Browser**: Open http://localhost:7474 and log in using the configured username and password.

7. **Run Graph Algorithms**: Use the `interface.py` and `tester.py` scripts to perform BFS and PageRank on the ingested graph data.

## Results

- Successfully ingested and transformed NYC taxi trip data into a live updating graph.
- Implemented BFS for shortest path queries.
- Implemented PageRank to rank locations based on traffic.
