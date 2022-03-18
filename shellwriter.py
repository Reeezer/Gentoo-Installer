# generates a structured shell file with verbosity and error checking

class ShellWriter:
    """Helper class to write a shell script"""
    
    def __init__(self, path:str, echo:bool=True, warn_autogen:bool=True) -> None:
        self.file = open(path, "w", newline='\n')
        
        # shebang
        self.file.write("#!/bin/sh\n")
        
        if warn_autogen:
            self.add_comment("WARNING! this file has been generated automatically")
        # echo the commands back as they are executed
        if echo:
            self.add_command("set -x", safe=False)
        
    def finalize(self) -> None:
        self.file.close()
    
    def add_command(self, command:str, safe=True) -> None:
        self.file.write(command + (" || exit 1\n" if safe else "\n")) # TODO make the script stop if something fails
        
    def add_comment(self, comment:str, space:bool=False) -> None:
        comment = f"# {comment}"
        if space:
            comment = f"\n{comment}\n"
        self.file.write(comment + "\n")
    
    def add_filevar(self, varname:str, filename:str) -> None:
        """reads a file and puts it in the shell file as a variable"""
        
        with open(filename, 'r') as varfile:
            # FIXME this looks and feels dirty af
            varstr = varfile.read().replace('$', '\\$').replace('"', '\\"').replace('\n', '\\n\n') # avoid problems with bash
            self.file.write(f"{varname}=\"{varstr}\"\n")
