#!/usr/bin/env python3
"""
Weekly Report Generator for Argo Capital
Generates performance report every Sunday
"""
import boto3
import os
import sys
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Database paths
if os.path.exists("/root/argo-production"):
    BASE_DIR = Path("/root/argo-production")
else:
    BASE_DIR = Path(__file__).parent.parent.parent.parent

DB_FILE = BASE_DIR / "data" / "signals.db"


def get_performance_metrics():
    """Get performance metrics from database"""
    if not DB_FILE.exists():
        print(f"⚠️  Database not found: {DB_FILE}")
        return None

    try:
        conn = sqlite3.connect(str(DB_FILE))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get date range for this week
        week_start = datetime.now(timezone.utc) - timedelta(days=7)
        week_start_str = week_start.strftime('%Y-%m-%d')

        # Total signals this week
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM signals
            WHERE timestamp >= ?
        """, (week_start_str,))
        total_signals = cursor.fetchone()['total']

        # Completed signals (with outcome)
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN outcome = 'loss' THEN 1 ELSE 0 END) as losses,
                AVG(CASE WHEN outcome = 'win' THEN profit_loss_pct END) as avg_win_pct,
                AVG(CASE WHEN outcome = 'loss' THEN profit_loss_pct END) as avg_loss_pct
            FROM signals
            WHERE timestamp >= ? AND outcome IS NOT NULL
        """, (week_start_str,))
        completed = cursor.fetchone()

        # Premium signals (confidence >= 95)
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN outcome = 'loss' THEN 1 ELSE 0 END) as losses
            FROM signals
            WHERE timestamp >= ? AND confidence >= 95 AND outcome IS NOT NULL
        """, (week_start_str,))
        premium = cursor.fetchone()

        # All-time stats
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN outcome = 'loss' THEN 1 ELSE 0 END) as losses
            FROM signals
            WHERE outcome IS NOT NULL
        """)
        all_time = cursor.fetchone()

        conn.close()

        # Calculate win rates
        completed_total = completed['total'] or 0
        completed_wins = completed['wins'] or 0
        completed_losses = completed['losses'] or 0
        win_rate = (completed_wins / completed_total * 100) if completed_total > 0 else 0

        premium_total = premium['total'] or 0
        premium_wins = premium['wins'] or 0
        premium_win_rate = (premium_wins / premium_total * 100) if premium_total > 0 else 0

        all_time_total = all_time['total'] or 0
        all_time_wins = all_time['wins'] or 0
        all_time_win_rate = (all_time_wins / all_time_total * 100) if all_time_total > 0 else 0

        return {
            'week': {
                'total_signals': total_signals,
                'completed_signals': completed_total,
                'wins': completed_wins,
                'losses': completed_losses,
                'win_rate': round(win_rate, 2),
                'avg_win_pct': round(completed['avg_win_pct'] or 0, 2),
                'avg_loss_pct': round(completed['avg_loss_pct'] or 0, 2),
            },
            'premium': {
                'total': premium_total,
                'wins': premium_wins,
                'win_rate': round(premium_win_rate, 2),
            },
            'all_time': {
                'total': all_time_total,
                'wins': all_time_wins,
                'win_rate': round(all_time_win_rate, 2),
            }
        }
    except Exception as e:
        print(f"⚠️  Error getting metrics: {e}")
        return None


def generate_report():
    """Generate weekly performance report"""
    print(f"📊 Generating weekly report for week ending {datetime.now().strftime('%Y-%m-%d')}")

    try:
        # Get performance metrics
        metrics = get_performance_metrics()

        # Create S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION')
        )

        bucket = os.getenv('AWS_BUCKET_NAME')

        # Create report
        report_filename = f'weekly_report_{datetime.now().strftime("%Y%m%d")}.txt'

        with open(report_filename, 'w') as f:
            f.write(f"Argo Capital Weekly Report\n")
            f.write(f"{'=' * 50}\n")
            f.write(f"Week ending: {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
            f.write(f"\n")

            if metrics:
                f.write(f"WEEKLY PERFORMANCE SUMMARY\n")
                f.write(f"{'-' * 50}\n")
                f.write(f"Total Signals Generated: {metrics['week']['total_signals']}\n")
                f.write(f"Completed Signals: {metrics['week']['completed_signals']}\n")
                f.write(f"  - Wins: {metrics['week']['wins']}\n")
                f.write(f"  - Losses: {metrics['week']['losses']}\n")
                f.write(f"Win Rate: {metrics['week']['win_rate']}%\n")
                f.write(f"Average Win: +{metrics['week']['avg_win_pct']}%\n")
                f.write(f"Average Loss: {metrics['week']['avg_loss_pct']}%\n")
                f.write(f"\n")

                f.write(f"PREMIUM SIGNALS (95%+ Confidence)\n")
                f.write(f"{'-' * 50}\n")
                f.write(f"Total: {metrics['premium']['total']}\n")
                f.write(f"Wins: {metrics['premium']['wins']}\n")
                f.write(f"Premium Win Rate: {metrics['premium']['win_rate']}%\n")
                f.write(f"\n")

                f.write(f"ALL-TIME STATISTICS\n")
                f.write(f"{'-' * 50}\n")
                f.write(f"Total Completed Signals: {metrics['all_time']['total']}\n")
                f.write(f"Total Wins: {metrics['all_time']['wins']}\n")
                f.write(f"All-Time Win Rate: {metrics['all_time']['win_rate']}%\n")
            else:
                f.write(f"Performance Summary:\n")
                f.write(f"- Total Signals: Unable to retrieve\n")
                f.write(f"- Win Rate: Unable to retrieve\n")
                f.write(f"- Premium Win Rate: Unable to retrieve\n")
                f.write(f"\nNote: Database connection failed. Please check database path.\n")

        # Upload to S3
        if bucket:
            s3_key = f'reports/{datetime.now().year}/week_{datetime.now().strftime("%Y%m%d")}.txt'
            s3.upload_file(report_filename, bucket, s3_key)
            print(f"✅ Report uploaded to s3://{bucket}/{s3_key}")
        else:
            print(f"⚠️  AWS_BUCKET_NAME not set, skipping S3 upload")

        # Clean up
        os.remove(report_filename)

        print(f"✅ Weekly report completed successfully")
        return True

    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    generate_report()
