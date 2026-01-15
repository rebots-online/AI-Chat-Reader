# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.

"""
Centralized configuration management for AI Chat Reader.

Uses environment variables with sensible defaults for all configuration.
"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Application configuration with environment variable support."""

    # Directory paths
    project_root: Path
    data_dir: Path
    raw_data_dir: Path
    html_output_dir: Path
    assets_dir: Path
    templates_dir: Path

    # Processing options
    default_format: str = "html"
    max_file_size_mb: int = 100
    enable_markdown: bool = True
    enable_search: bool = True

    # Output options
    include_metadata: bool = True
    include_assets: bool = True
    minify_html: bool = False

    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None

    @classmethod
    def from_env(cls, project_root: Optional[Path] = None) -> "Config":
        """
        Create configuration from environment variables with defaults.

        Environment Variables:
            CHAT_DATA_DIR: Root data directory (default: project_root/data)
            CHAT_RAW_DIR: Raw input data directory (default: CHAT_DATA_DIR/raw)
            CHAT_OUTPUT_DIR: HTML output directory (default: CHAT_DATA_DIR/html)
            CHAT_LOG_LEVEL: Logging level (default: INFO)
            CHAT_LOG_FILE: Log file path (optional)

        Args:
            project_root: Project root directory. Defaults to current working directory.

        Returns:
            Config instance with environment overrides applied
        """
        if project_root is None:
            project_root = Path.cwd()

        # Get paths from environment or use defaults
        data_dir = Path(os.environ.get("CHAT_DATA_DIR", project_root / "data"))
        raw_data_dir = Path(os.environ.get("CHAT_RAW_DIR", data_dir / "raw"))
        html_output_dir = Path(os.environ.get("CHAT_OUTPUT_DIR", data_dir / "html"))
        assets_dir = project_root / "scripts" / "assets"
        templates_dir = project_root / "scripts" / "templates"

        # Get log file from environment
        log_file_str = os.environ.get("CHAT_LOG_FILE")
        log_file = Path(log_file_str) if log_file_str else None

        return cls(
            project_root=project_root,
            data_dir=data_dir,
            raw_data_dir=raw_data_dir,
            html_output_dir=html_output_dir,
            assets_dir=assets_dir,
            templates_dir=templates_dir,
            default_format=os.environ.get("CHAT_DEFAULT_FORMAT", "html"),
            max_file_size_mb=int(os.environ.get("CHAT_MAX_FILE_SIZE_MB", "100")),
            enable_markdown=os.environ.get("CHAT_ENABLE_MARKDOWN", "true").lower() == "true",
            enable_search=os.environ.get("CHAT_ENABLE_SEARCH", "true").lower() == "true",
            include_metadata=os.environ.get("CHAT_INCLUDE_METADATA", "true").lower() == "true",
            include_assets=os.environ.get("CHAT_INCLUDE_ASSETS", "true").lower() == "true",
            minify_html=os.environ.get("CHAT_MINIFY_HTML", "false").lower() == "true",
            log_level=os.environ.get("CHAT_LOG_LEVEL", "INFO").upper(),
            log_file=log_file,
        )

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.html_output_dir.mkdir(parents=True, exist_ok=True)


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.

    Returns:
        Config instance (creates one on first call)
    """
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def set_config(config: Config) -> None:
    """
    Set the global configuration instance.

    Args:
        config: Configuration instance to use
    """
    global _config
    _config = config
