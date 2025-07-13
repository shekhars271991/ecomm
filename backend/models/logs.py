from datetime import datetime

def create_log_models(db):
    """Factory function to create DbLog and ApiLog models with initialized db"""
    
    class DbLog(db.Model):
        __tablename__ = 'db_logs'
        id = db.Column(db.Integer, primary_key=True)
        operation = db.Column(db.String(500), nullable=False)
        database_type = db.Column(db.String(50), nullable=False, default='mysql')  # Track which database was used
        response_count = db.Column(db.Integer, default=0)
        time_taken_ms = db.Column(db.Float, nullable=False)
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'operation': self.operation,
                'database_type': self.database_type,
                'response_count': self.response_count,
                'time_taken_ms': self.time_taken_ms,
                'timestamp': self.timestamp.strftime('%H:%M:%S')
            }

    class ApiLog(db.Model):
        __tablename__ = 'api_logs'
        id = db.Column(db.Integer, primary_key=True)
        endpoint = db.Column(db.String(200), nullable=False)
        method = db.Column(db.String(10), nullable=False)
        status_code = db.Column(db.Integer, nullable=False)
        time_taken_ms = db.Column(db.Float, nullable=False)
        database_type = db.Column(db.String(50), nullable=False, default='mysql')
        session_id = db.Column(db.String(255))
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'endpoint': self.endpoint,
                'method': self.method,
                'status_code': self.status_code,
                'time_taken_ms': self.time_taken_ms,
                'database_type': self.database_type,
                'session_id': self.session_id,
                'timestamp': self.timestamp.strftime('%H:%M:%S')
            }
    
    return DbLog, ApiLog 