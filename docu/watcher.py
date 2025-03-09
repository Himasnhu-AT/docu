"""
File watching and live preview server functionality.
This module provides capabilities for:
1. Watching for file changes and regenerating documentation
2. Running a live preview server for HTML documentation
"""
import os
import time
import threading
from typing import Callable, List, Optional, Dict, Any
from pathlib import Path
import glob
import json

import livereload
import tornado.web
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .docgen import process_file


class DocuHandler(FileSystemEventHandler):
    """File system event handler for regenerating documentation."""
    
    def __init__(
        self,
        target_paths: List[str],
        output_format: str = 'html',
        output_dir: Optional[str] = None,
        template_name: str = 'default',
        doc_style: str = 'google',
        callback: Optional[Callable[[str], None]] = None,
        verbose: bool = False
    ):
        """Initialize the handler.
        
        Args:
            target_paths: List of file paths to watch
            output_format: Format of the output ('markdown' or 'html')
            output_dir: Directory to save the output file
            template_name: Name of the template to use for HTML output
            doc_style: Documentation style to parse
            callback: Function to call after regenerating documentation
            verbose: Whether to print verbose output
        """
        self.target_paths = {os.path.abspath(path) for path in target_paths}
        self.output_format = output_format
        self.output_dir = output_dir
        self.template_name = template_name
        self.doc_style = doc_style
        self.callback = callback
        self.verbose = verbose
        
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events.
        
        Args:
            event: The file system event
        """
        if event.is_directory:
            return
            
        file_path = os.path.abspath(event.src_path)
        
        # Only process Python files that are in our target paths
        if file_path.endswith('.py') and file_path in self.target_paths:
            if self.verbose:
                print(f"File changed: {file_path}")
                print(f"Regenerating documentation...")
                
            try:
                output = process_file(
                    file_path,
                    output_format=self.output_format,
                    output_dir=self.output_dir,
                    template_name=self.template_name,
                    doc_style=self.doc_style
                )
                
                if self.verbose:
                    if self.output_dir:
                        print(f"Documentation saved to: {output}")
                    else:
                        print("Documentation regenerated")
                
                if self.callback:
                    self.callback(output)
                    
            except Exception as e:
                print(f"Error regenerating documentation: {e}")


def watch_files(
    file_paths: List[str],
    output_format: str = 'html',
    output_dir: Optional[str] = None,
    template_name: str = 'default',
    doc_style: str = 'google',
    callback: Optional[Callable[[str], None]] = None,
    verbose: bool = False
) -> Observer:
    """Watch files for changes and regenerate documentation.
    
    Args:
        file_paths: List of file paths to watch
        output_format: Format of the output ('markdown' or 'html')
        output_dir: Directory to save the output file
        template_name: Name of the template to use for HTML output
        doc_style: Documentation style to parse
        callback: Function to call after regenerating documentation
        verbose: Whether to print verbose output
    
    Returns:
        The file observer, which can be stopped with observer.stop()
    """
    # Get unique directories to watch
    dirs_to_watch = {os.path.dirname(os.path.abspath(file_path)) for file_path in file_paths}
    
    observer = Observer()
    handler = DocuHandler(
        file_paths,
        output_format=output_format,
        output_dir=output_dir,
        template_name=template_name,
        doc_style=doc_style,
        callback=callback,
        verbose=verbose
    )
    
    for directory in dirs_to_watch:
        observer.schedule(handler, directory, recursive=False)
    
    observer.start()
    
    if verbose:
        print(f"Watching {len(file_paths)} files for changes...")
        
    return observer


def create_index_html(directory: str, skip_livereload_script: bool = False) -> str:
    """Create an index.html file in the given directory with links to all documentation files.
    
    Args:
        directory: Directory to scan for HTML and Markdown files
        skip_livereload_script: Whether to skip adding the livereload script
    
    Returns:
        Path to the created index.html file
    """
    # Get all documentation files (HTML and Markdown)
    html_files = glob.glob(os.path.join(directory, "*.html"))
    md_files = glob.glob(os.path.join(directory, "*.md"))
    all_files = html_files + md_files
    
    # Filter out index.html from the list to avoid displaying it
    all_files = [f for f in all_files if os.path.basename(f) != "index.html"]
    
    # Sort files by modification time (newest first)
    all_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    files_html = ""
    
    if not all_files:
        files_html = """
        <div class="no-files">
            <h3>No documentation files found</h3>
            <p>No HTML or Markdown files were found in this directory.</p>
            <p>Try generating documentation first with: <br><code>docu your_file.py --output-dir docs</code></p>
        </div>
        """
    else:
        # Generate HTML file cards
        for file_path in all_files:
            file_name = os.path.basename(file_path)
            mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(file_path)))
            
            # Get file type and try to extract template info for HTML files
            file_ext = os.path.splitext(file_path)[1][1:].upper()
            template_html = ""
            
            if file_ext.lower() == "html":
                # Check if filename contains template info (name_template.html format)
                name_parts = os.path.splitext(file_name)[0].split('_')
                if len(name_parts) > 1:
                    template_html = f'<span class="template-tag">{name_parts[-1]}</span>'
            
            files_html += f"""
            <div class="file-card">
                <a href="{file_name}">{file_name}</a>
                <div class="file-info">
                    {file_ext} document {template_html}
                </div>
                <div class="file-modified">
                    Modified: {mod_time}
                </div>
            </div>
            """
    
    # Create the full HTML file
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Docu: Documentation Index</title>
        <style>
            body {{
                font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
                line-height: 1.6;
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
                color: #333;
            }}
            h1 {{
                border-bottom: 1px solid #eaecef;
                padding-bottom: 0.5rem;
            }}
            .files {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 1rem;
                margin: 2rem 0;
            }}
            .file-card {{
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                padding: 1rem;
                transition: all 0.2s ease;
            }}
            .file-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            .file-card a {{
                text-decoration: none;
                color: #0366d6;
                font-weight: 500;
                font-size: 1.1rem;
                display: block;
                margin-bottom: 0.5rem;
            }}
            .file-info {{
                font-size: 0.9rem;
                color: #666;
            }}
            .template-tag {{
                display: inline-block;
                background: #f1f8ff;
                color: #0366d6;
                border-radius: 3px;
                padding: 0.1rem 0.4rem;
                margin-left: 0.5rem;
                font-size: 0.8rem;
            }}
            .file-modified {{
                margin-top: 0.5rem;
                font-size: 0.85rem;
                color: #888;
            }}
            .footer {{
                margin-top: 2rem;
                padding-top: 1rem;
                border-top: 1px solid #eaecef;
                font-size: 0.9rem;
                color: #666;
            }}
            .no-files {{
                background: #f6f8fa;
                border-radius: 6px;
                padding: 1.5rem;
                text-align: center;
                margin: 2rem 0;
            }}
        </style>
    </head>
    <body>
        <h1>Docu Documentation Index</h1>
        <p>Select a documentation file to view:</p>
        <div class="files">
            {files_html}
        </div>
        <div class="footer">
            <p>Generated by Docu. Access specific files directly by their URL.</p>
            <p><a href="https://github.com/Himasnhu-AT/docu" target="_blank">Docu on GitHub</a></p>
            <p>Directory path: {os.path.abspath(directory)}</p>
            <p>Files found: {len(all_files)}</p>
        </div>
        {'' if skip_livereload_script else '<script src="/livereload.js"></script>'}
    </body>
    </html>
    """
    
    # Write the HTML file to the directory
    index_path = os.path.join(directory, "index.html")
    with open(index_path, "w") as f:
        f.write(html_content)
    
    return index_path


# File list cache to avoid unnecessary index.html updates
_file_list_cache = {}

def should_update_index(directory: str) -> bool:
    """Check if the index.html file needs to be updated.
    
    Args:
        directory: Directory to scan for changes
    
    Returns:
        True if the files have changed since the last check, False otherwise
    """
    global _file_list_cache
    
    # Get all HTML and Markdown files
    html_files = set(glob.glob(os.path.join(directory, "*.html")))
    md_files = set(glob.glob(os.path.join(directory, "*.md")))
    all_files = html_files | md_files
    
    # Remove index.html from the list
    index_path = os.path.join(directory, "index.html")
    if index_path in all_files:
        all_files.remove(index_path)
    
    # Get file names and modification times as a cache key
    current_state = frozenset(
        (os.path.basename(f), os.path.getmtime(f)) 
        for f in all_files
    )
    
    # Check if the state has changed
    cache_key = directory
    if cache_key not in _file_list_cache or _file_list_cache[cache_key] != current_state:
        _file_list_cache[cache_key] = current_state
        return True
    
    return False


def update_index_if_needed(directory: str) -> None:
    """Update the index.html file if the directory contents have changed.
    
    Args:
        directory: Directory to scan for changes
    """
    if should_update_index(directory):
        create_index_html(directory)


def run_livereload_server(
    directory: str,
    port: int = 8000,
    host: str = "localhost",
    verbose: bool = False
) -> None:
    """Run a live reload server for previewing HTML documentation.
    
    Args:
        directory: Directory containing HTML files to serve
        port: Port to run the server on
        host: Host to bind the server to
        verbose: Whether to print verbose output
    """
    # Ensure we have an absolute directory path
    directory = os.path.abspath(directory)
    
    # Create an index.html file for directory listing
    create_index_html(directory)
    
    # Create a standard server
    server = livereload.Server()
    
    # Watch for changes to HTML and Markdown files
    server.watch(os.path.join(directory, "*.html"), lambda: None)
    server.watch(os.path.join(directory, "*.md"), lambda: None)
    
    # Add a handler to update the index.html only when the set of files changes
    # This is essential to prevent the infinite loop
    def safe_update_index():
        update_index_if_needed(directory)
    
    # Watch the directory with a throttled callback
    server.watch(directory, safe_update_index)
    
    if verbose:
        print(f"Starting live preview server at http://{host}:{port}")
        print(f"Serving files from {directory}")
        print(f"Visit http://{host}:{port}/ to see the documentation index")
        print("Press Ctrl+C to stop")
    
    # Serve files from the output directory
    server.serve(port=port, host=host, root=directory)


def watch_and_serve(
    file_paths: List[str],
    output_dir: str,
    template_name: str = 'default',
    doc_style: str = 'google',
    port: int = 8000,
    host: str = "localhost",
    verbose: bool = False
) -> None:
    """Watch files for changes and serve the documentation with live reloading.
    
    Args:
        file_paths: List of file paths to watch
        output_dir: Directory to save and serve the documentation from
        template_name: Name of the template to use for HTML output
        doc_style: Documentation style to parse
        port: Port to run the server on
        host: Host to bind the server to
        verbose: Whether to print verbose output
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate initial documentation for all files
    if verbose:
        print("Generating initial documentation...")
        
    for file_path in file_paths:
        try:
            output = process_file(
                file_path,
                output_format='html',
                output_dir=output_dir,
                template_name=template_name,
                doc_style=doc_style
            )
            if verbose:
                print(f"Generated: {output}")
        except Exception as e:
            print(f"Error generating documentation for {file_path}: {e}")
    
    # Start the file watcher
    observer = watch_files(
        file_paths,
        output_format='html',
        output_dir=output_dir,
        template_name=template_name,
        doc_style=doc_style,
        verbose=verbose
    )
    
    try:
        # Start the livereload server (this will block)
        run_livereload_server(
            directory=output_dir,
            port=port,
            host=host,
            verbose=verbose
        )
    except KeyboardInterrupt:
        observer.stop()
        
    observer.join()