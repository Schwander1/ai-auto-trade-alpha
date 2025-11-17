#!/usr/bin/env python3
"""
Cleanup Conversation Logs
Automatically removes old conversation logs based on retention policy

LOCAL DEVELOPMENT ONLY - Never runs in production
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add argo to path for environment detection
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root / "argo"))

try:
    from argo.core.environment import detect_environment
    ENVIRONMENT_DETECTION_AVAILABLE = True
except ImportError:
    ENVIRONMENT_DETECTION_AVAILABLE = False
    print("⚠️  Warning: Environment detection not available, defaulting to development")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ConversationCleanup")

# Configuration
WORKSPACE_ROOT = workspace_root
CONVERSATION_LOGS_DIR = WORKSPACE_ROOT / "conversation_logs"
SESSIONS_DIR = CONVERSATION_LOGS_DIR / "sessions"
DECISIONS_DIR = CONVERSATION_LOGS_DIR / "decisions"
INDEX_FILE = CONVERSATION_LOGS_DIR / "index.json"

# Retention policy
CONVERSATION_RETENTION_DAYS = 3
DECISION_RETENTION_DAYS = 30


def should_run() -> bool:
    """Check if cleanup should run (development only)"""
    if not ENVIRONMENT_DETECTION_AVAILABLE:
        logger.warning("Environment detection not available, assuming development")
        return True
    
    env = detect_environment()
    if env == 'production':
        logger.info("🚫 Production environment detected - cleanup disabled")
        return False
    
    logger.info(f"✅ Development environment detected - cleanup enabled")
    return True


def load_index() -> dict:
    """Load searchable index"""
    if not INDEX_FILE.exists():
        return {
            "version": "1.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "sessions": [],
            "decisions": []
        }
    
    try:
        with open(INDEX_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading index: {e}")
        return {
            "version": "1.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "sessions": [],
            "decisions": []
        }


def save_index(index: dict):
    """Save searchable index"""
    index["last_updated"] = datetime.now(timezone.utc).isoformat()
    try:
        with open(INDEX_FILE, 'w') as f:
            json.dump(index, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving index: {e}")


def cleanup_sessions():
    """Remove conversation sessions older than retention period"""
    if not SESSIONS_DIR.exists():
        return 0
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=CONVERSATION_RETENTION_DAYS)
    deleted_count = 0
    
    logger.info(f"🧹 Cleaning up sessions older than {CONVERSATION_RETENTION_DAYS} days (before {cutoff_date.date()})")
    
    # Load index
    index = load_index()
    remaining_sessions = []
    
    # Process date directories
    for date_dir in SESSIONS_DIR.iterdir():
        if not date_dir.is_dir():
            continue
        
        try:
            # Parse date from directory name
            dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d").date()
            
            if dir_date < cutoff_date.date():
                # Delete entire date directory
                for file_path in date_dir.rglob("*"):
                    if file_path.is_file():
                        file_path.unlink()
                        deleted_count += 1
                
                # Remove empty directories
                for subdir in sorted(date_dir.rglob("*"), reverse=True):
                    if subdir.is_dir():
                        try:
                            subdir.rmdir()
                        except OSError:
                            pass
                
                try:
                    date_dir.rmdir()
                except OSError:
                    pass
                
                logger.info(f"  ✅ Deleted session directory: {date_dir.name}")
            else:
                # Keep session, update index
                for file_path in date_dir.rglob("*.md"):
                    rel_path = str(file_path.relative_to(CONVERSATION_LOGS_DIR))
                    # Check if in index
                    for session in index.get("sessions", []):
                        if session.get("file") == rel_path:
                            remaining_sessions.append(session)
                            break
        
        except ValueError:
            # Invalid date format, skip
            logger.warning(f"  ⚠️  Invalid date directory: {date_dir.name}")
            continue
    
    # Update index
    index["sessions"] = remaining_sessions
    save_index(index)
    
    return deleted_count


def cleanup_decisions():
    """Remove decision summaries older than retention period"""
    if not DECISIONS_DIR.exists():
        return 0
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=DECISION_RETENTION_DAYS)
    deleted_count = 0
    
    logger.info(f"🧹 Cleaning up decisions older than {DECISION_RETENTION_DAYS} days (before {cutoff_date.date()})")
    
    # Load index
    index = load_index()
    remaining_decisions = []
    
    # Process date directories
    for date_dir in DECISIONS_DIR.iterdir():
        if not date_dir.is_dir():
            continue
        
        try:
            # Parse date from directory name
            dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d").date()
            
            if dir_date < cutoff_date.date():
                # Delete entire date directory
                for file_path in date_dir.rglob("*"):
                    if file_path.is_file():
                        file_path.unlink()
                        deleted_count += 1
                
                # Remove empty directories
                for subdir in sorted(date_dir.rglob("*"), reverse=True):
                    if subdir.is_dir():
                        try:
                            subdir.rmdir()
                        except OSError:
                            pass
                
                try:
                    date_dir.rmdir()
                except OSError:
                    pass
                
                logger.info(f"  ✅ Deleted decision directory: {date_dir.name}")
            else:
                # Keep decision, update index
                for file_path in date_dir.rglob("*.md"):
                    rel_path = str(file_path.relative_to(DECISIONS_DIR))
                    # Check if in index
                    for decision in index.get("decisions", []):
                        if decision.get("file") == rel_path:
                            remaining_decisions.append(decision)
                            break
        
        except ValueError:
            # Invalid date format, skip
            logger.warning(f"  ⚠️  Invalid date directory: {date_dir.name}")
            continue
    
    # Update index
    index["decisions"] = remaining_decisions
    save_index(index)
    
    return deleted_count


def main():
    """Main cleanup entry point"""
    logger.info("🧹 Starting Conversation Logs Cleanup")
    
    # Check environment
    if not should_run():
        logger.info("Cleanup exiting (production environment)")
        sys.exit(0)
    
    # Ensure directories exist
    CONVERSATION_LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run cleanup
    sessions_deleted = cleanup_sessions()
    decisions_deleted = cleanup_decisions()
    
    logger.info(f"✅ Cleanup complete:")
    logger.info(f"   - Sessions deleted: {sessions_deleted}")
    logger.info(f"   - Decisions deleted: {decisions_deleted}")
    logger.info(f"   - Retention: {CONVERSATION_RETENTION_DAYS} days (sessions), {DECISION_RETENTION_DAYS} days (decisions)")


if __name__ == "__main__":
    main()

