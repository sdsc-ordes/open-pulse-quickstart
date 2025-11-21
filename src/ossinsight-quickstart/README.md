# OSS Insight Quickstart

This project provides a quickstart guide and a Jupyter Notebook for analyzing GitHub repositories using the [OSS Insight API](https://ossinsight.io/). It focuses on mapping these insights to [CHAOSS](https://chaoss.community/) (Community Health Analytics Open Source Software) metrics to evaluate the health and sustainability of open source communities.

## What is OSS Insight?

[OSS Insight](https://ossinsight.io/) is a powerful tool developed by [PingCAP](https://pingcap.com/) that provides comprehensive insights into open source software. It analyzes billions of GitHub events to deliver real-time data and trends about developer activities, repository health, and community growth.

- **Website:** [https://ossinsight.io/](https://ossinsight.io/)
- **GitHub Repository:** [https://github.com/pingcap/ossinsight](https://github.com/pingcap/ossinsight)

## CHAOSS Metrics Mapping

The core of this quickstart is the `quickstart.ipynb` notebook, which demonstrates how to retrieve data from OSS Insight and interpret it through the lens of CHAOSS metrics.

Below is the mapping of the analysis sections in the notebook to the corresponding CHAOSS metrics:

| Notebook Section | OSS Insight Metric / Endpoint | CHAOSS Metric / Area | Description |
| :--- | :--- | :--- | :--- |
| **2. Star History** | Star History | **Growth-Maturity-Decline** | Tracks project popularity and growth trends over time. |
| **3. Commit Activity** | Commit Time Distribution | **Code Development - Commit Activity** | Analyzes when contributions happen to identify work patterns and timezones. |
| **4. PR Health** | PR Overview, Size, Time to Merge | **Code Development - Code Review Efficiency** | Evaluates the velocity and quality of the code review process. |
| **5. Issue Health** | Response Time, Opened vs Closed | **Issue Resolution & Responsiveness** | Measures how responsive the community is to user feedback and bugs. |
| **6. Trending Contributors** | Recent Trending Contributors | **Contribution Distribution**, **Bus Factor** | Identifies active code contributors and potential dependency risks (Bus Factor). |
| **7. Trending Issue Participants** | Recent Trending Issue Participants | **Issue Participants**, **Community Engagement** | Tracks user engagement and non-code contributions. |
| **8. Contributor Geography** | Contributor Geography | **D&I - Geographic Diversity** | Visualizes the global distribution of contributors to assess inclusivity. |
| **9. Organizational Affiliation** | Organizational Affiliation | **Organizational Diversity**, **Elephant Factor** | Checks if the project is dominated by a single company or has a diverse ecosystem. |

## Getting Started

1.  **Open the Notebook:** Open `quickstart.ipynb` in VS Code or your preferred Jupyter environment.
2.  **Install Dependencies:** Ensure you have the required Python packages installed:
    ```bash
    pip install requests pandas bokeh
    ```
3.  **Run the Analysis:** Execute the cells in order. You can change the `owner` and `repo` variables in **Section 1** to analyze any public GitHub repository.

## Resources

- [CHAOSS Metrics Knowledge Base](https://chaoss.community/kbtopic/all-metrics/)
- [OSS Insight API Documentation](https://ossinsight.io/docs/api)
