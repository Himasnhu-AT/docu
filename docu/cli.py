"""Command line interface for docu."""
import sys
import argparse
from typing import List, Optional
from .docgen import process_file
from .watcher import watch_files, run_livereload_server, watch_and_serve
import os

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate documentation from Python files'
    )
    parser.add_argument(
        'file_path',
        help='Path to the Python file to document'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'html'],
        default='html',
        help='Output format for the documentation'
    )
    parser.add_argument(
        '--output-dir', '-o',
        help='Directory to save the generated documentation'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--template', '-t',
        default='default',
        help='HTML template name to use (only applies to HTML output)'
    )
    parser.add_argument(
        '--doc-style', '-s',
        choices=['google', 'numpy', 'sphinx'],
        default='google',
        help='Documentation style to parse'
    )
    # Add watch mode argument
    parser.add_argument(
        '--watch', '-w',
        action='store_true',
        help='Watch file for changes and regenerate documentation automatically'
    )
    # Add preview server arguments
    parser.add_argument(
        '--serve', 
        action='store_true',
        help='Start a live preview server for HTML documentation (implies --watch)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port for the live preview server (default: 8000)'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='Host for the live preview server (default: localhost)'
    )
    parser.add_argument(
        '--files',
        nargs='+',
        help='Additional files to watch and generate documentation for (used with --watch or --serve)'
    )
    
    return parser.parse_args(args)

def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.
    Args:
        args: Command line arguments (uses sys.argv if None)
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parsed_args = parse_args(args)
    
    # Check if file exists
    if not os.path.exists(parsed_args.file_path):
        print(f"Error: File not found: {parsed_args.file_path}", file=sys.stderr)
        return 1
    
    # Check if it's a Python file
    if not parsed_args.file_path.endswith('.py'):
        print(f"Error: {parsed_args.file_path} must be a Python (.py) file", file=sys.stderr)
        return 1
    
    # For live preview server, output_dir is required
    if parsed_args.serve and not parsed_args.output_dir:
        print("Error: --output-dir is required when using --serve", file=sys.stderr)
        return 1

    if parsed_args.verbose:
        print(f"Processing file: {parsed_args.file_path}")
        print(f"Output format: {parsed_args.format}")
        if parsed_args.output_dir:
            print(f"Output directory: {parsed_args.output_dir}")
    
    # Collect all files to process
    files_to_process = [parsed_args.file_path]
    if parsed_args.files:
        # Validate additional files
        for file_path in parsed_args.files:
            if not os.path.exists(file_path):
                print(f"Error: Additional file not found: {file_path}", file=sys.stderr)
                return 1
            if not file_path.endswith('.py'):
                print(f"Error: {file_path} must be a Python (.py) file", file=sys.stderr)
                return 1
            files_to_process.append(file_path)
    
    try:
        if parsed_args.serve:
            # Start watch mode with live preview server
            if parsed_args.verbose:
                print("Starting watch mode with live preview server...")
                
            # Force HTML output format when serving
            if parsed_args.format != 'html':
                print("Notice: Switching to HTML format for live preview server")
                
            watch_and_serve(
                file_paths=files_to_process,
                output_dir=parsed_args.output_dir,
                template_name=parsed_args.template,
                doc_style=parsed_args.doc_style,
                port=parsed_args.port,
                host=parsed_args.host,
                verbose=parsed_args.verbose
            )
            return 0
            
        elif parsed_args.watch:
            # Start watch mode without server
            if parsed_args.verbose:
                print("Starting watch mode...")
                
            # First generate the initial documentation
            for file_path in files_to_process:
                output = process_file(
                    file_path,
                    output_format=parsed_args.format,
                    output_dir=parsed_args.output_dir,
                    template_name=parsed_args.template,
                    doc_style=parsed_args.doc_style
                )
                if parsed_args.output_dir:
                    print(f"Documentation saved to: {output}")
                else:
                    print(output)
            
            # Then watch for changes
            observer = watch_files(
                file_paths=files_to_process,
                output_format=parsed_args.format,
                output_dir=parsed_args.output_dir,
                template_name=parsed_args.template,
                doc_style=parsed_args.doc_style,
                verbose=parsed_args.verbose
            )
            
            try:
                print("Watching for file changes. Press Ctrl+C to stop...")
                while True:
                    # Keep the program running
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()
            return 0
        
        else:
            # One-time generation for the main file
            output = process_file(
                parsed_args.file_path,
                output_format=parsed_args.format,
                output_dir=parsed_args.output_dir,
                template_name=parsed_args.template,
                doc_style=parsed_args.doc_style
            )
            if parsed_args.output_dir:
                print(f"Documentation saved to: {output}")
            else:
                print(output)
            
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if parsed_args.verbose:
            raise
        return 1

# Compatibility with Click-style testing
main.name = "main"  # Add name attribute for Click test compatibility

if __name__ == '__main__':
    sys.exit(main())
