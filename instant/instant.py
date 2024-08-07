import click
import os
import sys
from dotenv import load_dotenv

load_dotenv()
# Assuming cli.py is in the root directory of your project
project_root = os.path.dirname(os.path.realpath(__file__))
plugin_folder = os.path.join(os.path.dirname(__file__), 'services')

sys.path.append(plugin_folder)
for service in os.listdir(plugin_folder):
    sys.path.append(os.path.join(plugin_folder, service))
    
class Instant(click.MultiCommand):
    """CLI that dynamically loads subcommands from service folders."""
    
    def list_commands(self, ctx):
        """List available command groups."""
        rv = []
        for service in os.listdir(plugin_folder):
            service_folder = os.path.join(plugin_folder, service)
            if os.path.isdir(service_folder):  # Ensure it's a directory
                rv.append(service)
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        """Get a specific command from the service folder."""
        ns = {}
        fn = os.path.join(plugin_folder, name, f'{name}_cli.py')
        if os.path.exists(fn):
            with open(fn) as f:
                code = compile(f.read(), fn, 'exec')
                eval(code, ns, ns)
        return ns.get('cli')

cli = Instant(help='This tool\'s subcommands are loaded from a '
            'plugin folder dynamically.')

if __name__ == '__main__':
    cli()