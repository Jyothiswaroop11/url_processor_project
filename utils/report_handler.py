import os
import base64
import time
import json
from datetime import datetime
from .config_handler import Configuration


class ReportHandler:
    @staticmethod
    def encode_image_to_base64(image_path):
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                return f"data:image/png;base64,{encoded_string}"
        except Exception as e:
            print(f"Error encoding image: {str(e)}")
            return None

    @staticmethod
    def calculate_stats(results):
        total = len(results)
        passed = sum(1 for r in results if r['status'] == 'Success')
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        total_duration = sum(result.get('load_time', 0) for result in results)
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': pass_rate,
            'total_duration': total_duration
        }

    @staticmethod
    def format_duration(ms):
        total_seconds = ms / 1000
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((ms % 1000))
        return f"{hours}h {minutes}m {seconds}s+{milliseconds:03d}ms"

    @staticmethod
    def get_styles():
        return """
            * { margin: 0; padding: 0; box-sizing: border-box; }

            body { 
                font-family: 'Inter', sans-serif;
                line-height: 1.6;
                background: #f8f9fa;
                color: #333;
            }

            .layout {
                display: flex;
                flex-direction: column;
                height: 100vh;
            }

            /* Stats Bar */
            .stats-bar {
                display: flex;
                justify-content: space-evenly;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            .stat-item {
                text-align: center;
                padding: 10px 25px;
                border-radius: 8px;
                backdrop-filter: blur(5px);
                transition: transform 0.3s ease;
                min-width: 150px;
            }

            .stat-item:hover {
                transform: translateY(-2px);
            }

            .stat-label {
                font-size: 0.8rem;
                color: rgba(255, 255, 255, 0.9);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 5px;
            }

            .stat-value {
                font-size: 1.5rem;
                font-weight: 700;
                transition: color 0.3s ease;
            }

            /* Custom stat colors */
            .stat-item.total {
                background: rgba(255, 255, 255, 0.2);
            }
            .stat-item.total .stat-value {
                color: #FFFFFF;
            }

            .stat-item.passed {
                background: rgba(40, 167, 69, 0.2);
            }
            .stat-item.passed .stat-value {
                color: #28a745;
            }

            .stat-item.failed {
                background: rgba(220, 53, 69, 0.2);
            }
            .stat-item.failed .stat-value {
                color: #dc3545;
            }

            .stat-item.pass-rate {
                background: rgba(255, 255, 255, 0.2);
                transition: all 0.3s ease;
            }

            .stat-item.duration {
                background: rgba(255, 255, 255, 0.2);
            }
            .stat-item.duration .stat-value {
                color: #FFFFFF;
            }

            /* Left Panel */
            .left-panel {
                width: 400px;
                background: white;
                border-right: 1px solid #ddd;
                display: flex;
                flex-direction: column;
            }

            /* URL List item layout */
            .url-item-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 100%;
            }

            .url-info {
                flex: 1;
            }

            .url-header {
                font-size: 0.85rem;
                color: #666;
                font-weight: 600;
                display: block;
            }

            .url-name {
                font-size: 0.9rem;
                word-break: break-all;
                margin-top: 5px;
            }

            .status-badge-container {
                margin-left: 10px;
                display: flex;
                align-items: center;
            }

            /* Filter Section */
            .filter-bar {
                padding: 10px;
                border-bottom: 1px solid #ddd;
                background: #f8f9fa;
            }

            .filter-controls {
                display: flex;
                gap: 5px;
                margin-bottom: 8px;
            }

            .filter-input {
                flex: 1;
                padding: 6px 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 0.8rem;
            }

            .filter-button {
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                background: #2193b0;
                color: white;
                cursor: pointer;
                font-size: 0.8rem;
            }

            .filter-button:hover {
                background: #1a7b93;
            }

            /* URL List */
            .url-list {
                list-style: none;
                overflow-y: auto;
                flex: 1;
            }

            .url-item {
                padding: 10px 15px;
                border-bottom: 1px solid #eee;
                cursor: pointer;
            }

            .url-item:hover {
                background: #f5f5f5;
            }

            .url-item.active {
                background: #e3f2fd;
                border-left: 3px solid #2193b0;
            }

            /* Content Layout */
            .content-wrapper {
                display: flex;
                flex: 1;
                overflow: hidden;
            }

            /* Right Panel */
            .right-panel {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
            }

            .url-content {
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
            }

            /* Status Badges */
            .status-badge {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.7rem;
                font-weight: 600;
                text-transform: uppercase;
            }

            .status-badge.pass { 
                background: #e8f5e9; 
                color: #2e7d32;
            }

            .status-badge.fail { 
                background: #ffebee; 
                color: #c62828;
            }

            .status-badge.info { 
                background: #e3f2fd; 
                color: #1976d2;
            }

            /* Screenshot Controls */
            .control-buttons {
                display: flex;
                gap: 10px;
                margin: 20px 0;
            }

            .control-button {
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-size: 0.8rem;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 5px;
                transition: all 0.3s ease;
            }

            .control-button.screenshot-btn {
                background: #2193b0;
                color: white;
            }

            .control-button.screenshot-btn.active {
                background: #dc3545;
            }

            .control-button.secondary {
                background: #e3f2fd;
                color: #1976d2;
            }

            /* Screenshot Container */
            .screenshot-container {
                display: none;
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            .screenshot {
                width: 100%;
                max-width: 100%;
                height: auto;
                border-radius: 4px;
                display: block;
                margin: 0 auto;
            }

            /* Steps Table */
            .steps-table {
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }

            .steps-table th,
            .steps-table td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #eee;
            }

            .steps-table th {
                background: #1e3c72;
                color: white;
                font-weight: 500;
                font-size: 0.9rem;
            }

            .steps-table tr:hover {
                background-color: #f8f9fa;
            }
        """

    @staticmethod
    def get_scripts():
        return """
            function applyFilters() {
                const searchText = document.getElementById('urlSearch').value.toLowerCase();
                const statusFilter = document.getElementById('statusFilter').value.toLowerCase();

                document.querySelectorAll('.url-item').forEach(item => {
                    const url = item.querySelector('.url-name').textContent.toLowerCase();
                    const statusElement = item.querySelector('.status-badge');
                    const status = statusElement.textContent.trim().toLowerCase();

                    let matchesSearch = url.includes(searchText);
                    let matchesStatus = statusFilter === 'all' || status === statusFilter;

                    item.style.display = matchesSearch && matchesStatus ? 'block' : 'none';
                });
            }

            function toggleScreenshot(index) {
                const container = document.getElementById(`screenshot-container-${index}`);
                const btn = document.getElementById(`screenshot-btn-${index}`);

                if (!container) {
                    console.error(`Screenshot container not found for index ${index}`);
                    return;
                }

                if (container.style.display === 'none' || container.style.display === '') {
                    container.style.display = 'block';
                    btn.innerHTML = '<i class="fas fa-times"></i> Hide Screenshot';
                    btn.classList.add('active');
                } else {
                    container.style.display = 'none';
                    btn.innerHTML = '<i class="fas fa-image"></i> Show Screenshot';
                    btn.classList.remove('active');
                }
            }

            function resetFilters() {
                document.getElementById('urlSearch').value = '';
                document.getElementById('statusFilter').value = 'all';
                document.querySelectorAll('.url-item').forEach(item => {
                    item.style.display = 'block';
                });
            }

            function refreshList() {
                location.reload();
            }

            function showContent(index) {
                document.querySelectorAll('.url-content').forEach(content => {
                    content.style.display = 'none';
                });

                document.getElementById(`content-${index}`).style.display = 'block';

                document.querySelectorAll('.url-item').forEach(item => {
                    item.classList.remove('active');
                });

                const selectedItem = document.querySelector(`[onclick="showContent(${index})"]`);
                if (selectedItem) {
                    selectedItem.classList.add('active');
                }
            }

            function showTestData(index) {
                const dataWindow = window.open('', '_blank', 'width=800,height=600');
                const data = document.getElementById(`test-data-${index}`).textContent;

                dataWindow.document.write(`
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Test Data</title>
                        <style>
                            body {
                                font-family: 'Inter', sans-serif;
                                padding: 20px;
                                margin: 0;
                                background: #f8f9fa;
                            }
                            pre {
                                background: white;
                                padding: 20px;
                                border-radius: 8px;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                overflow: auto;
                                margin: 0;
                            }
                        </style>
                    </head>
                    <body>
                        <pre><code>${JSON.stringify(JSON.parse(data), null, 2)}</code></pre>
                    </body>
                    </html>
                `);
            }

            window.onload = function() {
                const firstItem = document.querySelector('.url-item');
                if (firstItem) {
                    firstItem.click();
                }
            };
        """

    @staticmethod
    def generate_content_section(result, index):
        """Generate HTML content for a single test result."""
        try:
            # Calculate load time for both successful and failed URLs
            load_time = result.get('load_time', 0)
            if load_time == 0 and result.get('start_time'):
                end_time = result.get('end_time', time.time())
                load_time = (end_time - result['start_time']) * 1000

            content = f"""
                <div id="content-{index}" class="url-content" style="display: none;">
                    <!-- URL and Status Summary -->
                    <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 30px;">
                        <div style="flex: 1; min-width: 250px; background: #f8f9fa; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                            <div style="margin-bottom: 10px;">
                                <span style="font-size: 0.9rem; color: #666;">URL</span>
                                <div style="font-weight: 600; word-break: break-all;">{result['url']}</div>
                            </div>
                        </div>

                        <div style="flex: 0 0 auto; min-width: 150px; background: #f8f9fa; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="margin-bottom: 10px;">
                                            <span style="font-size: 0.9rem; color: #666;">Status</span>
                                            <div>
                                                <span class="status-badge {result['status'].lower()}" 
                                                      style="display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 13px; font-weight: 600;">
                                                    {result['status']}
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    <div style="flex: 0 0 auto; min-width: 150px; background: #f8f9fa; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                                        <div style="margin-bottom: 10px;">
                                            <span style="font-size: 0.9rem; color: #666;">Load Time</span>
                                            <div style="font-weight: 600;">{load_time:.2f} ms</div>
                                        </div>
                                    </div>

                                    <div style="flex: 0 0 auto; min-width: 150px; background: #f8f9fa; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                                        <div style="margin-bottom: 10px;">
                                            <span style="font-size: 0.9rem; color: #666;">Timestamp</span>
                                            <div style="font-weight: 600;">{result.get('timestamp', 'N/A')}</div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Test Steps Table -->
                                <div class="steps-section">
                                    <h3 style="margin-bottom: 15px;">Test Steps</h3>
                                    <table class="steps-table">
                                        <thead>
                                            <tr>
                                                <th>Step</th>
                                                <th>Status</th>
                                                <th>Timestamp</th>
                                                <th>Details</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                        """

            # Add all available logs to test steps
            steps = []
            # Add initialization log
            steps.append({
                'status': 'INFO',
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'message': f"Initializing test for URL: {result['url']}"
            })

            # Add Chrome driver initialization log
            steps.append({
                'status': 'INFO',
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'message': "Chrome WebDriver initialized"
            })

            # Add navigation log
            steps.append({
                'status': 'INFO',
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'message': f"Navigating to URL: {result['url']}"
            })

            # Add existing steps
            if result.get('steps'):
                steps.extend(result['steps'])

            # Add error log if present
            if result.get('error'):
                steps.append({
                    'status': 'FAIL',
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'message': f"Error encountered: {result['error']}"
                })

            # Add completion log
            steps.append({
                'status': 'INFO',
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'message': f"Test completed with status: {result['status']}"
            })

            # Add test steps with step numbers
            for step_num, step in enumerate(steps, 1):
                step_status = {
                    'FATAL': 'fail',
                    'PASS': 'pass',
                    'SUCCESS': 'pass',
                    'FAIL': 'fail',
                    'INFO': 'info'
                }.get(step['status'], 'info')

                content += f"""
                                            <tr>
                                                <td>{step_num}</td>
                                                <td>
                                                    <span class="status-badge {step_status}">
                                                        {step['status']}
                                                    </span>
                                                </td>
                                                <td>{step['timestamp']}</td>
                                                <td>{step['message']}</td>
                                            </tr>
                            """

            content += """
                                        </tbody>
                                    </table>
                                </div>
                        """

            # Error section if any
            if result['status'] != 'Success' and result.get('error'):
                content += f"""
                                <div class="error-section" style="margin: 20px 0;">
                                    <h3 style="margin-bottom: 15px; color: #dc3545;">Error Details</h3>
                                    <div class="error-details" style="background: #fff3f3; padding: 15px; border-radius: 8px; border-left: 4px solid #dc3545;">
                                        <pre style="margin: 0; white-space: pre-wrap; word-break: break-all; color: #dc3545;">{result.get('error', 'Unknown error')}</pre>
                                    </div>
                                </div>
                            """

            # Screenshot section
            content += f"""
                            <!-- Control Buttons -->
                            <div class="control-buttons">
                                <button id="screenshot-btn-{index}" 
                                        class="control-button screenshot-btn" 
                                        onclick="toggleScreenshot({index})">
                                    <i class="fas fa-image"></i> Show Screenshot
                                </button>
                                <button class="control-button secondary"
                                        onclick="showTestData({index})">
                                    <i class="fas fa-code"></i> View Test Data
                                </button>
                            </div>

                            <!-- Screenshot Container -->
                            <div id="screenshot-container-{index}" class="screenshot-container">
                        """

            # Screenshot handling
            if result.get('screenshot') and os.path.exists(result['screenshot']):
                try:
                    base64_image = ReportHandler.encode_image_to_base64(result['screenshot'])
                    if base64_image:
                        content += f"""
                                        <div style="background: white; padding: 15px; border-radius: 8px;">
                                            <img src="{base64_image}" 
                                                 class="screenshot" 
                                                 alt="Test Screenshot"
                                                 loading="lazy" />
                                        </div>
                                    """
                    else:
                        content += """
                                        <div style="padding: 20px; text-align: center; color: #dc3545;">
                                            Error loading screenshot image
                                        </div>
                                    """
                except Exception as e:
                    print(f"Error processing screenshot: {str(e)}")
                    content += f"""
                                    <div style="padding: 20px; text-align: center; color: #dc3545;">
                                        Error processing screenshot: {str(e)}
                                    </div>
                                """
            else:
                content += f"""
                                <div style="padding: 20px; text-align: center; color: #666;">
                                    No screenshot available
                                    {f"(File not found: {result.get('screenshot', 'N/A')})" if result.get('screenshot') else ""}
                                </div>
                            """

            content += """
                            </div>
                        """

            # Hidden test data
            content += f"""
                            <div id="test-data-{index}" style="display: none;">
                                {json.dumps(result)}
                            </div>
                        </div>
                        """

            return content

        except Exception as e:
            print(f"Error generating content section: {str(e)}")
            return f"""
                            <div id="content-{index}" class="url-content" style="display: none;">
                                <div class="error-message" style="color: red; padding: 20px;">
                                    Error generating content: {str(e)}
                                </div>
                            </div>
                        """

    @staticmethod
    def generate_html_report(results):
        """Generate complete HTML report from test results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Setup directories
        Configuration.backup_previous_reports()
        report_dir = Configuration.get_path("extent_report")
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

        report_path = os.path.join(report_dir, f"TestReport_{timestamp}.html")
        stats = ReportHandler.calculate_stats(results)

        # Determine pass rate color based on percentage
        def get_pass_rate_color():
            rate = stats['pass_rate']
            if rate < 25:
                return "#8B0000"  # Dark Red
            elif rate < 50:
                return "#FFA07A"  # Light Orange
            elif rate < 75:
                return "#90EE90"  # Light Green
            else:
                return "#228B22"  # Forest Green

        # Generate URL list items
        url_list_items = '''
                    '''.join(f'''
                        <li class="url-item" onclick="showContent({i})">
                            <div class="url-item-content">
                                <div class="url-info">
                                    <span class="url-header">Validating URL: </span>
                                    <span class="url-name">{result['url']}</span>
                                </div>
                                <div class="status-badge-container">
                                    <span class="status-badge {
        'pass' if result['status'] == 'Success' else 'fail'
        }">
                                        {'pass' if result['status'] == 'Success' else 'fail'}
                                    </span>
                                </div>
                            </div>
                        </li>
                    ''' for i, result in enumerate(results))

        # Generate HTML content
        html_content = f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Test Results - {timestamp}</title>
                        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
                        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
                        <style>{ReportHandler.get_styles()}</style>
                        <style>
                            .stat-item.pass-rate .stat-value {{
                                color: {get_pass_rate_color()};
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="layout">
                            <!-- Stats Bar -->
                            <div class="stats-bar">
                                <div class="stat-item total">
                                    <div class="stat-label">Total Tests</div>
                                    <div class="stat-value">{stats['total']}</div>
                                </div>
                                <div class="stat-item passed">
                                    <div class="stat-label">Passed</div>
                                    <div class="stat-value">{stats['passed']}</div>
                                </div>
                                <div class="stat-item failed">
                                    <div class="stat-label">Failed</div>
                                    <div class="stat-value">{stats['failed']}</div>
                                </div>
                                <div class="stat-item pass-rate">
                                    <div class="stat-label">Pass Rate</div>
                                    <div class="stat-value">{stats['pass_rate']:.1f}%</div>
                                </div>
                                <div class="stat-item duration">
                                    <div class="stat-label">Duration</div>
                                    <div class="stat-value">{ReportHandler.format_duration(stats['total_duration'])}</div>
                                </div>
                            </div>

                            <!-- Main Content -->
                            <div class="content-wrapper">
                                <!-- Left Panel -->
                                <div class="left-panel">
                                    <div class="filter-bar">
                                        <div class="filter-controls">
                                            <input type="text" 
                                                   id="urlSearch" 
                                                   class="filter-input" 
                                                   placeholder="Search URLs..."
                                                   oninput="applyFilters()">
                                            <button class="filter-button" 
                                                    onclick="refreshList()" 
                                                    title="Refresh List">
                                                <i class="fas fa-sync-alt"></i>
                                            </button>
                                        </div>
                                        <div class="filter-controls">
                                            <select id="statusFilter" 
                                                    class="filter-input" 
                                                    onchange="applyFilters()">
                                                <option value="all">All Status</option>
                                                <option value="pass">Passed</option>
                                                <option value="fail">Failed</option>
                                            </select>
                                            <button class="filter-button" 
                                                    onclick="resetFilters()" 
                                                    title="Clear Filters">
                                                <i class="fas fa-times"></i> Clear
                                            </button>
                                        </div>
                                    </div>

                                    <ul class="url-list">
                                        {url_list_items}
                                    </ul>
                                </div>

                                <!-- Right Panel -->
                                <div class="right-panel">
                                    {'''
                                    '''.join(ReportHandler.generate_content_section(result, i)
                                             for i, result in enumerate(results))}
                                </div>
                            </div>
                        </div>

                        <script>{ReportHandler.get_scripts()}</script>
                    </body>
                    </html>
                """

        # Write report to file
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return report_path

    @staticmethod
    def create_data_viewer_html(data):
        """Create HTML for the data viewer popup."""
        return f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Test Data Viewer</title>
                        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
                        <style>
                            body {{
                                font-family: 'Inter', sans-serif;
                                line-height: 1.6;
                                padding: 20px;
                                background: #f8f9fa;
                                margin: 0;
                            }}

                            .data-container {{
                                background: white;
                                padding: 20px;
                                border-radius: 8px;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                            }}

                            pre {{
                                margin: 0;
                                white-space: pre-wrap;
                                word-wrap: break-word;
                                font-family: 'Consolas', monospace;
                                font-size: 14px;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="data-container">
                            <pre><code>{json.dumps(data, indent=2)}</code></pre>
                        </div>
                    </body>
                    </html>
                """
