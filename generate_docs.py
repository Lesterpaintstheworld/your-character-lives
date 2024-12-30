"""Documentation generator for CK3 AI Assistant"""

import os
import shutil
import mkdocs.commands.build
from config import Config

def generate_documentation():
    """Generate static documentation website using MkDocs"""
    try:
        # Ensure docs directory exists
        os.makedirs("docs/assets", exist_ok=True)

        # MkDocs configuration
        config = {
            'site_name': 'CK3 AI Assistant',
            'theme': Config.DOCS_THEME,
            'docs_dir': 'docs',
            'site_dir': Config.DOCS_OUTPUT_DIR,
            'nav': [
                {'Home': 'index.md'},
                {'Installation': 'installation.md'},
                {'Usage': 'usage.md'},
                {'API Reference': 'api_reference.md'},
                {'Configuration': 'configuration.md'},
                {'Plugins': 'plugins.md'},
                {'Contributing': 'contributing.md'},
                {'Changelog': 'changelog.md'},
            ]
        }

        # Build documentation
        mkdocs.commands.build.build(config)
        print(f"Documentation generated successfully in {Config.DOCS_OUTPUT_DIR}")
        return True

    except Exception as e:
        print(f"Error generating documentation: {str(e)}")
        return False

if __name__ == "__main__":
    generate_documentation()
