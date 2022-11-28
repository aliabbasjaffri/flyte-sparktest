import datetime
import random
from operator import add
import flytekit
from flytekitplugins.spark import Spark
from flytekit import task, workflow
from flytekit.core.resources import Resources
import torch
from pyspark import SparkContext 


@task(requests=Resources(gpu="1"))
def test_spark() -> str:
    msg = torch.cuda.is_available()
    
    sc = SparkContext.getOrCreate() 
    data = range(10000) 
    distData = sc.parallelize(data)
    distData.filter(lambda x: not x&1).take(10)

    return f"Cuda: {msg} .  pyspark output: {distData}"


@task(
    task_config=Spark(
        # this configuration is applied to the spark cluster
        spark_conf={
            "spark.driver.memory": "1000M",
            "spark.executor.memory": "1000M",
            "spark.executor.cores": "1",
            "spark.executor.instances": "2",
            "spark.driver.cores": "1",
        }
    ),
    limits=Resources(mem="2000M"),
    cache_version="1",
    requests=Resources(gpu="1")
)
def hello_spark(partitions: int) -> str:
    print("Starting Spark with Partitions: {}".format(partitions))
    msg = torch.cuda.is_available()

    n = 100000 * partitions
    sess = flytekit.current_context().spark_session
    count = (
        sess.sparkContext.parallelize(range(1, n + 1), partitions).map(f).reduce(add)
    )
    pi_val = 4.0 * count / n
    print("Pi val is :{}".format(pi_val))
    return f"Cuda: {msg} pi_val: {pi_val}"


def f(_):
    x = random.random() * 2 - 1
    y = random.random() * 2 - 1
    return 1 if x**2 + y**2 <= 1 else 0


@task(cache_version="1")
def print_every_time(value_to_print: str, date_triggered: datetime.datetime) -> int:
    print("My printed value: {} @ {}".format(value_to_print, date_triggered))
    return 1


@workflow
def my_wf(triggered_date: datetime.datetime) -> str:
    pi = hello_spark(partitions=100)
    print_every_time(value_to_print=pi, date_triggered=triggered_date)
    res = test_spark()
    return f"pi: {pi}, \nres:{res}"


if __name__ == "__main__":
    print(f"Running my_wf() {my_wf(triggered_date=datetime.datetime.now())}")