from flask import has_app_context

def create_database_tracker(app, db, models):
    """Factory function to create DatabaseTracker with initialized dependencies"""
    
    DbLog = models['DbLog']
    ApiLog = models['ApiLog']
    
    class DatabaseTracker:
        def __init__(self):
            self.enabled = app.config.get('DEMO_MODE', False)
        
        def log_query(self, query_type, query, start_time, end_time, result_count=None, database_type='mysql'):
            if not self.enabled:
                return
            
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Format the operation string
            operation = f"{query_type}: {str(query)}"
            
            # Debug output
            print(f"📊 Logging {database_type} query: {operation[:100]}...")
            
            # Create and save the log entry
            log_entry = DbLog(
                operation=operation,
                database_type=database_type,
                response_count=result_count or 0,
                time_taken_ms=round(duration, 2)
            )
            
            try:
                # Ensure we have an active Flask app context
                if not has_app_context():
                    print("❌ No Flask app context for logging")
                    return
                    
                db.session.add(log_entry)
                db.session.commit()
                print(f"✅ Successfully logged {database_type} query")
            except Exception as e:
                # If we can't log to db, just continue - don't break the app
                db.session.rollback()
                print(f"❌ Failed to log {database_type} query: {e}")
                # Also print more details for debugging
                print(f"   Query: {operation}")
                print(f"   Database type: {database_type}")
                print(f"   Error type: {type(e).__name__}")
        
        def get_recent_queries(self):
            # Get last 10 queries from database, most recent first
            try:
                logs = DbLog.query.order_by(DbLog.timestamp.desc()).limit(10).all()
                return [log.to_dict() for log in logs]
            except Exception as e:
                print(f"Failed to get recent queries: {e}")
                return []
        
        def clear_queries(self):
            try:
                DbLog.query.delete()
                db.session.commit()
            except Exception as e:
                db.session.rollback()
        
        def log_api_call(self, endpoint, method, status_code, start_time, end_time, session_id=None, database_type='mysql'):
            if not self.enabled:
                return
            
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Debug output
            print(f"🌐 Logging API call: {method} {endpoint} - {status_code} ({duration:.2f}ms)")
            
            # Create and save the API log entry
            log_entry = ApiLog(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                time_taken_ms=round(duration, 2),
                database_type=database_type,
                session_id=session_id
            )
            
            try:
                # Ensure we have an active Flask app context
                if not has_app_context():
                    print("❌ No Flask app context for API logging")
                    return
                    
                db.session.add(log_entry)
                db.session.commit()
                print(f"✅ Successfully logged API call")
            except Exception as e:
                # If we can't log to db, just continue - don't break the app
                db.session.rollback()
                print(f"❌ Failed to log API call: {e}")
        
        def get_recent_api_logs(self):
            # Get last 20 API logs from database, most recent first
            try:
                logs = ApiLog.query.order_by(ApiLog.timestamp.desc()).limit(20).all()
                return [log.to_dict() for log in logs]
            except Exception as e:
                print(f"Failed to get recent API logs: {e}")
                return []
        
        def clear_api_logs(self):
            try:
                ApiLog.query.delete()
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Failed to clear API logs: {e}")
    
    return DatabaseTracker() 