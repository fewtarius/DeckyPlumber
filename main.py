import os
import logging
import decky_plugin
import controller_utils
import device
import file_timeout
import plugin_update
import plugin_settings

class Plugin:
    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        decky_plugin.logger.info("Hello World!")

    async def get_settings(self):
        results = plugin_settings.get_settings()

        try:
            results['pluginVersionNum'] = f'{decky_plugin.DECKY_PLUGIN_VERSION}'

            results['deviceName'] = device.get_device_name()
        except Exception as e:
            decky_plugin.logger.error(e)

        return results

    async def save_per_game_profiles_enabled(self, enabled: bool):
        return plugin_settings.set_setting('perGameProfilesEnabled', enabled)

    async def save_controller_settings(self, payload):
        currentGameId = payload.get('currentGameId')
        controllerProfiles = payload.get('controllerProfiles')
        result = plugin_settings.set_all_controller_profiles(controllerProfiles)

        if currentGameId:
            controller_utils.sync_controller_settings(currentGameId)
        return result

    # sync state in settings.json to actual controller hardware
    async def sync_controller_settings(self, currentGameId):
        return controller_utils.sync_controller_settings(currentGameId)

    async def ota_update(self):
        # trigger ota update
        try:
            with file_timeout.time_limit(15):
                plugin_update.ota_update()
        except Exception as e:
            logging.error(e)

    # Function called first during the unload process, utilize this to handle your plugin being removed
    async def _unload(self):
        decky_plugin.logger.info("Goodbye World!")
        pass

    # Migrations that should be performed before entering `_main()`.
    async def _migration(self):
        decky_plugin.logger.info("Migrations")
        # # Here's a migration example for logs:
        # # - `~/.config/decky-template/template.log` will be migrated to `decky_plugin.DECKY_PLUGIN_LOG_DIR/template.log`
        # decky_plugin.migrate_logs(os.path.join(decky_plugin.DECKY_USER_HOME,
        #                                        ".config", "decky-template", "template.log"))
        # # Here's a migration example for settings:
        # # - `~/homebrew/settings/template.json` is migrated to `decky_plugin.DECKY_PLUGIN_SETTINGS_DIR/template.json`
        # # - `~/.config/decky-template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_SETTINGS_DIR/`
        # decky_plugin.migrate_settings(
        #     os.path.join(decky_plugin.DECKY_HOME, "settings", "template.json"),
        #     os.path.join(decky_plugin.DECKY_USER_HOME, ".config", "decky-template"))
        # # Here's a migration example for runtime data:
        # # - `~/homebrew/template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_RUNTIME_DIR/`
        # # - `~/.local/share/decky-template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_RUNTIME_DIR/`
        # decky_plugin.migrate_runtime(
        #     os.path.join(decky_plugin.DECKY_HOME, "template"),
        #     os.path.join(decky_plugin.DECKY_USER_HOME, ".local", "share", "decky-template"))

    async def log_info(self, info):
        logging.info(info)