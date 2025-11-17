#!/usr/bin/env python3
"""
Conversation Logger Service
Automatically logs user-AI conversations from Cursor IDE

LOCAL DEVELOPMENT ONLY - Never runs in production
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List
import hashlib

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
logger = logging.getLogger("ConversationLogger")

# Configuration
WORKSPACE_ROOT = workspace_root
CONVERSATION_LOGS_DIR = WORKSPACE_ROOT / "conversation_logs"
SESSIONS_DIR = CONVERSATION_LOGS_DIR / "sessions"
DECISIONS_DIR = CONVERSATION_LOGS_DIR / "decisions"
INDEX_FILE = CONVERSATION_LOGS_DIR / "index.json"

# Cursor conversation storage locations (macOS)
CURSOR_STORAGE_LOCATIONS = [
    Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "workspaceStorage",
    Path.home() / "Library" / "Application Support" / "Cursor" / "logs",
    Path.home() / ".cursor",
    Path.home() / "Library" / "Caches" / "Cursor",
]


def should_run() -> bool:
    """Check if conversation logging should run (development only)"""
    if not ENVIRONMENT_DETECTION_AVAILABLE:
        logger.warning("Environment detection not available, assuming development")
        return True
    
    env = detect_environment()
    if env == 'production':
        logger.info("🚫 Production environment detected - conversation logging disabled")
        return False
    
    logger.info(f"✅ Development environment detected - conversation logging enabled")
    return True


def ensure_directories():
    """Ensure all required directories exist"""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
    CONVERSATION_LOGS_DIR.mkdir(parents=True, exist_ok=True)


def is_cursor_running() -> bool:
    """Check if Cursor application is currently running"""
    try:
        # Check for Cursor process on macOS
        result = subprocess.run(
            ['pgrep', '-f', 'Cursor'],
            capture_output=True,
            text=True,
            timeout=2
        )
        return result.returncode == 0 and len(result.stdout.strip()) > 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        # If pgrep fails, try alternative method
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return 'Cursor' in result.stdout
        except Exception:
            logger.debug(f"Could not check Cursor process: {e}")
            # Assume Cursor is running if we can't check (fail open)
            return True


def find_cursor_storage() -> Optional[Path]:
    """Find Cursor conversation storage location"""
    for location in CURSOR_STORAGE_LOCATIONS:
        if location.exists():
            logger.info(f"📁 Found Cursor storage: {location}")
            return location
    
    logger.warning("⚠️  Cursor storage not found in common locations")
    return None


def load_index() -> Dict:
    """Load or create searchable index"""
    if INDEX_FILE.exists():
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


def save_index(index: Dict):
    """Save searchable index"""
    index["last_updated"] = datetime.now(timezone.utc).isoformat()
    try:
        with open(INDEX_FILE, 'w') as f:
            json.dump(index, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving index: {e}")


def extract_decisions(conversation_text: str) -> List[str]:
    """Extract key decisions from conversation"""
    decisions = []
    lines = conversation_text.split('\n')
    
    # Look for decision indicators
    decision_keywords = [
        "decided", "decision", "implement", "implemented", "chose", "selected",
        "going with", "will use", "using", "adopted", "approved"
    ]
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in decision_keywords):
            # Get context (previous and next lines)
            context_start = max(0, i - 1)
            context_end = min(len(lines), i + 2)
            context = '\n'.join(lines[context_start:context_end])
            decisions.append(context.strip())
    
    return decisions


def log_conversation(conversation_data: Dict, cursor_storage: Optional[Path]):
    """Log a conversation to sessions directory"""
    timestamp = datetime.now(timezone.utc)
    date_str = timestamp.strftime("%Y-%m-%d")
    time_str = timestamp.strftime("%H%M%S")
    
    # Create date directory
    date_dir = SESSIONS_DIR / date_str
    date_dir.mkdir(parents=True, exist_ok=True)
    
    # Create session file
    session_file = date_dir / f"session_{time_str}.md"
    
    # Generate content
    content = f"""# Conversation Session

**Timestamp:** {timestamp.isoformat()}
**Date:** {date_str}
**Time:** {time_str}

---

## Conversation

{conversation_data.get('content', 'No content available')}

---

## Metadata

- **Source:** Cursor IDE
- **Storage Location:** {cursor_storage or 'Unknown'}
- **Hash:** {hashlib.sha256(conversation_data.get('content', '').encode()).hexdigest()[:16]}

"""
    
    try:
        with open(session_file, 'w') as f:
            f.write(content)
        
        logger.info(f"✅ Logged conversation: {session_file}")
        
        # Update index
        index = load_index()
        index["sessions"].append({
            "file": str(session_file.relative_to(CONVERSATION_LOGS_DIR)),
            "timestamp": timestamp.isoformat(),
            "date": date_str,
            "hash": hashlib.sha256(conversation_data.get('content', '').encode()).hexdigest()[:16]
        })
        save_index(index)
        
        # Extract and log decisions
        decisions = extract_decisions(conversation_data.get('content', ''))
        if decisions:
            log_decisions(decisions, timestamp)
        
        return True
    except Exception as e:
        logger.error(f"Error logging conversation: {e}")
        return False


def log_decisions(decisions: List[str], timestamp: datetime):
    """Log extracted decisions to decisions directory"""
    date_str = timestamp.strftime("%Y-%m-%d")
    time_str = timestamp.strftime("%H%M%S")
    
    # Create date directory
    date_dir = DECISIONS_DIR / date_str
    date_dir.mkdir(parents=True, exist_ok=True)
    
    # Create decision file
    decision_file = date_dir / f"decision_{time_str}.md"
    
    content = f"""# Decision Summary

**Timestamp:** {timestamp.isoformat()}
**Date:** {date_str}
**Time:** {time_str}

---

## Decisions

"""
    
    for i, decision in enumerate(decisions, 1):
        content += f"### Decision {i}\n\n{decision}\n\n---\n\n"
    
    try:
        with open(decision_file, 'w') as f:
            f.write(content)
        
        logger.info(f"✅ Logged decisions: {decision_file}")
        
        # Update index
        index = load_index()
        index["decisions"].append({
            "file": str(decision_file.relative_to(CONVERSATION_LOGS_DIR)),
            "timestamp": timestamp.isoformat(),
            "date": date_str,
            "count": len(decisions)
        })
        save_index(index)
        
        return True
    except Exception as e:
        logger.error(f"Error logging decisions: {e}")
        return False


def wait_for_cursor(max_wait_time: int = 300) -> bool:
    """
    Wait for Cursor to start running
    
    Args:
        max_wait_time: Maximum time to wait in seconds (default: 5 minutes)
    
    Returns:
        True if Cursor is running, False if timeout
    """
    check_interval = 30  # Check every 30 seconds
    elapsed = 0
    
    logger.info("⏳ Waiting for Cursor to start...")
    
    while elapsed < max_wait_time:
        if is_cursor_running():
            logger.info("✅ Cursor detected - resuming monitoring")
            return True
        
        time.sleep(check_interval)
        elapsed += check_interval
        
        if elapsed % 60 == 0:  # Log every minute
            logger.debug(f"Still waiting for Cursor... ({elapsed}s elapsed)")
    
    logger.warning(f"⏱️  Timeout waiting for Cursor ({max_wait_time}s)")
    return False


def monitor_cursor_conversations(cursor_storage: Path):
    """Monitor Cursor storage for new conversations (only when Cursor is running)"""
    logger.info(f"🔍 Monitoring Cursor storage: {cursor_storage}")
    
    # Track processed files
    processed_files = set()
    cursor_not_running_count = 0
    
    # Check for conversation files
    conversation_patterns = [
        "**/*conversation*",
        "**/*chat*",
        "**/*message*",
        "**/*.json",
        "**/*.log"
    ]
    
    while True:
        try:
            # Check if Cursor is running before monitoring
            if not is_cursor_running():
                cursor_not_running_count += 1
                
                if cursor_not_running_count == 1:
                    logger.info("💤 Cursor is not running - pausing monitoring")
                    logger.info("   Service will resume automatically when Cursor starts")
                
                # Wait for Cursor to start (check every 30 seconds)
                time.sleep(30)
                continue
            
            # Cursor is running - reset counter and continue monitoring
            if cursor_not_running_count > 0:
                logger.info("✅ Cursor detected - resuming monitoring")
                cursor_not_running_count = 0
            
            # Scan for new files
            new_files = []
            for pattern in conversation_patterns:
                try:
                    for file_path in cursor_storage.rglob(pattern):
                        if file_path.is_file() and str(file_path) not in processed_files:
                            # Check if file is recent (modified in last hour)
                            mtime = file_path.stat().st_mtime
                            if time.time() - mtime < 3600:  # Last hour
                                new_files.append(file_path)
                except (OSError, PermissionError) as e:
                    # Storage might be temporarily unavailable
                    logger.debug(f"Could not access {pattern}: {e}")
                    continue
            
            # Process new files
            for file_path in new_files:
                try:
                    # Read file content
                    if file_path.suffix == '.json':
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            conversation_data = {
                                "content": json.dumps(data, indent=2),
                                "source": str(file_path)
                            }
                    else:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            conversation_data = {
                                "content": content,
                                "source": str(file_path)
                            }
                    
                    # Log conversation
                    log_conversation(conversation_data, cursor_storage)
                    processed_files.add(str(file_path))
                    
                except Exception as e:
                    logger.warning(f"Error processing file {file_path}: {e}")
            
            # Sleep before next check
            time.sleep(60)  # Check every minute
            
        except KeyboardInterrupt:
            logger.info("🛑 Stopping conversation logger service")
            break
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            time.sleep(60)


def main():
    """Main service entry point"""
    logger.info("🚀 Starting Conversation Logger Service")
    
    # Check environment
    if not should_run():
        logger.info("Service exiting (production environment)")
        sys.exit(0)
    
    # Ensure directories exist
    ensure_directories()
    
    # Check if Cursor is running
    if not is_cursor_running():
        logger.info("💤 Cursor is not currently running")
        logger.info("⏳ Waiting for Cursor to start...")
        
        # Wait for Cursor to start (with timeout)
        if not wait_for_cursor(max_wait_time=300):
            logger.warning("⏱️  Cursor not detected after waiting - service will continue checking")
            logger.info("💡 Service will resume automatically when Cursor starts")
    
    # Find Cursor storage
    cursor_storage = find_cursor_storage()
    
    if not cursor_storage:
        logger.warning("⚠️  Cursor storage not found - service will monitor but may not find conversations")
        logger.info("💡 Service will continue running and check periodically")
        logger.info("💡 Service will also wait for Cursor to start if it's not running")
        # Still run but with limited functionality
        while True:
            # Check if Cursor is running
            if is_cursor_running():
                cursor_storage = find_cursor_storage()
                if cursor_storage:
                    break
            time.sleep(300)  # Check every 5 minutes
    
    # Start monitoring
    try:
        monitor_cursor_conversations(cursor_storage)
    except KeyboardInterrupt:
        logger.info("🛑 Service stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

