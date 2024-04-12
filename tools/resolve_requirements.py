import requests
import sys
import re
from typing import Tuple, Optional
from packaging import version, specifiers

def parse_pip_spec(spec: str) -> Tuple[str, Optional[str]]:
    match = re.match(r'([^=<>!~]+)(.*)', spec)
    if match:
        package_name = match.group(1).strip()
        version_spec = match.group(2).strip() or None
        return package_name, version_spec
    else:
        raise ValueError(f"Invalid package spec: {spec}")

def fetch_package_versions(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        versions = data["releases"].keys()
        print(f"Available versions of {package_name}:")
        return list(versions)
    except requests.RequestException as e:
        print(f"Error fetching package versions: {e}")
        return []

import re

def fetch_required_dist(package_name, version):
    url = f"https://pypi.org/pypi/{package_name}/{version}/json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        requires_dist = data.get('info', {}).get('requires_dist', [])
        
        if not requires_dist:
            print(f"No dependencies found for {package_name} version {version}.")
            return []

        dependencies = []
        for dist in requires_dist:
            dist = dist.split(";")[0].strip()
            match = re.match(r'([^=<>!~]+)(.*)', dist)
            if match:
                pkg_name = match.group(1).strip()
                version_spec = match.group(2).strip() or None
                dependencies.append((pkg_name, version_spec))
        
        print(f"Processed dependencies for {package_name} version {version}: {dependencies}")
        return dependencies
    except requests.RequestException as e:
        print(f"Error fetching required distribution info: {e}")
        return []

def filter_versions(versions, spec):
    specifier = specifiers.SpecifierSet(spec) if spec else specifiers.SpecifierSet()
    return [v for v in versions if v in specifier]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <package_name>")
        sys.exit(1)
    
    pkg_name, version_spec = parse_pip_spec(sys.argv[1])
    candidate_versions = fetch_package_versions(pkg_name)

    if version_spec:
        candidate_versions = filter_versions(candidate_versions, version_spec)
    
    if candidate_versions:
        best_version = max(candidate_versions, key=version.parse)
        print(f"Best matching version: {best_version}")
        required_dist = fetch_required_dist(pkg_name, best_version)
        print(f"Required_dist: {required_dist}")
    else:
        print("No matching versions found.")

