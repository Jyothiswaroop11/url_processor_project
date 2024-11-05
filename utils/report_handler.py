import os
from datetime import datetime
from .config_handler import Configuration


class ReportHandler:
    @staticmethod
    def generate_html_report(results):
        """Generate HTML report with detailed test steps"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create ExtentReport directory if it doesn't exist
        report_dir = os.path.join(Configuration.get_path("reports"), "ExtentReport")
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

        report_path = os.path.join(report_dir, f"TestReport_{timestamp}.html")

        start_time = results[0]['timestamp'] if results else timestamp
        end_time = results[-1]['timestamp'] if results else timestamp
        duration = f"{(results[-1]['load_time'] - results[0]['load_time']) / 1000:.2f}s" if results else "0s"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: white;
                }}
                .header {{
                    margin-bottom: 20px;
                }}
                .title {{
                    font-size: 24px;
                    color: #333;
                    margin-bottom: 10px;
                }}
                .execution-info {{
                    margin-bottom: 15px;
                }}
                .timestamp {{
                    display: inline-block;
                    padding: 5px 10px;
                    color: white;
                    border-radius: 3px;
                    margin-right: 10px;
                    font-size: 12px;
                }}
                .start-time {{
                    background-color: #4CAF50;
                }}
                .end-time {{
                    background-color: #2196F3;
                }}
                .duration {{
                    color: #666;
                    font-size: 12px;
                }}
                .details-table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                .details-table th {{
                    background-color: #f5f5f5;
                    padding: 10px;
                    text-align: left;
                    border: 1px solid #ddd;
                    font-weight: bold;
                    color: #666;
                }}
                .details-table td {{
                    padding: 10px;
                    border: 1px solid #ddd;
                }}
                .status-badge {{
                    display: inline-block;
                    padding: 3px 8px;
                    border-radius: 3px;
                    font-size: 12px;
                    color: white;
                }}
                .Fatal {{
                    background-color: #d9534f;
                }}
                .Pass {{
                    background-color: #5cb85c;
                }}
                .Fail {{
                    background-color: #d9534f;
                }}
                .info-icon {{
                    color: #2196F3;
                    margin-right: 5px;
                }}
                .screenshot {{
                    max-width: 800px;
                    margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">Report</div>
                <div class="execution-info">
                    <span class="timestamp start-time">{start_time}</span>
                    <span class="timestamp end-time">{end_time}</span>
                    <span class="duration">Duration: {duration}</span>
                </div>
            </div>

            <table class="details-table">
                <thead>
                    <tr>
                        <th>STATUS</th>
                        <th>TIMESTAMP</th>
                        <th>DETAILS</th>
                    </tr>
                </thead>
                <tbody>
        """

        for result in results:
            for step in result['steps']:
                status_class = {
                    'FATAL': 'Fatal',
                    'PASS': 'Pass',
                    'SUCCESS': 'Pass',
                    'FAIL': 'Fail',
                    'INFO': 'Pass'
                }.get(step['status'], 'Pass')

                html_content += f"""
                    <tr>
                        <td>
                            <span class="status-badge {status_class}">{step['status']}</span>
                        </td>
                        <td>{step['timestamp']}</td>
                        <td>
                            <span class="info-icon">ℹ</span>
                            {step['message']}
                            {f'<br><img src="{os.path.relpath(step["screenshot"], report_dir)}" class="screenshot"/>' if 'screenshot' in step else ''}
                        </td>
                    </tr>
                """

        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return report_path