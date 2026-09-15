from mcp.server import MCPServer


from config import load_config
from tools.diagnostics import register_diagnostic_tools
from tools.terraform import register_terraform_tools
from tools.docker import register_docker_tools
#from tools.kubernetes import register_kubernetes_tools
#from resources.infrastructure import register_resources
#from prompts.operations import register_prompts


config = load_config()


mcp = MCPServer(config.name)


register_diagnostic_tools(mcp, config)
register_terraform_tools(mcp, config)
register_docker_tools(mcp, config)
#register_kubernetes_tools(mcp, config)


#register_resources(mcp, config)
#register_prompts(mcp, config)



if __name__ == "__main__":
    mcp.run(transport=config.transport)