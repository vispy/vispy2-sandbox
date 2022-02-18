import re

class Command:
    
    CREATE  = "create"
    EXECUTE = "execute"
    REQUEST = "request"
    
    def __init__(self, name, object, method, **kwargs):
        self.name = name
        self.object = object
        self.method = method
        self.parameters = kwargs

    def __str__(self):
        """ Debuf representation """
        
        if self.name == self.CREATE:
            return f"CREATE {self.method}[{self.object}]"
        elif self.name == self.EXECUTE:
            return f"EXECUTE [Object {self.object}].{self.method}(...)"
        elif self.name == self.REQUEST:
            return f"REQUEST [Object {self.object}].{self.method}(...)"
        return "UNKNOWN command"

                
    def call(self, objects="objects"):
        """ String representation that can be evaluated """
        
        # Replace object identification with actual objects
        # "#1" -> objects["#1"]


        if not len(self.parameters):
            params = ""
        else:
            params = "**" + re.sub(r"('#[0-9]+')",
                                   r"%s[\1]" % objects,
                                   str(self.parameters))
        if self.name == Command.CREATE:
            return "%s(%s)"% (self.method, params)
        else:
            return "%s[\"%s\"].%s(%s)" % (
                objects, self.object, self.method, params)
        
    def yaml(self):
        """ Yaml representation """

        s = ""
        s += f"- {self.name}:\n"
        s += f"    object: \"{self.object}\"\n"
        s += f"    method: {self.method}\n"
        s += f"    parameters: "
        if len(self.parameters):
            s += "\n"
            for key, value in self.parameters.items():
                s += f"      {key}: {value}\n"
        else:
            s += "{}\n"
        s += "\n"
        return s


# ----------------------------------------------------------------------------        
if __name__ == "__main__":

    commands = [
        Command(Command.CREATE, "#1", "Framebuffer"),
        Command(Command.CREATE, "#2", "Viewport"),
        Command(Command.CREATE, "#3", "Renderer"),
        Command(Command.EXECUTE, "#3", "clear", viewport = "#2", color="#ffffff"),
        Command(Command.REQUEST, "#3", "render", format = "raw") ]

    for command in commands:
        print(command)
#    for command in commands:
#        print(command.yaml())
#    for command in commands:
#        print(command.call())
