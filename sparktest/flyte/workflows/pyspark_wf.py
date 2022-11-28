import datetime
import random
from operator import add

import flytekit
from flytekit import Resources, task, workflow

# %%
# The following import is required to configure a Spark Server in Flyte:
from flytekitplugins.spark import Spark


# %%
# Spark Task Sample
# ^^^^^^^^^^^^^^^^^
#
# This example shows how a Spark task can be written simply by adding a ``@task(task_config=Spark(...)...)`` decorator.
# Refer to `Spark <https://github.com/flyteorg/flytekit/blob/9e156bb0cf3d1441c7d1727729e8f9b4bbc3f168/plugins/flytekit-spark/flytekitplugins/spark/task.py#L18-L36>`__
# class to understand the various configuration options.
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
)
def hello_spark(partitions: int) -> float:
    print("Starting Spark with Partitions: {}".format(partitions))

    n = 100000 * partitions
    sess = flytekit.current_context().spark_session
    count = (
        sess.sparkContext.parallelize(range(1, n + 1), partitions).map(f).reduce(add)
    )
    pi_val = 4.0 * count / n
    print("Pi val is :{}".format(pi_val))
    return pi_val


def f(_):
    x = random.random() * 2 - 1
    y = random.random() * 2 - 1
    return 1 if x**2 + y**2 <= 1 else 0


# %%
# This is a regular python function task. This will not execute on the spark cluster
@task(cache_version="1")
def print_every_time(value_to_print: float, date_triggered: datetime.datetime) -> int:
    print("My printed value: {} @ {}".format(value_to_print, date_triggered))
    return 1


# %%
# The Workflow shows that a spark task and any python function (or any other task type) can be chained together as long as they match the parameter specifications.
@workflow
def my_spark(triggered_date: datetime.datetime) -> float:
    """
    Using the workflow is still as any other workflow. As image is a property of the task, the workflow does not care
    about how the image is configured.
    """
    pi = hello_spark(partitions=50)
    print_every_time(value_to_print=pi, date_triggered=triggered_date)
    return pi


# %%
# Workflows with spark tasks can be executed locally. Some aspects of spark, like links to plugins_hive metastores may not work, but these are limitations of using Spark and are not introduced by Flyte.
if __name__ == "__main__":
    """
    NOTE: To run a multi-image workflow locally, all dependencies of all the tasks should be installed, ignoring which
    may result in local runtime failures.
    """
    print(f"Running {__file__} main...")
    print(
        f"Running my_spark(triggered_date=datetime.datetime.now()){my_spark(triggered_date=datetime.datetime.now())}"
    )
