from rloopDefinitionApp import DefinitionGenerator

if __name__ == "__main__":
    generator = DefinitionGenerator()
    generator.load_all()
    generator.save()
