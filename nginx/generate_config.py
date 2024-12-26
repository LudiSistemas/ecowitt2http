import yaml
import os

def load_config():
    with open('nginx/config.yml', 'r') as file:
        return yaml.safe_load(file)

def generate_nginx_config():
    config = load_config()
    
    # Set environment variables for template
    os.environ['NGINX_PORT'] = str(config['nginx']['port'])
    os.environ['SERVER_NAME'] = config['nginx']['server_name']
    os.environ['FRONTEND_PORT'] = str(config['services']['frontend']['port'])
    os.environ['BACKEND_PORT'] = str(config['services']['backend']['port'])
    
    # Read template
    with open('nginx/templates/default.conf.template', 'r') as file:
        template = file.read()
    
    # Replace variables
    config_content = template
    for key, value in os.environ.items():
        config_content = config_content.replace(f'${{{key}}}', value)
    
    # Write final config
    os.makedirs('nginx/conf.d', exist_ok=True)
    with open('nginx/conf.d/default.conf', 'w') as file:
        file.write(config_content)

if __name__ == "__main__":
    generate_nginx_config() 