from __future__ import print_function

from builtins import object, str
from typing import Dict, Optional, Tuple

from empire.server.common.empire import MainMenu
from empire.server.core.module_models import EmpireModule
from empire.server.utils.module_util import handle_error_message


class Module(object):
    """
    STOP. In most cases you will not need this file.
    Take a look at the wiki: https://bc-security.gitbook.io/empire-wiki/module-development
    """

    @staticmethod
    def generate(
        main_menu: MainMenu,
        module: EmpireModule,
        params: Dict,
        obfuscate: bool = False,
        obfuscation_command: str = "",
    ) -> Tuple[Optional[str], Optional[str]]:
        # First method: Read in the source script from module_source
        module_source = main_menu.installPath + "/data/module_source/..."
        if obfuscate:
            main_menu.obfuscationv2.obfuscate_module(
                module_source=module_source, obfuscation_command=obfuscation_command
            )
            module_source = module_source.replace(
                "module_source", "obfuscated_module_source"
            )
        try:
            f = open(module_source, "r")
        except:
            return handle_error_message(
                "[!] Could not read module source path at: " + str(module_source)
            )

        module_code = f.read()
        f.close()

        # If you'd just like to import a subset of the functions from the
        #   module source, use the following:
        #   script = helpers.generate_dynamic_powershell_script(module_code, ["Get-Something", "Set-Something"])
        script = module_code

        # Second method: For calling your imported source, or holding your
        #   inlined script. If you're importing source using the first method,
        #   ensure that you append to the script variable rather than set.
        #
        # The script should be stripped of comments, with a link to any
        #   original reference script included in the comments.
        #
        # If your script is more than a few lines, it's probably best to use
        #   the first method to source it.
        #
        # script += """
        script = """
function Invoke-Something {

}
Invoke-Something"""

        script_end = ""

        # Add any arguments to the end execution of the script
        for option, values in params.items():
            if option.lower() != "agent":
                if values and values != "":
                    if values.lower() == "true":
                        # if we're just adding a switch
                        script_end += " -" + str(option)
                    else:
                        script_end += " -" + str(option) + " " + str(values)
        if obfuscate:
            script_end = main_menu.obfuscationv2.obfuscate(
                script_end, obfuscation_command
            )
        script += script_end
        script = main_menu.obfuscationv2.obfuscate_keywords(script)

        return script
