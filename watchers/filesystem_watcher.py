"""
File System Watcher for AI Employee
Monitors the Inbox folder for new files and creates action items
"""
import time
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from base_watcher import BaseWatcher

class DropFolderHandler(FileSystemEventHandler):
    """Handles file system events in the Inbox folder"""

    def __init__(self, vault_path: Path, logger):
        self.vault_path = vault_path
        self.inbox = vault_path / 'Inbox'
        self.needs_action = vault_path / 'Needs_Action'
        self.logger = logger
        self.processed_files = set()

    def on_created(self, event):
        """Called when a file is created in the Inbox"""
        if event.is_directory:
            return

        source = Path(event.src_path)

        # Avoid processing the same file multiple times
        if source in self.processed_files:
            return

        # Wait a moment to ensure file is fully written
        time.sleep(1)

        try:
            self.logger.info(f'New file detected: {source.name}')
            self.create_action_file(source)
            self.processed_files.add(source)
        except Exception as e:
            self.logger.error(f'Error processing {source.name}: {e}')

    def create_action_file(self, source: Path):
        """Create a markdown file in Needs_Action for the dropped file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        action_file = self.needs_action / f'FILE_{timestamp}_{source.stem}.md'

        # Get file info
        file_size = source.stat().st_size
        file_type = source.suffix

        content = f"""---
type: file_drop
original_name: {source.name}
file_path: {source.absolute()}
size_bytes: {file_size}
file_type: {file_type}
detected: {datetime.now().isoformat()}
priority: medium
status: pending
---

## New File Detected

A new file has been dropped in the Inbox folder and needs processing.

### File Details
- **Name**: {source.name}
- **Size**: {file_size:,} bytes
- **Type**: {file_type}
- **Location**: {source.absolute()}

### Suggested Actions
- [ ] Review file contents
- [ ] Determine appropriate action
- [ ] Process or forward as needed
- [ ] Move to Done when complete

### Notes
Add any relevant notes or context here.
"""

        action_file.write_text(content, encoding='utf-8')
        self.logger.info(f'Created action file: {action_file.name}')

class FileSystemWatcher(BaseWatcher):
    """Watcher that monitors the Inbox folder for new files"""

    def __init__(self, vault_path: str):
        super().__init__(vault_path, check_interval=5)
        self.inbox = self.vault_path / 'Inbox'

        # Ensure Inbox exists
        self.inbox.mkdir(exist_ok=True)

        # Setup watchdog observer
        self.observer = Observer()
        self.event_handler = DropFolderHandler(self.vault_path, self.logger)

    def check_for_updates(self) -> list:
        """Not used in watchdog pattern, but required by base class"""
        return []

    def create_action_file(self, item) -> Path:
        """Not used in watchdog pattern, but required by base class"""
        pass

    def run(self):
        """Start the file system watcher"""
        self.logger.info(f'Starting FileSystemWatcher')
        self.logger.info(f'Monitoring: {self.inbox}')
        self.logger.info('Drop files into the Inbox folder to trigger actions')

        # Schedule the observer
        self.observer.schedule(self.event_handler, str(self.inbox), recursive=False)
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info('Stopping FileSystemWatcher...')
            self.observer.stop()

        self.observer.join()
        self.logger.info('FileSystemWatcher stopped')

if __name__ == '__main__':
    # Get vault path from command line or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        # Default to AI_Employee_Vault in parent directory
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'

    watcher = FileSystemWatcher(str(vault_path))
    watcher.run()
