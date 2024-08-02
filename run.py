from src.module.yml import Yml

yml_loader = Yml(src="config/config.yml")

yml_loader.load()
