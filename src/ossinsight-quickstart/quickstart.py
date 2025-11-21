import requests
import pandas as pd
from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool, LinearColorMapper, BasicTicker, PrintfTickFormatter, ColorBar
from bokeh.transform import transform

def get_repo_info(owner, repo):
    url = f"https://api.ossinsight.io/gh/repo/{owner}/{repo}"
    res = requests.get(url)
    res.raise_for_status()
    return res.json()["data"]

def get_star_history(repo_id: int) -> pd.DataFrame:
    url = f"https://api.ossinsight.io/q/analyze-stars-history?repoId={repo_id}"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()["data"]   # list of dicts with event_month, repo_id, total
    df = pd.DataFrame(data)
    if df.empty:
        return df
    
    df["event_month"] = pd.to_datetime(df["event_month"])
    df = df.rename(columns={"event_month": "date", "total": "stargazers"})
    return df

def get_commit_time_distribution(repo_id: int) -> pd.DataFrame:
    url = f"https://api.ossinsight.io/q/analyze-commits-time-distribution?repoId={repo_id}&period=last_1_year"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()["data"]
    df = pd.DataFrame(data)
    return df

def get_pr_overview(repo_id: int) -> dict:
    url = f"https://api.ossinsight.io/q/analyze-repo-pr-overview?repoId={repo_id}"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()["data"]
    return data[0] if data else {}

def get_pr_size_history(repo_id: int) -> pd.DataFrame:
    url = f"https://api.ossinsight.io/q/analyze-pull-requests-size-per-month?repoId={repo_id}"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()["data"]
    df = pd.DataFrame(data)
    if not df.empty:
        df["event_month"] = pd.to_datetime(df["event_month"])
        df = df.rename(columns={"event_month": "date"})
    return df

def get_pr_merge_time(repo_id: int) -> pd.DataFrame:
    url = f"https://api.ossinsight.io/q/analyze-pull-request-open-to-merged?repoId={repo_id}"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()["data"]
    df = pd.DataFrame(data)
    if not df.empty:
        df["event_month"] = pd.to_datetime(df["event_month"])
        df = df.rename(columns={"event_month": "date"})
    return df

def get_issue_overview(repo_id: int) -> dict:
    url = f"https://api.ossinsight.io/q/analyze-repo-issue-overview?repoId={repo_id}"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()["data"]
    return data[0] if data else {}

def get_issue_response_time(repo_id: int) -> pd.DataFrame:
    url = f"https://api.ossinsight.io/q/analyze-issue-open-to-first-responded?repoId={repo_id}"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()["data"]
    df = pd.DataFrame(data)
    if not df.empty:
        df["event_month"] = pd.to_datetime(df["event_month"])
        df = df.rename(columns={"event_month": "date"})
    return df

def get_issue_opened_closed(repo_id: int) -> pd.DataFrame:
    url = f"https://api.ossinsight.io/q/analyze-issue-opened-and-closed?repoId={repo_id}"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()["data"]
    df = pd.DataFrame(data)
    if not df.empty:
        df["event_month"] = pd.to_datetime(df["event_month"])
        df = df.rename(columns={"event_month": "date"})
    return df

def get_geo_distribution(repo_id: int, metric_type: str = "pr_creators") -> pd.DataFrame:
    """
    metric_type options: 'pr_creators', 'stargazers', 'issue_creators'
    """
    endpoints = {
        "pr_creators": f"https://api.ossinsight.io/q/analyze-pull-request-creators-map?repoId={repo_id}",
        "stargazers": f"https://api.ossinsight.io/q/analyze-stars-map?repoId={repo_id}&period=all_times",
        "issue_creators": f"https://api.ossinsight.io/q/analyze-issue-creators-map?repoId={repo_id}"
    }
    
    url = endpoints.get(metric_type)
    if not url:
        return pd.DataFrame()
        
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()["data"]
    df = pd.DataFrame(data)
    return df

def get_company_distribution(repo_id: int) -> pd.DataFrame:
    url = f"https://api.ossinsight.io/q/analyze-pull-request-creators-company?repoId={repo_id}"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()["data"]
    df = pd.DataFrame(data)
    return df

def get_trending_pr_contributors(repo_id: int) -> pd.DataFrame:
    url = f"https://api.ossinsight.io/q/analyze-people-code-pr-contribution-rank?repoId={repo_id}&excludeBots=true"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()["data"]
    df = pd.DataFrame(data)
    return df

def get_trending_issue_contributors(repo_id: int) -> pd.DataFrame:
    url = f"https://api.ossinsight.io/q/analyze-people-issue-comment-contribution-rank?repoId={repo_id}&excludeBots=true"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()["data"]
    df = pd.DataFrame(data)
    return df

def get_issue_creators_company(repo_id: int) -> pd.DataFrame:
    url = f"https://api.ossinsight.io/q/analyze-issue-creators-company?repoId={repo_id}"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()["data"]
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    owner = "DeepLabCut"
    repo = "DeepLabCut"

    print(f"Fetching info for {owner}/{repo}...")
    try:
        repo_info = get_repo_info(owner, repo)
        repo_id = repo_info["id"]

        print("Repo:", repo_info["full_name"])
        print("Repo ID:", repo_id)
        print("Stars (live GitHub count):", repo_info["stargazers_count"])

        print("Fetching star history...")
        df_stars = get_star_history(repo_id)
        
        if df_stars.empty:
            print("No star history data returned for this repository.")
        else:
            print(f"Found {len(df_stars)} months of data.")
            print(df_stars.tail())

            # Output to static HTML file
            output_file("star_history.html", title=f"Star History - {owner}/{repo}")
            
            p = figure(
                title=f"Stargazers Over Time – {owner}/{repo}",
                x_axis_type='datetime',
                width=900, height=420,
                tools="pan,wheel_zoom,box_zoom,reset"
            )

            p.line(df_stars['date'], df_stars['stargazers'], line_width=2)
            p.circle(df_stars['date'], df_stars['stargazers'], size=3)

            p.add_tools(HoverTool(
                tooltips=[("Date", "@x{%F}"), ("Stars", "@y")],
                formatters={"@x": "datetime"}
            ))

            p.xaxis.axis_label = "Date"
            p.yaxis.axis_label = "Cumulative Stars"
            
            print("Generating plot to star_history.html...")
            show(p)
            print("Done.")

        print("Fetching commit time distribution...")
        df_commits = get_commit_time_distribution(repo_id)
        
        if df_commits.empty:
            print("No commit data found.")
        else:
            print(f"Found {len(df_commits)} data points.")
            
            # Prepare data for heatmap
            days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            hours = [str(x) for x in range(24)]
            
            df_commits["day_name"] = df_commits["dayofweek"].apply(lambda x: days[x])
            df_commits["hour_str"] = df_commits["hour"].astype(str)
            
            # Bokeh HeatMap
            output_file("commits_heatmap.html", title=f"Commit Heatmap - {owner}/{repo}")
            
            mapper = LinearColorMapper(palette="Viridis256", low=df_commits.pushes.min(), high=df_commits.pushes.max())

            p2 = figure(title=f"Commit Time Distribution - {owner}/{repo}",
                       x_range=hours, y_range=list(reversed(days)),
                       x_axis_location="above", width=900, height=400,
                       tools="hover,save,pan,box_zoom,reset,wheel_zoom")

            p2.rect(x="hour_str", y="day_name", width=1, height=1, source=df_commits,
                    fill_color=transform('pushes', mapper), line_color=None)

            p2.add_tools(HoverTool(
                tooltips=[
                    ('Day', '@day_name'),
                    ('Hour', '@hour'),
                    ('Pushes', '@pushes'),
                ]
            ))
            
            color_bar = ColorBar(color_mapper=mapper, location=(0, 0),
                                 ticker=BasicTicker(desired_num_ticks=len(days)))

            p2.add_layout(color_bar, 'right')
            p2.axis.axis_line_color = None
            p2.axis.major_tick_line_color = None
            p2.axis.major_label_text_font_size = "10pt"
            p2.axis.major_label_standoff = 0
            p2.xaxis.major_label_orientation = 0

            print("Generating plot to commits_heatmap.html...")
            show(p2)
            print("Done.")

        # --- PR Analysis ---
        print("Fetching PR Overview...")
        pr_overview = get_pr_overview(repo_id)
        if pr_overview:
            print("PR Overview:")
            print(f"  Total PRs: {pr_overview.get('pull_requests')}")
            print(f"  PR Creators: {pr_overview.get('pull_request_creators')}")
            print(f"  PR Reviews: {pr_overview.get('pull_request_reviews')}")
            print(f"  PR Reviewers: {pr_overview.get('pull_request_reviewers')}")
        
        print("Fetching PR Size History...")
        df_pr_size = get_pr_size_history(repo_id)
        if not df_pr_size.empty:
            output_file("pr_size_history.html", title=f"PR Size History - {owner}/{repo}")
            
            sizes = ['xs', 's', 'm', 'l', 'xl', 'xxl']
            # Colors for 6 categories
            colors = ["#e8f5e9", "#c8e6c9", "#a5d6a7", "#81c784", "#66bb6a", "#4caf50"] 
            
            p3 = figure(title=f"PR Size Distribution Over Time - {owner}/{repo}",
                        x_axis_type="datetime", width=900, height=400,
                        tools="pan,wheel_zoom,box_zoom,reset")
            
            p3.vbar_stack(sizes, x='date', width=20 * 24 * 3600 * 1000, source=df_pr_size,
                          color=colors, legend_label=sizes)
            
            p3.legend.location = "top_left"
            p3.legend.orientation = "horizontal"
            p3.yaxis.axis_label = "Number of PRs"
            
            print("Generating plot to pr_size_history.html...")
            show(p3)
            print("Done.")

        print("Fetching PR Merge Time...")
        df_merge_time = get_pr_merge_time(repo_id)
        if not df_merge_time.empty:
            output_file("pr_merge_time.html", title=f"PR Merge Time - {owner}/{repo}")
            
            p4 = figure(title=f"Median PR Merge Time (Hours) - {owner}/{repo}",
                        x_axis_type="datetime", width=900, height=400,
                        tools="pan,wheel_zoom,box_zoom,reset")
            
            p4.line(df_merge_time['date'], df_merge_time['p50'], line_width=2, color="navy", legend_label="Median Merge Time")
            p4.circle(df_merge_time['date'], df_merge_time['p50'], size=4, color="navy")
            
            p4.add_tools(HoverTool(
                tooltips=[("Date", "@x{%F}"), ("Median Hours", "@y{0.0}")],
                formatters={"@x": "datetime"}
            ))
            
            p4.yaxis.axis_label = "Hours to Merge"
            
            print("Generating plot to pr_merge_time.html...")
            show(p4)
            print("Done.")

        # --- Issue Analysis ---
        print("Fetching Issue Response Time...")
        df_issue_resp = get_issue_response_time(repo_id)
        if not df_issue_resp.empty:
            output_file("issue_response_time.html", title=f"Issue Response Time - {owner}/{repo}")
            
            p5 = figure(title=f"Median Issue Response Time (Hours) - {owner}/{repo}",
                        x_axis_type="datetime", width=900, height=400,
                        tools="pan,wheel_zoom,box_zoom,reset")
            
            p5.line(df_issue_resp['date'], df_issue_resp['p50'], line_width=2, color="firebrick", legend_label="Median Response Time")
            p5.circle(df_issue_resp['date'], df_issue_resp['p50'], size=4, color="firebrick")
            
            p5.add_tools(HoverTool(
                tooltips=[("Date", "@x{%F}"), ("Median Hours", "@y{0.0}")],
                formatters={"@x": "datetime"}
            ))
            
            p5.yaxis.axis_label = "Hours to First Response"
            
            print("Generating plot to issue_response_time.html...")
            show(p5)
            print("Done.")

        print("Fetching Issue Opened/Closed...")
        df_issue_oc = get_issue_opened_closed(repo_id)
        if not df_issue_oc.empty:
            output_file("issue_opened_closed.html", title=f"Issues Opened vs Closed - {owner}/{repo}")
            
            p6 = figure(title=f"Issues Opened vs Closed - {owner}/{repo}",
                        x_axis_type="datetime", width=900, height=400,
                        tools="pan,wheel_zoom,box_zoom,reset")
            
            p6.line(df_issue_oc['date'], df_issue_oc['opened'], line_width=2, color="green", legend_label="Opened")
            p6.line(df_issue_oc['date'], df_issue_oc['closed'], line_width=2, color="red", legend_label="Closed")
            
            p6.add_tools(HoverTool(
                tooltips=[("Date", "@x{%F}"), ("Opened", "@y"), ("Closed", "@closed")], # Note: @closed might need custom source if not sharing same y
                formatters={"@x": "datetime"}
            ))
            # To make hover work perfectly for both lines, we usually add them as separate renderers or use a shared source with specific tooltips.
            # For simplicity here, we'll just show the plot.
            
            p6.legend.location = "top_left"
            p6.yaxis.axis_label = "Count"
            
            print("Generating plot to issue_opened_closed.html...")
            show(p6)
            print("Done.")

        # --- Geographic Distribution ---
        print("Fetching Geographic Distribution (PR Creators)...")
        df_geo = get_geo_distribution(repo_id, "pr_creators")
        
        if not df_geo.empty:
            output_file("geo_distribution.html", title=f"Geographic Distribution - {owner}/{repo}")
            
            # Top 10 countries
            top10 = df_geo.head(10)
            countries = top10['country_or_area'].astype(str).tolist()
            counts = top10['count'].tolist()
            
            p7 = figure(title="Top 10 Contributor Countries (PR Creators)",
                        x_range=countries, width=800, height=400,
                        tools="hover,pan,wheel_zoom,box_zoom,reset")
            
            p7.vbar(x=countries, top=counts, width=0.6, color="teal")
            
            p7.xaxis.axis_label = "Country"
            p7.yaxis.axis_label = "Number of Contributors"
            p7.y_range.start = 0
            
            p7.add_tools(HoverTool(tooltips=[("Country", "@x"), ("Contributors", "@top")]))
            
            print("Generating plot to geo_distribution.html...")
            show(p7)
            print("Done.")

        # --- Company Distribution ---
        print("Fetching Company Distribution...")
        df_company = get_company_distribution(repo_id)
        
        if not df_company.empty:
            print("Top 10 Companies:")
            print(df_company.head(10))
            
            output_file("company_distribution.html", title=f"Company Distribution - {owner}/{repo}")
            
            # Top 10 companies
            top10_comp = df_company.head(10)
            companies = top10_comp['company_name'].astype(str).tolist()
            counts_comp = top10_comp['code_contributors'].tolist()
            
            p8 = figure(title="Top 10 Contributor Companies",
                        x_range=companies, width=800, height=400,
                        tools="hover,pan,wheel_zoom,box_zoom,reset")
            
            p8.vbar(x=companies, top=counts_comp, width=0.6, color="orange")
            
            p8.xaxis.axis_label = "Company"
            p8.yaxis.axis_label = "Number of Contributors"
            p8.y_range.start = 0
            p8.xaxis.major_label_orientation = 0.785 # 45 degrees
            
            p8.add_tools(HoverTool(tooltips=[("Company", "@x"), ("Contributors", "@top")]))
            
            print("Generating plot to company_distribution.html...")
            show(p8)
            print("Done.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
