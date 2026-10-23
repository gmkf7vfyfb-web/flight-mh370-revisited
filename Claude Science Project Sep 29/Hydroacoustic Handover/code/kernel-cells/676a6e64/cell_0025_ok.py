print([n for n in dir(host.agents) if not n.startswith('_')])
help(host.agents.update) if hasattr(host.agents,'update') else None
help(host.agents.switch) if hasattr(host.agents,'switch') else None