#!/usr/bin/env python3
"""
PRTG-like Monitoring System
A simple monitoring system that uses ping and SNMP to monitor servers and network devices.
"""

import os
import sys
import json
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from src.monitors.ping_monitor import PingMonitor
from src.monitors.snmp_monitor import SNMPMonitor
from src.database.db_handler import DatabaseHandler
from src.web.app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("monitoring.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def initialize_monitors(db_handler):
    """Initialize all monitoring modules"""
    ping_monitor = PingMonitor(db_handler)
    snmp_monitor = SNMPMonitor(db_handler)
    return ping_monitor, snmp_monitor

def schedule_monitoring_tasks(scheduler, ping_monitor, snmp_monitor):
    """Schedule all monitoring tasks"""
    # Run ping monitoring every minute
    scheduler.add_job(ping_monitor.check_all_hosts, 'interval', minutes=1)
    
    # Run SNMP monitoring every 5 minutes
    scheduler.add_job(snmp_monitor.check_all_devices, 'interval', minutes=5)
    
    logger.info("Monitoring tasks scheduled")

def main():
    """Main application entry point"""
    logger.info("Starting monitoring system")
    
    # Initialize database
    db_handler = DatabaseHandler()
    db_handler.initialize_db()
    
    # Initialize monitors
    ping_monitor, snmp_monitor = initialize_monitors(db_handler)
    
    # Initialize scheduler
    scheduler = BackgroundScheduler()
    schedule_monitoring_tasks(scheduler, ping_monitor, snmp_monitor)
    scheduler.start()
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Start web application with port from config
    app = create_app(db_handler)
    app.run(
        host=config['web']['host'],
        port=config['web']['port'],
        debug=config['web']['debug']
    )

if __name__ == '__main__':
    # الحصول على رقم المنفذ من متغير البيئة أو استخدام المنفذ الافتراضي 10000
    port = int(os.environ.get('PORT', 10000))
    
    # تشغيل التطبيق على العنوان 0.0.0.0 للسماح بالوصول من أي عنوان IP
    app.run(host='0.0.0.0', port=port, debug=True)
