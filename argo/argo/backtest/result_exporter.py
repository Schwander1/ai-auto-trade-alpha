#!/usr/bin/env python3
"""
Result Exporter
Export backtest results to various formats (CSV, JSON, Excel)
"""
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


class ResultExporter:
    """
    Export backtest results to various formats
    Supports: CSV, JSON, Excel
    """

    @staticmethod
    def export_to_json(
        results: Dict[str, Any],
        filepath: str,
        pretty: bool = True
    ) -> bool:
        """
        Export results to JSON file

        Args:
            results: Dictionary of results to export
            filepath: Output file path
            pretty: If True, format JSON with indentation

        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = Path(filepath)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                if pretty:
                    json.dump(results, f, indent=2, default=str)
                else:
                    json.dump(results, f, default=str)

            logger.info(f"✅ Exported results to JSON: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export JSON: {e}", exc_info=True)
            return False

    @staticmethod
    def export_to_csv(
        results: Dict[str, Any],
        filepath: str,
        flatten: bool = True
    ) -> bool:
        """
        Export results to CSV file

        Args:
            results: Dictionary of results to export
            filepath: Output file path
            flatten: If True, flatten nested dictionaries

        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = Path(filepath)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Flatten results if needed
            if flatten:
                flat_results = ResultExporter._flatten_dict(results)
            else:
                flat_results = results

            # Write CSV
            with open(output_path, 'w', newline='') as f:
                if isinstance(flat_results, list):
                    if flat_results:
                        writer = csv.DictWriter(f, fieldnames=flat_results[0].keys())
                        writer.writeheader()
                        writer.writerows(flat_results)
                elif isinstance(flat_results, dict):
                    writer = csv.DictWriter(f, fieldnames=flat_results.keys())
                    writer.writeheader()
                    writer.writerow(flat_results)

            logger.info(f"✅ Exported results to CSV: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}", exc_info=True)
            return False

    @staticmethod
    def export_to_excel(
        results: Dict[str, Any],
        filepath: str,
        sheet_name: str = "Backtest Results"
    ) -> bool:
        """
        Export results to Excel file

        Args:
            results: Dictionary of results to export
            filepath: Output file path
            sheet_name: Name of the Excel sheet

        Returns:
            True if successful, False otherwise
        """
        if not EXCEL_AVAILABLE:
            logger.error("openpyxl not available - cannot export to Excel")
            return False

        if not PANDAS_AVAILABLE:
            logger.error("pandas not available - cannot export to Excel")
            return False

        try:
            output_path = Path(filepath)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to DataFrame
            if isinstance(results, dict):
                # Single result
                df = pd.DataFrame([ResultExporter._flatten_dict(results)])
            elif isinstance(results, list):
                # Multiple results
                df = pd.DataFrame([ResultExporter._flatten_dict(r) for r in results])
            else:
                logger.error(f"Unsupported results type: {type(results)}")
                return False

            # Write to Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)

            logger.info(f"✅ Exported results to Excel: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export Excel: {e}", exc_info=True)
            return False

    @staticmethod
    def export_metrics_to_csv(
        metrics_list: List[Any],
        filepath: str
    ) -> bool:
        """
        Export list of BacktestMetrics to CSV

        Args:
            metrics_list: List of BacktestMetrics objects
            filepath: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = Path(filepath)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert metrics to dictionaries
            rows = []
            for metrics in metrics_list:
                if hasattr(metrics, '__dict__'):
                    row = metrics.__dict__.copy()
                elif isinstance(metrics, dict):
                    row = metrics.copy()
                else:
                    continue
                rows.append(row)

            if not rows:
                logger.warning("No metrics to export")
                return False

            # Write CSV
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

            logger.info(f"✅ Exported {len(rows)} metrics to CSV: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export metrics CSV: {e}", exc_info=True)
            return False

    @staticmethod
    def export_batch_results(
        batch_results: Dict[str, Any],
        output_dir: str,
        formats: List[str] = ['json', 'csv']
    ) -> Dict[str, bool]:
        """
        Export batch backtest results to multiple formats

        Args:
            batch_results: Results from BatchBacktester
            output_dir: Output directory
            formats: List of formats to export ('json', 'csv', 'excel')

        Returns:
            Dictionary mapping format to success status
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results = {}

        # Export summary
        if 'json' in formats:
            json_file = output_path / f"batch_results_{timestamp}.json"
            results['json'] = ResultExporter.export_to_json(batch_results, str(json_file))

        if 'csv' in formats:
            csv_file = output_path / f"batch_results_{timestamp}.csv"
            results['csv'] = ResultExporter.export_to_csv(batch_results, str(csv_file))

        if 'excel' in formats and EXCEL_AVAILABLE:
            excel_file = output_path / f"batch_results_{timestamp}.xlsx"
            results['excel'] = ResultExporter.export_to_excel(batch_results, str(excel_file))

        # Export individual symbol results if available
        if 'successful' in batch_results:
            metrics_list = list(batch_results['successful'].values())
            if metrics_list:
                metrics_csv = output_path / f"metrics_{timestamp}.csv"
                ResultExporter.export_metrics_to_csv(metrics_list, str(metrics_csv))

        return results

    @staticmethod
    def _flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(ResultExporter._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert list to string representation
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        return dict(items)
