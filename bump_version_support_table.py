import re
import toml

def get_latest_versions_from_cargo(cargo_toml_path: str) -> tuple[str, str]:
    """
    Extracts the plugin version and Bevy version from a Cargo.toml file.

    Args:
        cargo_toml_path (str): Path to the Cargo.toml file.

    Returns:
        tuple: A tuple containing the plugin version and Bevy version.
    """
    with open(cargo_toml_path, "r", encoding="utf-8") as file:
        cargo_data = toml.load(file)

    # Get the plugin version from the `[package]` section
    plugin_version = cargo_data.get("package", {}).get("version", "unknown")

    # remove patch version from plugin version
    plugin_version = plugin_version.rsplit(".", 1)[0]

    # Get the Bevy version from the `[dependencies]` section
    bevy_version = cargo_data.get("dependencies", {}).get("bevy", "unknown")
    
    # Handle cases where Bevy version is a table with features
    if isinstance(bevy_version, dict):
        bevy_version = bevy_version.get("version", "unknown")

    return bevy_version, plugin_version

def update_version_support_table(
    readme_path: str, 
    new_versions: tuple[str, str],
    plugin_name: str
):
    """
    Updates the version support table in a Bevy plugin README file.

    Args:
        readme_path (str): Path to the README.md file.
        new_versions tuple[str, str]: Tuple containing Bevy version and plugin version.
        plugin_name (str): Name of the plugin.
    """
    with open(readme_path, "r", encoding="utf-8") as file:
        readme_content = file.read()

    # Adjust the regex to find the version support table
    table_regex = re.compile(rf"(\| *bevy *\| *{plugin_name} *\|\r?\n\|-+\|\-+\|\r?\n)((\|.+?\|.*\+?\|\r?\n)*)", re.MULTILINE)
    match = table_regex.search(readme_content)

    if not match:
        print("Version support table not found in the README file.")
        return


    # parse existing rows
    versions = match.group(2).split("\n")
    versions = [version.split("|") for version in versions if version]
    versions = [(version[1].strip(), version[2].strip()) for version in versions]
    versions = dict(versions)

    # parse plugin version list
    for key in versions:
        versions[key] = [v.strip() for v in versions[key].split(",")]
        # remove previous main from versions
        versions[key] = [v for v in versions[key] if v != "main"]
    
    bevy_ver, plugin_ver = new_versions
    # add main for current plugin version
    versions[bevy_ver] = versions.get(bevy_ver, []) + [plugin_ver, "main"]

    # sorted versions by key
    versions = sorted(versions.items(), key=lambda x: x[0], reverse=True)

    print (versions)

    rows = ""
    # create new table rows
    for bevy_version, plugin_versions in versions:
        plugin_versions = ", ".join(plugin_versions)
        rows += f"|{bevy_version}|{plugin_versions}|\n"

    updated_content = table_regex.sub(f"\\1{rows}", readme_content)

    with open(readme_path, "w", encoding="utf-8") as file:
        file.write(updated_content)

    print("Version support table updated successfully.")

if __name__ == "__main__":
    readme_path = "README.md"
    cargo_path = "Cargo.toml"
    plugin_name = "bevy_trauma_shake"

    bevy_ver, plugin_ver = get_latest_versions_from_cargo(cargo_path)

    plugin_parts = plugin_ver.split(".")
    plugin_minor = int(plugin_parts[1])
    plugin_major = int(plugin_parts[0])
    if plugin_major == 0:
        plugin_ver = f"{plugin_major}.{plugin_minor + 1}"
    else:
        plugin_ver = f"{plugin_major + 1}.0"

    print(bevy_ver, plugin_ver)

    update_version_support_table(readme_path, (bevy_ver, plugin_ver), plugin_name)
