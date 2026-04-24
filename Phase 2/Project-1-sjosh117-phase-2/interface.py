from neo4j import GraphDatabase

class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()
        
    def close(self):
        self._driver.close()
        
    def bfs(self, start_node, last_node):
        # Implementation of Breadth-First Search algorithm
        with self._driver.session() as session:
            # Check and drop existing graph projection if needed
            check_graph_query = "CALL gds.graph.exists('bfsGraph') YIELD exists"
            if session.run(check_graph_query).single()['exists']:
                session.run("CALL gds.graph.drop('bfsGraph')")
            
            # Create a new graph projection for BFS
            create_projection_query = """
            CALL gds.graph.project(
                'bfsGraph',
                'Location',
                'TRIP'
            )
            """
            session.run(create_projection_query)
            
            # Find the node IDs for start and end locations
            find_start_query = """
            MATCH (source:Location {name: $start})
            RETURN id(source) AS sourceId
            """
            
            find_end_query = """
            MATCH (target:Location {name: $last})
            RETURN id(target) AS targetId
            """
            
            # Convert to integers if they're strings
            start_id = int(start_node) if isinstance(start_node, str) else start_node
            end_id = int(last_node) if isinstance(last_node, str) else last_node
            
            start_result = session.run(find_start_query, start=start_id)
            end_result = session.run(find_end_query, last=end_id)
            
            source_id = start_result.single()['sourceId']
            target_id = end_result.single()['targetId']
            
            # Execute BFS algorithm - key fix: using targetNodes array instead of targetNode
            execute_bfs_query = """
            CALL gds.bfs.stream('bfsGraph', {
                sourceNode: $sourceId,
                targetNodes: [$targetId]
            })
            YIELD path
            RETURN path
            """
            
            bfs_result = session.run(execute_bfs_query, sourceId=source_id, targetId=target_id)
            path_record = bfs_result.single()
            
            # Process the path result
            path_nodes = []
            
            if path_record and path_record['path']:
                # Extract node IDs from path
                path_obj = path_record['path']
                path_node_ids = [n.id for n in path_obj.nodes]
                
                # Get location IDs for these nodes
                get_locations_query = """
                MATCH (n)
                WHERE id(n) IN $node_ids
                RETURN n.name AS name
                ORDER BY CASE 
                    WHEN n.name = $start THEN 0 
                    WHEN n.name = $last THEN 2 
                    ELSE 1 
                END
                """
                
                locations_result = session.run(
                    get_locations_query, 
                    node_ids=path_node_ids,
                    start=start_id,
                    last=end_id
                )
                
                # Format the path
                for record in locations_result:
                    path_nodes.append({"name": record["name"]})
                
                # Ensure start and end are in the path
                if not path_nodes or path_nodes[0]["name"] != start_id:
                    path_nodes.insert(0, {"name": start_id})
                if not path_nodes or path_nodes[-1]["name"] != end_id:
                    path_nodes.append({"name": end_id})
            else:
                # No path found, return just start and end
                path_nodes = [{"name": start_id}, {"name": end_id}]
            
            # Clean up
            session.run("CALL gds.graph.drop('bfsGraph')")
            
            # Return the path in the expected format
            return [{"path": path_nodes}]
    
    def pagerank(self, max_iterations, weight_property):
        # Implementation of PageRank algorithm
        with self._driver.session() as session:
            # Check for existing projection
            projection_exists_query = "CALL gds.graph.exists('prGraph') YIELD exists"
            if session.run(projection_exists_query).single()['exists']:
                session.run("CALL gds.graph.drop('prGraph')")
            
            # Create graph projection with relationship properties
            properties = {}
            if weight_property:
                properties[weight_property] = {
                    "property": weight_property,
                    "defaultValue": 1.0
                }
                
                create_projection_query = """
                CALL gds.graph.project(
                    'prGraph',
                    'Location',
                    'TRIP',
                    {
                        relationshipProperties: $properties
                    }
                )
                """
                
                session.run(create_projection_query, properties=properties)
            else:
                # Create projection without properties
                create_projection_query = """
                CALL gds.graph.project(
                    'prGraph',
                    'Location',
                    'TRIP'
                )
                """
                session.run(create_projection_query)
            
            # Run PageRank algorithm
            run_pagerank_query = """
            CALL gds.pageRank.stream('prGraph', {
                maxIterations: $max_iter,
                relationshipWeightProperty: $weight_prop
            })
            YIELD nodeId, score
            WITH nodeId, score
            MATCH (n) WHERE id(n) = nodeId
            RETURN n.name AS name, score
            ORDER BY score DESC
            """
            
            pagerank_results = session.run(
                run_pagerank_query, 
                max_iter=max_iterations,
                weight_prop=weight_property
            )
            
            # Process results
            all_results = list(pagerank_results)
            
            if all_results:
                # Get highest and lowest ranked nodes
                highest_ranked = {
                    "name": all_results[0]["name"],
                    "score": all_results[0]["score"]
                }
                
                lowest_ranked = {
                    "name": all_results[-1]["name"],
                    "score": all_results[-1]["score"]
                }
            else:
                # No results
                highest_ranked = {"name": None, "score": 0}
                lowest_ranked = {"name": None, "score": 0}
            
            # Clean up
            session.run("CALL gds.graph.drop('prGraph')")
            
            # Return results in expected format
            return [highest_ranked, lowest_ranked]
