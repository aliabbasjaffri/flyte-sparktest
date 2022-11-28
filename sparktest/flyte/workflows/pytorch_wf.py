import torch
from flytekit import task, workflow
from flytekit.core.resources import Resources


@task(requests=Resources(gpu="1"))
def say_hello() -> str:
    msg = torch.cuda.is_available()
    return f"hello world, torch is {msg}"


@workflow
def my_wf() -> str:
    res = say_hello()
    return res


if __name__ == "__main__":
    print(f"Running my_wf() {my_wf()}")
