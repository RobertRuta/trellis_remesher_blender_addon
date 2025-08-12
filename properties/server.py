import bpy


def update_api(self, context):
    self.api_url = f"http://{self.server_host}:{self.server_port}"


class AutoRemesherServerProperties(bpy.types.PropertyGroup):
    """Connection/server related settings."""

    server_host: bpy.props.StringProperty(
        name="Host",
        default="localhost",
        description="Server host (usually localhost)",
        update=update_api
    )

    server_port: bpy.props.IntProperty(
        name="Port",
        default=8765,
        description="Server port",
        update=update_api
    )

    advanced_server_config: bpy.props.BoolProperty(
        name="Advanced URL Config",
        default=False,
        description="Enable manual API URL configuration"
    )

    api_url: bpy.props.StringProperty(
        name="API URL",
        default="http://localhost:8765",
        description="Override full URL to the backend API",
    )

    connection_status: bpy.props.StringProperty(
        name="",
        default="Unknown",
        description="Connection check result"
    )
