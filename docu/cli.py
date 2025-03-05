"""
Command-line interface for the docu documentation generator.
"""

import sys
import click
from rich.console import Console
from rich.panel import Panel

from .docgen import process_file


console = Console()


@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['markdown', 'html']), default='html',
              help='Output format for the documentation')
@click.option('--output-dir', '-o', type=click.Path(),
              help='Directory to save the generated documentation')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(file_path, format, output_dir, verbose):
    """Generate documentation from Python files using #/ comments.
    
    FILE_PATH is the path to the Python file to process.
    """
    try:
        if not file_path.endswith('.py'):
            console.print(Panel("[bold red]Error: File must be a Python (.py) file[/bold red]"))
            sys.exit(1)
            
        if verbose:
            console.print(f"[bold blue]Processing file:[/bold blue] {file_path}")
            console.print(f"[bold blue]Output format:[/bold blue] {format}")
            if output_dir:
                console.print(
                    f"[bold blue]Output directory:[/bold blue] {output_dir}"
                )
        
        result = process_file(file_path, output_format=format, output_dir=output_dir)
        
        if output_dir:
            console.print(f"[bold green]Documentation saved to:[/bold green] {result}")
        else:
            if format == 'markdown':
                console.print(
                    Panel.fit(result, title="Generated Documentation (Markdown)")
                )
            else:
                console.print("[bold green]Generated HTML Documentation:[/bold green]")
                console.print(
                    Panel(
                        result[:500] + "..." if len(result) > 500 else result
                    )
                )
                console.print(
                    "[italic]HTML output truncated. Use --output-dir to save the full HTML.[/italic]"
                )
    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if verbose:
            console.print_exception()
        sys.exit(1)


if __name__ == '__main__':
    main()