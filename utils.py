import subprocess

def open_with_vim(file_path: str) -> None:
    """
    指定されたファイルをvimで開きます。

    :param file_path: 開くファイルのパス。
    """
    subprocess.run(['vim', file_path])
