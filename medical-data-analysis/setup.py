from setuptools import setup, find_packages

setup(
    name="notion_integration",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "langchain",
        "notion-client",
        "openai",
        "python-dotenv",
        "pypdf",
        "html2text",
        "python-docx",
        "bs4",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "notion-sync=notion_integration.notion_data_syncer:main",
        ],
    },
) 