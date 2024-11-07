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

                /* Left Panel - Updated width */
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
                        margin-bottom: 15px;
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
                        border-radius: 8px;
                        padding: 15px;
                        margin-top: 10px;
                    }

                    .screenshot-container.visible {
                        display: block;
                    }

                    .screenshot {
                        width: 100%;
                        height: auto;
                        border-radius: 4px;
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

                function toggleScreenshot(index) {
                    const container = document.getElementById(`screenshot-container-${index}`);
                    const btn = document.getElementById(`screenshot-btn-${index}`);

                    if (container.classList.contains('visible')) {
                        container.classList.remove('visible');
                        btn.innerHTML = '<i class="fas fa-image"></i> Show Screenshot';
                        btn.classList.remove('active');
                    } else {
                        container.classList.add('visible');
                        btn.innerHTML = '<i class="fas fa-times"></i> Hide Screenshot';
                        btn.classList.add('active');
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
        content = f"""
                <div id="content-{index}" class="url-content" style="display: none;">
                    <h2>{result['url']}</h2>

                    <table class="steps-table">
                        <thead>
                            <tr>
                                <th width="15%">Status</th>
                                <th width="20%">Timestamp</th>
                                <th>Details</th>
                            </tr>
                        </thead>
                        <tbody>
            """

        for step in result['steps']:
            step_status = {
                'FATAL': 'fail',
                'PASS': 'pass',
                'SUCCESS': 'pass',
                'FAIL': 'fail',
                'INFO': 'info'
            }.get(step['status'], 'info')

            content += f"""
                    <tr>
                        <td>
                            <span class="status-badge {step_status.lower()}">
                                {step_status.upper()}
                            </span>
                        </td>
                        <td>{step['timestamp']}</td>
                        <td>{step['message']}</td>
                    </tr>
                """

        content += """
                        </tbody>
                    </table>
            """

        if result.get('screenshot'):
            base64_image = ReportHandler.encode_image_to_base64(result['screenshot'])
            if base64_image:
                content += f"""
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
                        <div id="screenshot-container-{index}" class="screenshot-container">
                            <img src="{base64_image}" 
                                 class="screenshot"
                                 alt="Test Screenshot"
                                 loading="lazy" />
                        </div>
                        <div id="test-data-{index}" style="display: none">
                            {json.dumps(result)}
                        </div>
                    """

        content += "</div>"
        return content

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

        # Generate URL list items with updated layout
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