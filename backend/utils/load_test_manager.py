import asyncio
import aiohttp
import time
import random
import statistics
import json
import os
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import logging
import threading

class LoadTestManager:
    def __init__(self, base_url: str = "http://localhost:5001", suppress_logging: bool = False):
        self.base_url = base_url
        self.session = None
        self.results = {}
        self.suppress_logging = suppress_logging
        self.test_scenarios = {
            # 'products': {'weight': 35, 'endpoint': '/api/products', 'method': 'GET'},
            'category': {'weight': 40, 'endpoint': '/api/products', 'method': 'GET', 'params': {'category': 'random'}},
            # 'search': {'weight': 20, 'endpoint': '/api/products', 'method': 'GET', 'params': {'search': 'random'}},
            'individual': {'weight': 30, 'endpoint': '/api/products/{id}', 'method': 'GET'},
            'cart': {'weight': 30, 'endpoint': '/api/cart', 'method': 'POST'}
        }
        self.search_terms = ['chicken', 'organic', 'fresh', 'milk', 'bread', 'apple', 'cheese', 'pasta', 'rice', 'eggs']
        self.categories = list(range(1, 11))  # Categories 1-10
        self.product_ids = list(range(1, 101))  # Product IDs 1-100
        
        # Progress tracking
        self.progress_lock = threading.Lock()
        self.total_requests = 0
        self.completed_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.start_time = None
        self.last_progress_update = 0
        self.response_times = []  # Track actual response times for live metrics
        
        # Setup logging
        if not suppress_logging:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.disabled = True
    
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _get_weighted_scenario(self) -> str:
        """Select a scenario based on weights"""
        rand_val = random.random() * 100
        cumulative = 0
        
        for scenario, config in self.test_scenarios.items():
            cumulative += config['weight']
            if rand_val <= cumulative:
                return scenario
        
        return 'products'  # Fallback
    
    def _prepare_request(self, scenario: str, session_id: str) -> Dict[str, Any]:
        """Prepare request parameters for a scenario"""
        config = self.test_scenarios[scenario]
        
        request_data = {
            'method': config['method'],
            'endpoint': config['endpoint'],
            'headers': {'User-Agent': f'LoadTest-Session-{session_id}'},
            'params': {'session_id': session_id}
        }
        
        # Add database header (will be set by caller)
        if 'params' in config:
            if 'category' in config['params']:
                request_data['params']['category'] = random.choice(self.categories)
            if 'search' in config['params']:
                request_data['params']['search'] = random.choice(self.search_terms)
        
        if scenario == 'individual':
            request_data['endpoint'] = config['endpoint'].format(id=random.choice(self.product_ids))
        
        if scenario == 'cart':
            request_data['json'] = {
                'product_id': random.choice(self.product_ids),
                'quantity': random.randint(1, 3),
                'session_id': session_id
            }
        
        return request_data
    
    async def _make_request(self, request_data: Dict[str, Any], database: str) -> Dict[str, Any]:
        """Make an HTTP request and measure response time"""
        start_time = time.time()
        endpoint_path = request_data['endpoint']
        try:
            # Add database header
            headers = request_data.get('headers', {})
            headers['X-Database'] = database
            
            # Add suppress logging header during load tests
            if self.suppress_logging:
                headers['X-Suppress-Logging'] = '1'
                
            url = f"{self.base_url}{endpoint_path}"
            
            if not self.session:
                raise RuntimeError("Session not initialized")
            
            async with self.session.request(
                method=request_data['method'],
                url=url,
                headers=headers,
                params=request_data.get('params'),
                json=request_data.get('json')
            ) as response:
                response_time = time.time() - start_time
                content = await response.text()
                
                return {
                    'status_code': response.status,
                    'response_time': response_time,
                    'success': response.status == 200,
                    'content_length': len(content),
                    'error': None,
                    'endpoint': endpoint_path
                }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                'status_code': 0,
                'response_time': response_time,
                'success': False,
                'content_length': 0,
                'error': str(e),
                'endpoint': endpoint_path
            }
    
    def _update_progress(self, database: str, progress_callback: Optional[Callable] = None):
        """Update progress and call callback if provided"""
        with self.progress_lock:
            if progress_callback and self.start_time:
                current_time = time.time()
                elapsed = current_time - self.start_time
                
                # Calculate current RPS
                current_rps = self.completed_requests / elapsed if elapsed > 0 else 0
                
                # Calculate success rate
                success_rate = (self.successful_requests / self.completed_requests * 100) if self.completed_requests > 0 else 0
                
                # Calculate real-time average response time from actual measurements
                avg_response_time = statistics.mean(self.response_times) if self.response_times else 0
                
                # Only call callback every 0.1 seconds to avoid spam
                if current_time - self.last_progress_update > 0.1:
                    progress_callback(database, self.completed_requests, self.total_requests, current_rps, success_rate, self.failed_requests, avg_response_time)
                    self.last_progress_update = current_time
    
    async def _simulate_user(self, user_id: int, database: str, requests_per_user: int, session_id: str,
                           progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """Simulate a single user's load testing"""
        # Use shared session id per database to ensure all requests map to same session
        user_session_id = f"{session_id}_u{user_id}"
        user_results = []
        
        for request_num in range(requests_per_user):
            # Select scenario
            scenario = self._get_weighted_scenario()
            
            # Prepare request
            request_data = self._prepare_request(scenario, user_session_id)
            
            # Make request
            result = await self._make_request(request_data, database)
            result['scenario'] = scenario
            result['user_id'] = user_id
            result['request_num'] = request_num
            
            user_results.append(result)
            
            # Update progress tracking
            with self.progress_lock:
                self.completed_requests += 1
                if result['success']:
                    self.successful_requests += 1
                else:
                    self.failed_requests += 1
                
                # Record response time for live metrics (keep last 100 for performance)
                self.response_times.append(result['response_time'])
                if len(self.response_times) > 100:
                    self.response_times = self.response_times[-100:]
            
            # Update progress callback
            self._update_progress(database, progress_callback)
            
            # Small delay between requests (realistic user behavior)
            await asyncio.sleep(random.uniform(0.1, 0.5))
        
        return user_results
    
    async def run_load_test(self, database: str, concurrent_users: int, requests_per_user: int, 
                          progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Run load test for a specific database"""
        self.logger.info(f"Starting load test for {database} with {concurrent_users} users, {requests_per_user} requests each")
        
        # Initialize progress tracking
        with self.progress_lock:
            self.total_requests = concurrent_users * requests_per_user
            self.completed_requests = 0
            self.successful_requests = 0
            self.failed_requests = 0
            self.start_time = time.time()
            self.last_progress_update = 0
            self.response_times = []  # Reset response times for new test
        
        # Create tasks for all users
        tasks = []
        for user_id in range(concurrent_users):
            # Pass progress_callback to ensure real-time updates
            task = self._simulate_user(
                user_id,
                database,
                requests_per_user,
                f"{database}_session",
                progress_callback,
            )
            tasks.append(task)
        
        # Run all users concurrently
        user_results = await asyncio.gather(*tasks)
        
        # Flatten results
        all_results = []
        for user_result in user_results:
            all_results.extend(user_result)
        
        end_time = time.time()
        total_duration = end_time - self.start_time
        
        # Calculate metrics
        metrics = self._calculate_metrics(all_results, total_duration)
        
        return {
            'database': database,
            'test_config': {
                'concurrent_users': concurrent_users,
                'requests_per_user': requests_per_user,
                'total_requests': len(all_results)
            },
            'duration': total_duration,
            'metrics': metrics,
            'raw_results': all_results
        }
    
    def _calculate_metrics(self, results: List[Dict[str, Any]], total_duration: float) -> Dict[str, Any]:
        """Calculate comprehensive metrics from results"""
        if not results:
            return {}
        
        # Overall metrics
        response_times = [r['response_time'] for r in results]
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        overall_metrics = {
            'total_requests': len(results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(results) * 100,
            'requests_per_second': len(results) / total_duration,
            'avg_response_time': statistics.mean(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'median_response_time': statistics.median(response_times),
            'p95_response_time': self._percentile(response_times, 95),
            'p99_response_time': self._percentile(response_times, 99)
        }
        
        # Scenario-specific metrics
        scenario_metrics = {}
        scenarios = set(r['scenario'] for r in results)
        
        for scenario in scenarios:
            scenario_results = [r for r in results if r['scenario'] == scenario]
            scenario_times = [r['response_time'] for r in scenario_results]
            scenario_success = [r for r in scenario_results if r['success']]
            
            scenario_metrics[scenario] = {
                'total_requests': len(scenario_results),
                'successful_requests': len(scenario_success),
                'success_rate': len(scenario_success) / len(scenario_results) * 100,
                'avg_response_time': statistics.mean(scenario_times),
                'min_response_time': min(scenario_times),
                'max_response_time': max(scenario_times),
                'p95_response_time': self._percentile(scenario_times, 95)
            }
        
        # Error analysis
        error_analysis = {}
        if failed_requests:
            error_map: Dict[str, Dict[str, Any]] = {}
            for req in failed_requests:
                error_key = f"HTTP_{req['status_code']}" if req['status_code'] > 0 else "Network_Error"
                error_entry = error_map.setdefault(error_key, {
                    'count': 0,
                    'message': req['error'] or f"HTTP {req['status_code']}",
                    'endpoints': set()
                })
                error_entry['count'] += 1
                error_entry['endpoints'].add(req.get('endpoint', ''))
            
            # Convert sets to lists for JSON serialization
            for key, val in error_map.items():
                val['endpoints'] = sorted(list(filter(None, val['endpoints'])))
            
            error_analysis = {
                'total_errors': len(failed_requests),
                'error_rate': len(failed_requests) / len(results) * 100,
                'details': error_map
            }
        
        return {
            'overall': overall_metrics,
            'by_scenario': scenario_metrics,
            'errors': error_analysis
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    async def run_comparison_test(self, databases: List[str], concurrent_users: int, 
                                requests_per_user: int, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Run load test across multiple databases for comparison"""
        self.logger.info(f"Starting comparison test across databases: {databases}")
        
        comparison_results = {}
        
        for database in databases:
            self.logger.info(f"Testing database: {database}")
            
            # Run test for this database
            result = await self.run_load_test(database, concurrent_users, requests_per_user, progress_callback)
            comparison_results[database] = result
            
            # Small delay between database tests
            await asyncio.sleep(1)
        
        # Generate comparison summary
        comparison_summary = self._generate_comparison_summary(comparison_results)
        
        return {
            'comparison_summary': comparison_summary,
            'detailed_results': comparison_results,
            'test_timestamp': datetime.now().isoformat()
        }
    
    def _generate_comparison_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary comparing all databases"""
        summary = {
            'performance_ranking': [],
            'key_metrics': {},
            'recommendations': []
        }
        
        # Extract key metrics for comparison
        db_metrics = {}
        for db, result in results.items():
            metrics = result['metrics']['overall']
            db_metrics[db] = {
                'avg_response_time': metrics['avg_response_time'],
                'requests_per_second': metrics['requests_per_second'],
                'success_rate': metrics['success_rate'],
                'p95_response_time': metrics['p95_response_time']
            }
        
        # Ranking by average response time (lower is better)
        ranking = sorted(db_metrics.items(), key=lambda x: x[1]['avg_response_time'])
        summary['performance_ranking'] = [{'database': db, 
                                         'avg_response_time': metrics['avg_response_time'],
                                         'success_rate': metrics['success_rate'],
                                         'throughput': metrics['requests_per_second']} 
                                        for db, metrics in ranking]
        
        # Key metrics summary
        summary['key_metrics'] = {
            'fastest_avg_response': min(db_metrics.values(), key=lambda x: x['avg_response_time']),
            'highest_throughput': max(db_metrics.values(), key=lambda x: x['requests_per_second']),
            'most_reliable': max(db_metrics.values(), key=lambda x: x['success_rate'])
        }
        
        # Generate recommendations
        fastest_db = ranking[0][0]
        summary['recommendations'] = [
            f"{fastest_db} shows the best average response time performance",
            f"Consider {fastest_db} for latency-sensitive applications",
            "Review the detailed metrics for specific use case requirements"
        ]
        
        return summary
    
    def export_results(self, results: Dict[str, Any], format: str = 'json') -> str:
        """Export results in specified format"""
        if format == 'json':
            return json.dumps(results, indent=2)
        elif format == 'summary':
            return self._generate_text_summary(results)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_text_summary(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable text summary"""
        summary_lines = []
        summary_lines.append("=== Load Test Results Summary ===")
        summary_lines.append(f"Test completed at: {results.get('test_timestamp', 'Unknown')}")
        summary_lines.append("")
        
        if 'comparison_summary' in results:
            summary_lines.append("Performance Ranking:")
            for i, rank in enumerate(results['comparison_summary']['performance_ranking'], 1):
                summary_lines.append(f"{i}. {rank['database']}: {rank['avg_response_time']:.3f}s avg response time")
            summary_lines.append("")
            
            summary_lines.append("Recommendations:")
            for rec in results['comparison_summary']['recommendations']:
                summary_lines.append(f"- {rec}")
        
        return "\n".join(summary_lines) 