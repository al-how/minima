from . import server
import asyncio
import sys
import locale

def configure_encoding():
    """Configure proper encoding for the system."""
    if sys.platform == 'win32':
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except locale.Error:
            # Fallback if en_US.UTF-8 is not available
            pass
        
    # Configure stdout/stderr encoding
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def main():
    """Main entry point for the package."""
    # Set up proper encoding before running the async loop
    configure_encoding()
    
    # Run the async server
    asyncio.run(server.main())

# Expose important items at package level
__all__ = ['main', 'server']