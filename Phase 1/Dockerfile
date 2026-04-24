# Base image: ubuntu:22.04
FROM ubuntu:22.04

# ARGs
# https://docs.docker.com/engine/reference/builder/#understand-how-arg-and-from-interact
ARG TARGETPLATFORM=linux/amd64,linux/arm64
ARG DEBIAN_FRONTEND=noninteractive

# neo4j installation and some cleanup
RUN apt-get update && \
    apt-get install -y wget gnupg software-properties-common && \
    wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add - && \
    echo 'deb https://debian.neo4j.com stable latest' > /etc/apt/sources.list.d/neo4j.list && \
    add-apt-repository universe && \
    apt-get update && \
    apt-get install -y nano unzip neo4j python3-pip && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


# TODO: Complete the Dockerfile
# Install git for repository cloning
RUN apt-get update && apt-get install -y git && apt-get clean

# Configure Neo4j server to accept remote connections
RUN sed -i 's/#server.default_listen_address=0.0.0.0/server.default_listen_address=0.0.0.0/' /etc/neo4j/neo4j.conf
RUN sed -i 's/#server.http.listen_address=:7474/server.http.listen_address=:7474/' /etc/neo4j/neo4j.conf
RUN sed -i 's/#server.bolt.listen_address=:7687/server.bolt.listen_address=:7687/' /etc/neo4j/neo4j.conf

# Set the initial password for Neo4j database
RUN neo4j-admin dbms set-initial-password project1phase1

# Install required Python packages
RUN pip3 install --upgrade pip
RUN pip3 install neo4j pandas pyarrow requests

# Create directory for project files
RUN mkdir -p /cse511
WORKDIR /cse511

# Clone the project repository and download dataset
RUN git clone https://github.com/SP-2025-CSE511-Data-Processing-at-Scale/Project-1-sjosh117.git /cse511
RUN wget -O /cse511/yellow_tripdata_2022-03.parquet https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-03.parquet

# Install Neo4j Graph Data Science (GDS) plugin
RUN mkdir -p /var/lib/neo4j/plugins/
RUN wget -P /tmp/ https://graphdatascience.ninja/neo4j-graph-data-science-2.15.0.zip
RUN unzip /tmp/neo4j-graph-data-science-2.15.0.zip -d /tmp/
RUN mv /tmp/neo4j-graph-data-science-2.15.0.jar /var/lib/neo4j/plugins/

# Configure Neo4j to allow GDS procedures
RUN grep -q "dbms.security.procedures.unrestricted" /etc/neo4j/neo4j.conf && \
    sed -i 's/dbms.security.procedures.unrestricted=.*/dbms.security.procedures.unrestricted=gds.*,apoc.*/' /etc/neo4j/neo4j.conf || \
    echo "dbms.security.procedures.unrestricted=gds.*,apoc.*" >> /etc/neo4j/neo4j.conf
RUN echo "dbms.security.procedures.allowlist=gds.*,apoc.*" >> /etc/neo4j/neo4j.conf

# Add a delay before running the data loader to ensure Neo4j is fully started
RUN echo '#!/bin/bash\nneo4j start\nsleep 30\npython3 /cse511/data_loader.py\nneo4j stop' > /cse511/run_loader.sh
RUN chmod +x /cse511/run_loader.sh

# Run the data loader script
RUN chmod +x /cse511/data_loader.py && \
    /cse511/run_loader.sh

# Expose neo4j ports
EXPOSE 7474 7687

# Start neo4j service and show the logs on container run
CMD ["/bin/bash", "-c", "neo4j start && tail -f /dev/null"]