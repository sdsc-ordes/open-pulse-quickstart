# open-pulse-quickstart

Quickstart for Open Pulse. Tutorials and how-tos

## What's Open Pulse?

Open Pulse is an Open Research Data (ORD) toolset developed by **EPFL Open Science** and the **SDSC**. It automates the discovery and monitoring of open-source software (OSS) produced at EPFL, laying the groundwork for making these contributions visible, measurable, and valued within research institutions.

Unlike traditional metrics, which emphasize volume (e.g., downloads or citations), **Open Pulse** puts **community vitality and engagement** at the center — tracking, for example, how actively software is updated, how often issues are resolved, and how software contributions evolve over time. Furthermore, Open Pulse segments repositories by type and discipline, allowing exploration of metrics related to specific research communities.

The platform brings all the data together into **three complementary components** to help make such community contributions visible and actionable:

| **Component** | **What it’s for?** | **Think of it as…** | **Powered by…** |
|----------------|--------------------|----------------------|------------------|
| **Development metrics** | To keep an eye on how active and healthy a software or research community is. | A live dashboard showing who's contributing, how often, and what they're doing — kind of like tracking the *pulse* of a community. | **GrimoireLab**, a set of open-source tools from the Linux Foundation. |
| **Community network** | To explore relationships between things like code repositories, contributors, and organizations. | A tool to answer questions like “Which people are working across multiple projects?” or “How are different organizations connected?” | **Neo4j**, a graph database, and **Cypher**, a language for querying graphs (like SQL but for networks). |
| **Repositories metadata** | To store and query semantic metadata about repositories — like what field of science they belong to, what license they use, or how FAIR (Findable, Accessible, Interoperable, Reusable) they are. | A smart filing cabinet that lets you ask complex questions like “Show me all repositories in biology that use an MIT License and have a Docker image.” | **Tentris**, a database for linked data, and **SPARQL**, a query language for this type of data. |

By combining these layers, **Open Pulse** provides a foundation for **evidence-based evaluation of open-source contributions**, with an emphasis on **community health, engagement, and relevance** across EPFL’s research landscape.

In this Quickstart we will show you how to start accessing this data

## How to use this Quickstart?

TBD: You can run this quickstart in Renku or in local by using the dockerimage we provide

### Development metrics 

The standard for community metrics are the CHAOSS metrics.

> **Disclaimer:** We originally intended to deploy a **GrimoireLab** instance for this session. However, due to technical issues, it will not be available for the hackathon. Instead, we offer **OSS Insight** as a powerful alternative to analyze repository metrics and community health.

You can get started with the **OSS Insight Quickstart** located in `src/ossinsight-quickstart/`.
- **Notebook:** `src/ossinsight-quickstart/quickstart.ipynb`
- **Guide:** `src/ossinsight-quickstart/README.md`

This quickstart maps OSS Insight API data to CHAOSS metrics, allowing you to visualize:
- Project Growth (Stars)
- Development Activity (Commits, PRs)
- Community Responsiveness (Issues)
- Contributor Diversity (Geography, Organizations)

![alt text](docs/images/oss.gif)

**Resources:**
- **CHAOSS:** [Website](https://chaoss.community/) | [Metrics Knowledge Base](https://chaoss.community/kbtopic/all-metrics/)
- **OSS Insight:** [Website](https://ossinsight.io/) | [API Docs](https://ossinsight.io/docs/api)
- **Example:** [DeepLabCut Analysis](https://ossinsight.io/analyze/DeepLabCut/DeepLabCut#overview) 

### Community Network

Relationships are structure in a property-graph and accessed via Cypher Queries.

You can explore the graph via the Neo4J User Interface of via the `neo4j-quickstart` notebook or script.

- Code there allows you to run CYPHER queries, remember you can explore [graph patterns (such as shortest path between 2 nodes)](https://neo4j.com/docs/cypher-manual/current/patterns/).
- You can download into a pandas dataframe part of the graph. The Graph being huge, we do not recommend reading the entire thing into Pandas.
- Visualization code is also made available for the graphs. 

![alt text](docs/images/Neo4J.png)

Link to Neo4j Open Pulse Instance: 
- Neo4J Browser: http://128.178.219.51:7503
- Neo4J Bolt: http://128.178.219.51:7504
Documentation: https://neo4j.com/docs/
Cypher Tutorial: https://neo4j.com/docs/cypher-manual/current/appendix/tutorials/

### Repositories Metadata

Metadata and semantic properties are stored in a RDF-compatible database based on the Imaging Plaza Ontology (ORD Project). We can query its results with SPARQL queries.

You can query the repositories' metadata via the quickstart notebook of the `tentris-quickstart`
You can also combine the queries to tentris about the extracted data with queries to WikiData for more complex information extraction. (see examples in notebook)

![alt text](docs/images/Tentris.png)

Link to Tentris Open Pulse: http://128.178.219.51:7502/ui
Documentation: https://docs.tentris.io/
SPARQL Tutorial: https://sparql.dev/

## Credits

SDSC