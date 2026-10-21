from pathlib import Path


def load_prompt(name:str):
    # 定义路径
    path = Path(__file__).parents[2] / "prompts" / f"{name}.prompt"
    # 读取数据
    return path.read_text(encoding="utf-8")

if __name__ == '__main__':
    print(load_prompt("correct_sql"))
