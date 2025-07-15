from flask import request, jsonify
from flask_restful import Resource
import asyncio
import json
import logging
import threading
import time
from datetime import datetime
from utils.load_test_manager import LoadTestManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global test state
test_state = {
    'current_test': None,
    'test_results': {},
    'test_progress': {},
    'test_thread': None,
    'is_running': False,
    'is_paused': False
}

class LoadTestResource(Resource):
    def __init__(self):
        self.load_test_manager = None
    
    def post(self):
        """Start a new load test"""
        try:
            data = request.get_json()
            
            # Validate input
            required_fields = ['databases', 'concurrent_users', 'requests_per_user']
            for field in required_fields:
                if field not in data:
                    return {'error': f'Missing required field: {field}'}, 400
            
            databases = data['databases']
            concurrent_users = data['concurrent_users']
            requests_per_user = data['requests_per_user']
            test_name = data.get('name', f'Load Test {datetime.now().strftime("%Y%m%d_%H%M%S")}')
            
            # Validate databases
            valid_databases = ['mysql', 'aerospike', 'mongodb']
            for db in databases:
                if db not in valid_databases:
                    return {'error': f'Invalid database: {db}. Valid options: {valid_databases}'}, 400
            
            # Validate numeric parameters
            if not isinstance(concurrent_users, int) or concurrent_users <= 0:
                return {'error': 'concurrent_users must be a positive integer'}, 400
            
            if not isinstance(requests_per_user, int) or requests_per_user <= 0:
                return {'error': 'requests_per_user must be a positive integer'}, 400
            
            # Check if already running
            if test_state['is_running']:
                return {'error': 'Another load test is already running'}, 409
            
            # Start the load test in a separate thread
            test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            test_state['current_test'] = test_id
            test_state['is_running'] = True
            test_state['is_paused'] = False
            
            # Initialize progress
            test_state['test_progress'][test_id] = {
                'test_id': test_id,
                'status': 'initializing',
                'current_database': databases[0] if databases else 'unknown',
                'progress_percentage': 0,
                'elapsed_time': 0,
                'estimated_remaining': 0,
                'current_users': 0,
                'requests_completed': 0,
                'requests_total': concurrent_users * requests_per_user * len(databases),
                'current_rps': 0,
                'success_rate': 0,
                'errors': 0,
                'live_metrics': {
                    'response_time': 0,
                    'throughput': 0,
                    'error_rate': 0
                }
            }
            
            # Start test in background thread
            test_thread = threading.Thread(
                target=self._run_background_test,
                args=(test_id, databases, concurrent_users, requests_per_user, test_name)
            )
            test_thread.daemon = True
            test_thread.start()
            test_state['test_thread'] = test_thread
            
            return {
                'status': 'started',
                'test_id': test_id,
                'message': 'Load test started successfully'
            }, 200
            
        except Exception as e:
            logger.error(f"Failed to start load test: {str(e)}")
            return {'error': f'Failed to start load test: {str(e)}'}, 500
    
    def _run_background_test(self, test_id, databases, concurrent_users, requests_per_user, test_name):
        """Run the load test in background thread"""
        try:
            # Update progress
            test_state['test_progress'][test_id]['status'] = 'running'
            
            # Store start time
            start_time = time.time()
            
            # Run the async test
            results = asyncio.run(self._run_async_test(databases, concurrent_users, requests_per_user, test_id))
            
            # Store end time
            end_time = time.time()
            
            # Create complete result structure with configuration
            complete_results = {
                'test_id': test_id,
                'config': {
                    'name': test_name,
                    'databases': databases,
                    'concurrent_users': concurrent_users,
                    'requests_per_user': requests_per_user,
                    'ramp_up_time': 0,
                    'test_duration': 0,
                    'scenarios': {
                        'products': True,
                        'category': True,
                        'search': True,
                        'individual': True,
                        'cart': True
                    },
                    'custom_scenarios': [],
                    'think_time': 0.3,
                    'timeout': 30,
                    'retry_count': 0,
                    'environment': 'test'
                },
                'start_time': datetime.fromtimestamp(start_time).isoformat(),
                'end_time': datetime.fromtimestamp(end_time).isoformat(),
                'duration': end_time - start_time,
                'comparison_summary': results.get('comparison_summary', {}),
                'detailed_results': results.get('detailed_results', {}),
                'test_timestamp': results.get('test_timestamp', datetime.now().isoformat())
            }
            
            # Store results
            test_state['test_results'][test_id] = complete_results
            test_state['test_progress'][test_id]['status'] = 'completed'
            test_state['test_progress'][test_id]['progress_percentage'] = 100
            
        except Exception as e:
            logger.error(f"Load test failed: {str(e)}")
            test_state['test_progress'][test_id]['status'] = 'failed'
            test_state['test_progress'][test_id]['error'] = str(e)
        finally:
            test_state['is_running'] = False
            test_state['current_test'] = None
    
    async def _run_async_test(self, databases, concurrent_users, requests_per_user, test_id):
        """Run the async load test with progress tracking"""
        start_time = time.time()
        
        async with LoadTestManager(suppress_logging=True) as manager:
            # Progress callback function
            def progress_callback(db_name, completed, total, current_rps, success_rate, errors, avg_response_time):
                elapsed = time.time() - start_time
                progress_percent = (completed / total) * 100 if total > 0 else 0
                
                # Update progress
                test_state['test_progress'][test_id].update({
                    'current_database': db_name,
                    'progress_percentage': progress_percent,
                    'elapsed_time': elapsed,
                    'estimated_remaining': (elapsed / (completed / total)) - elapsed if completed > 0 else 0,
                    'current_users': concurrent_users,
                    'requests_completed': completed,
                    'current_rps': current_rps,
                    'success_rate': success_rate,
                    'errors': errors,
                    'live_metrics': {
                        'response_time': avg_response_time * 1000,  # Convert seconds to milliseconds
                        'throughput': current_rps,
                        'error_rate': (errors / completed) * 100 if completed > 0 else 0
                    }
                })
            
            results = await manager.run_comparison_test(
                databases, concurrent_users, requests_per_user, progress_callback
            )
            return results
    
    def get(self):
        """Get information about load testing capabilities"""
        return {
            'available_databases': ['mysql', 'aerospike', 'mongodb'],
            'test_scenarios': {
                'products': {'weight': 35, 'description': 'Get all products'},
                'category': {'weight': 25, 'description': 'Get products by category'},
                'search': {'weight': 20, 'description': 'Search products'},
                'individual': {'weight': 15, 'description': 'Get individual product'},
                'cart': {'weight': 5, 'description': 'Add to cart'}
            },
            'metrics_collected': [
                'response_time', 'throughput', 'success_rate', 'error_analysis',
                'percentiles', 'scenario_breakdown'
            ]
        }, 200

class LoadTestResultsResource(Resource):
    def get(self, test_id):
        """Get results for a specific test"""
        if test_id not in test_state['test_results']:
            return {'error': 'Test not found'}, 404
        
        return test_state['test_results'][test_id], 200

class LoadTestStatusResource(Resource):
    def get(self, test_id=None):
        """Get current load test status"""
        if test_id:
            # Get specific test status
            if test_id not in test_state['test_progress']:
                return {'error': 'Test not found'}, 404
            return test_state['test_progress'][test_id], 200
        else:
            # Get general status
            return {
                'status': 'running' if test_state['is_running'] else 'ready',
                'current_test': test_state['current_test'],
                'is_paused': test_state['is_paused'],
                'available_endpoints': [
                    'POST /api/load-test - Start a new load test',
                    'GET /api/load-test - Get load test capabilities',
                    'GET /api/load-test/results/<test_id> - Get test results',
                    'GET /api/load-test/status - Get current status',
                    'GET /api/load-test/status/<test_id> - Get specific test status',
                    'POST /api/load-test/stop - Stop current test',
                    'POST /api/load-test/pause - Pause current test',
                    'POST /api/load-test/resume - Resume paused test'
                ]
            }, 200

class LoadTestControlResource(Resource):
    def post(self, action):
        """Control load test (stop, pause, resume)"""
        if action == 'stop':
            if not test_state['is_running']:
                return {'error': 'No active load test to stop'}, 400
            
            # Stop the test
            test_state['is_running'] = False
            test_state['is_paused'] = False
            if test_state['current_test']:
                test_state['test_progress'][test_state['current_test']]['status'] = 'stopped'
            
            return {'message': 'Load test stopped'}, 200
        
        elif action == 'pause':
            if not test_state['is_running']:
                return {'error': 'No active load test to pause'}, 400
            
            test_state['is_paused'] = True
            if test_state['current_test']:
                test_state['test_progress'][test_state['current_test']]['status'] = 'paused'
            
            return {'message': 'Load test paused'}, 200
        
        elif action == 'resume':
            if not test_state['is_running'] or not test_state['is_paused']:
                return {'error': 'No paused load test to resume'}, 400
            
            test_state['is_paused'] = False
            if test_state['current_test']:
                test_state['test_progress'][test_state['current_test']]['status'] = 'running'
            
            return {'message': 'Load test resumed'}, 200
        
        else:
            return {'error': 'Invalid action. Use: stop, pause, or resume'}, 400

class LoadTestExportResource(Resource):
    def get(self, test_id):
        """Export test results in different formats"""
        if test_id not in test_state['test_results']:
            return {'error': 'Test not found'}, 404
        
        format_type = request.args.get('format', 'json')
        
        try:
            manager = LoadTestManager()
            results = test_state['test_results'][test_id]
            
            if format_type == 'json':
                return results, 200
            elif format_type == 'summary':
                summary = manager._generate_text_summary(results)
                return {'summary': summary}, 200
            elif format_type == 'csv':
                # Generate CSV format
                csv_data = self._generate_csv_data(results)
                return csv_data, 200, {'Content-Type': 'text/csv'}
            elif format_type == 'pdf':
                # For now, return the summary as PDF would require additional libraries
                return {'message': 'PDF export not yet implemented'}, 501
            else:
                return {'error': 'Invalid format. Use: json, summary, csv, or pdf'}, 400
        
        except Exception as e:
            return {'error': f'Export failed: {str(e)}'}, 500
    
    def _generate_csv_data(self, results):
        """Generate CSV data from test results"""
        csv_lines = []
        csv_lines.append("Database,Avg Response Time (ms),Throughput (req/s),Success Rate (%),Total Requests,Errors")
        
        for db_name, db_results in results.get('detailed_results', {}).items():
            metrics = db_results.get('metrics', {}).get('overall', {})
            csv_lines.append(f"{db_name},{metrics.get('avg_response_time', 0) * 1000:.2f},{metrics.get('requests_per_second', 0):.2f},{metrics.get('success_rate', 0):.2f},{metrics.get('total_requests', 0)},{metrics.get('failed_requests', 0)}")
        
        return '\n'.join(csv_lines)

def create_load_test_resources():
    """Create load test resources with shared state"""
    
    return {
        'LoadTestResource': LoadTestResource,
        'LoadTestResultsResource': LoadTestResultsResource,
        'LoadTestStatusResource': LoadTestStatusResource,
        'LoadTestControlResource': LoadTestControlResource,
        'LoadTestExportResource': LoadTestExportResource
    } 