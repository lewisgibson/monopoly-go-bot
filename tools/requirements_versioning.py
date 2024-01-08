import pkg_resources

#This is only to be run when you know the current versions of dependencies is working after they've been updated. It will update the requirements.txt file automatically.

with open('requirements.txt', 'r') as file:
    required = {line.split('==')[0].strip() for line in file if line.strip()}

installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}

project_packages = {k: v for k, v in installed_packages.items() if k in required}

with open('requirements.txt', 'w') as file:
    for package, version in project_packages.items():
        file.write(f"{package}=={version}\n")

print("requirements.txt has been updated.")
