from setuptools import setup, find_packages

setup(
    name="open-webui-extensions",
    version="0.1.0",
    description="Extension system for pip-installed Open WebUI",
    author="Open WebUI Team",
    author_email="info@openwebui.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.68.0",
        "pydantic>=1.8.2",
        "uvicorn>=0.15.0",
        "aiofiles>=0.7.0",
        "python-multipart>=0.0.5",
        "PyYAML>=6.0",
        "requests>=2.26.0",
        "jinja2>=3.0.1",
    ],
    entry_points={
        "console_scripts": [
            "webui-extensions=open_webui_extensions.cli:main",
        ],
        "openwebui.plugins": [
            "extensions=open_webui_extensions.plugin:OpenWebUIExtensionsPlugin",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
)
