import importlib
from typing import Dict, Any, List

from desktop.config.settings import Settings
from desktop.plugins.base import Plugin


class PluginManager:
    def __init__(self, settings: Settings, user_role: str = 'user'):
        self.settings = settings
        self.user_role = user_role or 'user'
        self.plugins: Dict[str, Plugin] = {}
        self._load_plugins()

    def _load_plugins(self):
        plugin_config = self.settings.get_plugin_config()
        available = plugin_config.get('available', {})
        enabled = set(plugin_config.get('enabled', []))
        for plugin_id, meta in available.items():
            module = importlib.import_module(meta['module'])
            cls = getattr(module, meta['class'])
            instance: Plugin = cls(meta.get('config', {}))
            instance.id = plugin_id
            instance.name = meta.get('name', plugin_id)
            instance.description = meta.get('description', '')
            instance.allowed_roles = meta.get('allowed_roles', [])
            if plugin_id in enabled:
                instance.activate()
            self.plugins[plugin_id] = instance

    def list_plugins(self) -> List[Plugin]:
        return list(self.plugins.values())

    def enable_plugin(self, plugin_id: str):
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            return
        plugin.activate()
        cfg = self.settings.get_plugin_config()
        enabled = set(cfg.get('enabled', []))
        enabled.add(plugin_id)
        cfg['enabled'] = list(enabled)
        self.settings.update_plugin_config(cfg)

    def disable_plugin(self, plugin_id: str):
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            return
        plugin.deactivate()
        cfg = self.settings.get_plugin_config()
        enabled = set(cfg.get('enabled', []))
        if plugin_id in enabled:
            enabled.remove(plugin_id)
        cfg['enabled'] = list(enabled)
        self.settings.update_plugin_config(cfg)

    def execute(self, plugin_id: str, query: str) -> str:
        plugin = self.plugins.get(plugin_id)
        if not plugin or not plugin.enabled:
            return 'Плагин недоступен или отключен.'
        if plugin.allowed_roles and self.user_role not in plugin.allowed_roles:
            return 'У вас нет прав для использования этого плагина.'
        return plugin.execute(query)


