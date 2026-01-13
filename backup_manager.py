import os
import pymysql
from datetime import datetime
import subprocess
from app import get_db_connection
from config import Config

BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')

def ensure_backup_directory():
    """Create backups directory if it doesn't exist"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    return BACKUP_DIR

def create_backup():
    """Create a database backup"""
    ensure_backup_directory()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"backup_{Config.MYSQL_DB}_{timestamp}.sql"
    
    # Use Python-based backup method (more reliable)
    return create_python_backup(backup_filename)

def create_python_backup(filename):
    """Create backup using Python (fallback method)"""
    backup_path = os.path.join(BACKUP_DIR, filename)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        with open(backup_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"-- MySQL Backup\n")
            f.write(f"-- Database: {Config.MYSQL_DB}\n")
            f.write(f"-- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"SET FOREIGN_KEY_CHECKS=0;\n\n")
            
            # Get all tables
            cursor.execute("SHOW TABLES")
            result = cursor.fetchall()
            
            # Handle the table list extraction (works with both dict and tuple results)
            if result and isinstance(result[0], dict):
                # Get the first key from the dictionary (it will be 'Tables_in_<database_name>')
                table_key = list(result[0].keys())[0]
                tables = [row[table_key] for row in result]
            else:
                tables = [row[0] for row in result]
            
            for table in tables:
                # Get table structure
                cursor.execute(f"SHOW CREATE TABLE `{table}`")
                create_table = cursor.fetchone()
                f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
                f.write(f"{create_table['Create Table']};\n\n")
                
                # Get table data
                cursor.execute(f"SELECT * FROM `{table}`")
                rows = cursor.fetchall()
                
                if rows:
                    # Get column names
                    cursor.execute(f"DESCRIBE `{table}`")
                    columns = [col['Field'] for col in cursor.fetchall()]
                    
                    f.write(f"INSERT INTO `{table}` ({', '.join([f'`{col}`' for col in columns])}) VALUES\n")
                    
                    for i, row in enumerate(rows):
                        values = []
                        for col in columns:
                            val = row[col]
                            if val is None:
                                values.append('NULL')
                            elif isinstance(val, (int, float)):
                                values.append(str(val))
                            elif isinstance(val, datetime):
                                values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                            else:
                                val_str = str(val).replace("'", "\\'").replace("\\", "\\\\")
                                values.append(f"'{val_str}'")
                        
                        if i < len(rows) - 1:
                            f.write(f"({', '.join(values)}),\n")
                        else:
                            f.write(f"({', '.join(values)});\n\n")
            
            f.write("SET FOREIGN_KEY_CHECKS=1;\n")
        
        return backup_path
    finally:
        cursor.close()
        conn.close()

def list_backups():
    """List all available backups"""
    ensure_backup_directory()
    backups = []
    
    for filename in os.listdir(BACKUP_DIR):
        if filename.endswith('.sql'):
            filepath = os.path.join(BACKUP_DIR, filename)
            stat = os.stat(filepath)
            backups.append({
                'filename': filename,
                'filepath': filepath,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_mtime)
            })
    
    return sorted(backups, key=lambda x: x['created'], reverse=True)

def delete_backup(filename):
    """Delete a backup file"""
    filepath = os.path.join(BACKUP_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

def restore_backup(filename):
    """Restore database from backup"""
    filepath = os.path.join(BACKUP_DIR, filename)
    
    if not os.path.exists(filepath):
        raise Exception("Backup file not found")
    
    # Use Python-based restore (more reliable)
    return restore_python_backup(filepath)

def restore_python_backup(filepath):
    """Restore backup using Python (fallback method)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
            # Split by semicolons and execute each statement
            statements = sql_script.split(';\n')
            for statement in statements:
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        cursor.execute(statement)
                    except Exception as e:
                        print(f"Warning: {e}")
            
            conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()

def get_backup_size_total():
    """Get total size of all backups"""
    ensure_backup_directory()
    total = 0
    for filename in os.listdir(BACKUP_DIR):
        if filename.endswith('.sql'):
            filepath = os.path.join(BACKUP_DIR, filename)
            total += os.path.getsize(filepath)
    return total

def cleanup_old_backups(keep_count=10):
    """Delete old backups, keeping only the most recent ones"""
    backups = list_backups()
    if len(backups) > keep_count:
        for backup in backups[keep_count:]:
            delete_backup(backup['filename'])
